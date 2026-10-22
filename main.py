# main.py — how you talk to your team.
#
#   python3 main.py ask "how much should I charge for pre-roll joints?"
#   python3 main.py route "find studies on CBD half-life"     (test routing)
#   python3 main.py chat                                     (back-and-forth)
#   python3 main.py ask "..." --review                       (with review pass)
#
# `route` is a learning tool: it prints which agent the Chief picks, so
# you can watch the routing get smarter as you sharpen agents/chief.md.

import argparse
import json
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

from core import llm, memory, router, worker


def load_config():
    with open(os.path.join(BASE, "config.json")) as handle:
        return json.load(handle)


def make_client(config):
    return llm.LLM(config["backend_url"], config["model"])


def one_ask(client, args, config):
    answer = worker.run_task(
        client, args.question, config,
        do_review=args.review or config.get("review_default", False),
    )
    print()
    print(answer)


def chat_loop(client, config):
    print("mini-alexandria chat — empty line or Ctrl+C to exit.")
    while True:
        try:
            line = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not line:
            return
        answer = worker.run_task(
            client, line, config,
            do_review=config.get("review_default", False),
        )
        print()
        print(answer)
        print()


def route_only(client, args, config):
    role = router.route(client, args.question, config["roster"])
    print(role)
    memory.remember("route-test", args.question[:120], "route -> " + role)


def main():
    config = load_config()
    client = make_client(config)
    parser = argparse.ArgumentParser(description="mini-alexandria")
    parser.add_argument("command", choices=["ask", "chat", "route"])
    parser.add_argument("question", nargs="?", default="")
    parser.add_argument("--review", action="store_true")
    args = parser.parse_args()

    if args.command == "chat":
        chat_loop(client, config)
    elif args.command == "route":
        if not args.question:
            sys.exit("usage: python3 main.py route \"your question\"")
        route_only(client, args, config)
    else:
        if not args.question:
            sys.exit("usage: python3 main.py ask \"your question\"")
        one_ask(client, args, config)


if __name__ == "__main__":
    main()