#!/usr/bin/env python3
"""Offline spatial mix from real recordings and the scene's generated walk/emitters."""
import argparse,json,pathlib,wave,subprocess
import numpy as np
p=argparse.ArgumentParser();p.add_argument('root',type=pathlib.Path);p.add_argument('--duration',type=float,default=18);a=p.parse_args();root=a.root
pl=json.load(open(root/'assets/placements.json'));emit=json.load(open(root/'out/emitters.json'));manifest=json.load(open(root/'audio/manifest.json'));rate=48000;n=int(a.duration*rate);mix=np.zeros((n,2),np.float64)
def read(role):
    v=next(v for v in manifest['assets'] if v['role']==role)
    with wave.open(str(root/'audio'/v['file'])) as f:
        assert f.getframerate()==rate and f.getsampwidth()==2 and f.getnchannels()==1
        return np.frombuffer(f.readframes(f.getnframes()),'<i2').astype(float)/32768
seconds=np.arange(n)/rate;keys=np.array([k['f']/24 for k in pl['walk']]);pos=np.array([k['pos'] for k in pl['walk']]);listener=np.stack([np.interp(seconds,keys,pos[:,j]) for j in range(3)],axis=1)
# Position-to-gain evaluated at 100 Hz to keep memory/work bounded.
for role,volume in [('creek',.36),('wind',.19),('bird',.14),('insects',.07)]:
    source=read(role);source/=max(.02,np.sqrt(np.mean(source**2)))*8
    # Crossfade loop endpoints over 100 ms; source recordings remain real.
    fade=min(4800,len(source)//8);source[:fade]*=np.linspace(0,1,fade);source[-fade:]*=np.linspace(1,0,fade)
    stream=np.resize(source,n);anchors=np.array([v['pos_m'] for v in emit if v['role']==role]);small=listener[::480];delta=anchors[None,:,:]-small[:,None,:];distance=np.linalg.norm(delta,axis=2);which=np.argmin(distance,axis=1);d=distance[np.arange(len(small)),which];pan=np.clip(delta[np.arange(len(small)),which,0]/15,-.7,.7);gain=volume/(1+(d/18)**2)
    for side,sgn in [(0,-1),(1,1)]:mix[:,side]+=stream*np.interp(seconds,seconds[::480],gain*np.sqrt((1+sgn*pan)/2))
used=[]
for i,step in enumerate(pl['steps']):
    if step['time']>=a.duration:continue
    role=step['surface'];source=read(role);window=min(len(source),int(.28*rate));energy=np.convolve(source[::480]**2,np.ones(12)/12,'same');peak=int(np.argmax(energy))*480;start=max(0,min(len(source)-window,peak-window//3));clip=source[start:start+window].copy();clip*=np.minimum(np.arange(len(clip))/240,1)*np.minimum(np.arange(len(clip))[::-1]/1200,1);clip*=.2/max(.03,np.max(np.abs(clip)));offset=int(step['time']*rate);end=min(n,offset+len(clip));pan=-.2 if i%2 else .2
    for side,sgn in [(0,-1),(1,1)]:mix[offset:end,side]+=clip[:end-offset]*np.sqrt((1+sgn*pan)/2)
    used.append(dict(time=step['time'],surface=role))
peak=float(np.max(np.abs(mix)));mix*=min(1,.9/max(peak,.001));dest=root/'out/walk_audio.wav'
with wave.open(str(dest),'wb') as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(rate);f.writeframes((mix*32767).astype('<i2').tobytes())
json.dump(dict(duration_s=a.duration,method='Offline stereo distance/pan approximation from procedural anchors and walk; ffmpeg mux',real_recordings=True,peak_before_limiting=peak,peak_final=float(np.max(np.abs(mix))),rms=float(np.sqrt(np.mean(mix**2))),steps=used),open(root/'out/audio_mix.json','w'),indent=2)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(dest),'-lavfi','showspectrumpic=s=1200x500:legend=1',str(root/'out/audio_spectrogram.png')],check=True)
print('MIX_OK',a.duration,len(used),peak)
