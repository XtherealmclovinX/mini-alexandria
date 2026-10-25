# core/runs.py — one JSONL line per task, and a stats summary over it.
# Same idea as the big system's `hermes runs` / `hermes stats`: what ran,
# where it came from, which agent took it, how long it took.
#
# The file is data/runs.jsonl — human-readable, one JSON object per line.

import json
import os
import time
from collections import Counter

BASE = os.path.dirname(os.path.dirname(__file__))
RUNS_PATH = os.path.join(BASE, "data", "runs.jsonl")


def record(source, agent, seconds, reviewed):
    os.makedirs(os.path.dirname(RUNS_PATH), exist_ok=True)
    entry = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "source": source,
        "agent": agent,
        "seconds": round(seconds, 1),
        "reviewed": bool(reviewed),
    }
    with open(RUNS_PATH, "a") as handle:
        handle.write(json.dumps(entry) + "\n")


def load_runs():
    runs = []
    try:
        with open(RUNS_PATH, "r") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    runs.append(json.loads(line))
                except ValueError:
                    continue
    except FileNotFoundError:
        pass
    return runs


def stats():
    runs = load_runs()
    if not runs:
        print("no runs recorded yet (they land in data/runs.jsonl)")
        return
    today = time.strftime("%Y-%m-%d")
    week = [r for r in runs if r.get("time", "") >= _week_ago()]
    by_agent = Counter(r.get("agent", "?") for r in runs)
    by_source = Counter(r.get("source", "?") for r in runs)
    durations = [r.get("seconds", 0) for r in runs if isinstance(r.get("seconds"), (int, float))]
    avg = sum(durations) / len(durations) if durations else 0
    print("total runs: " + str(len(runs)) + " · today: "
          + str(len([r for r in runs if r.get("time", "").startswith(today)]))
          + " · last 7 days: " + str(len(week)))
    print("by agent:   " + ", ".join(a + " " + str(n) for a, n in by_agent.most_common()))
    print("by source:  " + ", ".join(s + " " + str(n) for s, n in by_source.most_common()))
    print("avg task time: " + str(round(avg, 1)) + "s · reviewed: "
          + str(len([r for r in runs if r.get("reviewed")])))
    for run in runs[-5:]:
        print("last: " + run.get("time", "?") + " [" + run.get("source", "?")
              + "/" + run.get("agent", "?") + "] " + str(run.get("seconds", "?")) + "s")


def _week_ago():
    import datetime
    seven = datetime.date.today() - datetime.timedelta(days=7)
    return seven.strftime("%Y-%m-%d")