import os, json, re
from common import run, BASE
B = os.path.expanduser("~/cs-audit/gemini-hackathon/assets/built")
SPEC = os.path.expanduser("~/cs-audit/gemini-hackathon/reset/unreal-models/specs-from-managed-agent")
names = sorted(os.listdir(B))
scores = {}
for n in names:
    rs = sorted([d for d in os.listdir(f"{B}/{n}") if d.startswith("round-")]) if os.path.isdir(f"{B}/{n}") else []
    if rs:
        try: scores[n] = json.load(open(f"{B}/{n}/{rs[-1]}/critic.json")).get("score")
        except Exception: pass
inv = "\n".join(f"{n}\t{scores.get(n,'')}" for n in names)
p = ("GAP ANALYSIS on the THRU Blender model lane's real output. Below is the inventory of all " + str(len(names)) + " built Blender assets "
     "(name<TAB>latest Argon critic score /10). Write it to /workspace/inventory.tsv, then with python: bucket assets by PCT region "
     "(SoCal desert, Sierra, NorCal, Oregon, Washington, trail towns/roads/vehicles/gear), count coverage and mean score per bucket, and list low scorers (<5). "
     "Then research online which VISUALLY SIGNATURE real PCT objects are MISSING (things a thru-hiker would instantly recognize) and emit 5 asset specs for "
     "the most important missing ones (one FILE block each, specs/<name>.json, asset-spec schema). Also emit COVERAGE.md (FILE block) with the bucket table, "
     "the low-scorer list, and the missing-asset ranking with reasons.\n\nINVENTORY:\n" + inv)
r, files, it = run("thru-asset-librarian", p, p[:1500] + f"... [+inventory of {len(names)} assets]", label="librarian/gap-analysis-blender-inventory")
od = f"{BASE}/outputs/asset-librarian"; os.makedirs(od, exist_ok=True)
for k, v in files.items():
    if k.endswith(".json"):
        try: d = json.loads(v)
        except Exception: continue
        name = re.sub(r"[^a-z0-9_]+", "_", str(d.get("name", "x")).lower())[:60]
        d["_provenance"] = {"agent": "thru-asset-librarian", "interaction_id": r["interaction_id"], "environment_id": r["environment_id"], "job": "gap-analysis vs assets/built inventory"}
        json.dump(d, open(f"{SPEC}/gap_{name}.json", "w"), indent=1)
    else:
        open(f"{od}/{os.path.basename(k)}", "w").write(v)
print("gap", r["status"], r["interaction_id"], r["environment_id"], r["seconds"], list(files), flush=True)
