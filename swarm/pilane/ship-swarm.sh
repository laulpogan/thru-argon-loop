#!/bin/bash
# Dell: wait for the bundle, ship to 6 pilane pods, start shard runners in pod tmux; register swarm-N lanes for sync; then merge results back every 2 min.
H=~/cs-audit/gemini-hackathon; P=$H/pilane
until grep -q BUNDLE_DONE $P/bundle.log; do sleep 15; done
PODS=(6 7 8 14 15 16); N=${#PODS[@]}
for s in $(seq 0 $((N-1))); do
  POD=thru-cpu-overflow-pilane-${PODS[$s]}
  read IP PORT < <(python3 -c "import json;p=json.load(open('$H/overflow/$POD-pod.json'));p=p.get('data',p);s=[x for x in p['runtime']['ports'] if x['privatePort']==22 and x['isIpPublic']][0];print(s['ip'],s['publicPort'])")
  E="ssh -o BatchMode=yes -o ConnectTimeout=15 -o UserKnownHostsFile=$H/overflow/known_hosts -p $PORT"
  rsync -az -e "$E" /tmp/swarm-bundle.tar.zst $P/pjob.sh $P/prunner.sh root@$IP:/work/ && \
  $E root@$IP "cd /work && tar -I zstd -xf swarm-bundle.tar.zst && tmux new-session -d -s lane-swarm-$s 'bash /work/prunner.sh $s $N 8'" && \
  echo "swarm-$s $POD $IP $PORT" >> $P/lanes.tsv && echo "$(date +%T) launched swarm-$s on $POD" >> $P/launch.log
done
while [ $(date +%H%M) -lt 1800 ]; do
  for s in $(seq 0 $((N-1))); do
    O=$H/reset/swarm-$s/pod/out; [ -d $O ] || continue
    [ -d $O/swarm ] && rsync -a --ignore-existing $O/swarm/ $H/swarm/
    for m in $(ls $O | grep -v "^swarm$"); do rsync -a --ignore-existing $O/$m/ $H/council/$m/; done
  done
  sleep 120
done
