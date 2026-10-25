import os, json
from common import run, jpg_b64, BASE
P = os.path.expanduser("~/cs-audit/gemini-hackathon/reset/unreal/PROGRESSION")
OUT = f"{BASE}/outputs/art-director"; os.makedirs(OUT, exist_ok=True)
stills = ["1505_hero_low_iter2-dense-route-hiker-pack-trees.png", "1505_wide_iter2-dense-route-hiker-pack-trees.png",
          "1505_hiker_iter2-dense-route-hiker-pack-trees.png", "1440_wide_iter1-first-render.png"]
log = open(f"{P}/LOG.md").read()
p1 = ("Here are 4 Unreal Engine 5.6 render stills from THRU (in order: " + ", ".join(stills) + "). Scene intent: a High Sierra creek crossing on the "
      "PCT/JMT at golden hour, a hiker on a log/bridge path, granite boulders, conifers, ferns/grass. Build log for context:\n" + log +
      "\nNo Blender turntables exist yet. Do the full photoreal-critique skill: find 4-6 real CC-licensed reference photos on Wikimedia Commons, "
      "compare, score each still 1-10, and write FIXES.md (save to /workspace/out/FIXES.md AND emit it as a FILE block).")
inp = [{"type": "text", "text": p1}] + [{"type": "image", "mime_type": "image/jpeg", "data": jpg_b64(f"{P}/{s}")} for s in stills]
r1, f1, it1 = run("thru-art-director", inp, p1 + " [+4 inline jpg stills]", label="art-director/turn1")
for k, v in f1.items(): open(f"{OUT}/{os.path.basename(k)}", "w").write(v)
print("turn1", r1["status"], r1["interaction_id"], r1["environment_id"], r1["seconds"], list(f1))
if r1["environment_id"]:
    p2 = ("Continue in the same sandbox. Re-open /workspace/out/FIXES.md and the reference photos you saved earlier (list /workspace to prove they persisted). "
          "Turn the P0/P1 fixes into a machine-readable UE5 task list FIXES-TASKS.json: [{id, priority, target (material|foliage|lighting|asset|camera), "
          "ue_object, parameter, current_guess, target_value, reference_url, expected_score_gain}]. Validate it with python, then emit it as a FILE block. "
          "Also emit a 5-line JUDGE-SUMMARY.md: the single biggest gap between the renders and the real Sierra, and the fastest 3 wins.")
    r2, f2, it2 = run("thru-art-director", p2, p2, environment=r1["environment_id"], previous=r1["interaction_id"], label="art-director/turn2-same-env")
    for k, v in f2.items(): open(f"{OUT}/{os.path.basename(k)}", "w").write(v)
    print("turn2", r2["status"], r2["interaction_id"], r2["environment_id"], r2["seconds"], list(f2))
