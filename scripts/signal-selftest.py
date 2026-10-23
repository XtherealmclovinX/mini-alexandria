# scripts/signal-selftest.py — prove the Signal layer before real use.
# Run AFTER ./start.sh (bridge + daemon must be up). Checks:
#   1. config present    2. daemon answers version
#   3. daemon sees the account   4. (optional) sends a test message
# Usage:
#   python3 scripts/signal-selftest.py            (checks 1-3)
#   python3 scripts/signal-selftest.py --send     (also sends "signal test")

import json
import os
import sys
import urllib.request

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append(ok)
    print(("PASS " if ok else "FAIL ") + name + (" — " + detail if detail else ""))


def rpc(base, method, params, timeout=10):
    body = json.dumps({"jsonrpc": "2.0", "id": 7,
                       "method": method, "params": params}).encode()
    req = urllib.request.Request(base + "/api/v1/rpc", data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read())


def main():
    path = os.path.join(BASE, "config.local.json")
    if not os.path.exists(path):
        path = os.path.join(BASE, "config.json")
    config = json.load(open(path))
    sig = config.get("signal", {})
    account = sig.get("account", "")
    check("config signal section",
          bool(sig) and account.startswith("+") and "X" not in account,
          "account: " + (account[:6] + "..." if account else "MISSING"))
    check("allowlist", len(sig.get("allowed", [])) >= 1,
          "%d allowed numbers" % len(sig.get("allowed", [])))

    base = "http://127.0.0.1:%d" % int(sig.get("daemon_http_port", 8080))
    try:
        result = rpc(base, "version", {})
        check("daemon version", bool(result.get("result")),
              json.dumps(result.get("result", {}))[:60])
    except Exception as error:
        check("daemon version", False, str(error))
        print("daemon not reachable — was start.sh run with signal enabled?")
        return 1

    try:
        result = rpc(base, "listAccounts", {})
        accounts = json.dumps(result.get("result", {}))
        check("account loaded", account in accounts.replace(" ", ""),
              "daemon accounts include the configured number: %s" % account)
    except Exception as error:
        check("account loaded", False, str(error))

    if "--send" in sys.argv and allowed_ok(sig):
        target = sig["allowed"][0]
        try:
            result = rpc(base, "send",
                         {"account": account, "recipient": [target],
                          "message": "mini-alexandria signal test"})
            check("test send to " + target, "error" not in result,
                  "check the phone — a 'signal test' message should arrive")
        except Exception as error:
            check("test send", False, str(error))

    print()
    print("SIGNAL SELFTEST: " + ("ALL PASS" if all(RESULTS) else "FAILURES PRESENT"))
    return 0 if all(RESULTS) else 1


def allowed_ok(sig):
    return bool(sig.get("allowed"))


if __name__ == "__main__":
    sys.exit(main())