#!/bin/bash
# Staggered launch of extended Argon lane orchestrators (Dell disk is saturated; 45 s apart).
H=~/cs-audit/gemini-hackathon
for S in vegetation-assets rocks terrain ground sky seasons trail props hiker wildlife route cinematics performance qa writeup npcs ui design narrative localisation; do
  tmux has-session -t trailboss-reset-$S 2>/dev/null && continue
  mkdir -p $H/reset/$S
  tmux new-session -d -s trailboss-reset-$S "$H/prompts/reset/launch-ext.sh $S"
  echo "$(date +%T) launched trailboss-reset-$S" >> $H/reset/launcher.log
  sleep 45
done
