#!/data/data/com.termux/files/usr/bin/sh
# signal-install.sh — everything Signal needs, in one script.
# Run:  sh ~/mini-alexandria/scripts/signal-install.sh
# Installs: proot-distro + Debian, Java 25, signal-cli, aarch64 native lib.
# Long step (~10-15 min). Keep plugged in. Wi-Fi on.

set -e
echo "== Signal install: phase 1 (Termux side) =="

if ! command -v proot-distro >/dev/null 2>&1; then
    pkg install -y proot-distro
fi
if ! proot-distro list 2>/dev/null | grep -q "debian.*installed"; then
    proot-distro install debian
fi

echo "== phase 2: inside Debian (this prints a lot; normal) =="
# the repo folder stays visible inside Debian via the bind below
proot-distro login debian --bind "$HOME":"$HOME" -- \
    bash "$HOME/mini-alexandria/scripts/signal-install-debian.sh"

echo ""
echo "DONE. next step: register his number (see GUIDE-04 part 2)"