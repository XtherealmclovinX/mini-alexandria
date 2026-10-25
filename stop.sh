#!/data/data/com.termux/files/usr/bin/sh
# stop.sh — shut the model server and signal bridge down. Saves battery.
cd "$(dirname "$0")"
if pkill -f "llama-server"; then
    echo "llama-server stopped."
else
    echo "llama-server was not running."
fi
pkill -f "core/signal_bridge.py" 2>/dev/null
pkill -f "signal-cli" 2>/dev/null
exit 0