# GUIDE-04 — Add Signal to mini-alexandria

Text your mini-alexandria agents from the Signal app like a real team.
Same rules as when it was built: every command is one short line typed
by hand, everything runs on the phone, nothing leaves except your Signal
messages.

**Before you start:** close all other apps, plug in, Wi-Fi on. The first
step takes 10–15 minutes. Signal needs ~400MB of extra memory — it will
work, but the standing rule (close apps) now matters even more.

**Have ready before Step 2:** the bot's own phone number (a real number
that can receive one SMS or voice call) — the bot becomes *its own*
Signal account — and yours + his numbers for the allowlist.

---

## Part 1 — Install (10–15 min, one-time)

### First, update to the version with Signal:

    cd ~/mini-alexandria && git pull

### Then install everything (one command, prints a lot):

    sh ~/mini-alexandria/scripts/signal-install.sh

Success looks like: `apt` output, a Java 25 version line, a downloaded
signal-cli version, and the last two lines:
`signal-cli 0.14.x (or similar)` then `INSTALL OK`.

If it prints `NOT FOUND: could not locate an aarch64 libsignal asset` —
the library source moved. Send back the whole output; that is always
enough to fix.

---

## Part 2 — Give the bot its number (one-time, 2 minutes)

Registration: the number becomes a Signal account. If that number is
ALREADY in someone's Signal app, this will unregister it — use a free
number.

### Register (replace with the bot's real number):

    proot-distro login debian -- signal-cli -u +1BOTNUMBER register

Success looks like: `Verification message sent` (SMS or a voice call
arrives).

### Verify with the code you receive:

    proot-distro login debian -- signal-cli -u +1BOTNUMBER verify 123-456

Success looks like: `Verified the number ...` — the bot's Signal account
now exists, living inside the phone.

---

## Part 3 — Tell it who may talk (2 minutes)

### Copy the example and edit the three numbers:

    cp ~/mini-alexandria/config.local.json.example ~/mini-alexandria/config.local.json
    nano ~/mini-alexandria/config.local.json

In nano: replace `+1XXXXXXXXXX` with the bot's number, then the two
allowed numbers (his first, then yours). Ctrl+O, Enter saves; Ctrl+X
exits. This file NEVER goes to GitHub (it is ignored by git).

---

## Part 4 — First run (proof of life)

### Start everything (model server + bridge in one go):

    sh ~/mini-alexandria/start.sh

Success looks like: `ready. talk to your team:` AND a new line
`signal bridge starting too (log: data/signal-bridge.log)`.

### Check the Signal layer:

    python3 ~/mini-alexandria/scripts/signal-selftest.py

Success looks like: `PASS config signal section`, `PASS allowlist`,
`PASS daemon version`, `PASS account loaded`, ending
`SIGNAL SELFTEST: ALL PASS`.

### Optional — confirm messages actually travel:

    python3 ~/mini-alexandria/scripts/signal-selftest.py --send

The first allowed number receives "mini-alexandria signal test".

### The real test — from the Signal app, text the bot's number:

    how much should I charge for pre-rolls at a market stall?

Success looks like: nothing for a minute (routing + drafting on a phone),
then an answer from the bot in the same chat. `data/signal-bridge.log`
shows `[signal] task from ...` lines for every attempt.

---

## Normal days

    sh ~/mini-alexandria/start.sh     — brings up model + Signal together
    sh ~/mini-alexandria/stop.sh      — stops both (do this when idle: phone
                                        stays cool, battery survives)

Only allowed numbers get answers; anyone else's texts are logged as
DENIED in `data/signal-bridge.log` (nothing goes to the agents).

## If something breaks

| What you see | What to do |
|---|---|
| `FAIL daemon version` | Bridge/daemon not running: `sh start.sh`, then `tail -20 data/signal-cli.log` |
| `INSTALL OK` missing / NOT FOUND in Part 1 | Send back the full output of the install command |
| Verify code rejected | Number got no SMS: re-run register with `--voice` at the end for a call |
| Bot silent but selftest passes | Check `data/signal-bridge.log` — `[signal] task from` lines only appear for ALLOWED numbers |
| Answers one person, silence for another | Update first (`git pull`). Text the bot from the ignored person's account, then `tail -5 data/signal-bridge.log` — a `[signal] message DENIED from` line names the EXACT identifier that account presents (phone number or UUID from Signal's privacy settings). Put THAT identifier in `config.local.json` (a UUID is accepted now), then `sh stop.sh && sh start.sh` and text again |
| Phone crawls during Signal runs | Close apps; also `nano config.json`, set `llama_context` 2048 → 1024 (frees ~150MB), restart |
| `NOT READY` / memory kill | The RAM rule again: close apps, stop, start |
| Wrong answers only under Signal | Send `data/signal-bridge.log` back — the fix ships as an update |

## Updates

    cd ~/mini-alexandria && git pull

Then `sh stop.sh && sh start.sh` to load the new version.

## Remove Signal completely (optional)

    proot-distro remove debian
    nano ~/mini-alexandria/config.local.json   (set "enabled" to false)

The rest of mini-alexandria is untouched.

---

*Signal layer v0.1 · bot number + allowlist stay on the phone only*