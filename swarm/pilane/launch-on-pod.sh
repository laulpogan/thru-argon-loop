#!/bin/bash
# Dell: launch-on-pod.sh <lane> <pod-name>: ship lane files (+ code tree once per pod) and start the pi+Argon orchestrator in pod tmux.
H=~/cs-audit/gemini-hackathon; L=$1; POD=$2; D=$H/reset/$L; P=$H/pilane
read IP PORT < <(python3 -c "import json;p=json.load(open('$H/overflow/$POD-pod.json'));p=p.get('data',p);s=[x for x in p['runtime']['ports'] if x['privatePort']==22 and x['isIpPublic']][0];print(s['ip'],s['publicPort'])")
SSH="ssh -o BatchMode=yes -o ConnectTimeout=15 -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile=$H/overflow/known_hosts -p $PORT root@$IP"
RS="rsync -az -e \"ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile=$H/overflow/known_hosts -p $PORT\""
mkdir -p $D
# lane goal: prefer the original lane prompt goal file
G=$(ls $H/prompts/reset/ext-$L.md $H/prompts/reset/$L.md 2>/dev/null | head -1)
{ cat $P/PI-COMMON.md | sed "s/<lane>/$L/g; s/<LANE>/$(echo $L | tr a-z- A-Z_)/g"; echo; echo "LANE GOAL (from the retired lane's prompt; paths under ~/cs-audit/gemini-hackathon on the Dell are not on this pod unless copied into /work/lanes/$L/shared):"; cat $G 2>/dev/null; } > $D/PROMPT-pi.md
$SSH "mkdir -p /work/lanes/$L/shared /work/lanes/$L/patches /work/lanes/$L/out" || exit 1
if ! $SSH "test -d /work/thru/.git"; then
  eval $RS /tmp/thru-code-81a73b3b50.tar.zst root@$IP:/work/ && $SSH "cd /work && mkdir -p thru && tar -I zstd -xf thru-code-81a73b3b50.tar.zst -C thru && cd thru && git init -q && git config user.email argon@thru.local && git config user.name 'Argon lane' && git add -A >/dev/null && git commit -qm 'base fleet/thru 81a73b3b50 (code only)' && git tag base"
fi
eval $RS $P/pi-loop.sh root@$IP:/work/pi-loop.sh
cp $D/PROMPT-pi.md /tmp/pilane-$L-PROMPT.md
eval $RS /tmp/pilane-$L-PROMPT.md root@$IP:/work/lanes/$L/PROMPT.md
for f in HANDOFF.md STEER.md STATUS.md LOG.md PLAN.md; do [ -f $D/$f ] && eval $RS $D/$f root@$IP:/work/lanes/$L/$f; done
[ -d $D/shared-extra ] && eval $RS $D/shared-extra/ root@$IP:/work/lanes/$L/shared/
eval $RS $H/walkthrough/route.json $H/walkthrough/route-hero.json $H/model3/GUIDE.md root@$IP:/work/lanes/$L/shared/ 2>/dev/null
[ -f $H/reset/assetfactory/manifest/argon-manifest.json ] && eval $RS $H/reset/assetfactory/manifest/argon-manifest.json root@$IP:/work/lanes/$L/shared/
ffmpeg -loglevel error -y -i $H/walkthrough/before-run1/frames/f-00380.png -vf scale=960:-1 /tmp/pilane-before.jpg 2>/dev/null; eval $RS /tmp/pilane-before.jpg root@$IP:/work/lanes/$L/shared/before-campo.jpg
$SSH "tmux has-session -t lane-$L 2>/dev/null || tmux new-session -d -s lane-$L 'bash /work/pi-loop.sh $L'"
echo "$L $POD $IP $PORT" >> $P/lanes.tsv
echo "$(date +%T) launched $L on $POD" >> $P/launch.log
