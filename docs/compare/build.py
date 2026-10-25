#!/usr/bin/env python3
# Rebuild side-by-side.jpg + SCORES.md. GODOT_SET/UNREAL_SET dirs hold hero_low/wet_stones/trail/wide.jpg + scores.raw
import json,os,sys,time
from PIL import Image,ImageDraw,ImageFont
os.chdir('/workspace/argon/compare')
G=os.environ.get('GODOT_SET','godot-dry'); GL=os.environ.get('GODOT_LABEL','Godot current best (Pitcrew full dry look-argon capture, 2:49 PM; add-on variant paused at 2:49)')
U=os.environ.get('UNREAL_SET','unreal'); UL=os.environ.get('UNREAL_LABEL','Unreal iter'+open('unreal/ITER').read().strip().replace('iter',''))
shots=["hero_low","wet_stones","trail","wide"]; keys=["reflection","wetness","dust_roughness","light","geometry","texture"]; ab=["R","W","D","L","G","T"]
def load(p):
    t=open(p).read(); return json.loads(t[t.find('{'):t.rfind('}')+1])
sc={G:load(f'{G}/scores.raw'),U:load(f'{U}/scores.raw')}
W,H=640,360; f=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",20); fs=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",17)
sheet=Image.new("RGB",(W*4,40+2*(H+60)),(15,15,15)); d=ImageDraw.Draw(sheet)
d.text((10,8),f"THRU hero creek: Godot (top) vs Unreal (bottom). Argon six-score AAA critic, 0-10. {time.strftime('%H:%M')} PT",fill="white",font=f)
for r,(S,lab) in enumerate(((G,GL),(U,UL))):
    y=40+r*(H+60); m=sum(sc[S][s][k] for s in shots for k in keys)/24
    d.text((10,y+4),f"{lab}  |  mean {m:.1f}",fill=(255,210,120),font=f)
    for i,s in enumerate(shots):
        im=Image.open(f"{S}/{s}.jpg").convert("RGB"); im=im.resize((W,int(im.height*W/im.width))).crop((0,0,W,H))
        sheet.paste(im,(i*W,y+30)); v=sc[S][s]
        txt=f"{s}  "+" ".join(f"{a}{v[k]}" for a,k in zip(ab,keys))+f"  avg {sum(v[k] for k in keys)/6:.1f}"
        d.rectangle((i*W,y+30+H-28,i*W+W,y+30+H),fill=(0,0,0)); d.text((i*W+6,y+30+H-25),txt,fill="white",font=fs)
sheet.save("side-by-side.jpg",quality=88)
L=["# Hero creek: Godot vs Unreal, Argon six-score AAA critic","",f"Built {time.strftime('%H:%M')} PT. Each set scored with one gemini-4-argon call against AAA-STANDARD.md, 0-10; 7 or above passes. Key: R=REFLECTION W=WETNESS D=DUST/ROUGHNESS L=LIGHT G=GEOMETRY T=TEXTURE.","",
f"- Top row: **{GL}** (`{G}/`)",f"- Bottom row: **{UL}** (`{U}/`, from reset/unreal/out/LOOP.md)",
"- Shots use the Unreal names from reset/unreal/CAMERAS.json. The Godot images are the closest existing framings (low, wet-cobble, detail, overview), not re-rendered from Unreal's cameras. No build has a hiker-in-frame shot yet.","",
"| Shot | Build | R | W | D | L | G | T | Mean |","|---|---|---|---|---|---|---|---|---|"]
for s in shots:
    for S,n in ((G,"Godot"),(U,"Unreal")):
        v=[sc[S][s][k] for k in keys]; L.append(f"| {s} | {n} | "+" | ".join(map(str,v))+f" | {sum(v)/6:.1f} |")
for S,n in ((G,"Godot"),(U,"Unreal")):
    L.append(f"| **all** | {n} | "+" | ".join(f"{sum(sc[S][s][k] for s in shots)/4:.1f}" for k in keys)+f" | **{sum(sc[S][s][k] for s in shots for k in keys)/24:.1f}** |")
L+=["","## Critic notes"]+[f"- **{n} / {s}:** {sc[S][s].get('note','')}" for S,n in ((G,"Godot"),(U,"Unreal")) for s in shots]
if os.path.exists('godot-current/scores.raw'):
    g0=load('godot-current/scores.raw'); L+=["","Also scored: Godot after-rain look-argon capture (2:31 PM) per-shot means: "+", ".join(f"{s} {sum(g0[s][k] for k in keys)/6:.1f}" for s in shots)]
L+=["","Unreal LOOP.md (its own critic):","```",open('unreal/LOOP.md').read().strip(),"```"]
open('SCORES.md','w').write("\n".join(L)+"\n"); print("ok")
