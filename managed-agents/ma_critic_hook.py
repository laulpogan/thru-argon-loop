"""Parallel critic hook for the live Unreal loop.
Watches reset/unreal/PROGRESSION/ for new render stills and sends them to the persisted managed agent
`thru-art-director`, reusing ONE persistent sandbox (environment_id) + interaction chain across iterations,
so the agent keeps /workspace/memory/critiques.jsonl and its reference photos as memory.
Writes reset/unreal/out/managed-critic/<stamp>.json (critic.sh-compatible schema) + reset/unreal/MANAGED-CRITIC.md,
and appends a one-line pointer to reset/unreal/STEER.md so the next render iteration picks the fixes up.
usage: ma_critic_hook.py [--once] [--env ENV_ID --prev INTERACTION_ID]"""
import os, sys, json, time, glob, re
from common import run, jpg_b64, BASE
U = os.path.expanduser("~/cs-audit/gemini-hackathon/reset/unreal")
P = f"{U}/PROGRESSION"; OUT = f"{U}/out/managed-critic"; os.makedirs(OUT, exist_ok=True)
STATE = f"{BASE}/hook_state.json"
st = json.load(open(STATE)) if os.path.exists(STATE) else {"env": None, "prev": None, "done": [], "iters": 0}
a = sys.argv
if "--env" in a: st["env"] = a[a.index("--env") + 1]
if "--prev" in a: st["prev"] = a[a.index("--prev") + 1]
DIR = a[a.index("--dir") + 1] if "--dir" in a else None
TAG = a[a.index("--tag") + 1] if "--tag" in a else None
def params():
    for p in ((f"{OUT}/params_current.json",) + (f"{U}/src-snapshot/src/params.json",)):
        if os.path.exists(p): return open(p).read()
    return "{}"
def step():
    src = DIR or P
    new = sorted(f for f in glob.glob(f"{src}/*.png") + glob.glob(f"{src}/*.jpg") if os.path.basename(f) not in st["done"])
    if not new: return False
    if TAG:
        pref = TAG; batch = new[:5]
    else:
        pref = os.path.basename(new[-1]).split("_")[0]
        batch = [f for f in new if os.path.basename(f).startswith(pref)][:5]
    names = [os.path.basename(f) for f in batch]
    txt = ("LIVE LOOP ITERATION. New Unreal stills from the render loop: " + ", ".join(names) + ".\n"
           "Memory: first `mkdir -p /workspace/memory` and read /workspace/memory/critiques.jsonl if it exists (your earlier critiques of previous iterations), "
           "and reuse reference photos you already saved in this sandbox. Compare the new stills against the real Sierra references AND against your previous critique: "
           "say what improved/regressed.\nThe loop's tunable knobs (params.json):\n" + params() +
           "\nReturn the critique as ONE FILE block named critique.json with EXACTLY this schema (critic.sh compatible): "
           '{"iteration":"' + pref + '","scores":{"<still name>":n},"overall":n,"delta_vs_previous":"...","top_issues":["max 6, concrete"],'
           '"param_changes":{"light":{},"water":{},"granite":{},"dust":{},"geo":{}},"code_suggestions":["max 4"],"references":[{"url":"","license":""}]}. '
           "param_changes must only use keys that exist in params.json, with new numeric values. Scores 0-10, harsh (real photo = 10). "
           + (("The loop APPLIED your previous param_changes for this pass (params shown above are what was rendered). Explicitly cite your previous critique: "
              "for each previous top issue say fixed / partly / not fixed, and give the score change per shot. ") if st["iters"] else "") + "Before answering, append the critique as one line to /workspace/memory/critiques.jsonl.")
    inp = [{"type": "text", "text": txt}] + [{"type": "image", "mime_type": "image/jpeg", "data": jpg_b64(f)} for f in batch]
    env = st["env"] or "remote"
    r, files, it = run("thru-art-director", inp, txt + f" [+{len(batch)} inline jpg stills]", environment=env, previous=st["prev"],
                       label=f"art-director/live-hook-iter{pref}")
    print(time.strftime("%H:%M:%S"), pref, r["status"], r["interaction_id"], r["environment_id"], r["seconds"], list(files), flush=True)
    if r["status"] != "completed": return False
    st["env"] = r["environment_id"] or st["env"]; st["prev"] = r["interaction_id"]; st["done"] += names; st["iters"] += 1
    json.dump(st, open(STATE, "w"), indent=1)
    crit = files.get("critique.json")
    if crit is None:
        m = re.search(r"\{.*\}", r["output_text"] or "", re.S); crit = m.group(0) if m else None
    try: cj = json.loads(crit)
    except Exception: cj = {"raw": crit}
    cj["_managed_agent"] = {"agent": "thru-art-director", "interaction_id": r["interaction_id"], "environment_id": r["environment_id"], "stills": names}
    stamp = time.strftime("%H%M")
    json.dump(cj, open(f"{OUT}/{stamp}_{pref}.json", "w"), indent=1)
    md = (f"# Managed art-director critique (live hook) {time.strftime('%H:%M')} PT\n- agent `thru-art-director`, interaction `{r['interaction_id']}`\n"
          f"- persistent environment `{r['environment_id']}` (iteration {st['iters']} of the memory chain)\n- stills: {', '.join(names)}\n"
          f"- overall: {cj.get('overall')}  scores: {json.dumps(cj.get('scores'))}\n- delta vs previous: {cj.get('delta_vs_previous')}\n\n## Top issues\n"
          + "\n".join(f"- {x}" for x in cj.get("top_issues", [])) + f"\n\n## param_changes (params.json keys)\n```json\n{json.dumps(cj.get('param_changes'), indent=1)}\n```\n")
    # merged params for the next render iteration (params.json + managed param_changes, only existing keys)
    try:
        base = json.loads(params()); pc = cj.get("param_changes") or {}
        for grp, kv in pc.items():
            if grp in base and isinstance(kv, dict):
                for k, v in kv.items():
                    if k in base[grp]: base[grp][k] = v
        json.dump(base, open(f"{OUT}/params_next.json", "w"), indent=1)
        md += f"\nMerged next-iteration params: `reset/unreal/out/managed-critic/params_next.json`\n"
    except Exception as e: print("merge err", e)
    open(f"{U}/MANAGED-CRITIC.md", "w").write(md)
    with open(f"{U}/STEER.md", "a") as f:
        f.write(f"\n[{time.strftime('%H:%M')}] MANAGED-AGENT CRITIC (thru-art-director, env {r['environment_id'][:24]}...): iter {pref} overall {cj.get('overall')}/10. "
                f"param_changes + top issues in reset/unreal/MANAGED-CRITIC.md and out/managed-critic/{stamp}_{pref}.json; apply on next iteration.\n")
    return True
if "--once" in a: step()
else:
    while True:
        try: step()
        except Exception as e: print("hook error", str(e)[:300], flush=True)
        time.sleep(60)
