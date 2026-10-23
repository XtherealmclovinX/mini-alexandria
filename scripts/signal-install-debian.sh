#!/bin/bash
# signal-install-debian.sh — runs INSIDE proot Debian (launched by signal-install.sh).
# Installs Java 25 + signal-cli + aarch64 libsignal, then verifies.
set -e

echo "[debian] apt update + tools"
apt-get update -qq
apt-get install -y -qq curl unzip jq file >/dev/null

echo "[debian] trying openjdk 25 from apt"
if ! java --version 2>/dev/null | grep -q '"25\.'; then
    apt-get install -y -qq openjdk-25-jre-headless >/dev/null 2>&1 || true
fi
if ! java --version 2>/dev/null | grep -q '"25\.'; then
    echo "[debian] apt openjdk 25 not available — using Temurin JRE 25 (aarch64)"
    mkdir -p /opt/jre25
    curl -sL "https://api.adoptium.net/v3/binary/latest/25/ga/linux/aarch64/jre/hotspot/normal/eclipse" \
        | tar -xz -C /opt/jre25 --strip-components=1
    ln -sf /opt/jre25/bin/java /usr/local/bin/java
fi
java --version

echo "[debian] latest signal-cli release"
VER=$(curl -s https://api.github.com/repos/AsamK/signal-cli/releases/latest | jq -r .tag_name)
echo "[debian] signal-cli version: $VER"
curl -sL "https://github.com/AsamK/signal-cli/releases/download/$VER/signal-cli-$VER-linux.tar.gz" \
    | tar -xz -C /opt/
mv "/opt/signal-cli-$VER" /opt/signal-cli

echo "[debian] aarch64 libsignal native library"
mkdir -p /opt/signal-libs
LIB_URL=$(curl -s https://api.github.com/repos/exquo/signal-libs-build/releases/latest \
    | jq -r '.assets[].browser_download_url' | grep -i "aarch64" | head -1)
if [ -z "$LIB_URL" ]; then
    echo "NOT FOUND: could not locate an aarch64 libsignal asset."
    echo "Paste this whole output back — the library source moved."
    exit 1
fi
echo "[debian] lib from: $LIB_URL"
curl -sL "$LIB_URL" -o /tmp/lib.zip
unzip -o -j /tmp/lib.zip -d /tmp/libx/
find /tmp/libx -name "*libsignal*jni*.so" -exec cp {} /opt/signal-libs/ \; \
    || find /tmp/libx -name "*.so" -exec cp {} /opt/signal-libs/ \;
ls -la /opt/signal-libs/

echo "[debian] creating the signal-cli command"
cat > /usr/local/bin/signal-cli <<'WRAP'
#!/bin/bash
CP=$(ls /opt/signal-cli/lib/*.jar | tr '\n' ':')
exec ${JAVA_HOME:-/usr/local/bin}/java -Djava.library.path=/opt/signal-libs \
    -cp "$CP" org.asamk.signal.Main "$@"
WRAP
chmod +x /usr/local/bin/signal-cli

echo ""
echo "[debian] verifying: signal-cli --version (next line must show a version)"
signal-cli --version
echo "INSTALL OK"