# THRU Unreal Systems Drop (`reset/unreal/systems/`)

Delivered by lane **`unreal-systems`** (2026-10-25 15:02 PT, ahead of 15:15 PT first-drop gate).
Ports THRU's Godot 4 gameplay, camera, footstep/surface, audio ambience, and time-of-day/atmosphere systems to Unreal Engine 5.6 (`ghcr.io/epicgames/unreal-engine:dev-slim-5.6.1`).

---

## 1. Delivered System Specs & Copy-Ready UE 5.6 Python Scripts

| System | Spec Document | UE 5.6 Python + CLI Script | Pre-Computed Data / Masters |
|---|---|---|---|
| **1. Trail-Follow & Camera** | `trail-follow.md` | `ue_trail_follow.py` | `trail_follow_keyframes_39p2s_dense.json` (39.20s / 2,353 frames @ 60fps synced to `path-hero-after-dense.json` with 4s bridge pause at frames `1479..1718`), `trail_follow_keyframes_36s.json` (22s walk @ `1.40 m/s` + 14s bridge linger, 60fps), `trail_follow_keyframes_10s.json` (10s walk @ `1.35 m/s`, 60fps) |
| **2. Spatial Audio Ambience** | `audio-ambience.md` | `ue_audio_ambience.py` | `unreal_hero_36s_16lufs.wav` (`-16.00 LUFS`, `-1.59 dBTP`), `unreal_walk_62s_16lufs.wav` (`-16.01 LUFS`, `-1.40 dBTP`, also copied to `../import/audio/ambience_62s.wav`), `unreal_walk_10s_16lufs.wav` (`-16.11 LUFS`) |
| **3. Footstep Surfaces & Dust** | `footstep-surfaces.md` | `ue_footstep_surfaces.py` | `footstep_events_36s.json` (`38` steps: `24` decomposed granite, `4` gravel abutment, `10` wood bridge, `14` `NS_TreadDust` puffs) |
| **4. Time of Day & Atmosphere**| `time-of-day.md` | `ue_time_of_day.py` | `time_of_day_hero.json` (`sky_hour = 17.6`, June 29 1998, `sun_pitch = -9.0 deg`, `4100 K`, `10 lux`, `altitude_haze = 0.4827`, `fog_density = 0.00348`, Lumen/VSM CVars) |

---

## 2. Quick Integration into `ue_main.py` & `post.py` on `thru-unreal-1`

### A. Inside `ue_main.py`
```python
import sys
sys.path.insert(0, "/workspace/unreal/systems")
import ue_trail_follow, ue_footstep_surfaces, ue_audio_ambience, ue_time_of_day

# 1. Bind PhysicalMaterials (PM_Granite, PM_DecomposedGranite, PM_WoodBridge, PM_Gravel, PM_WaterSplash)
ue_footstep_surfaces.setup_unreal_footstep_surfaces()

# 2. Spawn Golden-Hour Atmosphere, Volumetric Fog, SkyAtmosphere (#2e66b5 Sierra zenith) & PostProcessVolume
atmo_cfg, atmo_cvars = ue_time_of_day.apply_unreal_time_of_day(sy=AX["sy"], sky_hour=17.6, elevation_m=2348.28)
CV.update(atmo_cvars)

# 3. Spawn Spatial Creek Spline & Dusk Ambience Actors
ue_audio_ambience.setup_unreal_audio_ambience(audio_src_dir="/workspace/unreal/assets", sy=AX["sy"])

# 4. Build SeqWalk with FK-synced walk play_rate (speed / 1.0181) + velocity-aligned yaw + bridge linger
ue_trail_follow.build_unreal_trail_follow(
    seq_name="SeqWalk", speed_mps=1.40, fps=60,
    walk_duration_s=22.0, linger_duration_s=14.0, sy=AX["sy"]
)
```

### B. Inside `post.py` (Direct `-16.0 LUFS` Audio Mux)
Replace the two-stem `amix` in `post.py` with the pre-mastered `-16.0 LUFS` walkthrough audio (`unreal_hero_36s_16lufs.wav` or `unreal_walk_62s_16lufs.wav`):
```bash
ffmpeg -y -framerate 60 -i walk.%04d.png -i /workspace/unreal/systems/unreal_hero_36s_16lufs.wav \
  -map 0:v:0 -map 1:a:0 -shortest -c:v libx264 -profile:v high -preset slow -crf 16 \
  -pix_fmt yuv420p -c:a aac -ar 48000 -b:a 256k walk.mp4
```

---

## 3. Source & License Provenance (Cross-Referenced with `reset/unreal/ASSET-PACKS.md`)

| Asset / File | Source Path (Dell) | Author / Origin | License | Public Video (YouTube) OK? |
|---|---|---|---|---|
| `hiker_male.glb` (rig + `walk` / `idle` clips) | `~/Source/Thru-2/godot/assets/people/quaternius/hiker_male.glb` | Quaternius Universal Base Characters | **CC0-1.0** | YES |
| `creek_near.wav`, `creek_far.wav`, `creek_medium.wav` | `~/cs-audit/gemini-hackathon/reset/audiomix/masters/creek_*.wav` | kurt, *"Stream Sounds"* (`stream1_kurt`, `stream3_kurt`), OpenGameArt | **CC-BY-3.0** *(credit in YouTube description)* | YES (with attribution) |
| `Sierra_alpine_dusk.wav` | `~/cs-audit/gemini-hackathon/audio/masters/ambience/Sierra_alpine_dusk.wav` | THRU audio lane (procedural master) | **THRU Original** | YES |
| `wind_pines_soft/medium/strong.wav` | `~/cs-audit/gemini-hackathon/reset/audiomix/masters/wind_pines_*.wav` | Freesound `81797`, `843927`, `520540` | **CC0-1.0** | YES |
| `mountain_chickadee_1583116.wav`, `2127131.wav`, `canyon_wren_1320386.wav` | `~/cs-audit/gemini-hackathon/reset/audiomix/masters/` & `audio/masters/ambience/` | iNaturalist field recordings (`1583116`, `2127131`, `1320386`) | **CC0-1.0** | YES |
| `decomposed_granite_01..04.wav`, `step_granite_01..04.wav`, `step_gravel_01..04.wav`, `step_wood_01..04.wav`, `splash_01..04.wav` | `~/cs-audit/gemini-hackathon/audio/masters/sfx/` & `reset/audiomix/masters/` | Freesound CC0 foley (`384880`, `556002`, `398680`, `828885`, `148802`, `369838`, `369580`) | **CC0-1.0** | YES |
| `music_sierra_conifer.wav`, `creeks_bed.wav`, `creeks_melody.wav` | `~/cs-audit/gemini-hackathon/reset/audiomix/masters/` & `audio/masters/music/` | THRU audio lane (`lyria-3.5`) | **THRU Original** | YES |
| `trail-follow.md`, `audio-ambience.md`, `footstep-surfaces.md`, `time-of-day.md`, `ue_*.py` | `~/cs-audit/gemini-hackathon/reset/unreal/systems/` | THRU `unreal-systems` lane (ported from `Thru-2` Godot 4 code) | **THRU Original** | YES |

### Required YouTube Description Attribution Line
> Stream ambience: "Stream Sounds" by kurt (https://opengameart.org/content/stream-sounds), licensed under CC-BY-3.0 (https://creativecommons.org/licenses/by/3.0/).
