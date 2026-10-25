import sys,os,glob,shutil,json,subprocess
D=sys.argv[1]; HOLD=24; names=["hero_low","wet_stones","trail","wide","hiker"]
os.makedirs(f"{D}/stills_pick",exist_ok=True)
fr=sorted(glob.glob(f"{D}/stills/*.png")); print("still frames",len(fr))
for i,n in enumerate(names):
    want=[f for f in fr if f.endswith(f".{HOLD*(i+1)-1:04d}.png")]
    if want: shutil.copy(want[0],f"{D}/stills_pick/{n}.png")
w=sorted(glob.glob(f"{D}/walk/*.png"))
if w:
    pat=w[0].rsplit(".",2)[0]+".%04d.png"
    A="/workspace/unreal/assets"
    subprocess.run(["ffmpeg","-y","-loglevel","error","-framerate","60","-start_number",w[0].rsplit(".",2)[1],"-i",pat,"-i",f"{A}/Sierra_alpine_dusk.wav","-i",f"{A}/creek_medium.wav",
      "-filter_complex","[0:v]scale=in_range=full:out_range=tv,format=yuv420p[v];[1:a]volume=0.9[b];[2:a]volume=0.8[c];[b][c]amix=inputs=2:duration=longest,aresample=48000[a]","-map","[v]","-map","[a]","-shortest",
      "-c:v","libx264","-profile:v","high","-preset","slow","-crf","16","-colorspace","bt709","-color_primaries","bt709","-color_trc","bt709","-color_range","tv","-movflags","+faststart","-c:a","aac","-ar","48000","-b:a","256k",f"{D}/walk.mp4"],check=False)
    print("walk frames",len(w),os.path.exists(f"{D}/walk.mp4"))
