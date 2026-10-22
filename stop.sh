#!/data/data/com.termux/files/usr/bin/sh
# stop.sh — shut the model server down. Saves battery and cools the phone.
cd "$(dirname "$0")"
if pkill -f "llama-server"; then
    echo "stopped."
else
    echo "llama-server was not running."
fi