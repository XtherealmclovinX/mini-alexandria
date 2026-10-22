# mini-alexandria

A small, private AI team you run yourself — a primitive version of the
bigger "Alexandria" pattern. Five agents, one local model, one script to
start and one to stop.

```
        you ask a question
              │
       Chief of Staff  (decides which agent handles it)
              │
   ┌──────────┼──────────┬──────────────┐
cannabis-ops  research  marketing      (any of the 5)
              │
        VP of Review     (optional pass: critique + fix)
              │
        memory + kanban  (everything lands somewhere)
```

## Quick start

    sh start.sh            # starts the model server (waits until ready)
    python3 main.py chat   # then just talk to your team

## Your first edit

Agents are plain text files in `agents/`. Open any one with `nano` and
change the mission to make the agent more yours. That is the whole idea.

## Files

| Path | What it is |
|---|---|
| `start.sh` / `stop.sh` | run / stop everything |
| `main.py` | how you talk to the team (`ask`, `chat`, `route`, `kanban`) |
| `config.json` | model name, URL, settings |
| `agents/*.md` | each agent's mission — yours to edit |
| `core/` | the small programs that make it work |
| `data/` | kanban board, memory log, drafts, logs |

## Learning map (read in this order)

1. `agents/chief.md` — how routing works
2. `core/llm.py` — the only way this talks to the model (~30 lines)
3. `core/worker.py` — question in, draft out
4. `core/review.py` — the critique pass
5. `core/memory.py` — where it remembers things