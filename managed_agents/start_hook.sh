#!/bin/bash
# waits for run_art.py (pid $1) to finish, then starts the live critic hook chained onto the art-director's persistent environment
cd ~/cs-audit/gemini-hackathon/managed-agents
while kill -0 $1 2>/dev/null; do sleep 5; done
read ENV PREV < <(.venv/bin/python -c "
import json
rs=[json.loads(l) for l in open('RUNS.jsonl') if '\"art-director/' in l]
rs=[r for r in rs if r['status']=='completed']
print(rs[-1]['environment_id'], rs[-1]['interaction_id'])")
.venv/bin/python -c "
import json; json.dump({'env':'$ENV','prev':'$PREV','done':['1440_hero_low_iter1-first-render.png','1440_wide_iter1-first-render.png'],'iters':0}, open('hook_state.json','w'), indent=1)"
set -a; . ~/.config/gemini/hackathon.env; set +a; export GEMINI_API_KEY="${GEMINI_API_KEY:-$GOOGLE_API_KEY}"
exec .venv/bin/python -u ma_critic_hook.py
