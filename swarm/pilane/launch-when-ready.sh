#!/bin/bash
# launch-when-ready.sh <pod-num> <lanes...>: wait for pod READY (retrying setup), then launch lanes on it in sequence.
H=~/cs-audit/gemini-hackathon; P=$H/pilane; n=$1; shift; POD=thru-cpu-overflow-pilane-$n
for t in $(seq 1 40); do grep -q "^READY $POD" $P/deploy-$n.log 2>/dev/null && break
  if [ $t -gt 6 ] && [ $((t % 4)) -eq 0 ] && ! pgrep -f "setup-cpu.py --name $POD\$" >/dev/null; then (cd $H/overflow && python3 setup-cpu.py --name $POD >> $P/deploy-$n.log 2>&1 && echo "READY $POD $(date +%T)" >> $P/deploy-$n.log); fi
  sleep 30; done
for l in "$@"; do $P/launch-on-pod.sh $l $POD >> $P/launch-$n.out 2>&1; done
