#!/bin/bash
# v3 (12:56 PT, Paul 12:54: "ignore the 200 cap"): terminates EVERY RunPod pod (GPU and CPU) at 18:00 PT. No dollar cap.
# Runaway guard only: burn > $150/hr writes RUNAWAY alert + PAUSE_SCALING file (no terminate). Spend still tracked. Auto top-up is on, so balance deltas alone undercount:
# spend = max(integrated currentSpendPerHr over time, balance drop adjusted for top-ups). State persists
# in watchdog.state so a restart keeps the running total. Runs in tmux trailboss-runpod-watchdog.
CAP=${CAP:-1000000000}; RUNAWAY=150; BN=~/cs-audit/gemini-hackathon/BOTTLENECKS.md
. ~/.config/runpod.env; D=~/cs-audit/gemini-hackathon/runpod; LOG=$D/watchdog.log; ST=$D/watchdog.state
q(){ curl -s -m 20 https://api.runpod.io/graphql -H "Authorization: Bearer $RUNPOD_API_KEY" -H 'content-type: application/json' -d "$1"; }
echo "$(date +%T) WATCHDOG_V3 start no-dollar-cap stop=18:00 PT runaway-alert=\$150/hr" >> $LOG
while true; do
  J=$(q '{"query":"query{myself{clientBalance currentSpendPerHr pods{id name desiredStatus}}}"}')
  OUTP=$(echo "$J" | python3 -c "
import sys,json,time,os
st_path='$ST'; cap=float('$CAP')
try: st=json.load(open(st_path))
except Exception: st={'integrated':0.0,'last_t':None,'last_bal':None,'bal_spent':0.0}
try:
  m=json.load(sys.stdin)['data']['myself']
except Exception:
  print('ERR - - 0 -'); sys.exit()
bal=float(m['clientBalance']); rate=float(m['currentSpendPerHr'] or 0); now=time.time()
if st['last_t'] is not None: st['integrated']+=rate*min(now-st['last_t'],600)/3600
if st['last_bal'] is not None and bal<st['last_bal']: st['bal_spent']+=st['last_bal']-bal
st['last_t']=now; st['last_bal']=bal
json.dump(st,open(st_path,'w'))
spent=max(st['integrated'],st['bal_spent'])
ids=' '.join(p['id'] for p in m['pods'])
print('%s %s %.2f %d %s'%(bal,rate,spent,1 if spent>=cap else 0,ids))
")
  read BAL RATE SPENT OVER IDS <<< "$OUTP"
  echo "$(date +%T) bal=$BAL rate=$RATE spent=$SPENT cap=$CAP pods=[$IDS]" >> $LOG
  if python3 -c "import sys;sys.exit(0 if float('${RATE:-0}' or 0)>$RUNAWAY else 1)" 2>/dev/null; then echo "- $(date +%T) RUNAWAY ALERT: RunPod burn \$$RATE/hr > \$$RUNAWAY/hr; scaling paused (touch $D/PAUSE_SCALING), nothing terminated. spent=\$$SPENT" >> $BN; echo runaway > $D/PAUSE_SCALING; else grep -qx runaway $D/PAUSE_SCALING 2>/dev/null \&\& rm -f $D/PAUSE_SCALING; fi
  if [ -n "$IDS" ] && { [ $(date +%H%M) -ge 1800 ] || [ "$OVER" = 1 ]; }; then
    for p in $IDS; do q "{\"query\":\"mutation{podTerminate(input:{podId:\\\"$p\\\"})}\"}" >> $LOG; echo " terminated $p" >> $LOG; done
  fi
  [ $(date +%H%M) -ge 1810 ] && [ -z "$IDS" ] && { echo "$(date +%T) WATCHDOG_DONE" >> $LOG; exit 0; }
  sleep 60
done
