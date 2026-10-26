# How Gemini 4 Argon transformed our workflow

**Project:** THRU — Paul Logan's photoreal co-op Pacific Crest Trail hiking game (`laulpogan/Thru-2`)  
**Sprint Date:** Sunday, October 25, 2026 (11:25 AM PT – 3:32 PM PT snapshot; 5:00 PM PT judging)  
**Repository:** `laulpogan/Thru-2` (hackathon artifacts in `~/cs-audit/gemini-hackathon`)

---

## 1. Headline Numbers & Models Used

Between 11:25 AM PT and 3:32 PM PT on October 25, 2026, our one-day Gemini 4 Argon hackathon sprint drove a fleet of local `tmux` orchestrators on an on-prem Dell workstation (`dellpromax`, NVIDIA RTX PRO 6000 Blackwell Workstation Edition, 97,887 MiB VRAM) and up to 49 cloud pods on RunPod.

### Fleet Headline Totals (3:32 PM PT Snapshot)

- **Logged `argon` CLI Calls (`calls.jsonl`):** **65,082 total calls** (**49,232 `ok`**) — *lower bound, because direct `pi` coding-agent harness calls bypass the `~/.local/bin/argon` wrapper and are not recorded in `calls.jsonl`.*
- **Logged Tokens (`calls.jsonl`):** **1,069,491,060 tokens (~1.07B tokens)** across all logged CLI calls (*lower bound; excludes direct `pi` session tokens*).
- **Generated Media Files (`calls.jsonl`):** **10,196 media files** logged by `argon` CLI (concept targets, PBR texture maps, Lyria music tracks, TTS voice lines); **`MEDIA-MANIFEST.tsv` tracks 6,003 rendered/audio/video files on disk totaling 52,598,389,815 bytes (48.99 GiB)**.
- **Peak Fleet Input Token Throughput (`pilane/podtpm.sh`, 13:43 PT):** **14.30M `gemini-4-argon` input tokens/min** across 49 RunPod pods + the Dell workstation, consisting of:
  - **9.85M tokens/min** `pi` context cache reads
  - **1.50M tokens/min** `pi` uncached input
  - **2.59M tokens/min** `argon` CLI calls on RunPod pods
  - **0.39M tokens/min** `argon` CLI calls on the Dell workstation
- **Review Swarm Verdicts (`swarm/progress.tsv`):** **444 verdicts** written out of 1,028 queued PR, blocked-row, and failed-asset jobs.
- **Model Council Judgments (`council/progress.tsv`):** **3,807 rows** logged across 8 model directories before the consensus aggregation script crashed.
- **Work Queue Expansion (`~/gen3d/work/queue.jsonl`):** Grew from **2,192 THRU rows** (11:30 AM PT) to **4,547 THRU rows** (**4,733 total rows** across all projects; **3,274 `done/` markers**).

### Models Used (`after/SNAPSHOT.md` — `calls.jsonl` Lower-Bound Totals)

Every model and batch/diagnostic handle recorded in `after/SNAPSHOT.md` is listed below with its exact call count, successful (`ok`) count, and logged token total, grouped by role:

#### A. Frontier Reasoning, Coding & Agentic Models
| Model | Calls | OK | Tokens | Primary Hackathon Role |
|---|---:|---:|---:|---|
| `gemini-4-argon` | 20,876 | 18,501 | 566,444,156 | Primary 3D generator author, shader coder, 4-view Art Director critic, PR reviewer, lane orchestrator |
| `gemini-3.1-pro-preview` | 272 | 272 | 2,196,131 | Blind second-opinion audio/image/production judge, lookdev comparison, model council |
| `gemini-pro-latest` | 1 | 1 | 5,052 | Model catalog verification probe (`allmodels-other`) |
| `gemini-3.1-pro-preview-customtools` | 1 | 1 | 3,799 | Custom-tools endpoint probe (`allmodels-other`) |
| `gemini-3.1-pro` | 16 | 0 | 0 | Unoffered model handle probed in `lookdev` (returned errors; replaced by `gemini-3.1-pro-preview`) |
| `gemini-2.5-pro` | 1 | 0 | 0 | Deprecated/unoffered handle for new users (404; dropped from council at 12:31 PT) |
| `antigravity-preview-09-2026` | 19 | 18 | 0 | Agentic workflow evaluation in `allmodels-other-agent` |
| `antigravity-preview-latest` | 11 | 10 | 0 | Agentic probe and initial council run (dropped from council due to 2M TPM cap) |
| `antigravity-preview-05-2026` | 10 | 9 | 0 | Agentic workflow evaluation in `allmodels-other-agent` |
| `gemini-2.5-computer-use-preview-10-2025` | 4 | 0 | 0 | Computer-use sandbox and QA probes (`allmodels-computer-use`, `reset-qa`; returned HTTP 503) |
| `aqa` | 2 | 1 | 0 | Attributed Question Answering probe (`allmodels-aqa`) |

#### B. High-Throughput Flash, Lite & Open Gemma Models
| Model | Calls | OK | Tokens | Primary Hackathon Role |
|---|---:|---:|---:|---|
| `gemini-3.8-flash` | 28,725 | 15,640 | 432,110,174 | Pod pump workers, blocked-row triage, `linekeeper-asset`, recipe critics, 32-lane SOTA sweep |
| `gemini-3.5-flash` | 1,062 | 1,046 | 13,886,998 | `linekeeper-asset`, `qc-argon-feed`, `linekeeper-creek`, council shard |
| `gemini-3.6-flash` | 1,153 | 1,086 | 12,155,569 | `linekeeper-asset`, `qc-argon-feed`, Lyria music scoring (`music-lyria`), council shard |
| `gemini-3-flash-preview` | 398 | 398 | 11,443,072 | `qc-argon-feed` review feeder and model council |
| `gemini-3.7-flash` | 1,008 | 752 | 4,803,001 | `linekeeper-asset`, `qc-argon-feed`, `linekeeper-creek`, council shard |
| `gemini-3.1-flash-lite` | 29 | 29 | 1,579,837 | Bulk GDScript summarization and reference tagging (`allmodels-small-bulk`, `allmodels-refs-tags`) |
| `gemini-3.5-flash-lite` | 29 | 29 | 1,547,200 | Bulk GDScript summarization and reference tagging (`allmodels-small-bulk`, `allmodels-refs-tags`) |
| `gemini-flash-lite-latest` | 29 | 29 | 1,479,927 | Bulk GDScript summarization and reference tagging (`allmodels-small-bulk`, `allmodels-refs-tags`) |
| `gemma-4-26b-a4b-it` | 8 | 2 | 21,910 | Open-weights small-model benchmark and vision check (`allmodels-small`) |
| `gemma-4-31b-it` | 8 | 2 | 15,449 | Open-weights small-model benchmark and council probe (dropped from council due to 16K TPM cap) |
| `gemini-flash-latest` | 1 | 1 | 5,092 | Catalog verification probe (`allmodels-other`) |
| `gemini-3.1-flash-lite-preview` | 1 | 1 | 1,538 | Catalog verification probe (`allmodels-other`) |
| `gemini-2.5-flash` | 1 | 0 | 0 | Legacy catalog probe (`allmodels-other`) |
| `gemini-2.5-flash-lite` | 1 | 0 | 0 | Legacy catalog probe (`allmodels-other`) |

#### C. Image Generation Models
| Model | Calls | OK | Tokens | Primary Hackathon Role |
|---|---:|---:|---:|---|
| `nano-banana-pro-preview` | 10,070 | 10,070 | 20,887,264 | Internal build-loop concept targets (`reset-assetfactory` 9,496 calls, wildlife, textures, lookdev, media) |
| `gemini-3-pro-image` | 142 | 142 | 246,452 | Tileable PBR texture synthesis, material expansion/repair, 6-model image bake-off |
| `gemini-nano-banana-2.1` | 12 | 12 | 32,734 | 6-model image generation bake-off (`allmodels-images`) |
| `gemini-3.1-flash-lite-image` | 12 | 12 | 20,931 | 6-model image generation bake-off (`allmodels-images`) |
| `gemini-3.1-flash-image` | 12 | 12 | 17,840 | 6-model image generation bake-off (`allmodels-images`) |
| `gemini-2.5-flash-image` | 12 | 12 | 16,945 | 6-model image generation bake-off (`allmodels-images`) |
| `gemini-3-pro-image-preview` | 1 | 1 | 1,653 | Image catalog probe (`allmodels-other-image`) |
| `gemini-3.1-flash-image-preview` | 1 | 1 | 341 | Image catalog probe (`allmodels-other-image`) |

#### D. Music Generation Models (Lyria)
| Model | Calls | OK | Tokens | Primary Hackathon Role |
|---|---:|---:|---:|---|
| `lyria-3.5` | 201 | 201 | 187,067 | 1990s Americana acoustic guitar & Sierra pastoral score cues (`audio`, `music-lyria`, `audiomix`, `reset-music`) |
| `lyria-3-clip-preview` | 151 | 151 | 62,739 | Short musical cue and motif candidates (`audio`, `reset-audio-foley`, `reset-audio-birds`) |
| `lyria-3-pro-preview` | 60 | 60 | 52,887 | Long-form score arrangements (`audio`) |

#### E. Speech Synthesis (TTS) & Audio Transcription Models
| Model | Calls | OK | Tokens | Primary Hackathon Role |
|---|---:|---:|---:|---|
| `gemini-3.8-flash-tts` | 65 | 65 | 49,312 | NPC hiker dialogue across 12 voices (`audio`, `reset-narrative`, `narrative`, `media`, `reset-audio-foley`) |
| `gemini-3.5-transcribe` | 63 | 63 | 11,406 | Automated transcription verification of generated NPC voice lines (`audio`, `allmodels-transcribe`) |
| `gemini-3.8-flash-lite-tts` | 25 | 25 | 175 | Lightweight TTS voice auditioning (`audio`) |
| `gemini-2.5-pro-preview-tts` | 1 | 1 | 157 | Pro TTS probe (`audio`) |
| `gemini-3.1-flash-tts-preview` | 1 | 1 | 109 | Flash TTS probe (`audio`) |

#### F. Deep Research, Spatial Robotics, Video & Embeddings
| Model | Calls | OK | Tokens | Primary Hackathon Role |
|---|---:|---:|---:|---|
| `deep-research-max-preview-04-2026` | 233 | 232 | 0 | Autonomous multi-step technical and ecological research (`research`, `allmodels-research`, `allmodels-research-revised`) |
| `deep-research-pro-preview-12-2025` | 120 | 120 | 0 | Deep research comparison and revised citation audits (`allmodels-research`, `allmodels-research-revised`) |
| `deep-research-preview-04-2026` | 116 | 116 | 0 | Deep research comparison and revised citation audits (`allmodels-research`, `allmodels-research-revised`) |
| `gemini-robotics-er-2-preview` | 24 | 24 | 204,143 | Embodied spatial QA and 2D/3D bounding-box anomaly detection on 50 gameplay frames (`allmodels-spatial`, `reset-qa`) |
| `gemini-omni-1.1-flash` | 5 | 5 | 0 | Anchored video motion reference generation (`allmodels-video`, `allmodels-probe`) |
| `gemini-omni-flash-preview` | 4 | 4 | 0 | Anchored video motion reference generation (`allmodels-video`) |
| `gemini-embedding-001` | 1 | 1 | 0 | Embedding endpoint verification (`allmodels-embeddings`) |
| `gemini-embedding-2-preview` | 1 | 1 | 0 | Embedding endpoint verification (`allmodels-embeddings`) |
| `gemini-embedding-2` | 1 | 1 | 0 | Embedding endpoint verification (`allmodels-embeddings`) |

#### G. Batch API Operations & Catalog Diagnostics (`batch` / `audio` lanes — Exact Rows from `after/SNAPSHOT.md`)
| Operation Handle in `calls.jsonl` | Calls | OK | Tokens | Role |
|---|---:|---:|---:|---|
| `argon-scale-3-poll` | 10 | 1 | 0 | Batch API scale-3 poll (`batch`) |
| `argon-scale-2-poll` | 3 | 3 | 0 | Batch API scale-2 poll (`batch`) |
| `argon-scale-4-poll` | 3 | 3 | 0 | Batch API scale-4 poll (`batch`) |
| `argon-50-poll` | 2 | 2 | 0 | Batch API 50-item poll (`batch`) |
| `flash-50-poll` | 2 | 2 | 0 | Batch API 50-item Flash poll (`batch`) |
| `argon-scale-5-poll` | 2 | 2 | 0 | Batch API scale-5 poll (`batch`) |
| `argon-scale-6-poll` | 2 | 2 | 0 | Batch API scale-6 poll (`batch`) |
| `argon-scale-7-poll` | 2 | 2 | 0 | Batch API scale-7 poll (`batch`) |
| `flash-scale-1-poll` | 2 | 2 | 0 | Batch API Flash scale-1 poll (`batch`) |
| `flash-scale-2-poll` | 2 | 2 | 0 | Batch API Flash scale-2 poll (`batch`) |
| `flash-scale-3-poll` | 2 | 2 | 0 | Batch API Flash scale-3 poll (`batch`) |
| `flash-50-upload-start` / `flash-50-upload-finalize` / `flash-50-create` / `flash-50-download` | 1 each (4 total) | 1 each (4 total) | 0 | 50-item `gemini-3.8-flash` Batch API lifecycle (`batch`) |
| `argon-50-create` | 1 | 1 | 0 | 50-item `gemini-4-argon` Batch API create (`batch`) |
| `flash-inline-small-probe-create` / `flash-inline-small-probe-poll` | 1 each (2 total) | 1 each (2 total) | 0 | Inline small Batch API probe (`batch`) |
| `argon-scale-1-upload-start`, `argon-scale-2-upload-start`, `argon-scale-3-upload-start`, `argon-scale-4-upload-start`, `argon-scale-5-upload-start`, `argon-scale-6-upload-start`, `argon-scale-7-upload-start` | 1 each (7 total) | 1 each (7 total) | 0 | Batch upload start for Argon scale 1–7 (`batch`) |
| `argon-scale-1-upload-finalize`, `argon-scale-2-upload-finalize`, `argon-scale-3-upload-finalize`, `argon-scale-4-upload-finalize`, `argon-scale-5-upload-finalize`, `argon-scale-6-upload-finalize`, `argon-scale-7-upload-finalize` | 1 each (7 total) | 1 each (7 total) | 0 | Batch upload finalize for Argon scale 1–7 (`batch`) |
| `argon-scale-1-create`, `argon-scale-2-create`, `argon-scale-3-create`, `argon-scale-4-create`, `argon-scale-5-create`, `argon-scale-6-create`, `argon-scale-7-create` | 1 each (7 total) | 1 each (7 total) | 0 | Batch job creation for Argon scale 1–7 (`batch`) |
| `argon-scale-1-poll` | 1 | 1 | 0 | Batch API scale-1 poll (`batch`) |
| `argon-scale-1-download`, `argon-scale-2-download`, `argon-scale-4-download`, `argon-scale-5-download`, `argon-scale-6-download`, `argon-scale-7-download` | 1 each (6 total) | 1 each (6 total) | 0 | Batch result download for Argon scale 1, 2, 4, 5, 6, 7 (`batch`) |
| `flash-scale-1-upload-start`, `flash-scale-2-upload-start`, `flash-scale-3-upload-start` | 1 each (3 total) | 1 each (3 total) | 0 | Batch upload start for Flash scale 1–3 (`batch`) |
| `flash-scale-1-upload-finalize`, `flash-scale-2-upload-finalize`, `flash-scale-3-upload-finalize` | 1 each (3 total) | 1 each (3 total) | 0 | Batch upload finalize for Flash scale 1–3 (`batch`) |
| `flash-scale-1-create`, `flash-scale-2-create`, `flash-scale-3-create` | 1 each (3 total) | 1 each (3 total) | 0 | Batch job creation for Flash scale 1–3 (`batch`) |
| `flash-scale-1-download`, `flash-scale-2-download`, `flash-scale-3-download` | 1 each (3 total) | 1 each (3 total) | 0 | Batch result download for Flash scale 1–3 (`batch`) |
| `argon-scale-3-list-diagnostic` / `batch-list-diagnostic` | 1 each (2 total) | 0 each (0 total) | 0 | Batch list diagnostic probes (`batch`) |
| `models` | 1 | 1 | 0 | Model catalog list call (`audio`) |

---

## 2. Before vs. After Metrics & Condensed Timeline

### Before vs. After Metrics Table

Honest accounting matters: **`fleet/thru` head did not move (`101a52b40e`)** during the hackathon window, and the queue growth from 2,192 to 4,547 THRU rows is mostly new Argon-generated asset and review rows rather than merged trunk features.

| Metric | BEFORE (~11:30 AM PT, `JOURNAL.md`) | AFTER (3:32 PM PT, `after/SNAPSHOT.md`) | Notes / Honest Context |
|---|---:|---:|---|
| **`fleet/thru` Trunk Head** | `101a52b40e` | `101a52b40e` | **Did not move.** Hackathon branches stayed isolated in draft PRs and lane worktrees. |
| **Total Queue Rows (`queue.jsonl`)** | — | **4,733** | Across all projects (`thru` 4,547, `slancha-brain` 49, `agent-dbg` 41, `prost` 18, `slancha-mesh` 18, `barkeep` 16, `wire` 9, `slancha-api` 7). |
| **THRU Queue Rows** | **2,192** | **4,547** | +2,355 rows, driven mostly by new Argon-generated asset and review rows. |
| **THRU `landed`** | 675 | **680** | +5 landed rows recorded in `done/` markers. |
| **THRU `reviewed`** | 0 (only 3 of 365 recent rows had a full-log read at 11:19 AM) | **1,194** | Shifted the primary fleet bottleneck from review scarcity to automated triage. |
| **THRU `pending` (no `done` marker)** | 305 | **1,460** | Newly queued Argon asset/biome generator rows awaiting pod execution or critique. |
| **THRU `draft_pr`** | 433 | **433** | Plus `asset_pass_draft_pr`: 10, `asset_pass_chamise_draft_pr`: 1. |
| **THRU `blocked`** | 250 | **252** | Triaged by swarm and Flash workers. |
| **THRU `asset_fail`** | 115 | **115** | Plus `already`: 163, `partial`: 97, `pushed`: 52, `completed`: 14, `done`: 13, `patch`: 11, `passed`: 9, `asset_pass`: 9, `draft`: 8, `timeout`: 7, `research`: 5, `proposal`: 5, `review`: 5, `held`: 1, `captured`: 1, `unreadable`: 1, `asset_partial`: 1. |
| **Total `done/` Markers** | — | **3,274** | Verified completion/review markers on disk. |
| **Open Pull Requests (`laulpogan/Thru-2`)** | **300+** (299 drafts) | **684** (681 drafts) | Includes 10 `[hackathon]` draft PRs (`#693`–`#702`) and Kanpai/Gemini fix draft PRs (`#688`–`#692`, `#703`–`#712`). |
| **Hero Scene Engine** | Godot 4.7.2 (`pct-region-0029`, silent video, hiker misses bridge & crab-walks at 4.6 m/s) | **Unreal Engine 5.6.1** (Lumen + VSM on L40S, Evermotion AM283 + HyperGrass + Arnklit rocks; candidate audio mix `after_walkthrough_mix.wav` at `-14.0 LUFS` pending listening review) | Paul selected Unreal Engine at 2:46 PM PT after side-by-side comparison; Godot AFTER clip (`hero-after-dryrun.mp4`) kept as verified backup. |

### Condensed Hackathon Timeline (Sunday, October 25, 2026 PT)

- **11:19 AM — Bottleneck identified:** Lane-output audit finds only **3 of 365** recent THRU queue rows had a full-log review. Review capacity, not generation, is the bottleneck across 2,192 THRU rows and 300+ open PRs.
- **11:25 AM — Key provisioned:** Paul receives the 24-hour Gemini API key (`~/.config/gemini/hackathon.env`, mode `600`). The `~/.local/bin/argon` wrapper logs every CLI invocation to `calls.jsonl` without ever logging the key.
- **11:26–11:37 AM — First read-only & creative lanes:** Five read-only audit jobs (`J1`–`J5`) launch first, followed by five creative lanes (`trail`, `model`, `media`, `research`, `fixes`).
- **11:48–11:49 AM — `agy` billing trap caught:** Google Antigravity CLI (`agy` 1.4.7) is launched for PR/asset swarms, but Quota Cop detects in 1 minute that `agy` headless mode bills the rationed weekly subscription pool (`46.9%` used) instead of `GEMINI_API_KEY`. Both `agy` lanes are killed immediately.
- **11:50–11:55 AM — `pi` + Argon swarm & Tier 3 20M TPM cap:** The `pi` coding agent (`0.86`) connects to `gemini-4-argon` with working shell tools in ~10 seconds. A 64-parallel `pi` swarm launches across **1,028 jobs** (659 PRs, 253 blocked rows, 116 failed assets), immediately hitting HTTP 429 (`20M input tokens/min per model` Tier 3 cap) and losing the first **225 jobs**. Relaunched at 32 parallel with 8-retry exponential backoff, sharding blocked rows onto `gemini-3.8-flash`.
- **12:13–12:38 PM — Autonomous 3D modelling & multi-model expansion:** After Round 1 `model` scores `0/7` photo passes in 2 rounds, `model2` launches evolutionary 4-variant rounds and `model3` implements Google's *"Building 3D Games and Procedural Worlds with Gemini 4 Argon"* guide autonomously in `pi`. At 12:30–12:31 PM, `audio`, `council` (8 models × 12 workers), `allmodels` (46 catalog models), and `lookdev` launch; key path is shared with Pitcrew, Studio, Kaizen, Brain, and Tensor.
- **12:45–13:09 PM — Total game reset fan-out & procedural rules:** BEFORE walkthroughs record for Campo Creek (45.0 s) and Sierra Hero Creek (36.0 s). Nine core reset orchestrators, 20 staggered extended lanes, 5 biome orchestrators (`socal-desert`, `high-sierra`, `norcal`, `oregon`, `washington`), and 5 procedural generation lanes (`terrain`, `scatter`, `trail`, `hydrology`, `sections`) launch under Paul's hard rules: full parameterised procedural generators with seeds, ecological placement rules, `WeatherState` runtime autoload (`dry` and `after-rain`), and surface-feel macro closeups.
- **13:02–13:25 PM — Dell load peak (227.48) & idle pod crisis (33/43 idle):** Local worktree checkouts and 50+ Codex drivers push Dell 1-minute load to **227.48** at 13:02 PT (`74%` disk `iowait` at 12:50 PT) and burn **39.0%** of weekly Codex quota by 13:35 PT. Meanwhile, at 13:16 PT, **33 of 43 RunPod pods** ($20.30/hr) sit idle because `assetfactory/gallery.py` crashed on `"Invalid asset id"` before queueing 194+ manifest rows. We engage `runpod/PAUSE_SCALING`, launch a Fleet Operator (`runpod/FLEET.md`) with pull-based `fleetq`, and renice/pause 46 local Codex lanes, dropping Dell load to ~18 by 13:30 PT.
- **13:32–13:40 PM — Unreal Engine 5.6.1 spike pod:** Paul asks for an Unreal Engine spike on its own machine. Dedicated L40S pod `thru-unreal-1` ($0.79/hr) is deployed at 13:32 PT; Paul links Epic + GitHub at 13:40 PT, and `ghcr.io/epicgames/unreal-engine:dev-slim-5.6.1` (46 GB unpacked) is pulled via 8-stream parallel `crane blob`.
- **13:37–14:06 PM — 100% Codex-to-`pi`+Argon migration & 14.30M tok/min peak:** All local Codex orchestrators are retired (last hackathon `codex exec` exits at **14:06:23 PT**, `CODEX-EXIT.md`) and relaunched as `pi` + `gemini-4-argon` loops across 15 CPU pods (`thru-cpu-overflow-pilane-1..16`), including 24 `recipe-critic` lanes across 1,120 asset recipes. At 13:43 PT, fleet-wide Argon input throughput reaches **14.30M tokens/min** (including **9.85M/min** `pi` cache reads).
- **14:21–14:51 PM — First UE5 renders, Godot vs. Unreal side-by-side, and Xvfb lock fix:** `thru-unreal-1` produces its first Lumen + VSM renders at 14:24 PT (`iter1`). At 14:46 PM PT (**2:46 PM PT**), after reviewing the 4-camera side-by-side comparison (`compare/`), Paul selects **Unreal Engine** for the hero presentation and relegates the Godot AFTER walkthrough (`hero-after-dryrun.mp4`) to backup. At 14:51 PT, we fix an inherited file-descriptor (`9>&-`) `Xvfb` `flock` wedge on `thru-render-1`.
- **14:55–15:37 PM — All-in Unreal pivot, purchased packs & candidate audio mix:** `UNREAL-SWITCH-LOG.md` stops Godot walkthrough/assetfactory lanes and scales 4 Unreal feeder lanes (`unreal-assets-veg`, `unreal-assets-rocks`, `unreal-landscape-export`, `unreal-systems`) to **3 parallel Argon workers each (12 workers)**. Paul's purchased packs (HyperGrass Vol. 1, Evermotion Archmodels vol. 283, Arnklit Cliffs & Rocks Pack 1) and YouTube-safe audio stems (`after_walkthrough_mix.wav` at `-14.0 LUFS`, currently pending listening review, plus `unreal_hero_36s_16lufs.wav` at `-16.00 LUFS`) are staged for the UE 5.6.1 scene.

---

## 3. Workflow Transformation by Job Type (Old Way vs. Argon Way)

### 3.1 PR Review Swarm & Multi-Model Council
- **Old Way:** Human or single-session Claude/Codex review of open PRs one at a time. At 11:19 AM PT, 300+ open PRs (299 drafts) sat in `laulpogan/Thru-2`, and only 3 of 365 recent queue rows had received a full-log read.
- **Argon Way:** We connected `pi` (`0.86`) to `gemini-4-argon` and fanned out **1,028 review jobs** (659 open PRs, 253 blocked/needs_input rows, 116 failed assets) at 32-way concurrency with exponential backoff, plus an 8-model **Model Council** (`gemini-3-flash-preview`, `gemini-3.1-pro-preview`, `gemini-3.5-flash`, `gemini-3.6-flash`, `gemini-3.7-flash`, plus initial probes on `antigravity-preview-latest`, `gemini-2.5-pro`, and `gemma-4-31b-it`).
- **Real Counts & Timings:**
  - **Swarm (`swarm/progress.tsv`):** **444 completed verdicts**: `114 CHANGES`, `92 SUPERSEDED`, `82 RETIRE`, `48 APPROVE`, `43 ?`, `26 REMAKE`, `10 CC0_SOURCE`, `9 NEEDS_PAUL`, `8 FIX`, `7 RETRY`, `2 UNCHAIN`, `2 REJECT`, `1 WAIT`.
  - **Council (`council/progress.tsv`):** **3,807 cross-model review rows** completed before GitHub API rate-limit exhaustion (`0/5000` GraphQL/core at 14:29 PT) and a syntax bug in `consensus.py` halted aggregation.
  - **Autonomous PR Fixes (`fixes` & `fixes2`):** Argon authored and unit-tested local fixes for PR `#666` (`fixes`, 2 Argon calls, 307,855 tokens) and top J1 `CHANGES` findings `#683`, `#676`, and `#648` (`fixes2`, 4 Argon calls, 40,260 tokens; all 3 unit suites green in CPU-only verification by 13:09 PT).

### 3.2 Blocked-Row Triage & Linekeeper Verification
- **Old Way:** Blocked queue rows (`250` blocked at 11:30 AM PT) waited for manual producer inspection of multi-megabyte build and test logs.
- **Argon Way:** When the initial 64-worker swarm hit Argon's 20M TPM ceiling at 11:54 AM PT, we sharded all **253 blocked/needs_input rows** onto `gemini-3.8-flash` (using its independent 20M TPM pool) and ran continuous `linekeeper` verification workers across `3.5-flash`, `3.6-flash`, `3.7-flash`, `3.8-flash`, and `gemini-4-argon`.
- **Real Counts & Timings:**
  - **Queue Triage:** `reviewed` rows in `queue.jsonl` rose from **0** (3 manual reads) before the sprint to **1,194 `reviewed` rows** and **3,274 total `done/` markers** by 15:32 PT.
  - **Linekeeper Calls (`calls.jsonl`):** `linekeeper-asset` logged **4,709 `gemini-3.8-flash` calls** (23,399,178 tokens), **696 `gemini-3.5-flash` calls** (3,456,973 tokens), **698 `gemini-3.6-flash` calls** (3,417,140 tokens), and **897 `gemini-3.7-flash` calls** (685 ok, 3,412,641 tokens); `linekeeper-review` logged **129 `gemini-4-argon` calls** (3,578,311 tokens); `linekeeper-aaa` logged **186 `gemini-4-argon` calls** (1,239,593 tokens); `linekeeper-creek` logged **177 `gemini-3.8-flash` calls** (1,263,038 tokens).

### 3.3 Parameterised Asset Factory & Failed-Asset Remakes
- **Old Way:** One-off static Blender meshes built serially on the Dell workstation, leaving **115 `asset_fail` rows** in the queue and starving biomes of species growth stages.
- **Argon Way:** Under the 13:08–13:09 PT procedural directive, 5 biome orchestrators generated **655 structured asset requests** (`socal-desert` 184, `washington` 165, `high-sierra` 123, `norcal` 108, `props` 60, `oregon` 15) expanding the manifest to **1,120 parameterised asset recipes** (`seed + species/type + age + season + weather`). We provisioned 32+ RunPod CPU pods running headless Blender 3.0.1 and launched **24 parallel `recipe-critic` lanes** (4 per 8-vCPU pod, ~47 recipes per lane) plus `pump-pod` workers.
- **Real Counts & Timings:**
  - `reset-assetfactory` logged **9,251 `gemini-4-argon` calls** (159,714,711 tokens), **2,896 `gemini-3.8-flash` calls** (49,865,306 tokens), and **9,496 `nano-banana-pro-preview` calls** (19,665,671 tokens, **9,503 media files**) for internal build-loop targets.
  - `pump-pod` logged **19,382 `gemini-3.8-flash` calls** (6,324 ok, 346,055,065 tokens) and **5,045 `gemini-4-argon` calls** (2,700 ok, 148,331,519 tokens).
  - By 14:57 PT, `assets/built/` held **832 built asset directories** (`ls assets/built` = 834 entries including `.` and `..`).

### 3.4 Full-Trail PCT Photo Atlas (`trail`)
- **Old Way:** Ad-hoc reference photo lookups per landmark without systematic coverage of the 2,650-mile Pacific Crest Trail or quantitative gap scoring against in-game renders.
- **Argon Way:** The `trail` lane (`ARGON_LANE=trail`) built a complete **30 Halfmile/PCTA letter-section photo atlas** (`CA-A` through `CA-R`, `OR-A` through `OR-F`, `WA-H` through `WA-K`, explicitly splitting `CA-R` and `OR-A` at the state border), analyzed **219 permitted reference photos** (after quarantining 9 prohibited entries from the 228-image seed library) plus licensed Wikimedia Commons acquisitions, generated artist specifications per section (`SECTION_SPECS/`), and scored in-game capture frames against real-photo contact sheets.
- **Real Counts & Timings:**
  - **687 `gemini-4-argon` calls** (all 687 `ok`, **38,484,396 tokens**), plus 5 `gemini-3.8-flash` calls (16,472 tokens) and 4 `nano-banana-pro-preview` calls (6,581 tokens).
  - Rejudged 45 `CA-E`, `CA-L`, `CA-M`, and `WA-J` game captures against refreshed deficit specs by 14:05 PT and produced `SECTION_ATLAS.json` (506 KB) and `PHOTO_ANALYSES.json` (4.10 MB).

### 3.5 Autonomous & Evolutionary 3D Modelling (`model`, `model2`, `model3`)
- **Old Way:** Single-pass script generation where an agent writes a Blender script once or twice and stops when the mesh looks like a low-poly placeholder.
- **Argon Way:** We ran a controlled progression across three 3D modelling architectures:
  1. **`model` (Round 1, 11:37 AM – 12:13 PM):** Codex-driven 2-round loop (22 Argon calls, 351,818 tokens). Scored **0/7 photo gate passes** because 2 rounds were insufficient for complex organic geometry.
  2. **`model2` (12:13 PM – 14:06 PM):** Evolutionary tournament (149 Argon calls, 5,637,496 tokens) generating **4 parallel Blender Python variants per round across 6–7 rounds** for granite rock, Jeffrey pine, and creek bed (`72` evolutionary variants total, 3 views each, verified in `model2/RESULT.md`). Selected elite native triangle counts: **rock 728,474 tris**, **pine 3,742,703 tris**, **creek 500,680 tris**.
  3. **`model3` (12:38 PM – 14:29 PM):** Autonomous `pi` + `gemini-4-argon` loop implementing Google's *"Building 3D Games and Procedural Worlds with Gemini 4 Argon"* guide across 4 subjects (boulder, pine, creek, trail sign): Nano Banana concept target -> 2D proportion grid -> parameterised Blender Python generator -> 4-view diagnostic plate (3/4, close-up, low angle, wireframe) -> strict Art Director critic subagent scoring 0–10.

### 3.6 Media Repaints & Concept Targets (`media`)
- **Old Way:** Describing desired lighting or shader changes in text prompts without visual look-targets, or manually painting over screenshots.
- **Argon Way:** The `media` lane used `nano-banana-pro-preview` (90 calls, 90 media files, 169,639 tokens) and `gemini-4-argon` (109 calls, 356,932 tokens) to generate photoreal repaints of existing THRU frames across 36 scene directories (`media/repaints/01`..`36`), finishing 20 verified repaint pairs by the 1:02 PM checkpoint (`MEDIA_DONE`).
- **Crucial Lesson & Policy Shift:** Vision critique at 1:02 PM showed that **Nano Banana repaints invent geometry** (adding boulders, streams, and canopy silhouettes that do not exist in the underlying 3D scene). At 1:08 PM PT, Paul issued a hard rule: Nano Banana images are **internal build-loop targets only** and are never presented as engine renders.

### 3.7 Full Audio Environment: Score, Birdsong, Foley & Mastered Mixes (`audio`, `reset/music`, `reset/audiomix`, `reset/unreal/import/audio`)
- **Old Way:** The BEFORE walkthrough videos (`walkthrough/before-run1/walk.mp4` and `before-hero/walk.mp4`) exported with **0 audio streams** (`-an`, `--audio-driver Dummy`), and live Master-bus recording (`handoffs/playtest/REPORT.md`) proved music was completely absent (`0.0 dBFS`, not instantiated in `geo_expedition.gd`) with faint footsteps at `-33.39 dBFS` to `-35.73 dBFS` RMS.
- **Argon Way:** We split audio across four specialized pipelines combining Google's generative audio models (for music and NPC speech) with licensed CC0/CC-BY-3.0 field recordings and physical acoustic modeling (after SOTA & listening gates confirmed generated foley sounded artificial):
  - **Candidate Soundtrack & Voice Pack (`audio/RESULT.md`, completed 13:20 PT):** **1,355 metadata-recorded calls** (662 `gemini-4-argon`, 234 `gemini-3.1-pro-preview`, 148 `lyria-3-clip-preview`, 112 `lyria-3.5`, 60 `lyria-3-pro-preview`, 61 `gemini-3.5-transcribe`, 25 `gemini-3.8-flash-tts`, 25 `gemini-3.8-flash-lite-tts`, 25 `gemini-3.8-flash`, 1 `gemini-2.5-pro-preview-tts`, 1 `gemini-3.1-flash-tts-preview`, 1 `models`). Produced **400 catalog entries (3.26 GB)** with **232 model-retained**: **55 music pieces (40.8 minutes)** from 316 Lyria attempts covering **37/54 cue roles**, **42 NPC voice lines across 12 voices** verified by `gemini-3.5-transcribe`, **80 ambience** and **55 effects** entries, and **114 verified seamless OGG/WAV loops**.
  - **6-Layer Adaptive Score (`reset/music/RESULT.md`):** Parameterised generator (`build_score.py`) using a phase-coherent 4th-order Linkwitz-Riley linear-phase FFT crossover at `1600 Hz` (`Foundation <= 1.6 kHz`, `Motion > 1.6 kHz`) across Chaparral (50.0 s), Montane (54.0 s), and Night (60.0 s) with loop boundary steps of $1.69 \times 10^{-9}$ to $4.07 \times 10^{-9}\text{ FS}$. Scored **9.67/10** from the Argon critic and passed headless Godot 4.7.2 verification (`argon_music_proof.gd`, exit 0).
  - **Unreal Engine Hero Audio Pack (`reset/unreal/import/audio/` & `reset/audiomix/`):** 100% YouTube-safe, copyright-clean stems and masters synced to the hiker's exact footplant frames (`systems/footplants_final.json`):
    - **Field Foley (`foley/`):** 8 dirt/gravel step variants, 6 wet-stone step variants, 8 hollow wooden bridge boot steps (`bridge_steps_01..08.wav`), 6 timber plank flex creaks (`bridge_creak_01..06.wav`, triggered 40–120 ms after heel strike), 6 backpack rustle one-shots + loop, and 3-distance creek loops (`creek_distant_loop.wav`, `creek_mid_loop.wav`, `creek_close_babble_loop.wav`) + `creek_passby_surge.wav` (CC0 Freesound + CC-BY-3.0 `kurt` on OpenGameArt).
    - **Sierra Bird Ecology (`birds/`):** 60.0 s seamless stereo beds (`birds_dawn_sparse_loop.wav` at `-22.5 LUFS`, `birds_hero_bed_loop.wav` at `-18.8 LUFS`) plus **26 mono 3D one-shot WAVs** across 8 species: Mountain Chickadee (4), Hermit Thrush (4), Dark-eyed Junco (3), Steller's Jay (3), American Dipper (3, creek boulders 8–28 m), White-crowned Sparrow (3), Pacific Wren (3), and Clark's Nutcracker (3, restricted to `>2,600 m` ridges and excluded from the `2,348 m` creek bed), governed by a Poisson no-repeat permutation spec.
    - **Candidate Mix & Stems (Pending Listening Review):** `reset/unreal/import/audio/mix/after_walkthrough_mix.wav` (55.0 s, 48 kHz 24-bit, **`-14.0 LUFS`**, `<= -1.0 dBTP`) with 5 sample-aligned stems (`stem_ambience_creek.wav`, `stem_birds.wav`, `stem_foley_steps.wav`, `stem_music.wav`, `stem_wind_roomtone.wav`), plus `reset/unreal/import/audio/unreal_hero_36s_16lufs.wav` (36.0 s, **`-16.00 LUFS`**, `-1.59 dBTP`) and `ambience_62s.wav` (`-16.01 LUFS`, `-1.40 dBTP`). Note: `after_walkthrough_mix.wav` has **not** passed the listening review (no `REVIEW.md` `PASS` exists in `reset/unreal/import/audio/`, and `reset/audiomix/HANDOFF.md` notes the listening gate blocks on environmental masking), so it remains a candidate mix pending review rather than an approved final master.

### 3.8 Deep Research & 32-Lane SOTA Sweep (`research`, `allmodels`, `SOTA.md`)
- **Old Way:** Developers manually searching documentation or relying on unverified model memory for shader math and engine flags.
- **Argon Way:**
  - **Foundation Research (`research`):** Completed 6 architectural decisions by 13:02 PT using **37 `deep-research-max-preview-04-2026` calls** (36 ok) and **7 `gemini-4-argon` calls** (378,111 tokens).
  - **3-Agent Deep Research Audit (`allmodels/RESULT.md`):** Executed **480 HTTP attempts (including polls)** across `deep-research-max-preview-04-2026` (195 calls across primary + revised), `deep-research-pro-preview-12-2025` (120 calls), and `deep-research-preview-04-2026` (116 calls), audited by `gemini-4-argon` (`allmodels-citation-audit`, 36 calls, 1,565,619 tokens). When Argon's citation audit rejected all 12 first drafts for unverified claims, the pipeline automatically ran a 13/13 revised source-bound pass (`research/REPORT.md`).
  - **32-Lane SOTA Sweep (`SOTA-SUMMARY.md`, ~14:35 PT):** Generated `reset/<lane>/SOTA.md` across 32 lanes using `gemini-3.8-flash` and verified every cited URL with `curl` (127 links checked; 22 returned 404 and were explicitly marked `UNVERIFIED`), ranking the top 10 AAA fixes per hour (Beer-Lambert water absorption, Lagarde waterline wetness, Vlachos two-phase flow normals, raking golden-hour sun, SSR/SSIL/SSAO tuning).

### 3.9 Image-Model Bake-Off & PBR Texture Library (`allmodels-images`, `reset-textures`)
- **Old Way:** Hand-hunting CC0 textures that rarely matched specific Sierra decomposed granite or wet cobble transitions.
- **Argon Way:**
  - **6-Model Image Bake-Off (`allmodels/images/BAKEOFF.md`):** Tested `nano-banana-pro-preview`, `gemini-3-pro-image`, `gemini-nano-banana-2.1`, `gemini-3.1-flash-lite-image`, `gemini-3.1-flash-image`, and `gemini-2.5-flash-image` (12 calls each = 72 bake-off calls, 206 total image attempts) judged blindly by `gemini-3.1-pro-preview` and `gemini-4-argon`, producing 41 candidate materials with derived normal/roughness maps, 25 section concepts, and 6 hiker outfits.
  - **PBR Texture Factory (`reset-textures`, commit `aaa78febc5`):** Used **87 `gemini-4-argon` calls** (441,554 tokens), **42 `nano-banana-pro-preview` calls** (40 media files), and **20 `gemini-3-pro-image` calls** (20 media files) to synthesize and Blender-verify seamless PBR material sets (`albedo`, `normal`, `roughness`, `ao`, `height`) for `granite`, `decomposed_granite` (with lug-sole footprint closeup), `creek_cobbles`, and 4K `jeffrey_bark` (with raking-light closeup), which were then imported into both Godot and Unreal Engine 5.6.1 (with green-channel flipped DirectX normals for UE).

### 3.10 Unreal Engine 5.6.1 Build with Parallel Argon Workers per Pod
- **Old Way:** Single-engine bottleneck in Godot 4 where custom Forward+ water, terrain, and foliage shaders required days of low-level shader debugging to approximate GI and reflections.
- **Argon Way:** On dedicated L40S pod `thru-unreal-1` (112 vCPU, 503 GB RAM, 48 GB VRAM, $0.79/hr), `pi` + `gemini-4-argon` drove a headless UE 5.6.1 container (`dev-slim-5.6.1`) via Python (`gen.py` + `ue_main.py` + Movie Render Queue) while **12 parallel `pi` + `gemini-4-argon` feeder workers** (4 lanes × 3 workers each, launched at 15:00:57 PT in `UNREAL-SWITCH-LOG.md`) built and exported scene components in parallel:
  - `unreal-assets-veg` (`w1` conifers, `w2` shrubs, `w3` ground cover/ferns/litter)
  - `unreal-assets-rocks` (`w1` boulders, `w2` wet waterline creek cobbles, `w3` gravel and trail scree)
  - `unreal-landscape-export` (`w1` heightmap, `w2` creek spline and bridge, `w3` 1,528 scatter placements and cameras)
  - `unreal-systems` (`w1` hiker locomotion/camera rig, `w2` footsteps and audio hooks, `w3` time-of-day sun/sky/fog)

---

## 4. The Godot-to-Unreal Pivot

### 4.1 Why Godot Plateaued on the Hero Creek Scene
Throughout the first three hours, multiple lanes attacked the Middle Fork San Joaquin crossing (`pct-region-0029`, June 29, 1998, 17.6h golden hour) in Godot 4.7.2:
- **Playtest Baseline (`handoffs/playtest/REPORT.md` & `BEFORE-REVIEW.md`):** In the BEFORE walkthrough (`81a73b3b50`), the hiker missed the wooden footbridge entirely and waded through the rocky creek bed (`t = 28.0–35.0s`), moved at a `4.606 m/s` (10.3 mph) jog with `>3.2 m/s` of foot sliding before hitting a **`59.92 m/s` (134 mph) warp sprint** at frame 1255, crab-walked sideways (`75°–90°` yaw offset), and walked past a creek rendered as an unshaded flat white ribbon. On physical GTX 1070 hardware, frame rate collapsed to **7.30 fps average** in Campo (`3.40 fps` 1% low, `383.9 ms` worst hitch) and **13.54 fps average** in Hero Creek (`4.61 fps` 1% low).
- **Playtest Locomotion & Bridge Fix (`handoffs/playtest/AFTER-READY.md`):** Playtest patched `walkthrough.playop.gd` to fix `body.rotation.y = heading`, disable the Flow 13x speed hijack, pace walking at `1.38–1.40 m/s`, pin `trail_day = 120`, and raycast onto the bridge deck. The resulting dry-run video (`walkthrough/playop-after/hero-after-dryrun.mp4`, 1080 frames, 36.0 s, 0 black frames, `-16.1 LUFS` muxed stereo audio) verified that the hiker walked straight ahead and crossed dead-center over the wooden bridge (`f00385`–`f00660`).
- **Visual Plateau in Godot (`reset/hero-creek/HANDOFF.md`, `model2/RESULT.md`, `lookdev/HANDOFF.md`):**
  - Even with 138 procedural placements, 6 granite GLB LODs, and a `2.08x` wet/dry luminance shader contrast wired into `pct_world.gd`, Argon's strict 4-image Art Director critique of the live Godot dry AFTER capture (`reset/hero-creek/capture/argon-after-dry-critic.txt`) **rejected** the visual quality: **`REFLECTION: 2/10`, `WETNESS: 1/10`, `DUST/ROUGHNESS: 3/10`, `LIGHT QUALITY: 3/10`**, citing the straight V-trench channel, opaque grey water under the bridge, and flat foliage lighting.
  - In `model2`, the standalone Blender creek bed plateaued at **3.0/4** in rounds 3 and 6 (dropping to **2.5/4** in round 5 as a dry gravel bed with no water).
  - In `lookdev`, Round 4 was **rejected** because it made Hauser Creek water brighter and more opaque while adding `+0.97 ms` median GPU time, `+153` draw calls, and `+84.8k` primitives at Southern Terminus.

### 4.2 The Side-by-Side Comparison (`compare/*/scores.raw`)
At 14:41–14:57 PT, we ran a blind 4-camera (`hero_low`, `wet_stones`, `trail`, `wide`) Art Director evaluation across `compare/godot-current/`, `compare/godot-dry/`, and the early `compare/unreal/` blockout (`iter2` before purchased asset packs). Every score below comes verbatim from `compare/*/scores.raw` (scale 1–10):

| Camera / Metric | `godot-current` (`scores.raw`) | `godot-dry` (`scores.raw`) | `unreal` early procedural blockout (`scores.raw`) | Key Critic Observation (`scores.raw`) |
|---|---:|---:|---:|---|
| **`hero_low`** (Refl / Wet / Dust / Light / Geom / Tex) | 2 / 1 / 2 / 3 / 3 / 2 | 2 / 1 / 2 / 3 / 2 / 2 | 3 / 2 / 2 / 3 / 1 / 2 | Godot: untextured grey terrain, straight concrete-like V-trench with a tree growing out of the middle of the water channel. Unreal iter1/2: better SSR ripples and sun reflection, but procedural cone-stack trees needed real meshes. |
| **`wet_stones`** (Refl / Wet / Dust / Light / Geom / Tex) | 1 / 1 / 2 / 2 / 3 / 2 | 1 / 1 / 2 / 2 / 2 / 2 | 3 / 2 / 2 / 3 / 1 / 2 | Godot: camera obstructed by bridge deck planks and stretched rail UVs; neon-orange/green bush blobs. Unreal: unobstructed bank view with SSR, needed real rock/cobble geometry. |
| **`trail`** (Refl / Wet / Dust / Light / Geom / Tex) | 2 / 1 / 2 / 3 / 2 / 2 | 2 / 1 / 2 / 3 / 2 / 2 | 2 / 1 / 2 / 3 / 1 / 1 | Godot: water looks like crinkled tin foil in a razor-straight trench; tree clips through stream. Unreal: needed PBR decomposed granite tread and real conifers. |
| **`wide`** (Refl / Wet / Dust / Light / Geom / Tex) | 2 / 2 / 2 / 3 / 2 / 2 | 2 / 1 / 2 / 3 / 2 / 2 | 2 / 1 / 2 / 3 / 1 / 1 | Godot: grey-boxed CSG trench, 90-degree painted stripe trail, flat lighting without GI. Unreal: Lumen GI and volumetric sky worked out of the box; only placeholder procedural cone trees held the score down. |

**The Decision (2:46 PM PT):** Paul inspected the side-by-side renders and saw that Godot's fundamental rendering ceiling (flat terrain shading, razor-straight V-trench hydro mesh, lack of Lumen global illumination) could not be fixed before 5:00 PM, whereas Unreal Engine 5.6.1 already had working Lumen GI, Virtual Shadow Maps, SkyAtmosphere, and water reflections—and only needed THRU's real 3D assets and Paul's purchased nature packs swapped in for the placeholder cones. At **2:46 PM PT**, Paul chose **Unreal Engine** as the primary AFTER showcase, keeping the fixed Godot walkthrough (`walkthrough/playop-after/hero-after-dryrun.mp4`) as backup.

### 4.3 Unreal Engine 5.6.1 Progression (`reset/unreal/JOURNAL.md`, `compare/unreal/LOOP.md` & `PROGRESSION/LOG.md`)

![Unreal Engine 5.6.1 Progression Strip (14:40 to 15:05 PT)](after/unreal-progression-strip.jpg)

1. **`14:21 PT` — `iter0` (`compare/unreal/iter0_broken` — First Real UE Render, Broken):** Terrain and water triangles were wound downward (backface-culled) and auto-exposure clamp was too tight. Fixed grid winding and exposure in 3 minutes.
2. **`14:24 / 14:40 PT` — `iter1` (`PROGRESSION/1440_hero_low_iter1-first-render.png`, `1440_wide_iter1-first-render.png`):** First working 1920x1080 renders on L40S (`thru-unreal-1`) with Lumen + Virtual Shadow Maps (VSM) and Movie Render Queue (8 temporal samples, ~45 s render after ~1.5 min build). Procedural creek terrain, translucent `Surface-ForwardShading` refractive water with panned normals and depth fade, golden-hour sun. Argon critic (`gemini-4-argon`, 8 images, 10.6k tokens, 19 s) scored **2.0/10 overall** (`hero_low 1.5`, `wet_stones 2.5`, `trail 2.0`, `wide 2.0`), flagging the placeholder cone-stack pines and clay-like procedural boulders.
3. **`14:40 PT` — Early Procedural `iter2` (`compare/unreal/iter2` & `LOOP.md`):** Added smooth GLB normals, triplanar granite mapping, cleared `hero_low` camera framing, cobble clusters, and dome repositioning. On the procedural loop rubric (`compare/unreal/LOOP.md`), score rose to **3.1/10 overall** (`hero_low 3.5`, `wet_stones 4.0`, `trail 2.5`, `wide 2.5`); under the harsh 6-axis AAA standard (`compare/unreal/scores.raw`), it scored `1–3/10` because trees were still procedural cone stacks.
4. **`15:05 PT` — Asset-Integrated `iter2` (`PROGRESSION/1505_hero_low_iter2-dense-route-hiker-pack-trees.png`, `1505_hiker_iter2-dense-route-hiker-pack-trees.png`, `1505_wide_iter2-dense-route-hiker-pack-trees.png`):** Replaced procedural placeholders with Playtest's dense route, the Quaternius `hiker_male` character with procedural 1990s hiking outfit (boots, khaki pants, flannel shirt, external-frame backpack, hat) on the bridge path, THRU photoreal conifers (`jeffrey_open`, `fir_white_tall`, `fir_red_mature` LOD0, ~45 MB GLB each), `hero_granite_a/b/c` (20,480 tris each), Poly Haven `fern_02` and `grass_medium_01`, and Argon-baked PBR texture sets (with green channel flipped for UE DirectX normals). Argon critic scored **2.6/10 overall** (`hero_low 2.5`, `wet_stones 2.5`, `trail 3.0`, `wide 3.0`, `hiker 2.0`).
5. **`15:08–15:37 PT` — Final Pass with Purchased Packs (`reset/unreal/ASSET-PACKS.md` & `ASSETS-IN-SCENE.md`):**
   - **HyperGrass Vol. 1 Wild Green (Purchased, Greg Zdunek):** **~1,700 instances** (`medium_01/09`, `tall_03`, `short_01/07`, `sprout_04`, `patch_medium/short`) as primary ground cover across all shots.
   - **Evermotion Archmodels vol. 283 (Purchased, 120 EUR):** **40k-triangle game-ready GLB LOD0 trees** (`ponderosa_pine`, `grand_fir`, `western_hemlock`, `riparian_willow_a/b`, `riparian_sycamore`) — **14 riparian + ~25 upslope + ~110 distant** trees, alongside **~70 near + ~110 distant** THRU photoreal conifers, **~15** incense cedar / Coulter pine, **34** manzanita/chamise shrubs, and **~90** cured needlegrass clumps.
   - **Arnklit Cliffs & Rocks Pack 1 (Purchased):** **~44 instances** (`boulders 1-6`, `rocks 1-4`, `piles 1-2`, `cliffs 2/4`) plus **34** THRU hero granite boulders and **~10** Poly Haven Namaqualand boulders along the creek banks.
   - **Why Nanite Was Off (`ASSETS-IN-SCENE.md`):** NVIDIA driver `550.144.03` on the L40S pod lacked `VK_KHR_compute_shader_derivatives`, causing UE 5.6.1 to reject Vulkan SM6 and run on `SF_VULKAN_SM5`. Because Nanite requires SM6, Paul directed at 15:12 PT to skip Nanite and use the 40k-triangle LOD0 GLBs instead of the 1.3M-triangle full-res Evermotion FBX files.
   - **Seeded PCG-Style Scatter (`seed 1998`):** Rather than the UE PCG plugin, `gen.py` ran a deterministic rule-based Python scatter with PCG-style ecological bands: density falloff with distance from the creek, a cleared trail corridor, dusty trail-edge short grass/needlegrass, a wet bank zone with ferns and riparian willows/sycamores, and conifers upslope, surrounded by a 1.2 km outer skirt and skyline ridge ring.

---

## 5. Fleet-Wide Impact Across Specialist Bots (`handoffs/`)

At 12:22 PM PT, realizing our local `argon` CLI was using only ~1.7M of the 20M TPM cap, we shared the key path (`~/.config/gemini/hackathon.env`, never the value) across our specialist fleet bots:

### 5.1 Pitcrew (`handoffs/pitcrew.md`)
- **Usage:** 8 `gemini-4-argon` calls (6 in shared `calls.jsonl`, 2 in `~/lanes/pitcrew-kanpai-argon/argon-calls.jsonl`), **251,407 input tokens, 37,140 output tokens (354,077 total including thinking)**, 0 HTTP 429s.
- **Results:**
  - **Dell Health Audit (`pitcrew-health`):** Argon ingested 24h of systemd journal warnings and feeder logs (**3,098 records**) and ranked the top 10 faults. Pitcrew live-verified **9 of 10 rows**, while catching speculative root causes Argon got wrong (e.g., Argon blamed a network failure for a botnet selfcheck fault that was actually a PostgreSQL syntax error).
  - **Kanpai v2 Code Review (`pitcrew-kanpai-review`):** Argon reviewed `origin/kanpai-v2` (`af272cea`) in two full-module chunks. Pitcrew wrote repro tests in a scratch worktree and **confirmed 4 real bugs out of 8 claims** with failing tests (`L2` ignored late `cancel_requested`, `L4` daemon restart blocking retry as unchanged evidence, `F3` leaked `HermesWorker.run` process on heartbeat exception, `F4` worktree path traversal defense-in-depth). Built an optional self-expiring Argon advisory-review hook (`dea4c83`, 14 focused tests pass).
  - **BYOA Architecture Rewrite (`pitcrew-byoa-fix`):** Rewrote two BYOA design proposals against 10 prior review findings in one call; cold Sonnet verification confirmed **2 of 3 HIGH findings resolved** (1 partial).
  - **Quota Cop Feeder (`qc-argon-feed`):** Routed and completed **5 of 5** eligible read-and-judge rows, while safety filters correctly held back 360 rows (286 for credential references).

### 5.2 Studio (`handoffs/studio.md`)
- **Usage:** **25 calls** in `studio-sla106-qa` (24 `gemini-4-argon`, 1 `gemini-3.8-flash`), all `ok`, in **5 minutes** (12:21–12:26 PM PT), plus 27 `gemini-4-argon` calls (61,942 tokens) in `studio-board`.
- **Results:** Visual QA of all **24 slides** of the Slancha Webinar 4 deck (`SLA-106`, draft v2), producing a prioritized fix ledger of **61 major and 50 minor findings** (catching leftover `[TBD]` placeholders, visible `prompt.md`/`thesis.md` source notes, off-brand template colors, and low-contrast text).

### 5.3 Tensor (`handoffs/tensor.md`)
- **Usage:** **504 total attempts** (`tensor-historical` 494 calls / 487 ok + `tensor-parity` 10 calls / 10 ok; 497 successful API judgments + 41 exact-payload receipt reuses; 7 HTTP 429s all recovered on first 30s retry), **472,407 input + 334,229 output = 806,636 tokens**.
- **Results:** Re-scored **8 historical/anchor/source-only evaluation runs** (**528 items**, 66 per run, plus **10 parity items** matching 10/10 on added-fact and clean-rewrite labels) under the upgraded `SLA-174` Argon judge protocol (pushed to `tensor/run-reports` at `bdedab9b`). Revealed that Argon is a substantially stricter factuality judge than the old local judge: on `bench-historical-v13c`, detected added facts rose from **16.67%** (old local judge) to **60.61% [48.48, 72.73]** under Argon, cutting clean rewrites from **66.67%** to **31.82% [21.21, 42.42]**.

### 5.4 Brain (`handoffs/brain.md`)
- **Usage:** 1 `gemini-4-argon` call (`brain-audit`), **73,537 input tokens**, 5 minutes 24 seconds wall time.
- **Results:** After strict local privacy/secret filtering (excluding 2,599 founder-visibility notes, 756 blocked-text notes, and 20 secret-regex hits out of 2,769 vault notes), Argon audited the **121 public-safe notes** (~59,653 corpus tokens). Local deterministic verification confirmed **15 of 15 Argon findings (100.0% pass rate, 0 rejected)**: **9 stale notes**, **2 cross-note conflicts**, and **4 missing links**.

### 5.5 Kaizen (`handoffs/kaizen.md` & `handoffs/kaizen-retro.md`)
- **Usage:** **15 `gemini-4-argon` calls** (`kaizen-smoke` 1, `kaizen-skills` 4, `kaizen-transcripts` 9, `kaizen-prs` 1, ~479k input tokens, ~14.7k output tokens, 0 failures) plus 1 `kaizen-retro` call (22,574 tokens).
- **Results:** Audited **35 workflow skill files** across 4 focus groups (finding 33 stale/contradictory/bloat items, verified verbatim by grep), **9 bot transcripts** (after dropping 51 sensitive messages), and **23 merged PRs** across 24 repos (identifying 13 Rule-25 review-log violations), then compiled the fact-checked operational retrospective (`handoffs/kaizen-retro.md`) with 10 concrete fleet-rule proposals.

### 5.6 Playtest (`handoffs/playtest/REPORT.md`, `BEFORE-REVIEW.md`, `AFTER-READY.md`)
- **Usage:** `playtest-before` (4 `gemini-3.8-flash` calls, 26,504 tokens) + `playtest` (6 `gemini-3.8-flash` calls, 15,169 tokens; 1 `gemini-4-argon` call, 8,128 tokens) + `pi` + `gemini-4-argon` loops (`pi-before.log`, `pi-pass.log`, `pi-after.log`).
- **Results:** Delivered the shot-by-shot BEFORE failure ledger (catching the 4.606 m/s jog, 134 mph warp sprint, 90° sideways crab-walk, Hero Creek bridge miss, and missing audio stream), ran physical **NVIDIA GTX 1070** benchmarks (`7.30 fps` Campo / `13.54 fps` Hero) and **5 off-trail/sprint brute-force stress tests** (`45.24 m` off-trail displacement, **0 terrain falls** across 2,430 frames), and authored/verified `walkthrough.playop.gd` + `hero-after-dryrun.mp4`.

### 5.7 Open Draft Pull Requests in `laulpogan/Thru-2`
Ten `[hackathon]` draft PRs (`#693`–`#702`) package the hackathon lane branches, alongside 15 Kanpai/Gemini automated PR review/fix branches (`#688`–`#692`, `#703`–`#712`):

| PR # | State | Branch (`headRefName`) | Title |
|---:|---|---|---|
| **#693** | Draft | `hackathon/argon-unreal` | `[hackathon] unreal` |
| **#694** | Draft | `hackathon/argon-hero-creek` | `[hackathon] hero-creek` |
| **#695** | Draft | `hackathon/argon-walkthrough-after` | `[hackathon] walkthrough-after` |
| **#696** | Draft | `hackathon/argon-assetfactory` | `[hackathon] assetfactory` |
| **#697** | Draft | `hackathon/argon-pathtrace` | `[hackathon] pathtrace` |
| **#698** | Draft | `hackathon/argon-hero-addons` | `[hackathon] hero-addons` |
| **#699** | Draft | `hackathon/argon-textures` | `[hackathon] textures` |
| **#700** | Draft | `hackathon/argon-biomes` | `[hackathon] biomes` |
| **#701** | Draft | `hackathon/argon-unreal-feeders` | `[hackathon] unreal-feeders` |
| **#702** | Draft | `hackathon/argon-ops` | `[hackathon] ops` |
| **#703–#712** | Draft | `work/kanpai-685` .. `work/kanpai-667` | 10 `Kanpai/Gemini` automated review-fix draft PRs (6 `[review APPROVE]`, 4 `[review CHANGES]`) |
| **#688–#692** | Draft | `work/kanpai-223` .. `work/kanpai-163` | 5 `Kanpai/Gemini` automated review-fix draft PRs (all 5 `[review APPROVE]`) |

---

## 6. Per-Lane Visual & Audio Results (Verified Relative Paths)

All image and audio paths below are relative to `~/cs-audit/gemini-hackathon` (`H`) and verified on disk.

### 6.1 Side-by-Side Engine Comparison (`compare/`)
- **Godot Current vs. Godot Dry vs. Unreal Engine (Hero Low Angle):**
  - Godot Current: `compare/godot-current/hero_low.jpg`
  - Godot Dry: `compare/godot-dry/hero_low.jpg`
  - Unreal Engine: `compare/unreal/hero_low.jpg`
- **Godot Current vs. Unreal Engine (Wide Vista, Wet Stones, Trail):**
  - Wide Vista: `compare/godot-current/wide.jpg` vs. `compare/unreal/wide.jpg`
  - Wet Stones: `compare/godot-current/wet_stones.jpg` vs. `compare/unreal/wet_stones.jpg`
  - Trail Corridor: `compare/godot-current/trail.jpg` vs. `compare/unreal/trail.jpg`

![Godot Current Hero Low](compare/godot-current/hero_low.jpg)
![Unreal Iter1 Hero Low](reset/unreal/PROGRESSION/1440_hero_low_iter1-first-render.png)
![Unreal Iter2 Hero Low (Dense Route, Hiker & Pack Trees)](reset/unreal/PROGRESSION/1505_hero_low_iter2-dense-route-hiker-pack-trees.png)
![Unreal Iter2 Wide Vista](reset/unreal/PROGRESSION/1505_wide_iter2-dense-route-hiker-pack-trees.png)

### 6.2 Unreal Engine 5.6.1 Timestamped Progression (`reset/unreal/PROGRESSION/`)
- **14:40 PT (`iter1` — First Lumen + VSM Render):**
  - Low Angle: `reset/unreal/PROGRESSION/1440_hero_low_iter1-first-render.png`
  - Wide Angle: `reset/unreal/PROGRESSION/1440_wide_iter1-first-render.png`
- **15:05 PT (`iter2` — Dense Route, Quaternius Hiker, THRU Photoreal Conifers, Hero Granite, Pack PBR):**
  - Low Angle: `reset/unreal/PROGRESSION/1505_hero_low_iter2-dense-route-hiker-pack-trees.png`
  - Hiker Close-up: `reset/unreal/PROGRESSION/1505_hiker_iter2-dense-route-hiker-pack-trees.png`
  - Wide Angle: `reset/unreal/PROGRESSION/1505_wide_iter2-dense-route-hiker-pack-trees.png`

### 6.3 Godot Hero Creek Before vs. Dry After (`reset/hero-creek/out/`)
- **Overview Pair:** `reset/hero-creek/out/hero-creek-before-overview.jpg` vs. `reset/hero-creek/out/hero-creek-dry-overview.jpg`
- **Low-Angle Pair:** `reset/hero-creek/out/hero-creek-before-low.jpg` vs. `reset/hero-creek/out/hero-creek-dry-low.jpg`
- **Wet Cobble & Riffle Pairs:** `reset/hero-creek/out/hero-creek-before-wet-cobble.jpg` vs. `reset/hero-creek/out/hero-creek-dry-wet-cobble.jpg`; `reset/hero-creek/out/hero-creek-before-riffle.jpg` vs. `reset/hero-creek/out/hero-creek-dry-riffle.jpg`

### 6.4 Lookdev Multi-Round Hero Locations (`lookdev/`)
- **Composite Before/After Contact Sheet:** `lookdev/before-after-sheet.jpg`
- **Campo Creek (Before vs. Round 5):** `lookdev/gallery/assets/campo_creek_before.jpg` vs. `lookdev/gallery/assets/campo_creek_round5.jpg`
- **Thousand Island Lake (Before vs. Round 4):** `lookdev/gallery/assets/thousand_island_lake_before.jpg` vs. `lookdev/gallery/assets/thousand_island_lake_round4.jpg`

![Lookdev Before vs After Sheet](lookdev/before-after-sheet.jpg)

### 6.5 Evolutionary 3D Modelling & Surface-Feel PBR Closeups (`model2/`, `reset/textures/`, `handoffs/playtest/`)
- **`model2` Creek Bed Evolution (Round 1 vs. Round 6 Scored Contact Sheets):** `model2/creek/r01/contact-scored.png` vs. `model2/creek/r06/contact-scored.png`
- **Surface-Feel Macro Closeups (`reset/textures/v3-remote-output/`):**
  - Dusty Decomposed Granite Tread with Footprint: `reset/textures/v3-remote-output/decomposed_granite/renders/dusty_footprint.png`
  - Jeffrey Pine Bark in Raking Light: `reset/textures/v3-remote-output/jeffrey_bark/renders/raking_light.png`
- **Playtest BEFORE Defect Evidence (`handoffs/playtest/before-screens/`):**
  - Flat White Ribbon Creek (`00:10`): `handoffs/playtest/before-screens/flat_white_creek_f0300.png`
  - Sideways 90° Hiker Crab-Walk (`00:06`): `handoffs/playtest/before-screens/hiker_facing_right_f0180.png`

![Model2 Creek Round 6 Scored Contact Sheet](model2/creek/r06/contact-scored.png)
![Decomposed Granite Dusty Footprint Closeup](reset/textures/v3-remote-output/decomposed_granite/renders/dusty_footprint.png)

### 6.6 Audio Deliverables & Stems (Relative Links)
- **Unreal AFTER Candidate Walkthrough Mix — Pending Listening Review (55.0 s, 48 kHz 24-bit, `-14.0 LUFS`; not yet cleared by `REVIEW.md` listening gate due to environmental masking):** [reset/unreal/import/audio/mix/after_walkthrough_mix.wav](reset/unreal/import/audio/mix/after_walkthrough_mix.wav)
  - Stem — Sierra Creek Ambience & Bridge Surge: [reset/unreal/import/audio/mix/stem_ambience_creek.wav](reset/unreal/import/audio/mix/stem_ambience_creek.wav)
  - Stem — Sierra Nevada Birds (7 species): [reset/unreal/import/audio/mix/stem_birds.wav](reset/unreal/import/audio/mix/stem_birds.wav)
  - Stem — Hiker Foley, Gravel/Wet-Stone Steps & Bridge Creaks: [reset/unreal/import/audio/mix/stem_foley_steps.wav](reset/unreal/import/audio/mix/stem_foley_steps.wav)
  - Stem — 1990s Americana Lyria Score: [reset/unreal/import/audio/mix/stem_music.wav](reset/unreal/import/audio/mix/stem_music.wav)
  - Stem — Mountain Room Tone & Pine Wind: [reset/unreal/import/audio/mix/stem_wind_roomtone.wav](reset/unreal/import/audio/mix/stem_wind_roomtone.wav)
- **Unreal Hero Creek 36.0 s Master (`-16.00 LUFS`, `-1.59 dBTP`):** [reset/unreal/import/audio/unreal_hero_36s_16lufs.wav](reset/unreal/import/audio/unreal_hero_36s_16lufs.wav)
- **Unreal 62.0 s Ambience Master (`-16.01 LUFS`, `-1.40 dBTP`):** [reset/unreal/import/audio/ambience_62s.wav](reset/unreal/import/audio/ambience_62s.wav)
- **Sierra 2,348 m Bird Bed Loop (60.0 s seamless stereo, `-18.8 LUFS`):** [reset/unreal/import/audio/birds/birds_hero_bed_loop.wav](reset/unreal/import/audio/birds/birds_hero_bed_loop.wav)
- **Wooden Footbridge Boot Steps & Timber Creaks Demo:** [reset/unreal/import/audio/foley/bridge_walk_demo.wav](reset/unreal/import/audio/foley/bridge_walk_demo.wav)
- **Godot Hero Creek 36.0 s Mix (`-16.0 LUFS`):** [reset/audiomix/hero_mix.wav](reset/audiomix/hero_mix.wav)
- **Godot Campo Walkthrough Mix:** [reset/audiomix/walkthrough_mix.wav](reset/audiomix/walkthrough_mix.wav)
- **Audio Candidate Pack 182-Second Top-12 Sampler:** [audio/sampler.mp3](audio/sampler.mp3)

---

## 7. What Broke & Where Gemini Was Weak

### 7.1 Operational & Infrastructure Failures

1. **The "Unlimited" Key's 20M TPM Per-Model Cap & HTTP 429s (11:54 AM PT):**
   - We launched our first `pi` + `gemini-4-argon` review swarm at 64-way parallelism assuming the hackathon key had no per-minute ceiling. In fact, the key enforced a Tier 3 limit of **20M input tokens/min per model**. The first **225 swarm jobs failed with HTTP 429** and produced zero output (`JOURNAL.md`, 11:54), and our `oh-my-pi` sub-agent test 429'd at the same time.
   - *Fix:* Dropped swarm concurrency to 32 with 8-retry exponential backoff, and sharded bulk queues across distinct model pools (`gemini-3.8-flash`, `3.7-flash`, `3.6-flash`, `3.5-flash`), each with its own independent 20M TPM allowance.
2. **The `Xvfb` `flock` File-Descriptor Wedge on `render-1` (14:51 PM PT):**
   - Remote capture scripts (`reset/lighting/{combined-b96,round1/delta-pod1}/remote-capture.sh`) acquired an exclusive `flock` on file descriptor `9` (`/opt/thru/render.lock`) and launched `Xvfb` in the background without closing fd `9`. The background `Xvfb` daemon inherited the open lock descriptor and held `thru-render-1` wedged long after the render exited, while `runpod/rounds.py` kept targeting hardcoded `thru-render-1`.
   - *Fix:* Added `9>&-` to all `Xvfb` launches (`JOURNAL.md`, 14:51), parameterized `THRU_RENDER_POD` in `rounds.py`, and wrote `runpod/ROUNDS-STOP`.
3. **33 of 43 RunPod Pods Sitting Idle at $20.30/hr (13:16 PM PT):**
   - Lanes provisioned cloud pods before queuing work. Worse, the `assetfactory` controller crashed on startup (`gallery.py "Invalid asset id"`), leaving **194+ manifest rows unsubmitted** and `0 pending` jobs in the queue at 13:15 PT (`handoffs/kaizen-retro.md`). In addition, two worker slots on a single pod simultaneously ran `worker/install-blender.sh` into the same archive path, failing **12 `fleetq` jobs** in ~12 seconds with `EOFError`.
   - *Fix:* Wrote `runpod/PAUSE_SCALING`, launched a central Fleet Operator (`runpod/FLEET.md`) with pre-baked idempotent pod bootstrap and pull-based `fleetq` dispatch across ~60 worker slots.
4. **Dell Workstation Overload (Peak Load 227.48 at 13:02 PT) & `SIGSTOP` Leak:**
   - Running 50+ local Codex orchestrators alongside 9 full git worktree checkouts and recursive repo greps drove Dell 1-minute load to **227.48** at 13:02:07 PT (`BOTTLENECKS.md`), `74%` disk `iowait` at 12:50 PT, and drained **356 GB of free disk** in two hours (`694 GB -> 338 GB`). When we tried to pause 46 lanes at 13:25 PT using `SIGSTOP` on a PID snapshot (`reset/PAUSED-PIDS.txt`, 1,211 PIDs), `codexwatch.sh` found **0 stopped and 59 running `codex exec` processes** 3 minutes later because child processes were spawned outside the snapshot.
   - *Fix:* Wrote `pilane/retire.sh` to recursively walk every `tmux` pane's process tree (`pgrep -P`) before killing the session, and migrated all 39+ lane orchestrators onto cloud `cpu3c` pods running `pi` + Argon.
5. **The `agy` Subscription Pool Confusion (11:48–11:49 AM PT):**
   - Google Antigravity CLI (`agy` 1.4.7) in headless `-p="prompt"` mode ignored `GEMINI_API_KEY` and billed the rationed weekly `agy-gemini` subscription pool (`46.9%` used at 11:49 AM, rising to `50.45%` by 13:36 PT). Quota Cop caught it in 60 seconds and we replaced `agy` with `pi` (`0.86`).
6. **Model Council Consensus Script Crash (`council/consensus.log`):**
   - Although the 8-model council logged **3,807 verdict rows** in `council/progress.tsv`, `council/consensus.py` (written inline via a shell heredoc) crashed at line 22 with `SyntaxError: unexpected character after line continuation character` caused by backslash-escaped quotes inside a nested Python f-string (`f'{m.replace(\"gemini-\",\"\")}={x}'`). As a result, **no `CONSENSUS.md` was ever generated**.
7. **Codex Weekly Quota Burn (39.0% at 13:35 PM PT):**
   - Using `codex exec` (`gpt-6.1-sol`) as the outer loop driver for 50+ lanes pushed weekly Codex quota to **39.0%** by 13:35 PT (`~/.fleet-monitor/quota-gauges.json`), triggering a Quota Cop freeze at 13:23 PT and our complete retirement of hackathon Codex sessions by 14:06:23 PT (`CODEX-EXIT.md`).

### 7.2 Honest Assessment: Where Gemini Models Were Weak

- **Image Repaints Invented Non-Existent 3D Geometry (`media`, `JOURNAL.md` 13:02):** `nano-banana-pro-preview` produced striking Sierra creek paintings in `media/repaints/`, but it hallucinated boulders, water channels, and tree trunks that did not exist in the underlying collision or terrain meshes. They could not be used as before/after proof and had to be restricted to internal look-targets.
- **Zero-Pass Round 1 3D Modelling & Evolutionary Plateau (`model`, `model2`, `JOURNAL.md` 12:13 & 13:02):** In `model` Round 1, giving `gemini-4-argon` only 2 rounds produced **0/7 photo gate passes**. Even with 6–7 evolutionary 4-variant rounds in `model2`, the standalone Blender creek bed **plateaued at 3.0/4** (dropping to 2.5/4 in round 5 as a dry gravel bed with no water), rock peaked at **2.5/4** (round 5) before slipping to **2.0/4** (round 6–7), and pine peaked at **2.75/4**. Furthermore, long Argon GLB export repair scripts in `model2` repeatedly hit an observed **32,768 combined thought/output token ceiling** despite requesting 65,536, sometimes returning only a newline (`model2/RESULT.md`).
- **Shader Regressions & Hallucinated Identifiers in `lookdev` (`lookdev/HANDOFF.md`):** Argon's Round 4 water candidate caused a direct visual regression in Hauser Creek (making water brighter and more opaque greyish-white while losing shoreline darkening) and added `+0.97 ms` GPU time and `+153` draw calls at Southern Terminus. Its first Round 5 water repair patch had to be rejected pre-apply by Codex because Argon wrote shader identifier typos (`ang`, `deep_ scatter`), off-path tangent normalization drift, and unmasked slope-as-rock foam.
- **Ungrounded SOTA Advice & Broken Links (`SOTA-SUMMARY.md`, `reset/unreal/SOTA.md`):** Running `gemini-3.8-flash` without search grounding across 32 SOTA briefs produced **22 broken (`404`) URLs out of 127 links checked**. Worse, in `reset/unreal/SOTA.md`, `gemini-3.8-flash` recommended running `UnrealEditor-Cmd` with `-nullrhi -RenderOffscreen` to render Path Tracer ground-truth frames—a fatal contradiction because `-nullrhi` disables the rendering hardware interface entirely (`SOTA-SUMMARY.md`).
- **Synthetic Foley & Fallible Audio Listening (`audio/RESULT.md`):** Both pure-nature Lyria pilots sounded musical/synthetic and were rejected, and procedural foley effects were unconvincing (forcing us to use real CC0/CC-BY field recordings for all Unreal footsteps, creaks, and creek water). When judging audio files, both `gemini-4-argon` and `gemini-3.1-pro-preview` hallucinated musical instruments inside procedural rain noise and **approved two field recordings whose metadata explicitly advertised road traffic or incompatible ecology** (`audio/RESULT.md`). Early TTS calls also read stage directions aloud until prompts were rewritten.
- **Temporal Video Rejections, Computer-Use 503s & Unverified First-Draft Citations (`allmodels/RESULT.md`):** In `allmodels`, all **9 video clips and the 48 s mood trailer** generated by `gemini-omni-1.1-flash` and `gemini-omni-flash-preview` were **rejected** by Argon's temporal consistency critic; `gemini-2.5-computer-use-preview-10-2025` failed with HTTP **503** on every live call; and all **12 initial Deep Research reports** failed Argon's strict citation verification pass and had to be re-run as 13 source-bound audits.
- **50% False-Positive Rate on Static Bug Claims & Security Prompt Refusals (`handoffs/pitcrew.md`):** In Pitcrew's Kanpai review, only **4 of 8** Argon bug claims were real bugs, every unit test Argon drafted guessed wrong function signatures or class names and had to be adapted by hand, and two security-framed code review prompts wasted **321 s and 365 s** only to return **3-token empty responses** due to provider safety filters until reframed as *"defensive correctness review of our own code"*.

---

## 8. What's Next

1. **Wire the Exact Godot Hero Export into the Unreal Scene:** The `unreal-landscape-export` workers landed the exact extracted Godot terrain (`heightmap_bridge_frame_1009`), `bridge_godot_exact.glb`, `water_ribbon`/`wet_bank` meshes, and **1,528 real instance placements** between 15:10 and 15:18 PT (`ASSETS-IN-SCENE.md`), just after the 15:40 PT scene-lock cutoff. Wiring those exact meshes into `ue_main.py` replaces the procedural approximation with 1:1 geographical parity.
2. **Enable Vulkan SM6 & Nanite on an Upgraded Driver Image:** Upgrading the RunPod container base from NVIDIA driver `550.144.03` to a driver supporting `VK_KHR_compute_shader_derivatives` unlocks Vulkan SM6, allowing UE 5.6.1 to enable **Nanite** and swap the 40k-triangle Evermotion AM283 LOD0 GLBs for the full 1.3M-triangle Archmodels FBX trees.
3. **Fix `council/consensus.py` & Land Verified Swarm Fixes:** Replace the broken nested f-string on line 22 of `council/consensus.py` to aggregate all **3,807 multi-model council verdicts**, and run cross-family Rule-25 reviews on the local `fixes2` commits (`#683`, `#676`, `#648`) and the 11 `[review APPROVE]` Kanpai/Gemini draft PRs so `fleet/thru` head (`101a52b40e`) advances cleanly.
4. **Enforce the 10 Kaizen Fleet-Rule Upgrades:** Land the post-mortem guardrails from `handoffs/kaizen-retro.md`—requiring queued work (`pending >= active_slots * 2`) before pod provisioning, `flock`-guarded idempotent bootstrap images, `9>&-` descriptor closure on all `Xvfb` wrappers, and unified `calls.jsonl` telemetry inside `pi` so fleet token accounting is never a lower bound again.
