# System 2: Spatial Audio Ambience, Creek Spline, Birdsong, Pine Wind & Lyria Score Ducking (`audio-ambience`)

Ported from THRU Godot 4 sources & audio lane contracts:
- `godot/scripts/trail_ambience.gd` (Creek polyline nearest-point emitter, `water_reach_m`, `water_level_at`, 18 m/s emitter slew, 16-sample terrain sightline occlusion, logarithmic octave LPF `20 kHz -> 650 Hz`, 70 m ring exposure probe, bimodal `bird_activity(hour)`)
- `godot/scripts/trail_audio.gd` (`AmbienceWater` bus, zone crossfades, ecology & wind beds)
- `godot/scripts/terrain_reverb.gd` (Multi-ring canyon enclosure probe, `343 m/s` wall return predelay, `Reverb` bus)
- `reset/audiomix/MUSIC-CONTRACT.md` & `reset/audiomix/OFFLINE_MIX.md` (Lyria score dry routing, water proximity ducking `8..50 m -> -3..0 dB`, foreground sidechain `-9 dB` `150 ms / 1.2 s`, footstep motion intensity `0.65`, `-16.0 LUFS` / `-1.4 dBTP` loudness target, wind/creek `120 Hz - 4 kHz` anti-masking EQ)

---

## 1. WAV Assets to Import into Unreal (`/Game/Audio/`)

All source WAV files reside on Dell under `/home/dellpromax/cs-audit/gemini-hackathon/reset/audiomix/masters/` and `/home/dellpromax/cs-audit/gemini-hackathon/audio/masters/` (48 kHz PCM WAV, loop-verified and loudness-audited).

| UE Asset Name | Dell Source Path (`~/cs-audit/gemini-hackathon/...`) | Role / Submix | Format / Loop | License & Attribution |
|---|---|---|---|---|
| `SW_Creek_Near` | `reset/audiomix/masters/creek_near.wav` | Creek spline close bed (`< 35 m`) -> `Submix_AmbienceWater` | 48 kHz Stereo, Loop | **CC-BY-3.0** — kurt, *"Stream Sounds"* (`stream1_kurt`), OpenGameArt |
| `SW_Creek_Far` | `reset/audiomix/masters/creek_far.wav` | Creek spline wide bed (`0..162 m`) -> `Submix_AmbienceWater` | 48 kHz Stereo, Loop | **CC-BY-3.0** — kurt, *"Stream Sounds"* (`stream3_kurt`), OpenGameArt |
| `SW_Creek_Medium` | `audio/masters/ambience/creek_medium.wav` | Creek riffle bed under bridge -> `Submix_AmbienceWater` | 48 kHz Stereo, Loop | **CC-BY-3.0** — kurt, *"Stream Sounds"*, OpenGameArt |
| `SW_Whitewater_Rocks` | `audio/masters/ambience/whitewater_rocks.wav` | Rapid/cascade spot emitter (`turbulence > 0`) -> `Submix_AmbienceWater` | 48 kHz Stereo, Loop | **CC-BY-3.0** — kurt, OpenGameArt |
| `SW_Sierra_Alpine_Dusk` | `audio/masters/ambience/Sierra_alpine_dusk.wav` | Golden-hour open air base bed -> `Submix_TerrainReverb` | 48 kHz Stereo, Loop | **THRU Original** (procedural ambience, public video clear) |
| `SW_Wind_Pines_Soft` | `reset/audiomix/masters/wind_pines_soft.wav` | Canopy breeze (`wind_zone < 0.35`) -> `Submix_AmbienceWind` | 48 kHz Stereo, Loop | **CC0-1.0** (`field_wind_pines_81797`) |
| `SW_Wind_Pines_Medium` | `reset/audiomix/masters/wind_pines_medium.wav` | Montane pine wind (`0.25..0.70`) -> `Submix_AmbienceWind` | 48 kHz Stereo, Loop | **CC0-1.0** (`field_wind_pines_843927`) |
| `SW_Wind_Pines_Strong` | `reset/audiomix/masters/wind_pines_strong.wav` | Exposed ridge gust (`> 0.55`) -> `Submix_AmbienceWind` | 48 kHz Stereo, Loop | **CC0-1.0** (`field_forest_wind_520540`) |
| `SW_Bird_Chickadee_A` | `reset/audiomix/masters/mountain_chickadee_1583116.wav` | 3D canopy bird call (Sierra conifer) -> `Submix_TerrainReverb` | 48 kHz Mono, One-Shot | **CC0-1.0** (iNaturalist 1583116, blind-verified clean) |
| `SW_Bird_Chickadee_B` | `audio/masters/ambience/mountain_chickadee_2127131.wav` | 3D canopy bird call (Sierra conifer) -> `Submix_TerrainReverb` | 48 kHz Mono, One-Shot | **CC0-1.0** (iNaturalist 2127131, blind-verified clean) |
| `SW_Bird_CanyonWren` | `reset/audiomix/masters/canyon_wren_1320386.wav` | 3D granite wall bird call -> `Submix_TerrainReverb` | 48 kHz Mono, One-Shot | **CC0-1.0** (iNaturalist 1320386, descending cascade phrase) |
| `SW_Bird_HermitThrush` | `reset/audio-birds/recorded/hermit_thrush_241027.wav` | 3D dusk conifer bird call -> `Submix_TerrainReverb` | 48 kHz Mono, One-Shot | **CC0-1.0** (Xeno-Canto / iNaturalist 241027) |
| `SW_Insects_Cricket` | `reset/audiomix/masters/insects_western_cricket.wav` | Dusk riparian insect layer -> `Submix_TerrainReverb` | 48 kHz Stereo, Loop | **CC0-1.0** (`western_cricket_794296`) |
| `SW_Music_Sierra_Conifer`| `reset/audiomix/masters/music_sierra_conifer.wav` | Hero golden-hour Lyria score -> `Submix_MusicDry` (`Master`) | 48 kHz Stereo, Finite | **THRU Original** (`lyria-3.5` generated for THRU) |
| `SW_Music_Creeks_Bed` | `audio/masters/music/creeks_bed.wav` | Synchronized low spectral score bed -> `Submix_MusicDry` | 48 kHz Stereo, Loop | **THRU Original** (`lyria-3.5`) |
| `SW_Music_Creeks_Melody`| `audio/masters/music/creeks_melody.wav` | Synchronized upper motion layer -> `Submix_MusicDry` | 48 kHz Stereo, Loop | **THRU Original** (`lyria-3.5`) |

> **Quality Gate Note (`audiomix/HANDOFF.md`)**: Do **not** use `stellers_jay_2191937.wav` un-trimmed (contains distant human murmur at 30s in raw source). Use `mountain_chickadee_1583116.wav`, `mountain_chickadee_2127131.wav`, `canyon_wren_1320386.wav`, and `hermit_thrush_241027.wav` at original pitch `1.0`.

---

## 2. Creek Near/Far Spatialization & Terrain Occlusion (`trail_ambience.gd`)

### 2.1 Closest-Point Follower on Creek Spline (`_closest_on_run`, ` _place`)
Instead of placing dozens of overlapping point emitters that cause comb filtering, THRU uses a single sliding `AAmbientSound` (or dual Near/Far `UAudioComponent` pair) that tracks the closest point $\mathbf{p}_{\text{water}}$ on the `USplineComponent` representing the Middle Fork San Joaquin channel (`y = center(x)`):
1. **Closest Spline Point**:
   $$\mathbf{p}_{\text{water}} = \text{CreekSpline}\to\text{FindLocationClosestToWorldLocation}(\mathbf{p}_{\text{hiker}}, \text{ESplineCoordinateSpace::World})$$
   $$d_{\text{span}} = \|\mathbf{p}_{\text{hiker},xy} - \mathbf{p}_{\text{water},xy}\|\quad(\text{horizontal ground distance in meters})$$
2. **Anti-Click Slew Limiter (`trail_ambience.gd:87-88, 515-524`)**:
   - `EMITTER_SLEW_MPS = 18.0 m/s` (`1800 cm/s`), `EMITTER_JUMP_M = 60.0 m` (`6000 cm`).
   - If the emitter is silent or $\|\mathbf{p}_{\text{emitter}} - \mathbf{p}_{\text{water}}\| > 60\text{ m}$, snap directly to $\mathbf{p}_{\text{water}}$; otherwise slew:
     $$\mathbf{p}_{\text{emitter}}^{+} = \text{FMath::VInterpConstantTo}(\mathbf{p}_{\text{emitter}}, \mathbf{p}_{\text{water}}, \Delta t, 1800.0)$$

### 2.2 Reach, Distance Gain & Near/Far Crossfade (`trail_ambience.gd:349-358`, `COVERAGE.md`)
- **Reach Distance ($R_{\text{water}}$)**:
  $$R_{\text{water}}(\text{flow}_{\text{mps}}) = 45.0 + 165.0 \cdot \text{clamp}\!\left(\frac{\text{flow}_{\text{mps}}}{1.2},\, 0.0,\, 1.0\right)\text{ m}$$
  For the Middle Fork San Joaquin crossing (`flow_mps = 0.85 m/s`), $R_{\text{water}} = 161.88\text{ m}$.
- **Open Distance Level ($L_{\text{open}}$)**:
  $$L_{\text{open}}(d_{\text{span}}) = \begin{cases} \left(1 - \frac{d_{\text{span}}}{R_{\text{water}}}\right)^{1.6} \cdot \text{clamp}(0.4 + 0.5 \cdot \text{flow}_{\text{mps}},\, 0, 1) & d_{\text{span}} < R_{\text{water}} \\ 0 & d_{\text{span}} \ge R_{\text{water}} \end{cases}$$
- **Near / Far Layer Crossfade (`0..35 m`)**:
  - `SW_Creek_Near` captures close splash, bubble, and riffle transients (`< 35 m`, peaking when crossing the bridge at $d_{\text{span}} \approx 0\text{ m}$).
  - `SW_Creek_Far` captures wide canyon wash (`0..162 m`).
  $$w_{\text{near}}(d_{\text{span}}) = \text{clamp}\!\left(1.0 - \frac{d_{\text{span}}}{35.0},\, 0.0,\, 1.0\right)^{1.2}, \qquad w_{\text{far}}(d_{\text{span}}) = 1.0 - 0.55\,w_{\text{near}}(d_{\text{span}})$$
  $$G_{\text{near}} = 0.50 \cdot L_{\text{occluded}} \cdot w_{\text{near}}, \qquad G_{\text{far}} = 0.50 \cdot L_{\text{occluded}} \cdot w_{\text{far}}$$
- **Anti-Masking Low-Pass Filter (`audiomix/HANDOFF.md`)**:
  - Apply a gentle `4000 Hz` 1-pole roll-off (`-6 dB/oct`) or `-8 dB` trim when mixing against Lyria acoustic guitar so high-frequency water hiss never masks the score.

### 2.3 Terrain Sightline Occlusion & Logarithmic Low-Pass Filter (`trail_ambience.gd:556-604`)
Every `0.25 s` (`REFRESH_SECONDS`), march `OCCLUSION_SAMPLES = 16` points along the 2D segment from hiker ear ($z_{\text{ear}} = z_{\text{ground}} + 1.6\text{ m}$) to $\mathbf{p}_{\text{water}}$:
1. Measure maximum terrain ridge rise above the straight sightline:
   $$\text{rise}_{\text{m}} = \max_{k=1..15}\!\left(0,\; z_{\text{terrain}}\!\left(\text{lerp}(\mathbf{p}_{\text{ear},xy}, \mathbf{p}_{\text{water},xy}, k/16)\right) - \text{lerp}(z_{\text{ear}}, z_{\text{water}}, k/16)\right)$$
2. Compute occlusion fraction (`OCCLUSION_FULL_RISE_M = 12.0 m`, `OCCLUDED_GAIN = 0.30`):
   $$b = \text{clamp}\!\left(\frac{\text{rise}_{\text{m}}}{12.0},\; 0.0,\; 1.0\right), \qquad L_{\text{occluded}} = L_{\text{open}} \cdot \text{lerp}(1.0,\, 0.30,\, b)$$
3. Slewed logarithmic octave Low-Pass Cutoff (`OPEN_CUTOFF_HZ = 20000 Hz`, `MUFFLED_CUTOFF_HZ = 650 Hz`, `MUFFLE_RATE = 0.8 /s`):
   $$m(t) = \text{move\_toward}(m(t-\Delta t),\, b,\, 0.8\,\Delta t), \qquad f_{\text{cutoff}}(m) = 20000.0 \times \left(\frac{650.0}{20000.0}\right)^{m}\text{ Hz}$$

---

## 3. Wind in Pines, Sierra Birdsong & Terrain Reverb

### 3.1 Topographic Exposure & Wind in Pines (`trail_ambience.gd:328-333, 691-709`)
- Sample `EXPOSURE_SAMPLES = 8` compass points on a ring of radius `EXPOSURE_RADIUS_M = 70.0 m`:
  $$\text{exposure} = \text{clamp}\!\left(0.5 + 0.5 \cdot \frac{z_{\text{here}} - \frac{1}{8}\sum_{i=0}^7 z_{\text{ring},i}}{30.0},\; 0.0,\; 1.0\right)$$
- For Sierra montane conifer (`form = "conifer_montane"`, `sheltered = 1.0`):
  $$\text{wind\_level} = \text{clamp}(0.12 + 0.88 \cdot \text{exposure},\, 0, 1) \cdot \text{lerp}(1.0,\, 0.4,\, \text{sheltered})$$
  $$\text{canopy\_level} = \text{sheltered} \cdot \text{clamp}(0.30 + 0.70 \cdot \text{exposure},\, 0, 1)$$
- **Mandatory EQ on `Submix_AmbienceWind`**: Band-limit with **High-Pass `120 Hz`** and **Low-Pass `4000 Hz`** at **`-8 dB` trim** (`audiomix/HANDOFF.md`) so pine needles sigh warmly without broadband white-noise harshness.

### 3.2 Sierra Birdsong (`trail_ambience.gd:364-369`)
- **Diurnal Curve**:
  $$\text{birds}(h) = \text{clamp}\!\left(\max\!\left(e^{-((h - 6.0)/1.7)^2},\; 0.75\,e^{-((h - 18.5)/1.5)^2},\; 0.22\cdot\mathbf{1}_{[7.0, 17.5]}(h)\right),\, 0, 1\right)$$
  At hero golden hour (`sky_hour = 17.6`), $\text{birds}(17.6) = 0.524$.
- **Spatial One-Shot Scheduler**:
  - Do **not** layer dense continuous bird loops over one another.
  - Trigger individual 3D one-shot calls (`SW_Bird_Chickadee_A`, `SW_Bird_Chickadee_B`, `SW_Bird_CanyonWren`, `SW_Bird_HermitThrush`) every `5.0..9.0 s` at canopy positions $(r \in [14, 35]\text{ m}, \theta \in [0, 2\pi), z \in [5, 14]\text{ m})$ with shuffled non-repeating selection and stereo pan $\in [-0.65, +0.65]$.

### 3.3 Terrain Reverb (`terrain_reverb.gd`)
- Sample 3 concentric rings (`60 m`, `140 m`, `240 m`) to compute horizon `enclosure` $\in [0, 1]$ and nearest canyon wall distance $R_{\text{wall}} \in [8, 260]\text{ m}$.
- Predelay (`speed_of_sound = 343.0 m/s`):
  $$t_{\text{predelay}} = \min\!\left(260.0\text{ ms},\; \frac{2000.0 \cdot R_{\text{wall}}}{343.0}\right)$$
- Configure `USubmixEffectReverbPreset` on `Submix_TerrainReverb`:
  - `DecayTime = lerp(0.65, 2.10, enclosure^0.8)` (at Sierra creek canyon `enclosure = 0.48`, `DecayTime = 1.45 s`).
  - `PreDelay = 52.0 ms` ($R_{\text{wall}} \approx 9\text{ m}$ canyon banks).
  - `HighFrequencyDamping = lerp(0.30, 0.45, enclosure^0.8) = 0.38`.
  - `WetLevel = lerp(0.06, 0.24, enclosure^0.8) = 0.16`, `DryLevel = 0.92`.

---

## 4. Lyria Score & Sidechain Ducking (`MUSIC-CONTRACT.md`)

1. **Routing**: `Submix_MusicDry` routes directly to `Master` (**dry**, never into `Submix_TerrainReverb`).
2. **Synchronized Playback (`AudioStreamSynchronized` -> `UQuartzClockHandle` / Dual `UAudioComponent`)**:
   - Start `SW_Music_Creeks_Bed` + `SW_Music_Creeks_Melody` (or `SW_Music_Sierra_Conifer`) at frame 0 with sample-accurate phase lock.
   - Base nominal gain: `-7.0 dB` (`+3.0 dB` corrective lift = `-4.0 dB` active level during walkthrough so fingerstyle guitar/cello sits clearly above the `-8 dB` trimmed creek/wind stems).
3. **Water Proximity Ducking (`8..50 m -> -3..0 dB`)**:
   $$G_{\text{water\_duck, dB}}(d_{\text{span}}) = -3.0 \times \text{clamp}\!\left(1.0 - \frac{d_{\text{span}} - 8.0}{50.0 - 8.0},\; 0.0,\; 1.0\right)\text{ dB}$$
   As the hiker walks onto the bridge ($d_{\text{span}} < 8\text{ m}$), the score ducks gently by `-3.0 dB` to let the Middle Fork San Joaquin riffles breathe, without disappearing.
4. **Foreground Cue Sidechain (`-9.0 dB`)**:
   - `USubmixEffectDynamicsProcessorPreset` keyed from `Submix_ForegroundCues` (or envelope follower): `AttackTime = 150 ms`, `ReleaseTime = 1200 ms`, `Reduction = -9.0 dB`.
5. **Footstep Motion Intensity**:
   - Each footfall sets `motion_target = 0.65` for `1.0 s`, smoothing upper-band `SW_Music_Creeks_Melody` gain over a `4.0 s` time constant.

---

## 5. Loudness Standard (`-16.0 LUFS` Integrated / `-1.4 dBTP` True Peak)

All rendered walkthrough audio (`walk.mp4` mux and standalone `.wav` deliverables) must meet EBU R128 / YouTube broadcast target:
- **Integrated Loudness ($I$)**: **`-16.0 LUFS`** ($\pm 0.2\text{ LU}$)
- **True PeakMax ($TP$)**: **`<= -1.4 dBTP`**
- **Loudness Range ($LRA$)**: `4.0 .. 9.0 LU`

See **`reset/unreal/systems/ue_audio_ambience.py`** for the complete UE 5.6 Python setup + offline `-16.0 LUFS` frame-accurate stem mixer.
