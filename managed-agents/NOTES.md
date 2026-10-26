**Worked**
- `agents.create` with `system_instruction` + mounted `.agents/AGENTS.md` + `.agents/skills/<name>/SKILL.md` worked first try for all 3 agents; invoked by ID with `background=True` + polling.
- Multimodal input: 4 real UE stills (downscaled 1280px JPEG, ~136k image tokens) went straight into the art director; it found real Wikimedia Commons references and wrote a 1-10 scored FIXES.md.
- Persistent environment: all 4 art-director interactions (critique, task list, live iter2 critique, pass-1 re-critique) ran in environment `935b320c904cc3c5537fbb9468d869ee`, re-opening its own FIXES.md and saved references; the hook keeps `/workspace/memory/critiques.jsonl` there.
- Fan-out: 18 parallel librarian sandboxes (8 at a time) + 1 gap-analysis job. No 429s were hit at this concurrency.
- Reference hygiene: an independent link check of every Wikimedia Commons file URL cited across the specs and FIXES.md found 158 of 159 resolve (HTTP 200). One 404 was a HABS .tif page. Licences were recorded by the agents and were not re-verified one by one.
- The gap-analysis job turned the Blender lane's real inventory (832 built assets + latest Argon critic scores) into a coverage table: Oregon has only 16 assets, and 82.5% of scored assets fall below 5/10.

**Did not work / caveats**
- Sandbox files cannot be pulled straight back to the Dell, so each agent re-emits its deliverables as `<<<FILE name>>>` blocks in its final answer. The caller parses those and writes them to disk.
- No Blender turntables existed under `reset/unreal-models/`, so the art director critiqued only Unreal stills.
- The closed loop ran 2 iterations. At iter2/1505 the agent scored 2.4/10 and wrote param_changes. The Unreal lane rendered pass 1 with those params, and the agent re-scored it at 1.7/10 in the same sandbox, citing its iteration-1 critique issue by issue. The score went down, and the agent blamed asset/camera regressions that landed in the same pass. The pass-2 params are in `params_next.json`.
- The pass-1 stills were copied box to Dell by hand and the hook was run with `--once --dir inbox/pass1`. The PROGRESSION watcher was stopped so two jobs would not share the sandbox at once.
- The live hook runs in parallel and does not modify the pod's `critic.sh`/`iterate.sh`. It feeds the loop through `reset/unreal/MANAGED-CRITIC.md`, `out/managed-critic/params_next.json` and a pointer line in `STEER.md`. The loop owner still has to apply `params_next.json`.
- Token use is high per job (about 0.5-5.5M input tokens), but 85-95% of it is cached. Agents ran on gemini-3.8-flash. Argon was not used inside the sandboxes (no managed credential was set up).
- Agent-emitted dimensions and PBR numbers are research estimates. They need human review before final art.
