# core/signal_bridge.py — Signal gateway for mini-alexandria.
#
# Architecture (all local, all on the phone):
#   Signal app <-> Signal servers <-> signal-cli daemon (inside proot Debian)
#        <-JSON-RPC over HTTP->  this bridge  <-> worker/review/memory
#
# Every Signal message from an ALLOWED number becomes one task; the reply
# goes back to that number. Everyone else's messages are ignored.
#
# Started automatically by start.sh when signal.enabled is true, or by hand:
#   python3 core/signal_bridge.py

import json
import os
import subprocess
import sys
import time
import urllib.request

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

from core import worker

PROOT = "proot-distro"
MAX_REPLY_CHARS = 2500


def load_config():
    with open(os.path.join(BASE, "config.json")) as handle:
        config = json.load(handle)
    local_path = os.path.join(BASE, "config.local.json")
    if os.path.exists(local_path):
        with open(local_path) as handle:
            config.update(json.load(handle))
    return config


def rpc(base_url, method, params, request_id, timeout=30):
    body = json.dumps({"jsonrpc": "2.0", "id": request_id,
                       "method": method, "params": params}).encode()
    request = urllib.request.Request(
        base_url + "/api/v1/rpc", data=body,
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read())


def start_daemon(distroname, account, http_port):
    """signal-cli daemon runs inside proot Debian (glibc requirement)."""
    print("[bridge] starting signal-cli daemon inside proot (%s)" % distroname)
    return subprocess.Popen(
        [PROOT, "login", distroname, "--",
         "signal-cli", "-u", account, "daemon", "--http",
         "127.0.0.1:%d" % http_port, "--no-receive-stdout"],
        stdout=open(os.path.join(BASE, "data", "signal-cli.log"), "a"),
        stderr=subprocess.STDOUT)


def wait_http(base_url, tries=40):
    for _ in range(tries):
        try:
            rpc(base_url, "version", {}, 0, timeout=2)
            return True
        except Exception:
            time.sleep(1)
    return False


def normalize_id(value):
    """Lowercase and drop separators so '+1 555 123-4567',
    '+15551234567', and dash-carrying UUIDs compare equal."""
    text = (value or "").strip().lower()
    return text.replace("-", "").replace(" ", "").replace(".", "")


def identifiers(envelope):
    """Every identifier signal-cli may present a sender as. Newer signal-cli
    versions (and username-registered accounts) show UUIDs where older ones
    showed phone numbers — matching on all of them is the point."""
    found = set()
    for key in ("sourceNumber", "source", "sourceUuid"):
        value = envelope.get(key)
        if isinstance(value, str) and value.strip():
            found.add(normalize_id(value))
    return found


def extract_tasks(entry, allowed):
    """Best-effort parse of one receive result — shapes vary by version."""
    out = []
    items = entry if isinstance(entry, list) else [entry]
    for item in items:
        envelope = item.get("envelope", item) if isinstance(item, dict) else {}
        if not isinstance(envelope, dict):
            continue
        sender = (envelope.get("sourceNumber") or envelope.get("source")
                  or envelope.get("sourceUuid") or "unknown")
        data = envelope.get("dataMessage") or {}
        text = (data.get("message") or "").strip() if isinstance(data, dict) else ""
        if not text:
            continue
        if identifiers(envelope) & allowed:
            out.append((sender, text))
        else:
            # Keep this log line: it is THE diagnostic for "bot replies to
            # one person but not another" — it names the identifier the
            # sender's Signal account actually presents.
            print("[signal] message DENIED from %s (identifiers: %s) "
                  "— not in allowed list" % (sender, sorted(identifiers(envelope))))
    return out


def send_reply(base_url, account, recipient, text):
    text = text[:MAX_REPLY_CHARS]
    return rpc(base_url, "send",
               {"account": account, "recipient": [recipient], "message": text},
               int(time.time()))


def main():
    config = load_config()
    signal = config.get("signal", {})
    if not signal.get("enabled"):
        sys.exit("[bridge] signal.enabled is false — nothing to do")
    account = signal.get("account")
    allowed = set(normalize_id(value) for value in signal.get("allowed", []))
    distroname = signal.get("proot_distro", "debian")
    port = int(signal.get("daemon_http_port", 8080))
    base_url = "http://127.0.0.1:%d" % port

    if not account:
        sys.exit("[bridge] signal.account missing (put the number in config.local.json)")
    if not allowed:
        sys.exit("[bridge] signal.allowed is empty — nobody may trigger the agents")

    proc = start_daemon(distroname, account, port)
    if not wait_http(base_url):
        print("[bridge] daemon did not answer after 40s — see data/signal-cli.log")
        proc.terminate()
        sys.exit(1)
    print("[bridge] signal-cli daemon up (http %s). poll %ds. allowed: %s"
          % (base_url, signal.get("poll_seconds", 3), sorted(allowed)))

    request_id = 100
    while True:
        try:
            answer = rpc(base_url, "receive",
                         {"account": account, "timeout": 4}, request_id)
            request_id += 1
            result = answer.get("result")
            if result:
                for sender, text in extract_tasks(result, allowed):
                    print("[signal] task from %s: %s" % (sender, text[:80]))
                    try:
                        reply = worker.run_task(
                            worker.llm.LLM(config["backend_url"], config["model"]),
                            text, config, do_review=config.get("signal_review", False),
                            source="signal")
                    except Exception as error:
                        reply = "agents had a problem: %s" % error
                    print("[signal] replying to %s" % sender)
                    send_reply(base_url, account, sender, reply)
            else:
                time.sleep(signal.get("poll_seconds", 3))
        except KeyboardInterrupt:
            print("[bridge] stopping")
            proc.terminate()
            return
        except Exception as error:
            print("[bridge] poll error (continuing): %s" % error)
            time.sleep(5)


if __name__ == "__main__":
    main()