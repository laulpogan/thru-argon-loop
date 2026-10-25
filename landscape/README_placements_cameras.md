# Hero Creek Object Placements, Trail Spline & Cameras (`unreal-landscape-export-w3`)

Exported from the live Godot 4.7.2 `pct-region-0029` scene (**Middle Fork San Joaquin River PCT Crossing**, `37.6538256, -119.0800196`, seed `19980029`, June 29 1998, `sky_hour` 17.6), combined with `reset/unreal/CAMERAS.json`, `walkthrough/playop-after/route-hero-after.json`, and `path-hero-after-dense.json`.

---

## 1. Deliverables in `reset/unreal/import/placements-cameras/` (and mirrored in `reset/unreal/import/landscape/`)

| File | Size | Description |
|---|---|---|
| `placements.json` | 7.6 MB | **2,364 procedural placements** across all 7 required categories (`rock`, `cobble`, `tree`, `foliage`, `log`, `bridge`, `trail`) with transforms in all 3 coordinate frames (`ue_bridge_frame`, `ue_anchor_centered`/`ue_anchor_cm`, `godot_transform`/`godot_m`), plus **981 drop-in `meshes`** and top-level keys (`L`, `W`, `water_z0`, `slope`, `deck_z`, `shots`, `hiker_still`, `walk`, `hiker_walk`, `trail`) for direct `ue_main.py` consumption. |
| `placements.csv` | 1.15 MB | Tabular CSV export (`51` columns) of all 2,364 placements with coordinates in all 3 frames, distances to creek centerline/bank/trail, `wetness`, `dust`, `wet_dry_state`, `roughness_target`, `albedo_darken_factor`, and `clearcoat_target`. |
| `placements_ue_spike.json` | 290 KB | Lightweight `ue_main.py` drop-in replacement for `/workspace/unreal/assets/placements.json` (`981` hero corridor meshes + `5` shots + `walk` + `hiker_walk` + `trail`). |
| `cameras.json` | 435 KB | All **5 UE spike still cameras** (`hero_low`, `wet_stones`, `trail`, `wide`, `hiker`) cross-checked against `reset/unreal/CAMERAS.json` (`0.000m` delta), `hiker_still`, **6 Godot `walkthrough.gd` hero views** (`overview`, `detail`, `low`, `wet-cobble`, `riffle`, `wireframe`), `walk_clip`, `ue_seq_walk_keyframes` (60fps), and `playop_after_dense_walk_sampled_15f` (`2,353` frames @ 60fps), with DEM clearance verification (`dem_clearance_check` & `real_dem_draped`). |
| `trail_spline.json` & `trail_spline.csv` | 281 KB / 17 KB | `139`-point Catmull-Rom crossing trail spline (`0.4m` step), `313`-point `0.5m` crossing spline, `10` `route-hero-after.json` waypoints, `58` canonical `pct-region-0029` route points within 600m, and `73` recorded 30fps walkthrough keyframes. |
| `ue_placements_and_cameras.py` | 7.1 KB | Drop-in Python loader and Unreal Engine 5.6 Editor spawner (`load_placements`, `load_cameras`, `load_trail_spline`, `spawn_cameras_in_ue`, `spawn_placements_in_ue`). |

---

## 2. Placement Breakdown (`2,364` Total Instances)

- **By Category**:
  - `tree`: `1,025` (`pinus_contorta_murrayana` Sierra lodgepole pine, `pinus_jeffreyi` Jeffrey pine, `abies_concolor` white fir, `salix_lasiolepis` riparian willow, `platanus_racemosa` sycamore, etc.)
  - `cobble`: `608` (`sierra_granite_cobble`, `sierra_creek_cobble`, `sierra_granite_scree` — including `67` deterministic waterline/riffle cobbles and boulders in the `hero_low` / `wet_stones` camera reach)
  - `foliage`: `375` (`pteridium_aquilinum` bracken/sword fern, `polyhaven_fern_02_a..d`, `polyhaven_grass_medium_01_a..d`, riparian sedges & shrubs)
  - `rock`: `276` (`hero_granite_a/b/c` boulders, `sierra_granite_slab`, `rock_moss_set_01`, `namaqualand_boulder_02`)
  - `log`: `61` (`sierra_fallen_pine`, `sierra_fallen_pine_low`, `snag_granite_pine` deadwood)
  - `trail`: `18` (`trail_tread_dg_bootprint` decomposed granite tread + `granite_rock_water_bar` drainage bars)
  - `bridge`: `1` (`bridge_main_000`, `weathered_wooden_footbridge_sect.glb`, `span_m = 13.5m`, `deck_y = 2348.3049m`)
- **By Surface State (`wet_dry_state`)**:
  - `submerged` (`49`): In-channel cobbles & boulder bases (`bank_offset < -0.15m`, `roughness_target = 0.08..0.10`, `albedo_darken = 0.35..0.40`, `clearcoat = 0.72..0.85`).
  - `wet_slick` (`58`): Capillary waterline & wet bank rocks (`wetness >= 0.60`, `roughness_target = 0.08..0.14`, `albedo_darken = 0.38..0.45`, `clearcoat = 0.55..0.85`).
  - `splash_zone` (`64`): Creek spray margin & bridge timbers (`0.18 <= wetness < 0.60`, `roughness_target = 0.24..0.42`).
  - `dry_dusty` (`2,193`): Upper bank, trail corridor, and forest floor (`roughness_target = 0.74..0.88`, decomposed granite trail dust `dust = 0.55..1.00`).

---

## 3. Coordinate Frame Cross-Check (`CAMERAS.json`)

Every record provides exact coordinates in **three frames**:
1. **`ue_bridge_frame`** (Matches `reset/unreal/CAMERAS.json`, `gen.py`, and `ue_main.py`):
   - Origin in Godot `pct-region-0029`: `(3049.482, 2347.261, 6249.796)` (`z_local = +1.020m` at bridge deck `2348.281m`).
   - `+x_local` along creek axis `CAX = (0.503, 0, 0.865)`, `+y_local` along bridge axis `BAX = (0.865, 0, -0.503)`, `+z_local = Y_godot - 2347.261`.
   - `location_cm = [x_local * 100.0, -y_local * 100.0, z_local * 100.0]` (`AX["sy"] = -1.0`).
2. **`ue_anchor_centered` / `ue_anchor_cm`** (North-aligned UE5 Z-up centimetres centered at hero anchor `(3049.4802, 2346.6019, 6249.7935)`):
   - `location_cm = [(X_godot - 3049.4802)*100.0, (Z_godot - 6249.7935)*100.0, (Y_godot - 2346.6019)*100.0]`.
3. **`godot_transform` / `godot_m`** (Godot `pct-region-0029` Y-up right-handed metres).

| Camera Shot | `local_m` `pos` | `ue.location_cm` | `ue.rotation` `(R, P, Y)` | Focal (mm) | `CAMERAS.json` Delta | Real 64m DEM Clearance |
|---|---|---|---|---|---|---|
| `hero_low` | `[9.0, 4.162, 0.095]` | `[900.0, -416.2, 9.5]` | `(0.0, 4.167, 156.985)` | `22` | `0.0005 m` / `0.0 cm` | `-0.882 m` (`dem_safe_z = 1.427m`) |
| `wet_stones` | `[4.2, 2.094, -0.009]` | `[420.0, -209.4, -0.9]` | `(0.0, -7.835, 134.829)` | `35` | `0.0002 m` / `0.0 cm` | `+0.332 m` (`OK`) |
| `trail` | `[4.5, -13.0, 1.999]` | `[450.0, 1300.0, 199.9]` | `(0.0, -4.162, -109.107)` | `28` | `0.0005 m` / `0.0 cm` | `+0.371 m` (`OK`) |
| `wide` | `[22.0, 12.164, 4.716]` | `[2200.0, -1216.4, 471.6]` | `(0.0, -9.239, 149.498)` | `20` | `0.0006 m` / `0.0 cm` | `+2.060 m` (`OK`) |
| `hiker` | `[-2.2, -5.2, 2.42]` | `[-220.0, 520.0, 242.0]` | `(0.0, -3.576, -59.931)` | `35` | `0.0002 m` / `0.0 cm` | `+1.919 m` (`OK`) |
