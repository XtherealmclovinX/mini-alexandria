#!/usr/bin/env bash
# diagnose-server.sh — READ-ONLY inventory of the Ubuntu server that will
# host a REAL hermes. Installs nothing, changes nothing, deletes nothing.
#
#   bash diagnose-server.sh
#
# Print the WHOLE output back — it is the input to the deploy plan.

set -u
say() { echo; echo "=== $* ==="; }
probe() { timeout 15 bash -c "$1" 2>&1 || echo "(probe failed or timed out: $1)"; }

say "OS / arch / kernel"
probe "cat /etc/os-release | head -3"
probe "uname -m"
probe "uname -r"

say "CPU"
probe "nproc"
probe "grep -m1 'model name' /proc/cpuinfo"

say "RAM"
probe "free -h"

say "Disk"
probe "df -h / | tail -1"

say "Docker"
probe "docker --version"
probe "docker compose version 2>/dev/null || docker-compose --version 2>/dev/null"
probe "docker ps >/dev/null 2>&1 && echo 'docker works without sudo' || echo 'docker needs sudo OR not installed'"
probe "groups | tr ' ' '\n' | grep -x docker || echo 'user not in docker group'"

say "Port clashes hermes components might want (8080, 8443, 3000)"
probe "ss -tlnp 2>/dev/null | grep -E ':8080|:8443|:3000 ' || echo '8080/8443/3000 all free'"

say "Python"
probe "python3 --version"

say "Systemd (services)"
probe "ps -p 1 -o comm="

say "Internet egress (signal + model downloads must reach out)"
probe "curl -s --max-time 8 -o /dev/null -w 'https %{http_code} in %{time_total}s' https://signal.org/ && echo"
probe "curl -s --max-time 8 -o /dev/null -w 'github %{http_code}' https://github.com/ && echo"

say "Virtualization (bare metal vs VPS)"
probe "systemd-detect-virt"

say "GPU (only matters if one exists)"
probe "nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null || echo 'no NVIDIA GPU'"

say "done — send the whole output back"