import json, time, os, re, random, threading, base64, io, traceback
from google import genai
BASE = os.path.expanduser("~/cs-audit/gemini-hackathon/managed-agents")
RUNS = os.path.join(BASE, "RUNS.jsonl")
_lock = threading.Lock()
client = genai.Client()  # key comes from env (sourced), never printed

def dump(o):
    try: return o.model_dump(mode="json", exclude_none=True)
    except Exception:
        try: return json.loads(json.dumps(o, default=str))
        except Exception: return str(o)

def log_run(rec):
    with _lock:
        with open(RUNS, "a") as f: f.write(json.dumps(rec, default=str) + "\n")

def extract_files(text):
    """Agents emit files as <<<FILE path>>> ... <<<END>>> blocks in their final answer."""
    out = {}
    for m in re.finditer(r"<<<FILE\s+([^>\s]+)\s*>>>\s*\n(.*?)\n\s*<<<END>>>", text or "", re.S):
        out[m.group(1).strip()] = m.group(2).strip("\n")
    return out

def run(agent_id, input_, prompt_text, environment="remote", previous=None, label="", max_wait=1500, tries=6):
    t0 = time.time(); err = None; it = None
    for attempt in range(tries):
        try:
            kw = dict(agent=agent_id, input=input_, environment=environment, background=True)
            if previous: kw["previous_interaction_id"] = previous
            it = client.interactions.create(**kw)
            while it.status in ("in_progress", "queued", None) and time.time() - t0 < max_wait:
                time.sleep(8)
                try: it = client.interactions.get(id=it.id)
                except Exception as e:
                    if "429" in str(e): time.sleep(15)
                    else: raise
            break
        except Exception as e:
            err = str(e)[:500]
            if "429" in err or "RESOURCE_EXHAUSTED" in err or "503" in err:
                time.sleep(min(120, 10 * 2 ** attempt) + random.random() * 5); continue
            break
    t1 = time.time()
    text = getattr(it, "output_text", None) if it else None
    files = extract_files(text)
    rec = dict(ts=time.strftime("%Y-%m-%dT%H:%M:%S%z"), label=label, agent=agent_id,
               interaction_id=getattr(it, "id", None), environment_id=getattr(it, "environment_id", None),
               previous_interaction_id=previous, status=getattr(it, "status", None) if it else "error",
               error=err, prompt=prompt_text, output_text=text, files=list(files),
               usage=dump(getattr(it, "usage", None)) if it else None, seconds=round(t1 - t0, 1))
    log_run(rec)
    return rec, files, it

def jpg_b64(path, maxw=1280, q=80):
    from PIL import Image
    im = Image.open(path).convert("RGB"); im.thumbnail((maxw, maxw))
    b = io.BytesIO(); im.save(b, "JPEG", quality=q); return base64.b64encode(b.getvalue()).decode()
