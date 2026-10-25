#!/bin/bash
# usage: iterate.sh N [walk=0|1]  -> renders out/iterN with current params.json, then Argon critic. Prints critique.
N=$1; WALK=${2:-0}; R=/workspace/unreal; D=$R/out/iter$N
mkdir -p $D; cp $R/src/params.json $D/params.json
cd $R/src && python3 gen.py $R/assets > $D/gen.log 2>&1 || { echo GEN_FAILED; tail -5 $D/gen.log; exit 1; }
WJ=false; [ "$WALK" = 1 ] && WJ=true
echo "{\"build\":true,\"reimport\":true,\"out\":\"$D\",\"stills\":true,\"walk\":$WJ,\"res\":[1920,1080],\"temporal\":8}" > $R/run.json
chown -R ue:ue $R/out $R/proj; chmod -R a+rX $R/src $R/assets $R/run.json
bash $R/src/run_ue.sh
cat $R/ue_stage.txt; [ -s $R/ue_error.txt ] && { echo UE_PY_ERROR; cat $R/ue_error.txt; }
python3 $R/src/post.py $D
ls $D/stills_pick/ 2>/dev/null
[ "$(ls $D/stills_pick 2>/dev/null | wc -l)" -ge 1 ] && bash $R/src/critic.sh $D && cat $D/critique.json
