#!/usr/bin/env python3
"""One live render -> watch -> critique -> fix -> verify cycle against gemini-4-argon.

Step 1 WATCH+CRITIQUE: send the current UE5 stills + real Sierra creek reference photos
        to gemini-4-argon (strict art director). Get per-shot scores, top issues and
        param_changes restricted to knobs that exist in params.json.
Step 2 FIX: apply param_changes to params.json (only existing numeric keys, clamped to
        +/-60% of the old value) and print the unified diff (the patch the loop applies).
Step 3 VERIFY: re-critique the re-rendered stills (live pod render, or the stored UE
        render the loop produced from that fix) with the same rubric and print the delta.

Key: read from env GEMINI_API_KEY only. Never printed.
"""
import argparse, base64, copy, difflib, io, json, os, sys, time, urllib.request, urllib.error, glob

MODEL = os.environ.get("ARGON_MODEL", "gemini-4-argon")
SHOTS = ["hero_low", "wet_stones", "trail", "wide", "hiker"]
RUBRIC = """You are a strict, senior art director for a photoreal hiking game (THRU, Pacific Crest Trail, Sierra Nevada).
The first images are Unreal Engine 5 renders of a hero creek scene (each preceded by its shot name). The last images are REAL PHOTOS of Sierra creeks (Tuolumne / Tenaya) for reference.
Target: Sierra creek at golden hour, clear running water that reflects light, wet slick granite, dusty trail ground, conifers.
Score each render 0-10 against the real photos (10 = indistinguishable from a photo; 5 = good game art; be harsh, most game renders are 3-6).
Focus on texture and lighting: water reflection/refraction/clarity, wet stone specular, dust on ground, sun color and shadow quality, exposure, composition.
The params.json below shows every tunable knob. Return ONLY JSON:
{"scores":{"<shot>":n,...},"overall":n,"top_issues":["max 5, concrete"],
 "param_changes":{"light":{...},"water":{...},"granite":{...},"dust":{...},"geo":{...}},
 "code_suggestions":["max 3"]}
param_changes must use only keys that exist in params.json, with new numeric values."""

def img_part(path, maxw=1280):
    try:
        from PIL import Image
        im = Image.open(path).convert("RGB"); im.thumbnail((maxw, maxw))
        b = io.BytesIO(); im.save(b, "JPEG", quality=82); data = b.getvalue()
    except Exception:
        data = open(path, "rb").read()
    return {"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(data).decode()}}

def argon(stills, refs, params, timeout=240):
    key = os.environ.get("GEMINI_API_KEY")
    if not key: sys.exit("GEMINI_API_KEY is not set in the environment")
    parts = [{"text": "=== params.json ===\n" + json.dumps(params, indent=1)}]
    for s in stills:
        parts += [{"text": f"=== RENDER {os.path.splitext(os.path.basename(s))[0]} ==="}, img_part(s)]
    for r in refs:
        parts += [{"text": f"=== REAL PHOTO {os.path.basename(r)} ==="}, img_part(r, 1024)]
    parts.append({"text": RUBRIC})
    body = json.dumps({"contents": [{"parts": parts}], "generationConfig": {"responseMimeType": "application/json"}}).encode()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
    t0 = time.time()
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, body, {"Content-Type": "application/json", "X-goog-api-key": key})
            d = json.load(urllib.request.urlopen(req, timeout=timeout)); break
        except urllib.error.HTTPError as e:
            msg = e.read()[:300].decode(errors="replace")
            if e.code in (429, 500, 503) and attempt < 2: time.sleep(4 * (attempt + 1)); continue
            sys.exit(f"Argon HTTP {e.code}: {msg}")
    txt = "".join(p.get("text", "") for p in d["candidates"][0]["content"]["parts"] if not p.get("thought"))
    txt = txt.strip().removeprefix("```json").removesuffix("```").strip()
    out = json.loads(txt)
    u = d.get("usageMetadata", {})
    return out, round(time.time() - t0, 1), u.get("promptTokenCount"), u.get("totalTokenCount")

def apply_changes(params, changes):
    new = copy.deepcopy(params); applied = []
    for grp, kv in (changes or {}).items():
        if grp not in new or not isinstance(kv, dict): continue
        for k, v in kv.items():
            if k not in new[grp]: continue
            old = new[grp][k]
            def clamp(o, n):
                if not isinstance(o, (int, float)) or not isinstance(n, (int, float)): return o
                lim = abs(o) * 0.6 if o else 1.0
                return round(max(o - lim, min(o + lim, n)), 4)
            if isinstance(old, list) and isinstance(v, list) and len(old) == len(v):
                nv = [clamp(a, b) for a, b in zip(old, v)]
            else:
                nv = clamp(old, v)
            if nv != old: new[grp][k] = nv; applied.append(f"{grp}.{k}: {old} -> {nv}")
    return new, applied

def show(tag, c, secs, ptok, ttok):
    sc = c.get("scores", {})
    print(f"\n[{tag}] gemini-4-argon verdict in {secs}s ({ptok} prompt tokens, {ttok} total)")
    print("  overall: %s/10   " % c.get("overall") + "  ".join(f"{k} {v}" for k, v in sc.items()))
    for i in c.get("top_issues", [])[:5]: print("  - " + i)

def stills_in(d): return sorted(f for f in glob.glob(os.path.join(d, "*")) if f.lower().endswith((".jpg", ".jpeg", ".png")))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", required=True); ap.add_argument("--refs", required=True)
    ap.add_argument("--params", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--verify-stills", help="re-rendered stills to re-critique (step 3)")
    ap.add_argument("--nrefs", type=int, default=3)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    params = json.load(open(a.params))
    stills = stills_in(a.stills); refs = stills_in(a.refs)[: a.nrefs]
    print(f"[1/3 WATCH+CRITIQUE] {len(stills)} UE5 stills ({a.stills}) + {len(refs)} real Sierra creek photos -> {MODEL}")
    c1, s1, p1, t1 = argon(stills, refs, params)
    json.dump(c1, open(f"{a.out}/critique.json", "w"), indent=1); show("critique", c1, s1, p1, t1)
    new, applied = apply_changes(params, c1.get("param_changes"))
    json.dump(new, open(f"{a.out}/params.next.json", "w"), indent=1)
    diff = "".join(difflib.unified_diff(json.dumps(params, indent=1).splitlines(True), json.dumps(new, indent=1).splitlines(True), "params.json", "params.next.json"))
    open(f"{a.out}/params.patch", "w").write(diff)
    print(f"\n[2/3 FIX] applied {len(applied)} parameter changes (only existing knobs, clamped):")
    for x in applied: print("  " + x)
    for x in c1.get("code_suggestions", [])[:3]: print("  code: " + x)
    print(f"  patch: {a.out}/params.patch")
    if not a.verify_stills:
        print("\n[3/3 VERIFY] skipped (no re-rendered stills given)"); return
    vs = stills_in(a.verify_stills)
    print(f"\n[3/3 VERIFY] re-critique of re-rendered stills ({a.verify_stills}), same rubric, same refs")
    c2, s2, p2, t2 = argon(vs, refs, new)
    json.dump(c2, open(f"{a.out}/verify.json", "w"), indent=1); show("verify", c2, s2, p2, t2)
    try:
        d = float(c2.get("overall")) - float(c1.get("overall"))
        print(f"\nLOOP RESULT: overall {c1.get('overall')} -> {c2.get('overall')}  (delta {d:+.1f})  " + ("FIX VERIFIED" if d > 0 else "NOT IMPROVED -> next iteration feeds verify.json back in"))
    except Exception: pass
    json.dump({"before": c1.get("overall"), "after": c2.get("overall"), "applied": applied}, open(f"{a.out}/summary.json", "w"), indent=1)

if __name__ == "__main__": main()
