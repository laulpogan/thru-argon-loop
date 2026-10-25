# System 1: Trail-Follow & Walkthrough Camera (`trail-follow`)

Ported from THRU Godot 4 sources:
- `godot/scripts/hiker.gd` (`ThruHiker` CharacterBody3D, walk animation speed scaling, slope-adaptive pitch lean, pack bottle pendulum)
- `godot/scripts/trail_camera.gd` (`TrailCamera` gait head-bob/sway, step lag stabilization, speed/vista FOV opening)
- `walkthrough/walkthrough.gd` (PCT polyline lookahead steering, 3rd-person follow boom, ground-clearance clamp, 14s bridge linger orbit)
- `walkthrough/route-hero.json` & `reset/unreal/route/route-hero-after.json` (Middle Fork San Joaquin PCT bridge crossing, region `pct-region-0029`, 11 canonical waypoints)
- `reset/unreal/CAMERAS.json` & `reset/unreal/src-snapshot/src/ue_main.py` (UE 5.6 coordinate mapping and Movie Render Queue `LevelSequence` setup)

---

## 1. Coordinate Frame & Spline Mapping (Godot -> Unreal 5.6)

### 1.1 Regional Godot Frame vs. Unreal Scene-Local Frame
- **Godot Regional Frame (`pct-region-0029`)**: Right-handed, meters, `+X` East, `+Y` Up (elevation m ASL), `+Z` South.
  - Hero bridge anchor (`CAMERAS.json`): `B_godot = (3049.482, 2348.281, 6249.796)` (`gen.py` horizontal reference `BC = (3049.5, 6249.8)`).
  - Bridge deck direction vector in horizontal `(X, Z)` plane: `BAX = (0.865, -0.503)` (unit vector along bridge crossing).
  - Creek channel direction vector (perpendicular to bridge): `CAX = (0.503, 0.865)`.
- **Scene-Local Meter Frame (`local_m`, Z-up)**:
  - Origin `(0, 0, DECK_Z)` is the center of the wooden footbridge over the Middle Fork San Joaquin creek.
  - For any Godot waypoint $P_{\text{godot}} = (X_g, Y_g, Z_g)$:
    $$\Delta X = X_g - 3049.5, \quad \Delta Z = Z_g - 6249.8$$
    $$x_{\text{local}} = \Delta X \cdot 0.503 + \Delta Z \cdot 0.865 \quad (\text{along creek axis, m})$$
    $$y_{\text{local}} = \Delta X \cdot 0.865 - \Delta Z \cdot 0.503 \quad (\text{along bridge axis, m})$$
    $$z_{\text{local}} = \begin{cases} \text{DECK\_Z} & \text{if } |x_{\text{local}}| < 0.8 \text{ and } |y_{\text{local}}| < 7.0 \\ z_{\text{terrain}}(x_{\text{local}}, y_{\text{local}}) & \text{otherwise} \end{cases}$$
- **Unreal Engine World Space (`cm`, Z-up, Left-Handed)**:
  - `Location_UE = unreal.Vector(x_local * 100.0, y_local * 100.0 * sy, z_local * 100.0)` where `sy = AX["sy"]` (`-1.0` when Interchange flips Y, or `+1.0` native).
  - Heading yaw in degrees (`unreal.Rotator(roll=0, pitch=0, yaw=yaw_deg)`):
    $$\text{yaw}_{\text{path}} = \text{atan2}(d_y \cdot s_y, d_x) \cdot \frac{180}{\pi}$$
    $$\text{yaw}_{\text{actor}} = \text{yaw}_{\text{path}} + \text{HIKER\_YAW} \quad (\text{where } \text{HIKER\_YAW} = -90.0^\circ)$$

### 1.2 Canonical Waypoints (`route-hero-after.json`)
| Waypoint # | Godot `(X, Y, Z)` (m) | Local `(x, y)` (m) | Surface Tag | Segment Notes |
|---:|---|---|---|---:|
| 0 | `(3038.0, 2351.0, 6280.0)` | `(20.38, -25.14)` | `PM_DecomposedGranite` | South approach trail |
| 1 | `(3040.5, 2350.2, 6272.0)` | `(14.68, -18.95)` | `PM_DecomposedGranite` | Trail descent |
| 2 | `(3042.0, 2349.4, 6264.0)` | `(8.51, -13.63)` | `PM_DecomposedGranite` | Pine duff / DG tread |
| 3 | `(3042.8, 2348.8, 6258.0)` | `(3.73, -9.92)` | `PM_Gravel` | Bridge south abutment |
| 4 | `(3043.6, 2348.4, 6253.2)` | `(0.00*, -6.81)` | `PM_WoodBridge` | Bridge south entry (`on_bridge`) |
| 5 | `(3046.5, 2348.6, 6251.5)` | `(0.00*, -3.45)` | `PM_WoodBridge` | Bridge south span |
| 6 | `(3049.5, 2348.8, 6249.8)` | `(0.00, 0.00)` | `PM_WoodBridge` | Bridge center (`linger_s = 14s` anchor) |
| 7 | `(3052.5, 2348.6, 6248.1)` | `(0.00*, +3.45)` | `PM_WoodBridge` | Bridge north span |
| 8 | `(3055.3, 2348.4, 6246.4)` | `(0.00*, +6.73)` | `PM_WoodBridge` | Bridge north exit |
| 9 | `(3058.0, 2348.6, 6245.0)` | `(0.12, +9.77)` | `PM_Gravel` | Bridge north abutment |
| 10 | `(3062.0, 2348.8, 6242.0)` | `(-0.46, +14.73)` | `PM_DecomposedGranite` | North trail exit |

*\*Note: For $|y_{\text{local}}| < 7.1\text{ m}$ (`BRIDGE_HALF + 0.3 m`), $x_{\text{local}}$ is clamped to `0.0 m` so the hiker walks straight down the wooden footbridge centerline without clipping handrails or stepping into water.*

---

## 2. Hiker Movement & Walk Cycle Synchronization

### 2.1 Forward Kinematics Measurement of `hiker_male.glb`
Measured directly from `/home/dellpromax/Source/Thru-2/godot/assets/people/quaternius/hiker_male.glb` (`Quaternius CC0 Universal Base Characters`):
- **Rig hierarchy**: `Armature` -> `root` -> `hips` -> `thigh_l`/`thigh_r` -> `shin_l`/`shin_r` -> `foot_l` (node 55) / `foot_r` (node 60).
- **Capsule collider (`hiker.gd:40-44`)**: `UCapsuleComponent` radius `32.0 cm` (`0.32 m`), half-height `90.0 cm` (`height = 1.80 m`), mesh scaled to `HEIGHT_M = 1.78 m`.
- **Facing direction (`hiker.gd:153`)**: Source glTF mesh faces `+Z`. During stance phase (lowest 35% of foot Y height), `foot_l` and `foot_r` translate at `dZ/dt = -0.8987 m/s` relative to root, confirming `+Z` is forward in glTF space. In UE5 after Interchange import, apply `HIKER_YAW = -90.0 deg` so the character faces along the spline velocity vector.
- **`walk` Animation Clip Metrics**:
  - **Clip length ($T_{\text{clip}}$)**: `1.3333 s` (32 frames at 24 fps).
  - **Single step foot excursion ($L_{\text{step}}$)**: `0.6787 m` (`foot_l`: `0.6846 m`, `foot_r`: `0.6728 m`).
  - **Full stride length (2 steps, $L_{\text{stride}}$)**: `1.3575 m`.
  - **Native ground speed at `play_rate = 1.0` ($v_{\text{native}}$)**:
    $$v_{\text{native}} = \frac{2 \cdot L_{\text{step}}}{T_{\text{clip}}} = \frac{1.3575\text{ m}}{1.3333\text{ s}} = 1.0181\text{ m/s}$$
  - **Exact Play Rate Formula (zero foot sliding)**:
    $$\text{PlayRate}(v) = \frac{v}{1.0181\text{ m/s}}$$

| Target Walk Speed $v$ (m/s) | Use Case | Exact `play_rate` (`v / 1.0181`) | Godot `hiker.gd:96` (`v / 1.4`) | Step Frequency (steps/s) |
|---:|---|---:|---:|---:|
| `1.15 m/s` | Current `gen.py` 10s spike walk | **`1.1296`** | `0.821` | `1.694 Hz` |
| `1.25 m/s` | `CAMERAS.json` `walk_clip` | **`1.2278`** | `0.893` | `1.842 Hz` |
| `1.35 m/s` | Mid-range trail pace | **`1.3260`** | `0.964` | `1.989 Hz` |
| **`1.40 m/s`** | **Canonical `route-hero-after.json` pace** | **`1.3751`** | `1.000` | **`2.063 Hz`** |
| `1.50 m/s` | Fast trail pace | **`1.4733`** | `1.071` | `2.210 Hz` |

### 2.2 Velocity-Aligned Steering & Anti-Crab-Walk (`walkthrough.gd:152-158`)
To prevent sideways crab-walking or abrupt snaps at waypoint corners:
1. Advance distance $s(t) = s_0 + \int_0^t v(\tau)\,d\tau$ along the resampled Catmull-Rom spline (`USplineComponent::GetLocationAtDistanceAlongSpline(s * 100.0, ESplineCoordinateSpace::World)`).
2. Query lookahead point at $s_{\text{ahead}} = \min(s + L_{\text{lookahead}}, s_{\text{end}})$ where $L_{\text{lookahead}} = 8.0\text{ m}$ (`steer_lookahead_m = 8.0` in `route-hero-after.json`, or `2.5 m` near bridge entry so the turn onto the bridge centerline aligns cleanly).
3. Smooth horizontal forward direction vector $\mathbf{f}_t$ using exponential decay (`0.08` per frame at 30 fps, equivalent to rate $\lambda = 2.5\text{ s}^{-1}$):
   $$\mathbf{f}_t = \text{ normalize}\!\left(\text{lerp}\!\left(\mathbf{f}_{t-1}, \frac{\mathbf{p}_{\text{ahead},xy} - \mathbf{p}_{t,xy}}{\|\mathbf{p}_{\text{ahead},xy} - \mathbf{p}_{t,xy}\|}, 1 - e^{-2.5 \Delta t}\right)\right)$$
4. Unwrap yaw angles across the $\pm 180^\circ$ branch cut before writing `MovieSceneFloatChannel` keys:
   ```python
   while yaw - prev_yaw > 180.0: yaw -= 360.0
   while yaw - prev_yaw < -180.0: yaw += 360.0
   ```

### 2.3 Secondary Gait Physics (`hiker.gd:85-124, 267-288`)
- **Slope-Adaptive Pitch Lean (`_step_slope_gait`)**:
  - Constants: `SLOPE_LEAN_CAP = 0.22 rad` (`12.6 deg`), pack forward lean `LOADED_LEAN = 0.09 rad` (`5.16 deg`).
  - Given ground normal $\mathbf{n}$ and horizontal forward unit vector $\mathbf{f}$:
    $$\theta_{\text{slope}} = \text{clamp}\!\left(\text{atan2}(\mathbf{n} \cdot \mathbf{f},\, n_z) \cdot 0.55,\; -0.22,\; +0.22\right)\text{ rad}$$
  - Rate-limited by `1.5 rad/s` (`85.9 deg/s`), added to `LoadedLean` (`+5.16 deg` forward pitch when wearing the 1990s pack).
- **Critically-Damped Water Bottle Pendulum (`_step_bottle`)**:
  - Attached to `spine_02` socket at local offset `(0.28, 1.25, 0.28) m`.
  - Constants: `BOTTLE_SWING_RAD = 0.22 rad` (`12.6 deg`), damping $\omega_0 = 10.0\text{ s}^{-1}$, velocity filter $\alpha = 1 - e^{-12 \Delta t}$.
  - Closed-form critical damping update per frame $\Delta t$:
    $$\mathbf{v}_{\text{filt}} = \text{lerp}(\mathbf{v}_{\text{filt}}, \mathbf{v}_{\text{local}}, 1 - e^{-12\Delta t})$$
    $$\boldsymbol{\theta}_{\text{target}} = \text{limit\_length}\!\left((v_{\text{filt},z}, -v_{\text{filt},x}) \cdot 0.025,\; 0.22\right)$$
    $$\boldsymbol{\delta} = \boldsymbol{\theta} - \boldsymbol{\theta}_{\text{target}}, \quad \mathbf{k} = (\dot{\boldsymbol{\theta}} + 10\boldsymbol{\delta})\Delta t, \quad d = e^{-10\Delta t}$$
    $$\boldsymbol{\theta}^{+} = \boldsymbol{\theta}_{\text{target}} + (\boldsymbol{\delta} + \mathbf{k})d, \quad \dot{\boldsymbol{\theta}}^{+} = (\dot{\boldsymbol{\theta}} - 10\mathbf{k})d$$

---

## 3. Walkthrough Camera Follow & Bridge Linger (`walkthrough.gd` + `trail_camera.gd`)

### 3.1 Camera Parameters (`route-hero-after.json` & `CAMERAS.json`)
| Parameter | `route-hero-after.json` Value | `CAMERAS.json` (`walk_clip`) | Unreal `UCineCameraComponent` Equivalent |
|---|---|---|---|
| **Filmback** | 16:9 aspect | `36.0 x 20.25 mm` | `Filmback.SensorWidth = 36.0`, `SensorHeight = 20.25` |
| **FOV / Focal Length** | `fov = 58 deg` (vertical) | `focal_mm = 24 mm` (`vfov = 45.75 deg`, `hfov = 73.74 deg`) | `CurrentFocalLength = 21.0 mm` (for 58° vFOV) or `24.0 mm` (hero cinematic) |
| **Aperture** | — | `f/5.6` | `CurrentAperture = 5.6`, `ManualFocusDistance = dist(cam, target) * 100` |
| **Follow Boom Back** | `back_m = 3.8 m` | `3.8 m` behind hiker | `-fwd * 380.0 cm` |
| **Follow Boom Side** | `0.0 m` (or `1.3 m` shoulder offset) | `1.3 m` to the right | `+right * 130.0 cm` (avoids hiker pack blocking center creek view) |
| **Follow Boom Up** | `up_m = 1.6 m` | `1.6 m` up | `+Z * 160.0 cm`, clamped to `max(z_hiker, z_terrain(cam_xy)) + 160.0 cm` |
| **Look-Ahead Target** | `look_ahead_m = 8.0 m`, `look_up_m = 0.9 m` | `8.0 m` ahead, `0.9 m` up | `pos_hiker + fwd * 800.0 cm + Z * 90.0 cm` |
| **Position/Target Smoothing** | `smooth = 0.06` (`lerp(..., 0.18)` @ 30fps) | Smooth spline | Exponential lag $\alpha = 1 - e^{-5.9 \Delta t}$ (`CameraLagSpeed = 5.9`) |
| **Linger Duration** | `linger_s = 14.0 s` (after `22.0 s` walk) | Optional at bridge center | Hiker stops on bridge (`idle` anim, `play_rate = 1.0`), camera orbits |
| **Linger Orbit** | `linger_orbit_deg = 40.0 deg`, `linger_rise_m = 1.2 m`, `linger_look_m = 7.0 m` | — | Over 14s, boom rotates $+40^\circ$ around $+Z$, rises $+120\text{ cm}$, target eases to `hiker + fwd * 700 cm + Z * 60 cm` |

### 3.2 First/Third-Person Gait Overlay (`trail_camera.gd:26-109`)
- **Gait Phase**: $\phi(t) = d_{\text{walked}}(t) \times 6.0\text{ rad/m}$ (`GAIT_RADIANS_PER_M = 6.0`).
- **Vertical Bob**: $z_{\text{bob}} = \sin(2\phi) \times 1.9\text{ cm} \times \text{gait}$ (`BOB_M = 0.019 m`).
- **Lateral Sway**: $y_{\text{sway}} = \sin(\phi) \times 1.3\text{ cm} \times \text{gait}$ (`SWAY_M = 0.013 m`).
- **Step Lag Stabilization**: When climbing steps $< 60\text{ cm}$ (`STEP_LIMIT_M = 0.60`), vertical offset lags behind by $\tau = 0.10\text{ s}$ (`SETTLE_SECONDS = 0.10`), clamped to $\pm 25\text{ cm}$ (`LAG_LIMIT_M = 0.25`).
- **Vista Reveal**: Every `0.15 s` (`PROBE_SECONDS`), cast a ray `300 m` ahead dropping `12 m` (`PROBE_REACH_M = 300`, `PROBE_DROP_M = 12`). Positive increase in unobstructed fraction adds to `reveal` (decaying with $\tau = 2.2\text{ s}$), lifting eye by $+9.0\text{ cm} \times \text{reveal}$ and widening FOV by $+4.5^\circ \times \text{reveal}$.

---

## 4. Unreal Engine 5.6 Implementation Architecture (Blueprint / C++)

### 4.1 Actor & Component Hierarchy
- **`AThruTrailSplineActor` (`AActor`)**:
  - `USplineComponent* TrailSpline`: Populated from `route-hero-after.json` waypoints converted to UE local cm (`ESplinePointType::Curve`).
  - `USplineComponent* CreekSpline`: Populated along `y = center(x)` for spatial audio and waterline queries.
- **`AThruHikerCharacter` (`ACharacter` or `ASkeletalMeshActor` in Sequencer)**:
  - `USkeletalMeshComponent* Mesh`: `/Game/Pack/hiker_male` with `RelativeRotation = (0, -90, 0)` and `AnimSequence` `/Game/Pack/hiker_male/walk` (`PlayRate = SpeedMps / 1.0181`).
  - `UStaticMeshComponent* PackMesh`: Attached to `spine_02` socket at `(0, 25, 118) cm`.
  - `USceneComponent* BottlePivot` -> `UStaticMeshComponent* BottleMesh`: Driven by critical-damped pendulum (`_step_bottle`).
  - `USpringArmComponent* FollowBoom`: `TargetArmLength = 380.0f`, `SocketOffset = FVector(0.0f, 130.0f, 160.0f)`, `bEnableCameraLag = true`, `CameraLagSpeed = 5.9f`.
  - `UCineCameraComponent* WalkthroughCamera`: `Filmback = 36x20.25mm`, `CurrentFocalLength = 24.0f`, `CurrentAperture = 5.6f`.

### 4.2 Sequencer (`ULevelSequence`) Direct Injection for MRQ Offscreen Render
Because `thru-unreal-1` renders via Movie Render Queue (`MoviePipelinePIEExecutor`), the most deterministic zero-jitter path is baking the spline evaluation, velocity-aligned yaw, `play_rate`-switched `walk`/`idle` animation sections, and smoothed camera follow + linger orbit directly into `/Game/Cine/SeqWalk` via `ue_trail_follow.py`.

See **`reset/unreal/systems/ue_trail_follow.py`** for the complete, copy-ready Python implementation.
