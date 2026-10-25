#!/bin/bash
echo "CODEX DISABLED 14:08 PT (Paul approved all-Argon; Quota Cop): use pilane/launch-on-pod.sh (pi + gemini-4-argon)" >&2; exit 1 # CODEX DISABLED
# usage: launch-reset.sh <system> <lane-folder>   (runs inside tmux trailboss-reset-<system>)
H=~/cs-audit/gemini-hackathon; S=$1; F=$2; mkdir -p "$F"
cat $H/prompts/reset/ORCH-COMMON.md $H/prompts/reset/$S.md > "$F/PROMPT.md"
cd ~ && ARGON_LANE=reset-$S ~/.local/bin/codex exec -m gpt-6.1-sol --dangerously-bypass-approvals-and-sandbox "$(cat "$F/PROMPT.md")" 2>&1 | tail -c 50M > "$F/codex.log"
echo "codex exited $(date +%T)" >> "$F/codex.log"
