#!/bin/bash
# usage: critic.sh ITERDIR  -> writes ITERDIR/critique.json (strict Argon art director, scores /10)
D=$1; cd /workspace/unreal
IM=""; for f in $D/stills_pick/*.png; do IM="$IM -i $f"; done
for r in /workspace/unreal/godot_ref.jpg refs/ref2.jpg refs/ref4.jpg refs/ref5.jpg refs/ref6.jpg; do IM="$IM -i $r"; done
ARGON_LANE=unreal-critic argon -m gemini-4-argon -f src/params.json $IM -g '{"responseMimeType":"application/json"}' - > $D/critique.json <<'P'
You are a strict, senior art director for a photoreal hiking game (THRU, Pacific Crest Trail, Sierra Nevada, 1980-1999).
The first images are Unreal Engine 5 renders of a hero scene (named by file: hero_low, wet_stones, trail, wide, hiker). Then 1 still from the Godot version of the same scene (composition target only). The last 4 images are REAL PHOTOS of Sierra creeks (Tuolumne / Tenaya) for reference.
Target: Sierra creek at golden hour, clear running water that reflects light, wet slick granite, dusty trail ground, conifers.
Score each render 0-10 against the real photos (10 = indistinguishable from a photo; 5 = good game art; be harsh, most game renders are 3-6).
Focus on texture and lighting: water reflection/refraction/clarity, wet stone specular, dust on ground, sun color and shadow quality, exposure, composition.
The params.json file shows every tunable knob. Return ONLY JSON:
{"scores":{"hero_low":n,"wet_stones":n,"trail":n,"wide":n,"hiker":n},"overall":n,
 "top_issues":["...max 6, concrete"],
 "param_changes":{"light":{...},"water":{...},"granite":{...},"dust":{...},"geo":{...}},
 "code_suggestions":["changes needing code edits to gen.py (geometry/textures) or ue_main.py (materials/lighting), concrete, max 4"]}
param_changes must use only keys that exist in params.json, with new numeric values.
P
echo CRITIC_EXIT $?
