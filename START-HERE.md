# START-HERE — mini-alexandria

Your private AI team, running on your phone. Five agents, one local
model, no cloud, nothing leaves the phone. This one document covers
install, first run, and normal use.

Read it once before typing anything. Every command is one short line,
typed by hand (don't copy-paste blocks — Termux and copy-paste don't
mix).

---

## What you are building

A team of 5 agents that answers questions and drafts work for you:

- **Chief of Staff** — decides which agent handles what you ask
- **Cannabis Business Ops** — grow / process / sell / operations
- **Science & Research** — what the evidence actually says
- **Marketing & Business Ideas** — customers, content, new ideas
- **VP of Review** — optional second pass that critiques drafts

The "brain" is a small AI model (1.5 billion parameters, downloaded
free) running entirely on your phone. Slow but real: expect a few words
per second. This is a learning phase — the same system, faster, comes
later when this moves to a computer.

You can read and edit everything. The agents are plain text files.

---

## Before you start

1. **Charge the phone and keep it on the charger** for all of Part 1.
2. **Wi-Fi on** — you'll download ~1GB and compile code one time.
3. **Close all other apps** when you actually run things. The phone has
   ~2GB of working spare memory; closing apps is the difference between
   "works" and "crawl".
4. Your Termux is verified working (Python, git, curl are all present).

---

## Part 1 — Install (one-time, 20–60 minutes)

### Step 1: get the code (~10 seconds)

    git clone https://github.com/XtherealmclovinX/mini-alexandria ~/mini-alexandria

Success looks like: no red errors, and it finishes fast.

### Step 2: build the model server (the long one — 20–60 min)

    sh ~/mini-alexandria/scripts/build-llama.sh

Success looks like: a wall of cmake output, then a long "building"
phase, ending with a line like `llama-server b4206` (that's a version
number) and `done. next step: sh scripts/get-model.sh`.
If the phone gets warm: normal. Keep it plugged in.

### Step 3: download the brain (~1GB, one-time)

    sh ~/mini-alexandria/scripts/get-model.sh

Success looks like: `done. next step: sh start.sh`.

If any step fails — skip to **If something breaks** at the bottom.
Nothing installed by these steps can harm the phone: everything lands
in two folders (`~/mini-alexandria` and `~/llama.cpp`), all inside
Termux's own space.

---

## Part 2 — First run (proof that it's alive)

### Close your apps. Then:

    sh ~/mini-alexandria/start.sh

Success looks like: `loading model (qwen2.5-1.5b...)` for up to a
minute, then `ready. talk to your team:  python3 main.py chat`

### Run the self-test:

    python3 ~/mini-alexandria/scripts/selftest.py

Success looks like: five lines starting with PASS (backend completion,
routing, memory write+read, kanban add, kanban move) and ending
`SELFTEST: ALL PASS`.

If you see any FAIL — that output is exactly what to send back.

### Your first real question:

    python3 ~/mini-alexandria/main.py ask "name three business ideas for a small cannabis brand, cheapest first"

Success looks like: `[route] task assigned to: marketing` (chief picking
the agent), then the answer arriving a few words at a time. The first
answer is the slowest.

### Talk to the team directly:

    python3 ~/mini-alexandria/main.py chat

Type and press Enter; each line is its own task. Empty line or Ctrl+C
exits.

---

## Part 3 — Normal days

**Start of a session:**

    sh ~/mini-alexandria/start.sh

**Stop when you're done (saves battery, cools the phone):**

    sh ~/mini-alexandria/stop.sh

**Get updates (when told one landed):**

    cd ~/mini-alexandria && git pull

**Keep board + memory for yourself:** the system writes what happened
to `data/memory.md` and work cards to `data/kanban.json` — that's how
it "remembers" between sessions. Both are plain files you can read.

**Make the agents more yours:** `nano ~/mini-alexandria/agents/chief.md`
(or any agent file) — edit the mission text and save. That's the whole
customization model.

**Useful extras:**

    python3 ~/mini-alexandria/main.py route "your question"   (watch chief pick)
    python3 ~/mini-alexandria/main.py ask "..." --review     (draft + critique + fix)

---

## If something breaks

| What you see | What to do |
|---|---|
| `Could not reach the model server` | The brain isn't running: `sh ~/mini-alexandria/start.sh` first |
| `model file missing` | Re-run Step 3: `sh scripts/get-model.sh` |
| `llama-server not built yet` | Re-run Step 2: `sh scripts/build-llama.sh` |
| Build dies with `Killed` mid-way | Close ALL apps, screen off, re-run — it resumes |
| Answers suddenly crawling or phone hot | `sh stop.sh`, close apps, start again |
| `git clone` fails | Check the URL; tell who sent you this |
| Download errors (404) | Tell who sent you this — the URL fix ships as an update |

Whenever stuck: send back the exact output — it's always enough to fix
the next step over chat, and fixes arrive as updates.

---

## Start over completely (optional, safe)

Everything lives in three folders inside Termux only. To wipe:

    rm -rf ~/mini-alexandria ~/llama.cpp ~/bin/llama-server

Nothing on the phone outside those three folders is touched.

---

*mini-alexandria v0 · local only · you own everything it writes*