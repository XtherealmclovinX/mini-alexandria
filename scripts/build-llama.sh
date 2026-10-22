#!/data/data/com.termux/files/usr/bin/sh
# build-llama.sh — build llama-server from source. One-time, 20-60 min.
# Keep the phone PLUGGED IN and somewhere cool while this runs.

set -e
if ! command -v cmake >/dev/null 2>&1; then
    pkg install -y cmake ninja
fi

if [ ! -d "$HOME/llama.cpp" ]; then
    git clone --depth 1 https://github.com/ggml-org/llama.cpp "$HOME/llama.cpp"
fi

cd "$HOME/llama.cpp"
git pull --ff-only 2>/dev/null || echo "(keeping offline copy — no network)"

echo "configuring (this prints a lot; normal) ..."
cmake -B build -DCMAKE_BUILD_TYPE=Release -DGGML_NATIVE=ON -DLLAMA_CURL=OFF

echo "building llama-server (the long step — 20-60 min on 6 cores) ..."
cmake --build build -j 6 --target llama-server

mkdir -p "$HOME/bin"
cp -f build/bin/llama-server "$HOME/bin/"
"$HOME/bin/llama-server" --version
echo "done. next step: sh scripts/get-model.sh"