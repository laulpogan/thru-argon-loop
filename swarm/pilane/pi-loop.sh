#!/bin/bash
# pi-loop.sh <lane> [lane-dir]: keeps the lane's pi orchestrator going until 15:35 PT. Model from <dir>/MODEL (default gemini-3.8-flash; Paul 2:15: Argon reserved for hero-creek + final verdicts). Backs off when a run dies fast (429).
L=$1; D=${2:-/work/lanes/$L}; cd $D; export ARGON_LANE=$L TZ=America/Los_Angeles
[ -f ~/.config/gemini/hackathon.env ] && { set -a; . ~/.config/gemini/hackathon.env; set +a; }
n=0; fast=0
while [ $(date +%H%M) -lt 1535 ]; do
  { [ -f STOP ] || [ -f PAUSED ]; } && { echo "=== STOP/PAUSED found $(date +%T), exiting" >> pi-runs.log; break; }
  n=$((n+1)); M=$(cat MODEL 2>/dev/null || echo gemini-3.8-flash); echo "=== run $n $(date +%T) model=$M" >> pi-runs.log
  if [ $n -eq 1 ]; then P="$(cat PROMPT.md)"; else P="$(cat PROMPT.md)

CONTINUATION (run $n): you have worked on this lane before. Read STATUS.md, PLAN.md, LOG.md, STEER.md and continue where you left off; do not redo finished work."; fi
  t0=$(date +%s); timeout 2700 pi --provider google --model $M -p "$P" >> pi-runs.log 2>&1
  if [ $(( $(date +%s) - t0 )) -lt 60 ]; then fast=$((fast+1)); sleep $(( (fast<6?fast:6)*20 + RANDOM%20 )); else fast=0; sleep 5; fi
done
echo "=== loop end $(date +%T)" >> pi-runs.log
