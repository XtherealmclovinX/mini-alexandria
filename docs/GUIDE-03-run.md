---
title: GUIDE 03 — Run It (Proof of Life)
system: mini-alexandria
status: current
created: 2026-10-22
---

[⬆ Back to [BUILD-PLAN]]

# GUIDE 03 — Run It (Proof of Life)

**Goal:** start the system, run the selftest, have a real conversation,
stop it cleanly.

**Before starting:** close all other apps (this is the difference between
working and crawling — 2.1GB was available after closing them). Keep the
phone on Wi-Fi, ideally charged. Expect **slow**: 1.5B on a phone is a few
words per second. That is normal; it is a learning machine.

## Commands in order

**Step 1 — start:**

    sh ~/mini-alexandria/start.sh

Expected: `loading model ... ` then, within ~60s:
`ready. talk to your team:  python3 main.py chat`

**Step 2 — selftest (proof of life for every layer):**

    python3 ~/mini-alexandria/scripts/selftest.py

Expected: lines starting `PASS backend completion`, `PASS routing`,
`PASS memory write+read`, `PASS kanban add`, `PASS kanban move`, ending
`SELFTEST: ALL PASS`.

## Verification

- All five PASS lines, and `SELFTEST: ALL PASS`
- `tail -5 ~/mini-alexandria/data/memory.md` shows a `selftest` entry

## First real task

    python3 ~/mini-alexandria/main.py ask "name three business ideas for a small cannabis brand, cheapest first"

Expected: `[route] task assigned to: marketing` (or research/chief), then
the answer a few seconds at a time. First run is slowest — the model warms.

## With review (the two-step quality pass)

    python3 ~/mini-alexandria/main.py ask "..." --review

Expected: `[route] ...`, then `[review] ...` lines, then the answer.
Roughly double the time of a plain ask.

## Everyday use

    sh ~/mini-alexandria/start.sh      # when you want to work
    python3 ~/mini-alexandria/main.py chat
    sh ~/mini-alexandria/stop.sh       # when you are done — saves battery

## Update days

    cd ~/mini-alexandria && git pull    # then re-run any script that changed

## Rollback / stop

`sh stop.sh` at any time. Nothing persists beyond the `data/` folder and
the server process — turning off Termux shuts everything down.

## Troubleshooting

- **`Could not reach the model server`** — server is not running: `sh start.sh`
  first; chat/ask never starts its server.
- **Phone gets hot / answer crawls after apps opened** — stop, close apps,
  start again.
- **`model file missing`** — Step 3 of GUIDE-02 was skipped: run
  `sh scripts/get-model.sh`.
- **route picks a strange agent** — that is a feature to learn on: edit
  `agents/chief.md` to tell it clearer rules, then test with
  `python3 main.py route "..."`.

[⬆ Back to [BUILD-PLAN]]