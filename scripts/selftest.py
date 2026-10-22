# scripts/selftest.py — proof of life for the whole system.
# Run AFTER start.sh. Exercises every layer and prints PASS/FAIL lines:
#   backend health -> single completion -> routing -> memory -> kanban
# No writes outside data/. Safe to run repeatedly.

import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

from core import kanban, llm as llm_mod, memory, router

RESULTS = []


def check(name, condition, detail=""):
    RESULTS.append(condition)
    print(("PASS " if condition else "FAIL ") + name + (" — " + detail if detail else ""))


def main():
    config = json.load(open(os.path.join(BASE, "config.json")))
    client = llm_mod.LLM(config["backend_url"], config["model"])

    # 1. backend reachable via a real (tiny) completion
    try:
        answer = client.chat(system="Reply with exactly: alive",
                             user="are you alive?",
                             max_tokens=5, temperature=0.0,
                             timeout=60)
        check("backend completion", "alive" in answer.lower(), answer)
    except Exception as error:
        check("backend completion", False, str(error))
        print("stop here — model server is not answering.")
        return 1

    # 2. routing returns a known roster name
    try:
        role = router.route(client, "what does evidence say about CBD for sleep?",
                            config["roster"])
        check("routing", role in config["roster"] or role == "chief",
              "picked: " + role)
    except Exception as error:
        check("routing", False, str(error))

    # 3. memory write + readback
    memory.remember("selftest", "diagnostic probe", "selftest ran; this entry exists")
    recall = memory.recall(2048)
    check("memory write+read", "selftest ran" in recall)

    # 4. kanban add + move + roundtrip on disk
    kanban.add("selftest probe card")
    board = kanban.load()
    probe = [c for c in board["cards"] if "selftest probe card" in c["title"]]
    check("kanban add", len(probe) == 1)
    if probe:
        kanban.move(probe[0]["id"], "done")
        board2 = kanban.load()
        moved = [c for c in board2["cards"] if c["id"] == probe[0]["id"]]
        check("kanban move", bool(moved) and moved[0]["status"] == "done")

    ok = all(RESULTS)
    print()
    print("SELFTEST: " + ("ALL PASS" if ok else "FAILURES PRESENT"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())