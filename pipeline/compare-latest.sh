# Dell: fetch newest complete Unreal iteration picks into compare/unreal and score it (skip if unchanged)
H=~/cs-audit/gemini-hackathon; C=$H/compare/unreal; read IP PORT N ST < <(cd ~/hackathon-git && python3 unrealpod.py)
SSH="ssh -o BatchMode=yes -o UserKnownHostsFile=$H/overflow/known_hosts -p $PORT"
IT=$(timeout 30 $SSH root@$IP 'cd /workspace/unreal/out; for d in $(ls -d iter[0-9]* | sort -V -r); do [ -f $d/stills_pick/wide.png ] && [ -f $d/stills_pick/hero_low.png ] && { echo $d; break; }; done')
[ -n "$IT" ] || exit 1; [ "$IT" = "$(cat $C/ITER)" ] && { echo same $IT; exit 0; }
rsync -a -e "$SSH" root@$IP:/workspace/unreal/out/$IT/stills_pick/ $C/pick/ && rsync -a -e "$SSH" root@$IP:/workspace/unreal/out/LOOP.md $C/LOOP.md
for s in hero_low wet_stones trail wide; do ffmpeg -loglevel error -y -i $C/pick/$s.png -vf scale=1600:-1 -q:v 3 $C/$s.jpg; done
set -a; . ~/.config/gemini/hackathon.env; set +a
PROMPT='You are a strict AAA art director. These 4 images are shots of a Sierra Nevada creek hero scene, in order: hero_low (bank-level low shot upstream), wet_stones (wet stones at the waterline), trail, wide. Score EACH shot 0-10 on REFLECTION, WETNESS, DUST_ROUGHNESS, LIGHT, GEOMETRY, TEXTURE against real Sierra creek photographs and the attached AAA standard (10 = indistinguishable from a photo / AAA game). Be harsh and consistent. Return ONLY JSON: {"hero_low":{"reflection":n,"wetness":n,"dust_roughness":n,"light":n,"geometry":n,"texture":n,"note":"..."},"wet_stones":{...},"trail":{...},"wide":{...}}'
ARGON_LANE=compare timeout 300 ~/.local/bin/argon -m gemini-4-argon -f $H/AAA-STANDARD.md -i $C/hero_low.jpg -i $C/wet_stones.jpg -i $C/trail.jpg -i $C/wide.jpg "$PROMPT" > $C/scores.new 2>$C/scores.err && [ -s $C/scores.new ] && mv $C/scores.new $C/scores.raw && echo $IT > $C/ITER && echo updated $IT
