IMG=ghcr.io/epicgames/unreal-engine
mkdir -p /workspace/unreal/blobs && cd /workspace/unreal/blobs
crane manifest $IMG:dev-slim-5.6.1 > manifest.json
python3 -c "import json;[print(l[\"digest\"]) for l in json.load(open(\"manifest.json\"))[\"layers\"]]" > layers.txt
get(){ d=$1; f=${d#sha256:}; for t in 1 2 3 4 5; do crane blob $IMG@$d > $f.part && echo $d | sha256sum >/dev/null && mv $f.part $f && echo OK $d && return 0; echo RETRY $t $d; sleep 3; done; echo FAIL $d; }
export -f get; export IMG
sort -u layers.txt | xargs -P 8 -I{} bash -c "get {}"
rm -f /root/.docker/config.json
echo DL_DONE; date
for d in $(cat layers.txt); do f=${d#sha256:}; tar xzf $f -C /opt/ue --wildcards "home/ue4/UnrealEngine/*" 2>/dev/null; echo X $f $?; done
date; echo PULL2_DONE
