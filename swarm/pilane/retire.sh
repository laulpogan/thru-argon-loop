#!/bin/bash
# Retire SIGSTOP-paused Codex lanes (parent 1:28 PM): SIGCONT exact PIDs of the session tree, then tmux kill-session; write HANDOFF.md.
H=~/cs-audit/gemini-hackathon; F=$H/reset/PAUSED-PIDS.txt
desc(){ local p=$1; echo $p; for c in $(pgrep -P $p); do desc $c; done; }
for s in $(grep -o "^trailboss-[a-z0-9-]*" $F | sort -u); do
  tmux has-session -t "$s" 2>/dev/null || continue
  pids=$(for pp in $(tmux list-panes -s -t "$s" -F "#{pane_pid}"); do desc $pp; done)
  kill -CONT $pids 2>/dev/null
  tmux kill-session -t "$s" && echo "$(date +%T) retired $s" >> $H/pilane/retired.log
  lane=${s#trailboss-}; lane=${lane#reset-}
  D=$H/reset/$lane; mkdir -p $D
  B=$(git -C ~/Source/Thru-2 branch --list "work/argon-*$lane*" | tr -d " *" | head -3 | tr "\n" " ")
  { echo "# HANDOFF: $lane (Codex orchestrator retired $(date +%H:%M) PT; relaunching as pi + gemini-4-argon)"
    echo "Branches: ${B:-none}"; for b in $B; do echo "- $b: $(git -C ~/Source/Thru-2 log -1 --format="%h %s" $b 2>/dev/null)"; done
    echo; echo "## Last STATUS.md"; tail -n 25 $D/STATUS.md 2>/dev/null
    echo; echo "## Last LOG.md lines"; tail -n 20 $D/LOG.md 2>/dev/null | cut -c1-400
    echo; echo "## Files in lane folder"; ls $D | head -60 | tr "\n" " "
  } > $D/HANDOFF.md
done
echo RETIRE_DONE >> $H/pilane/retired.log
