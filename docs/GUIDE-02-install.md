---
title: GUIDE 02 — Install on the Phone
system: mini-alexandria
status: current
created: 2026-10-22
---

[⬆ Back to [BUILD-PLAN]]

# GUIDE 02 — Install on the Phone

**Goal:** get the repo onto the phone, build the model server, download
the model.

**Who runs it:** the brother, over SSH (Termux sshd, port 8022) or
directly in Termux. Every step is one short line, typed by hand.

**Before starting:** close all other apps; plug the phone in; get on
Wi-Fi. Build time total: 20–60 min (one-time).

## Prerequisites check (from the diagnostic)

python3, git, clang, curl: all present. cmake: installed by the script.
Storage permission: not needed for this install.

## Commands in order (type each by hand)

**Step 1 — get the repo** (repo is private — see Troubleshooting before this):

    git clone https://github.com/XtherealmclovinX/mini-alexandria ~/mini-alexandria

**Step 2 — build the model server** (long; phone stays plugged in):

    sh ~/mini-alexandria/scripts/build-llama.sh

Expected: cmake configure output, then a long compile, ending in
`llama-server is built. next step: sh scripts/get-model.sh`.
The line `llama-server b<numbers>` near the end is the version — good sign.

**Step 3 — download the model** (~1GB):

    sh ~/mini-alexandria/scripts/get-model.sh

Expected: `downloading ~1GB ...` then `ls -lh` showing ~a 1.0GB file ending
`q4_k_m.gguf`, then `done. next step: sh start.sh`.

## Expected output at the end

`ls ~/mini-alexandria` shows: `README.md  agents  config.json  core
data  main.py  models  scripts  start.sh  stop.sh`

## Verification

    ls -lh ~/mini-alexandria/models/
    ~/bin/llama-server --version

Both must print real values (file size ≈1.0G; version line).

## Rollback

Nothing touched outside: `~/mini-alexandria/`, `~/llama.cpp/`, `~/bin/`.
Full undo = `rm -rf` those three folders (brother's choice, run manually).

## Troubleshooting

- **git clone fails** — the repo is not created yet, or private and SSH
  keys are not set up in Termux. Fix: make the clone URL right, or use
  the HTTPS URL.
- **build fails at cmake** — run `pkg install -y cmake ninja clang`, then
  re-run the build script.
- **build killed mid-way (Killed)** — RAM pressure: close ALL apps, turn
  off the screen, re-run. It resumes where it stopped.
- **model download 404s** — the file URL needs an update; report back and
  I fix `scripts/get-model.sh` in the repo (that is why updates are a
  `git pull`).

[⬆ Back to [BUILD-PLAN]]