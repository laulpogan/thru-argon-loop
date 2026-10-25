import os
from common import run, BASE
U = os.path.expanduser("~/cs-audit/gemini-hackathon/reset/unreal")
OUT = f"{BASE}/outputs/license-auditor"; os.makedirs(OUT, exist_ok=True)
credits = open(f"{U}/import/audio/CREDITS.md").read(); packs = open(f"{U}/ASSET-PACKS.md").read()
p = ("Audit these two text inventories for public YouTube safety (monetized trailer). First write them to /workspace/inputs/CREDITS.md and "
     "/workspace/inputs/ASSET-PACKS.md, then verify each licence claim against the real source pages on the web. Produce LICENSE-AUDIT.md and ATTRIBUTION.txt as FILE blocks.\n\n"
     "=== CREDITS.md (audio) ===\n" + credits + "\n\n=== ASSET-PACKS.md ===\n" + packs)
r, f, it = run("thru-license-auditor", p, p, label="license-auditor/turn1")
for k, v in f.items(): open(f"{OUT}/{os.path.basename(k)}", "w").write(v)
print("audit", r["status"], r["interaction_id"], r["environment_id"], r["seconds"], list(f))
