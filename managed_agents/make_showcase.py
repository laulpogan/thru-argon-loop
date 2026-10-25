import json, os, glob, collections
from common import BASE
SPEC = os.path.expanduser("~/cs-audit/gemini-hackathon/reset/unreal-models/specs-from-managed-agent")
runs = [json.loads(l) for l in open(f"{BASE}/RUNS.jsonl")]
agents = json.load(open(f"{BASE}/AGENTS.json"))
def tok(u, k):
    if not isinstance(u, dict): return 0
    return u.get(k) or 0
tot = collections.Counter(); per = collections.defaultdict(collections.Counter)
for r in runs:
    u = r.get("usage") or {}
    for k in ("total_tokens", "total_input_tokens", "total_output_tokens", "total_cached_tokens", "total_thought_tokens"):
        tot[k] += tok(u, k); per[r["agent"]][k] += tok(u, k)
    per[r["agent"]]["n"] += 1; per[r["agent"]]["ok"] += r["status"] == "completed"; per[r["agent"]]["sec"] += r["seconds"] or 0
fan = [r for r in runs if r['label'].startswith('librarian/fanout')]
specs = sorted(glob.glob(f"{SPEC}/*.json"))
def section(path, n=60):
    try: return "\n".join(open(path).read().splitlines()[:n])
    except Exception: return "(missing)"
A = f"{BASE}/outputs/art-director"; L = f"{BASE}/outputs/license-auditor"
envs = collections.Counter(r["environment_id"] for r in runs if r.get("environment_id"))
HOOK = os.path.expanduser("~/cs-audit/gemini-hackathon/reset/unreal/MANAGED-CRITIC.md")
NOTES = f"{BASE}/NOTES.md"
import sys
STATUS = sys.argv[1] if len(sys.argv) > 1 else "final"
md = f"""# THRU x Gemini Managed Agents: SHOWCASE ({STATUS}, generated {__import__('time').strftime('%H:%M')} PT)

> **How we used Managed Agents (submission blurb):** THRU runs three persisted Gemini Managed Agents: an art director that critiques every new Unreal render against real CC-licensed Sierra photos and feeds a scored fix list back into the render loop from one persistent sandbox that remembers past critiques, an asset librarian that fanned out across the whole Pacific Crest Trail in parallel sandboxes to write build-ready asset specs for our Blender lane, and a licence auditor that checks credits for YouTube safety. Each agent is defined once with its own instructions and mounted skills, then invoked by ID, so research, critique and compliance run as hosted jobs instead of on our overloaded workstation.

Gemini 4 Argon hackathon, category "best use of managed agents". Built and run on Oct 25 2026 (PT) from Paul Logan's Dell workstation with the
Interactions API (`google-genai` {__import__('importlib.metadata').metadata.version('google-genai')}), base agent `antigravity-preview-09-2026`, model `gemini-3.8-flash`.

**THRU** is a photoreal co-op Pacific Crest Trail hiking game (UE 5.6, Lumen). It needs three kinds of grind work done all the time:
art critique against reality, research for thousands of real-world assets, and licence hygiene before anything goes on YouTube.
Each one is now a **named, persisted managed agent**, each with its own system instruction, mounted `.agents/AGENTS.md` and a mounted `SKILL.md`.

## The agents (persisted by ID)

| Agent ID | Role | Mounted skill | Runs | Completed | Tokens |
|---|---|---|---|---|---|
""" + "\n".join(f"| `{a}` | {agents[a].get('description','')} | `.agents/skills/*/SKILL.md` | {per[a]['n']} | {per[a]['ok']} | {per[a]['total_tokens']:,} |" for a in agents) + f"""

## Why managed agents fit THRU
- **A hosted Linux sandbox per job.** Each critique, research or audit job gets its own Google-hosted VM with Python, web search and URL fetch, so the agent can
  actually download reference thumbnails, compute colour stats, validate JSON with `json.loads`, and hold intermediate files. Nothing runs on, or fills, the Dell (its disk is ~99% full).
- **Persistent environments.** The art director's 2nd turn reuses the same `environment_id`: it re-opens its own `FIXES.md` and saved reference photos
  from turn 1 and turns them into a machine-readable UE5 task list. That's a stateful art-review loop, not a stateless chat.
- **Fan-out at scale.** The asset librarian ran **{len(fan)} parallel interactions** (8 at a time, with 429 backoff), one per PCT section/theme from Campo to the Canadian border, plus 1 gap-analysis job over the Blender lane's 832-asset inventory,
  each in its own sandbox, producing **{len(specs)} asset-spec JSON files** that the Blender lane picks up directly.
- **Config as code.** Agents are defined once (`setup_agents.py`) with `agents.create`, invoked by ID, and the model is locked per agent.
- **Secrets stay out.** The API key is sourced only in the calling shell; no key appears in prompts, sandboxes, files or git.

## Totals
- Interactions run: **{len(runs)}** ({sum(r['status']=='completed' for r in runs)} completed), distinct sandboxes (environments): **{len(envs)}**
- Tokens: total {tot['total_tokens']:,} (input {tot['total_input_tokens']:,}, output {tot['total_output_tokens']:,}, cached {tot['total_cached_tokens']:,}, thinking {tot['total_thought_tokens']:,})
- Wall time per agent (sum of interactions): """ + ", ".join(f"{a} {per[a]['sec']/60:.1f} min" for a in agents) + f"""
- Full log: `managed-agents/RUNS.jsonl` (one row per interaction: interaction_id, environment_id, prompt, output_text, files, usage, seconds)

## 1. thru-art-director: Unreal stills vs the real High Sierra
Input: 4 real UE 5.6 render stills from `reset/unreal/PROGRESSION/` (iter1 + iter2) sent as inline images. No Blender turntables existed yet.

### FIXES.md (excerpt)
```markdown
{section(A + '/FIXES.md', 70)}
```

### Turn 2 in the same environment: JUDGE-SUMMARY.md
```markdown
{section(A + '/JUDGE-SUMMARY.md', 20)}
```

## 2. thru-asset-librarian: {len(fan)}-way fan-out across the PCT + Blender-inventory gap analysis
Output: `reset/unreal-models/specs-from-managed-agent/` ({len(specs)} files). Sample spec:
```json
{section(specs[0], 45) if specs else '(none)'}
```
### Gap analysis of the Blender lane's real output (COVERAGE.md excerpt)
```markdown
{section(BASE + '/outputs/asset-librarian/COVERAGE.md', 22)}
```
All specs:
""" + "\n".join(f"- `{os.path.basename(s)}`" for s in specs) + f"""

## 3. thru-license-auditor: YouTube safety
```markdown
{section(L + '/LICENSE-AUDIT.md', 50)}
```

## Live loop hook: managed critic inside the render loop
`managed-agents/ma_critic_hook.py` watches `reset/unreal/PROGRESSION/` for new render stills, sends each new batch to `thru-art-director` in the SAME
persistent environment (chained with `previous_interaction_id`), and the agent keeps `/workspace/memory/critiques.jsonl` in its sandbox so every critique says what improved
or regressed since the last iteration. Output is critic.sh-compatible JSON (`scores`, `overall`, `top_issues`, `param_changes` keyed to the loop's `params.json`), written to
`reset/unreal/out/managed-critic/` and `reset/unreal/MANAGED-CRITIC.md`, with a pointer appended to `reset/unreal/STEER.md` so the next render iteration applies it.

Latest hook output:
```markdown
{section(HOOK, 40)}
```

## Interaction ledger
| label | agent | status | interaction_id | environment_id | sec | tokens |
|---|---|---|---|---|---|---|
""" + "\n".join(f"| {r['label']} | {r['agent']} | {r['status']} | `{r['interaction_id']}` | `{r['environment_id']}` | {r['seconds']} | {tok(r.get('usage') or {}, 'total_tokens'):,} |" for r in runs) + """

## What worked, what did not
{open(NOTES).read() if os.path.exists(NOTES) else '(pending)'}
"""
open(f"{BASE}/SHOWCASE.md", "w").write(md); print("ok", len(runs), len(specs), dict(tot))
