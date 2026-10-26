# passhk.sh port host passname a b '<extra json fields, leading comma>'   (pass2.sh + clean gear/hiker import + hiker_alt files)
p=$1; h=$2; pn=$3; a=$4; b=$5; X=$6
ssh -p $p root@$h "tar xf - -C /workspace/unreal/src" < /tmp/srchk.tar
ssh -p $p root@$h "tar xf - -C /workspace/unreal/packs" < /tmp/gear.tar
ssh -p $p root@$h "tar xf - -C /workspace/unreal/packs" < /tmp/hiker_alt.tar
printf '{"build":true,"reimport":true,"out":"/workspace/unreal/out/%s","stills":false,"walk":true,"res":[1920,1080],"temporal":8,"walk_temporal":1,"walk_res":[1920,1080],"walk_range":[%s,%s],"skip_packs":["ponderosa_pine","grand_fir","western_hemlock","riparian_"]%s}\n' "$pn" "$a" "$b" "$X" > /tmp/run_$pn_$p.json
python3 -c "import json,sys;json.load(open('/tmp/run_$pn_$p.json'))" || { echo BADJSON; exit 1; }
ssh -p $p root@$h "cat > /workspace/unreal/run.next.json" < /tmp/run_$pn_$p.json
ssh -p $p root@$h "R=/workspace/unreal; cd \$R; tmux kill-session -t $pn 2>/dev/null; for q in \$(pgrep -u ue UnrealEditor); do kill \$q; done; rm -f nohiker.flag; [ -f packs/shrubs/bracken_cured.glb ] && mv packs/shrubs/bracken_cured.glb packs/bracken_cured.glb.off; rm -rf proj/Content/Pack/bracken_cured proj/Content/Mesh/backpack proj/Content/Mesh/hat proj/Content/Pack/hiker_alt proj/Content/T/T_Pack_D.uasset proj/Content/T/T_Pack_N.uasset; D=\$R/out/$pn; rm -rf \$D; mkdir -p \$D; cd src && python3 gen.py \$R/assets > \$D/gen.log 2>&1; tail -1 \$D/gen.log; cd \$R; mv run.next.json run.json; chown -R ue:ue proj out; chmod -R a+rX src assets run.json real packs; tmux new -d -s $pn \"UE_TIMEOUT=2400 bash src/run_ue.sh; python3 src/post.py \$D > \$D/post.log 2>&1\"; echo LAUNCHED_${h}_$p"
