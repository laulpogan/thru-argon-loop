# Live demo: one render → watch → critique → fix → verify cycle

```bash
git clone https://github.com/laulpogan/thru-argon-loop && cd thru-argon-loop
pip install pillow            # optional (used to downscale images); stdlib-only otherwise
export GEMINI_API_KEY=...     # read from env only
bash demo/run_loop.sh
```

What it prints (about 30–90 s; it took 26 s on our test run):
1. **[1/3 WATCH+CRITIQUE]** Four real UE5 stills (`demo/renders/iter1`) and three real Sierra creek photos (`pipeline/refs`) go to `gemini-4-argon`. You get per-shot scores out of 10 and the top issues.
2. **[2/3 FIX]** The script applies the critic's `param_changes` to `params.json` (only keys that already exist, each change clamped to ±60%). It prints every changed knob and writes `demo/out/<time>/params.patch`.
3. **[3/3 VERIFY]** It re-critiques the re-rendered stills with the same rubric and the same photos, then prints `LOOP RESULT: overall A -> B (delta)`.

In fallback mode, the re-render is `demo/renders/iter2`: the real UE5 render the autonomous loop produced at 14:40 PT from iter1's critique.

**Live against a running UE pod:**
```bash
UE_POD=root@<pod-host> UE_POD_PORT=<ssh-port> bash demo/run_loop.sh
```
This pulls the pod's latest `out/iterN/stills_pick`, critiques them, pushes `params.next.json` to the pod, and starts `iterate.sh N+1` (a real Unreal render, about 4–5 min). Run it again once that render lands to verify.

Artifacts: `demo/out/<time>/{critique.json, params.next.json, params.patch, verify.json, summary.json}`.
