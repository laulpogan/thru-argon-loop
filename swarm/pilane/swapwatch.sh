#!/bin/bash
# Dell tmux trailboss-pilane-swapwatch: when a running Codex lane exits (no codex process left in its tmux session),
# kill-session and relaunch the lane as pi + gemini-4-argon. Dell-bound lanes (need Dell repo/files) run pi on the Dell (light, API-only, nice 15); the rest go to the pilane pods.
H=~/cs-audit/gemini-hackathon; P=$H/pilane
DELL="integration walkthrough assetfactory hero-creek"
PODLANES="water lighting foliage audiomix textures particles wind models-wildlife"
desc(){ local p=$1; echo $p; for c in $(pgrep -P $p); do desc $c; done; }
podfor(){ awk '{print $2}' $P/lanes.tsv | sort | uniq -c | sort -n | head -1 | awk '{print $2}'; }
while [ $(date +%H%M) -lt 1530 ]; do
  for L in $DELL $PODLANES; do
    S=trailboss-reset-$L; [ $L = models-wildlife ] && S=trailboss-models-wildlife
    grep -q "^$L " $P/swapped.txt 2>/dev/null && continue
    tmux has-session -t $S 2>/dev/null || { [ -f $P/swapped.txt ] && grep -q "^$L " $P/swapped.txt || true; }
    if tmux has-session -t $S 2>/dev/null; then
      n=0; for pp in $(tmux list-panes -s -t $S -F "#{pane_pid}"); do for q in $(desc $pp); do grep -q codex /proc/$q/cmdline 2>/dev/null && n=$((n+1)); done; done
      [ $n -gt 0 ] && continue
      : # keep the session: its other windows (schedulers, captures) keep running
    fi
    if echo " $DELL " | grep -q " $L "; then
      D=$H/reset/$L; [ $L = walkthrough ] && D=$H/walkthrough
      { sed "s|/work/lanes/<lane>/|$D/|g; s|<lane>|$L|g; s|<LANE>|$(echo $L | tr a-z- A-Z_)|g" $P/PI-COMMON.md; echo; echo "DELL NOTE: you run ON THE DELL (orchestration and API calls only). Never run Godot/Blender here; send heavy jobs to the RunPod queue / Pitcrew per runpod/FLEET.md. Your git work happens in your existing work/* worktree (see HANDOFF.md); never write ~/Source/Thru-2 main checkout. Ignore the pod-only paths above (/work/thru)."; echo; echo "LANE GOAL:"; cat $H/prompts/reset/$L.md $H/prompts/reset/ext-$L.md 2>/dev/null; } > $D/PROMPT.md
      sed "s|cd /work/lanes/\$L|cd $D|" $P/pi-loop.sh > $D/pi-loop-dell.sh
      tmux new-session -d -s trailboss-pi-$L "nice -n 15 bash $D/pi-loop-dell.sh $L"
      echo "$L dell $(date +%T)" >> $P/swapped.txt
    else
      POD=$(podfor); $P/launch-on-pod.sh $L $POD >> $P/swapwatch.out 2>&1 && echo "$L $POD $(date +%T)" >> $P/swapped.txt
    fi
    echo "$(date +%T) swapped $L" >> $P/launch.log
  done
  sleep 60
done
