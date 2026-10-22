# core/kanban.py — the board, in one JSON file.
# Same idea as the big system's Kanban: work exists in one of four columns.
#
#   python3 core/kanban.py add "plan spring grow"
#   python3 core/kanban.py list
#   python3 core/kanban.py move 2 doing
#   python3 core/kanban.py move 1 done

import json
import os
import sys
import time

BASE = os.path.dirname(os.path.dirname(__file__))
BOARD = os.path.join(BASE, "data", "kanban.json")
STATUSES = ["todo", "doing", "review", "done"]


def load():
    try:
        with open(BOARD, "r") as handle:
            return json.load(handle)
    except FileNotFoundError:
        return {"cards": []}


def save(board):
    with open(BOARD, "w") as handle:
        json.dump(board, handle, indent=2)


def add(title):
    board = load()
    number = max([card["id"] for card in board["cards"]], default=0) + 1
    board["cards"].append({
        "id": number,
        "title": title,
        "status": "todo",
        "created": time.strftime("%Y-%m-%d"),
        "updated": time.strftime("%Y-%m-%d"),
    })
    save(board)
    print("added card #" + str(number) + " to todo: " + title)


def move(card_id, status):
    if status not in STATUSES:
        print("status must be one of: " + ", ".join(STATUSES))
        sys.exit(1)
    board = load()
    for card in board["cards"]:
        if str(card["id"]) == str(card_id):
            card["status"] = status
            card["updated"] = time.strftime("%Y-%m-%d")
            save(board)
            print("card #" + str(card_id) + " -> " + status)
            return
    print("no card with id " + str(card_id))


def list_cards(status=None):
    board = load()
    for card in board["cards"]:
        if status and card["status"] != status:
            continue
        print("#" + str(card["id"]) + " [" + card["status"] + "] "
              + card["title"] + " (" + card["updated"] + ")")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "add" and len(sys.argv) >= 3:
        add(" ".join(sys.argv[2:]))
    elif len(sys.argv) >= 2 and sys.argv[1] == "move" and len(sys.argv) >= 4:
        move(sys.argv[2], sys.argv[3])
    elif len(sys.argv) >= 2 and sys.argv[1] == "list":
        list_cards(sys.argv[2] if len(sys.argv) >= 3 else None)
    else:
        print(__doc__)