#!/bin/bash
# m3run.sh <slug> "<subject>" "<refs>"
set -a; . ~/.config/gemini/hackathon.env; set +a
M=~/cs-audit/gemini-hackathon/model3; S=$1; mkdir -p $M/$S; cd $M/$S
P=$(sed -e "s#{SLUG}#$S#g" -e "s#{SUBJECT}#$2#" -e "s#{REFS}#$3#" ~/cs-audit/gemini-hackathon/prompts/model3-task.md)
for try in 1 2 3 4 5 6; do
  ARGON_LANE=model3-$S timeout 10800 pi --provider google --model gemini-4-argon -p "$P" >> pi.log 2>&1
  grep -q MODEL3_DONE RESULT.md 2>/dev/null && break
  P="$P

CONTINUE: you were interrupted. Read PLAN.md, progress.html and your files in this folder, and resume from the latest round. Do not restart from scratch."
  sleep 60
done
