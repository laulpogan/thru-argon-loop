#!/bin/bash
# Dell tmux trailboss-pilane-sync: every 120 s pull each pod lane folder back to reset/<lane>/pod/ (STATUS etc. also copied to the lane root) and push STEER.md.
H=~/cs-audit/gemini-hackathon; P=$H/pilane
while [ $(date +%H%M) -lt 1800 ]; do
  sort -u $P/lanes.tsv 2>/dev/null | while read L POD IP PORT; do
    E="ssh -o BatchMode=yes -o ConnectTimeout=15 -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile=$H/overflow/known_hosts -p $PORT"
    D=$H/reset/$L; mkdir -p $D/pod
    nice rsync -az --max-size=200m --exclude PROMPT.md --exclude shared -e "$E" root@$IP:/work/lanes/$L/ $D/pod/ 2>>$P/sync.err
    for f in STATUS.md RESULT.md PLAN.md progress.html; do [ -f $D/pod/$f ] && cp $D/pod/$f $D/$f; done
    [ -f $D/STEER.md ] && rsync -az -e "$E" $D/STEER.md root@$IP:/work/lanes/$L/STEER.md 2>>$P/sync.err
    nice rsync -az -e "$E" root@$IP:/opt/overflow/calls.jsonl $P/calls-$POD.jsonl 2>/dev/null
  done
  sleep 120
done
