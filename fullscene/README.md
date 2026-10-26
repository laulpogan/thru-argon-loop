# THRU full procedural Unreal scene

GPU-only Unreal 5.6 scene pipeline; see docs/PROCEDURAL.md and docs/GAPS.md for actual scope and limitations. Dell is used for light export/orchestration only. Never mutate the source Thru-2 checkout.

Export pinned Godot files with tools/export_godot.py; download attributed field recordings with tools/audio_sources.py. Raw vendor inputs, renders and generated project packages stay out of Git. Runtime root is /workspace/fullscene. Install src/, config/, tools/launch.sh as launch.sh, required assets/library/fol_src/real/ inputs, project config and the compiled editor plugin. Generate with Python 3 + numpy/scipy/trimesh; launch UE as the ue user via `bash /workspace/fullscene/launch.sh` (or preserve its executable bit). Startup script is src/build_scene.py (or src/render_existing.py for saved scenes). Build plugin with Unreal RunUAT BuildPlugin on the pod; see plugin/FullsceneNiagara.uplugin.

Outputs and live verification are in the delivery REPORT.md and archived pod project. This repo intentionally contains source/config/docs only, not third-party raw assets or an Unreal engine distribution.

The delivery archive includes the saved editor project, compiled Linux plugin and required inputs. Runtime foliage paths are isolated under /workspace/fullscene. New Niagara assets use seed/template/mesh/scale-derived names; wildlife anchor transforms are consumed from the v2 chunk and paired with checked motion sidecars. See out/reviewer.json and REPORT.md for the bounded Claude review and final verification.
