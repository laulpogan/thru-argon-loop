#!/usr/bin/env bash
# One live critique -> fix -> verify cycle (about 60-90 s). Needs: python3, GEMINI_API_KEY in env.
#   bash demo/run_loop.sh            # fallback: saved real UE5 renders (iter1 -> iter2) in demo/renders/
#   UE_POD=user@host UE_POD_PORT=NNNN bash demo/run_loop.sh   # live: pull current stills from a running UE pod,
#       push the patched params.json and kick off the next real UE render there (iterate.sh, ~4-5 min).
set -euo pipefail
cd "$(dirname "$0")/.."
: "${GEMINI_API_KEY:?export GEMINI_API_KEY first (read from env only)}"
OUT=demo/out/$(date +%H%M%S); mkdir -p "$OUT"
STILLS=demo/renders/iter1; VERIFY=demo/renders/iter2; PARAMS=pipeline/runs/iter1/params.json
if [ -n "${UE_POD:-}" ]; then
  E="ssh -o BatchMode=yes -p ${UE_POD_PORT:-22}"
  IT=$($E "$UE_POD" 'cd /workspace/unreal/out && ls -d iter[0-9]* | sort -V | tail -1')
  echo "[live] pulling $IT stills + params from the running UE pod"
  mkdir -p "$OUT/live"; rsync -a -e "$E" "$UE_POD:/workspace/unreal/out/$IT/stills_pick/" "$OUT/live/"
  rsync -a -e "$E" "$UE_POD:/workspace/unreal/src/params.json" "$OUT/params.live.json"
  STILLS=$OUT/live; PARAMS=$OUT/params.live.json; VERIFY=""
fi
python3 demo/critic_fix.py --stills "$STILLS" --refs pipeline/refs --params "$PARAMS" --out "$OUT" ${VERIFY:+--verify-stills "$VERIFY"}
if [ -n "${UE_POD:-}" ]; then
  N=$(( ${IT#iter} + 1 ))
  rsync -a -e "$E" "$OUT/params.next.json" "$UE_POD:/workspace/unreal/src/params.json"
  $E "$UE_POD" "cd /workspace/unreal && nohup bash src/iterate.sh $N > out/demo_iter$N.log 2>&1 &"
  echo "[live] patched params pushed; real UE render iter$N started on the pod (re-run this script when it lands to verify)."
else
  echo "(fallback mode: step 3 re-critiques demo/renders/iter2, the real UE5 render the loop produced at 14:40 PT from iter1's critique)"
fi
echo "artifacts: $OUT"
