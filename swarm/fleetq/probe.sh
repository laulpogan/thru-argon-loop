#!/bin/bash
# probe.sh HOST:PORT NAME -> one-line diagnosis (read-only)
hp=$1; name=$2; ip=${hp%:*}; port=${hp#*:}
out=$(timeout 40 ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile=$HOME/cs-audit/gemini-hackathon/runpod/fleetq/known_hosts -o ConnectTimeout=15 -i ~/.ssh/id_ed25519 -p $port root@$ip '
echo "load=$(cut -d" " -f1 /proc/loadavg) nproc=$(nproc)";
echo "blender=$(command -v blender >/dev/null && echo y || echo n) godot=$(ls /opt/thru/godot* /usr/local/bin/godot* 2>/dev/null | head -1 | xargs -r basename) nvsmi=$(command -v nvidia-smi >/dev/null && nvidia-smi --query-gpu=name,utilization.gpu --format=csv,noheader 2>/dev/null | head -1 || echo none)";
echo "jobs=$(ls /opt/overflow/jobs 2>/dev/null | wc -l) fq=$(ls -d /opt/fleetq 2>/dev/null)";
ps -eo pid,etimes,pcpu,comm,args --sort=-pcpu | grep -v -E "ps -eo|sshd|bash -c|sleep|grep" | head -6 | cut -c1-160' 2>&1)
echo "=== $name $hp"; echo "$out"
