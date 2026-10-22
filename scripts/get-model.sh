#!/data/data/com.termux/files/usr/bin/sh
# get-model.sh — download the 1.5B model (~1GB) into models/.
# Needs ~1.5GB free. 90GB was free on the phone, so no worry there.

set -e
cd "$(dirname "$0")/.."
mkdir -p models

URL="https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf"
OUT="models/qwen2.5-1.5b-instruct-q4_k_m.gguf"

if [ -f "$OUT" ]; then
    echo "model already present: $OUT"
    exit 0
fi

echo "downloading ~1GB ..."
curl -L --fail --show-error "$URL" -o "$OUT"
ls -lh "$OUT"
echo "done. next step: sh start.sh"