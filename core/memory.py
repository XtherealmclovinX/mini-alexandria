# core/memory.py — append-only memory.
# Every task adds a short entry to data/memory.md. New tasks get the last
# N characters of that file as context, so the team "remembers" recent
# work without any database. This mirrors the big system's tenet concept
# at a beginner scale: if it isn't in the file, it doesn't exist.

import os
import time

BASE = os.path.dirname(os.path.dirname(__file__))
MEMORY_PATH = os.path.join(BASE, "data", "memory.md")


def remember(role, task, summary):
    os.makedirs(os.path.dirname(MEMORY_PATH), exist_ok=True)
    with open(MEMORY_PATH, "a") as handle:
        handle.write(
            "## " + time.strftime("%Y-%m-%d %H:%M") + " — " + role + "\n"
            "task: " + task[:200] + "\n"
            "result: " + summary + "\n\n"
        )


def recall(max_chars):
    """Tail of the memory file, or '' on first run."""
    try:
        with open(MEMORY_PATH, "r") as handle:
            content = handle.read()
    except FileNotFoundError:
        return ""
    return content[-max_chars:]