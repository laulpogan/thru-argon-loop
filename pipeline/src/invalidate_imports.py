#!/usr/bin/env python3
"""Run OUTSIDE the editor (launcher calls it). For every manifest entry whose source content changed,
move its Content packages to a trash dir so the next editor session imports them fresh (no in-place
replace_existing reimport -> no UE-23902 stale-texture crash). Nothing is deleted."""
import json,os,hashlib,shutil,time,sys
ROOT="/home/dellpromax/ue/ws"; CONTENT="/home/dellpromax/ue/proj/Content"
TRASH=f"/mnt/models/thru-ue/content_trash/{time.strftime('%Y%m%d-%H%M%S')}"
M=f"{ROOT}/import_manifest.json"
if not os.path.exists(M): print("no manifest; nothing to invalidate"); sys.exit(0)
man=json.load(open(M)); moved=0
def sig(f):
    h=hashlib.sha1()
    with open(f,"rb") as fh:
        for ch in iter(lambda: fh.read(1<<20),b""): h.update(ch)
    return h.hexdigest()
for src,e in list(man.items()):
    if not os.path.exists(src) or e.get("sig") is None: continue
    if sig(src)==e["sig"]: continue
    rel=e["dest"].replace("/Game/","",1)
    if src.lower().endswith((".png",".jpg",".jpeg",".tga",".exr")): paths=[os.path.join(CONTENT,rel,e["name"]+".uasset")]
    else: paths=[os.path.join(CONTENT,rel)]
    for pth in paths:
        if os.path.exists(pth):
            dst=os.path.join(TRASH,os.path.relpath(pth,CONTENT)); os.makedirs(os.path.dirname(dst),exist_ok=True); shutil.move(pth,dst); moved+=1
            print("invalidated",src,"->",dst)
    del man[src]
json.dump(man,open(M,"w"),indent=1); print("invalidated",moved)
