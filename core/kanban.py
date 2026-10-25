# core/kanban.py — the board, in one JSON file.
# Same verbs as the big system's kanban, same file simplicity:
#
#   python3 core/kanban.py add "plan spring grow"
#   python3 core/kanban.py list            (or: list doing)
#   python3 core/kanban.py show 2
#   python3 core/kanban.py complete 2      (todo/doing/blocked -> done)
#   python3 core/kanban.py move 2 review   (any column any column)
#   python3 core/kanban.py block 2 needs_input "waiting on license cost"
#   python3 core/kanban.py unblock 2       (blocked -> todo)
#   python3 core/kanban.py comment 2 "quoted three suppliers"
#   python3 core/kanban.py archive 2
#
# Every change appends one event line to the card, so the card's history
# is ON the card (the big system calls these events too). Old kanban.json
# files without events/notes still load fine.

import json
import os
import sys
import time

BASE = os.path.dirname(os.path.dirname(__file__))
BOARD = os.path.join(BASE, "data", "kanban.json")
STATUSES = ["todo", "doing", "review", "blocked", "done"]
BLOCK_KINDS = ["capability", "dependency", "needs_input", "transient"]


def load():
    try:
        with open(BOARD, "r") as handle:
            return json.load(handle)
    except FileNotFoundError:
        return {"cards": []}


def save(board):
    os.makedirs(os.path.dirname(BOARD), exist_ok=True)
    with open(BOARD, "w") as handle:
        json.dump(board, handle, indent=2)


def find(board, card_id):
    for card in board["cards"]:
        if str(card["id"]) == str(card_id):
            return card
    return None


def now():
    return time.strftime("%Y-%m-%d %H:%M")


def add(title):
    board = load()
    number = max([card["id"] for card in board["cards"]], default=0) + 1
    board["cards"].append({
        "id": number,
        "title": title,
        "status": "todo",
        "created": time.strftime("%Y-%m-%d"),
        "updated": time.strftime("%Y-%m-%d"),
        "events": [now() + " created in todo"],
        "notes": [],
    })
    save(board)
    print("added card #" + str(number) + " to todo: " + title)


def move(board, card, status):
    card["status"] = status
    card["updated"] = time.strftime("%Y-%m-%d")
    card.setdefault("events", []).append(now() + " -> " + status)
    save(board)


def complete(card_id):
    board = load()
    card = find(board, card_id)
    if not card:
        print("no card with id " + str(card_id))
        return
    move(board, card, "done")
    print("card #" + str(card_id) + " -> done")


def block(card_id, kind, reason):
    if kind not in BLOCK_KINDS:
        print("kind must be one of: " + ", ".join(BLOCK_KINDS))
        sys.exit(1)
    board = load()
    card = find(board, card_id)
    if not card:
        print("no card with id " + str(card_id))
        return
    move(board, card, "blocked")
    card.setdefault("notes", []).append(
        now() + " BLOCKED (" + kind + "): " + reason)
    card.setdefault("events", []).append(now() + " blocked: " + kind)
    save(board)
    print("card #" + str(card_id) + " blocked (" + kind + "): " + reason)


def unblock(card_id):
    board = load()
    card = find(board, card_id)
    if not card:
        print("no card with id " + str(card_id))
        return
    if card.get("status") != "blocked":
        print("card #" + str(card_id) + " is not blocked")
        return
    move(board, card, "todo")
    card.setdefault("events", []).append(now() + " unblocked")
    save(board)
    print("card #" + str(card_id) + " unblocked -> todo")


def comment(card_id, text):
    board = load()
    card = find(board, card_id)
    if not card:
        print("no card with id " + str(card_id))
        return
    card.setdefault("notes", []).append(now() + " " + text)
    card.setdefault("events", []).append(now() + " comment")
    save(board)
    print("card #" + str(card_id) + " comment saved")


def show(card_id):
    board = load()
    card = find(board, card_id)
    if not card:
        print("no card with id " + str(card_id))
        return
    print("#" + str(card["id"]) + " [" + card.get("status", "todo") + "] "
          + card["title"])
    print("created " + str(card.get("created", "?"))
          + " · updated " + str(card.get("updated", "?")))
    for note in card.get("notes", []):
        print("note: " + note)
    for event in card.get("events", []):
        print("event: " + event)


def archive(card_id):
    board = load()
    card = find(board, card_id)
    if not card:
        print("no card with id " + str(card_id))
        return
    archive_name = card["title"][:60] + " (archived " + now() + ")"
    for field, value in (("title", archive_name), ("status", "archived")):
        card[field] = value
    card.setdefault("events", []).append(now() + " archived")
    card["updated"] = time.strftime("%Y-%m-%d")
    save(board)
    print("card #" + str(card_id) + " archived (stays on the file, nothing "
          "is deleted)")


def list_cards(status=None):
    board = load()
    for card in board["cards"]:
        if status and card.get("status", "todo") != status:
            continue
        if status != "archived" and card.get("status") == "archived":
            continue
        print("#" + str(card["id"]) + " [" + card["status"] + "] "
              + card["title"] + " (" + card.get("updated", "?") + ")")


def cli():
    if len(sys.argv) >= 2 and sys.argv[1] == "add" and len(sys.argv) >= 3:
        add(" ".join(sys.argv[2:]))
    elif len(sys.argv) >= 2 and sys.argv[1] == "complete" and len(sys.argv) >= 3:
        complete(sys.argv[2])
    elif len(sys.argv) >= 2 and sys.argv[1] == "move" and len(sys.argv) >= 4:
        if sys.argv[3] not in STATUSES:
            print("status must be one of: " + ", ".join(STATUSES))
            sys.exit(1)
        board = load()
        card = find(board, sys.argv[2])
        if not card:
            print("no card with id " + str(sys.argv[2]))
            return
        move(board, card, sys.argv[3])
        print("card #" + str(sys.argv[2]) + " -> " + sys.argv[3])
    elif len(sys.argv) >= 2 and sys.argv[1] == "block" and len(sys.argv) >= 5:
        block(sys.argv[2], sys.argv[3], " ".join(sys.argv[4:]))
    elif len(sys.argv) >= 2 and sys.argv[1] == "unblock" and len(sys.argv) >= 3:
        unblock(sys.argv[2])
    elif len(sys.argv) >= 2 and sys.argv[1] == "comment" and len(sys.argv) >= 4:
        comment(sys.argv[2], " ".join(sys.argv[3:]))
    elif len(sys.argv) >= 2 and sys.argv[1] == "show" and len(sys.argv) >= 3:
        show(sys.argv[2])
    elif len(sys.argv) >= 2 and sys.argv[1] == "archive" and len(sys.argv) >= 3:
        archive(sys.argv[2])
    elif len(sys.argv) >= 2 and sys.argv[1] == "list":
        list_cards(sys.argv[2] if len(sys.argv) >= 3 else None)
    else:
        print(__doc__)


if __name__ == "__main__":
    cli()