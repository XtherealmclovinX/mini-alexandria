#!/data/data/com.termux/files/usr/bin/sh
# start.sh — launch llama-server, wait until it is ready, report honestly.
# On-demand: run this when you want to work, stop.sh when you are done.

set -e
cd "$(dirname "$0")"

PORT=$(python3 -c 'import json;print(json.load(open("config.json"))["llama_server_port"])')
THREADS=$(python3 -c 'import json;print(json.load(open("config.json"))["llama_threads"])')
CONTEXT=$(python3 -c 'import json;print(json.load(open("config.json"))["llama_context"])')
MODEL=$(python3 -c 'import json;print(json.load(open("config.json"))["model"])')
SIGNAL_ENABLED=$(python3 -c 'import json
c = json.load(open("config.json"))
try: c.update(json.load(open("config.local.json")))
except Exception: pass
print("true" if c.get("signal", {}).get("enabled") else "false")')
MODEL_PATH="models/$MODEL.gguf"

if [ ! -f "$MODEL_PATH" ]; then
    echo "model file missing: $MODEL_PATH"
    echo "run: sh scripts/get-model.sh"
    exit 1
fi
if [ -f "$HOME/bin/llama-server" ]; then
    SERVER="$HOME/bin/llama-server"
else
    echo "llama-server not built yet — run: sh scripts/build-llama.sh"
    exit 1
fi

pkill -f "llama-server" 2>/dev/null && sleep 2 || true

mkdir -p data
nohup "$SERVER" -m "$MODEL_PATH" --host 127.0.0.1 --port "$PORT" \
    -c "$CONTEXT" -t "$THREADS" > data/llama-server.log 2>&1 &
echo "loading model ($MODEL) — a 1.5B model may take 10-60s from cold storage"

i=0
while [ $i -lt 30 ]; do
    if curl -s --max-time 2 "http://127.0.0.1:$PORT/health" 2>/dev/null | grep -q "ok"; then
        if [ "$SIGNAL_ENABLED" = "true" ]; then
    pkill -f "core/signal_bridge.py" 2>/dev/null || true
    pkill -f "signal-cli" 2>/dev/null || true
    sleep 1
    nohup python3 core/signal_bridge.py > data/signal-bridge.log 2>&1 &
    echo "signal bridge starting too (log: data/signal-bridge.log)"
fi

echo "ready. talk to your team:  python3 main.py chat"
        exit 0
    fi
    sleep 2
    i=$((i + 1))
done

echo "NOT ready after 60s — look at the log:  tail -20 data/llama-server.log"
exit 1