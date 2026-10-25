# System 3: Footstep Surfaces, Physical Materials, Sound Cues & Tread Dust (`footstep-surfaces`)

Ported from THRU Godot 4 sources & foley lane contracts:
- `godot/scripts/trail_footsteps.gd` (`STRIDE_M = 0.78 m` distance-accumulated step cadence, non-repeating shuffle-bag `_draw`, foliage brush `BRUSH_RADIUS_M = 1.15 m`, `BRUSH_GAP_SECONDS = 1.4 s`, pitch/gain tables)
- `godot/scripts/pct_surface_identity.gd` (Regional surface patch manifest binding)
- `godot/scripts/tread_dust.gd` (`TreadDust` pooled 12-voice `GPUParticles3D` puff emitter, `particles_per_puff = 9`, `puff_life_s = 0.85`, `puff_lift_m = 0.06`, `dry_saturation = 0.45`, regional tread bands)
- `reset/audio-foley/COVERAGE.md` & `reset/audiomix/ASSET_MANIFEST.json` (Segmented 48 kHz CC0 foley banks for granite, decomposed granite, wood bridge, gravel, and water splash)

---

## 1. Five Physical Materials (`UPhysicalMaterial` & `EPhysicalSurface`)

Configure in `DefaultEngine.ini` under `[/Script/Engine.PhysicsSettings]` and create in `/Game/Physics/` via `ue_footstep_surfaces.py`:

| Surface Slot (`DefaultEngine.ini`) | Physical Material Asset | Friction / Restitution | Wet State Override (`Wetness > 0.5`) | Niagara VFX on Step | Sound Cue / MetaSound |
|---|---|---|---|---|---|
| `SurfaceType1="Granite"` | `/Game/Physics/PM_Granite` | `Friction = 0.85`, `Restitution = 0.15`, `Density = 2.65 g/cm3` | `Friction = 0.42` (slick wet granite near waterline), zero dust | None (or micro water sheen droplet if wet) | `/Game/Audio/Footsteps/SC_Step_Granite` |
| `SurfaceType2="DecomposedGranite"` | `/Game/Physics/PM_DecomposedGranite` | `Friction = 0.78`, `Restitution = 0.05`, `Density = 1.75 g/cm3` | `Friction = 0.65`, suppresses `NS_TreadDust` when `ground_wetness > 0.45` | `NS_TreadDust` (`9` grains, `0.85 s` life, `6 cm` lift, `dust_lift = 0.65` Sierra / `0.90` Desert) | `/Game/Audio/Footsteps/SC_Step_DecomposedGranite` |
| `SurfaceType3="WoodBridge"` | `/Game/Physics/PM_WoodBridge` | `Friction = 0.80`, `Restitution = 0.12`, `Density = 0.68 g/cm3` | `Friction = 0.55` | None | `/Game/Audio/Footsteps/SC_Step_WoodBridge` |
| `SurfaceType4="Gravel"` | `/Game/Physics/PM_Gravel` | `Friction = 0.72`, `Restitution = 0.08`, `Density = 1.90 g/cm3` | `Friction = 0.68`, suppresses dust | `NS_TreadDust` (`dust_lift = 0.25`, coarse talus grains) | `/Game/Audio/Footsteps/SC_Step_Gravel` |
| `SurfaceType5="WaterSplash"` | `/Game/Physics/PM_WaterSplash` | `Friction = 0.55`, `Restitution = 0.02`, `Density = 1.00 g/cm3` | Always wet (`Wetness = 1.0`) | `NS_WaterSplash` (radial crown droplets + expanding ripple decal) | `/Game/Audio/Footsteps/SC_Step_WaterSplash` |

---

## 2. Sound Cue Banks & Pitch/Gain Rules (`trail_footsteps.gd` + `ASSET_MANIFEST.json`)

Each surface uses a 4-to-6 variant **Non-Repeating Shuffle Bag** (`USoundNodeRandom` with `bRandomizeWithoutReplacement = true` inside a `USoundCue`, followed by `USoundNodeModulator` for pitch/volume jitter):

| Surface ID | UE SoundCue Asset | WAV Files to Import (`~/cs-audit/gemini-hackathon/...`) | Pitch Range (`Modulator`) | Gain (dB) | License & Source |
|---|---|---|---|---|---|
| `granite` | `SC_Step_Granite` | `reset/audiomix/masters/step_granite_01..04.wav` (+ `audio/masters/sfx/wet_rock_01..04.wav` when within `0.45 m` of creek waterline) | `[0.94, 1.06]` | `-10.0 dB` (`-8.5 dB` wet) | **CC0-1.0** (`recorded_wet_stone_398680` / `828885`) |
| `decomposed_granite` | `SC_Step_DecomposedGranite` | `audio/masters/sfx/decomposed_granite_01..06.wav` & `reset/audiomix/masters/step_dirt_01..04.wav` | `[0.92, 1.05]` | `-9.0 dB` | **CC0-1.0** (`recorded_decomposed_granite_384880` / `556002`, `PotatokingXII` 352870) |
| `wood_bridge` | `SC_Step_WoodBridge` | `reset/audiomix/masters/step_wood_01..04.wav` & `audio/masters/sfx/wooden_bridge_01..06.wav` | `[0.95, 1.05]` | `-8.5 dB` | **CC0-1.0** (`recorded_wooden_bridge_148802` / `369838`, `recorded_bridge_boots_642008`) |
| `gravel` | `SC_Step_Gravel` | `reset/audiomix/masters/step_gravel_01..04.wav` & `audio/masters/sfx/gravel_01..06.wav` | `[0.96, 1.08]` | `-8.0 dB` | **CC0-1.0** (`recorded_gravel_384880` / `556002`) |
| `water_splash` | `SC_Step_WaterSplash` | `audio/masters/sfx/splash_01..06.wav` & `audio/masters/sfx/field_splash_v01..06.wav` | `[0.90, 1.08]` | `-7.5 dB` | **CC0-1.0** (`recorded_splash_369580` / `612964`) |
| `foliage_brush` *(secondary)* | `SC_Foliage_Brush` | `reset/audiomix/pod/out/stems/footstep_foliage_brush_01.wav` | `[0.92, 1.12]` | `-13.0 dB` | **CC-BY-4.0** (Antoinemax OGA nature pack) |
| `pack_canteen` *(secondary)* | `SC_Foley_Canteen` | `audio/masters/sfx/field_canteen_v01..04.wav` | `[0.96, 1.04]` | `-18.0 dB` | **CC0-1.0** (`recorded_canteen_386436` / `850519`) |

---

## 3. Cadence, Surface Detection & Tread Dust Logic

### 3.1 Distance-Accumulated Cadence vs. AnimNotify (`trail_footsteps.gd:15, 74-90`)
THRU triggers footsteps from **ground distance covered** (`STRIDE_M = 0.78 m`), never a fixed wall-clock timer, so slow uphill climbs and stops on the bridge never machine-gun footsteps:
1. **Runtime Character (`AThruHikerCharacter::Tick`)**:
   - If `!GetCharacterMovement()->IsMovingOnGround()` or `HorizontalSpeed < 30.0f` (`0.3 m/s`), reset `DistanceAccum = 0.0f`.
   - Else `DistanceAccum += HorizontalSpeed * DeltaSeconds`.
   - When `DistanceAccum >= 78.0f` (`0.78 m`):
     - `DistanceAccum = FMath::Fmod(DistanceAccum, 78.0f)`
     - Fire `TriggerFootstep(CurrentFoot)` and notify `MusicSubsystem->OnMusicStep()` (`MUSIC-CONTRACT.md` holds `motion_intensity = 0.65` for `1.0 s`).
2. **Sequencer / AnimSequence (`UAnimNotify_PlayFootstep`)**:
   - In `/Game/Pack/hiker_male/walk` (`1.3333 s`, 32 frames @ 24 fps):
     - **Left Foot Strike (`foot_l`)**: Frame **`8`** (`t = 0.3333 s`, normalized phase `0.25`).
     - **Right Foot Strike (`foot_r`)**: Frame **`24`** (`t = 1.0000 s`, normalized phase `0.75`).
   - Because `play_rate = speed_mps / 1.0181`, the AnimNotify automatically scales its temporal cadence with walking speed (`0.6787 m` per step).

### 3.2 Surface Detection Hierarchy
At each foot strike location $\mathbf{p}_{\text{foot}}$:
1. **Physics Line Trace (`UKismetSystemLibrary::LineTraceSingle`)**:
   - Trace from $\mathbf{p}_{\text{foot}} + (0, 0, 35\text{ cm})$ to $\mathbf{p}_{\text{foot}} - (0, 0, 25\text{ cm})$ with `bReturnPhysicalMaterial = true`.
   - Read `HitResult.PhysMaterial->SurfaceType`:
     - Bridge mesh (`M_Wood` -> `PM_WoodBridge`) returns `SurfaceType3` (`wood_bridge`).
     - Boulders/slabs (`M_Granite` -> `PM_Granite`) return `SurfaceType1` (`granite`).
     - Water plane (`M_Water` -> `PM_WaterSplash`) returns `SurfaceType5` (`water_splash`).
2. **Terrain Mask Sub-Classification (`T_TerrainMask` RGB on `M_Terrain`)**:
   - When the trace hits the continuous `terrain` mesh (`M_Terrain`), sample the terrain mask coordinates $(u, v)$ (`gen.py:55-58`):
     - **Red channel (`bed > 0.5`)**: Creek cobble/granite bed $\to$ `granite` (or `water_splash` if $z \le z_{\text{water}}(x) + 8\text{ cm}$).
     - **Bridge abutment zone ($|x| < 2.5\text{ m},\; |y| \in [6.8, 9.6]\text{ m}$)**: Compacted talus/crushed rock approach $\to$ `gravel`.
     - **Green channel (`trail > 0.35`) or Blue channel (`bank`)**: Dry Sierra trail tread $\to$ `decomposed_granite`.

### 3.3 Pooled Tread Dust (`tread_dust.gd` -> Niagara `NS_TreadDust`)
- **Pool Budget (`tread_dust.gd:63-80`)**:
  - Fixed pool of `12` particle component instances (`pool_puffs = 12`), recycled round-robin without dynamic allocation.
  - Each burst spawns `9` dust grains (`particles_per_puff = 9`), lifetime `0.85 s` (`puff_life_s = 0.85`), starting `6.0 cm` (`puff_lift_m = 0.06`) above the boot heel.
- **Dryness Gate (`ground_is_dry`, `tread_dust.gd:104-112`)**:
  - Active only when `snow_cover <= 0.02`, `weather not in ("rain", "snow")`, `precip_mm <= 0.3`, and `ground_wetness <= 0.45` (`dry_saturation = 0.45`).
- **Regional Band Probability (`dust_lift`)**:
  - `decomposed_granite`: `0.65` in Sierra (`pct-region-0029`), `0.90` in SoCal Desert (`pct-region-0000`).
  - `gravel`: `0.25`.
  - `granite`, `wood_bridge`, `water_splash`: `0.0` (never kicks dust on rock, bridge timber, or wet creek banks).
- **Grain Color**: Tread base albedo (`#9e876b` Sierra granite sand) lifted `35%` toward white (`LinearColor(0.74, 0.67, 0.58, 0.42)`), roughness `0.92`, soft depth fade `12.0 cm`.

See **`reset/unreal/systems/ue_footstep_surfaces.py`** for the copy-ready UE 5.6 Python script that creates the `UPhysicalMaterial` assets, imports the WAV banks, builds the `USoundCue` assets with non-repeating random + pitch modulator nodes, binds physical materials to `M_Granite`, `M_Terrain`, `M_Wood`, `M_Water`, and exports the frame-exact footstep event ledger.
