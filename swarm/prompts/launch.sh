#!/bin/bash
echo "CODEX DISABLED 14:08 PT (Paul approved all-Argon; Quota Cop): use pilane/launch-on-pod.sh (pi + gemini-4-argon)" >&2; exit 1 # CODEX DISABLED
# usage: launch.sh <lane> <promptfile>
H=~/cs-audit/gemini-hackathon; L=$1; mkdir -p $H/$L
cat $H/prompts/COMMON.md $H/prompts/$2 > $H/$L/PROMPT.md
cd ~ && ARGON_LANE=$L ~/.local/bin/codex exec -m gpt-6.1-sol --dangerously-bypass-approvals-and-sandbox "$(cat $H/$L/PROMPT.md)" 2>&1 | tail -c 50M > $H/$L/codex.log
