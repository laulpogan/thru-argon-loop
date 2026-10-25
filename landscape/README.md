# Hero Creek Procedural Landscape Export for Unreal Engine 5.6 (`pct-region-0029`)

Extracted from the live Godot 4.7.2 `pct-region-0029` scene (**Middle Fork San Joaquin River PCT Crossing**, `37.6538256, -119.0800196`, seed `19980029`, June 29 1998 / `trail_day` 120, `sky_hour` 17.6) combined with `procgen-terrain` (`generated-v2`, 4m USGS 3DEP DEM + 12-iteration conservative thermal/hydraulic erosion) and `procgen-hydrology` (`generation-r4`, carved channel + D8 flow).

---

## 1. Files in `reset/unreal/import/landscape/`

| File | Size | Description |
|---|---|---|
| `heightmap.json` | 9.8 KB | World origin, metres/pixel, min/max height, 16-bit decode equations, UE5 Landscape Actor Scale3D/Location, and Godot Y-up (m) -> UE Z-up (cm) axis conversion formulas. |
| `heightmap_1009.png` / `.raw` (also `heightmap.png` / `.raw`) | 1.05 MB / 2.04 MB | **Primary 1009x1009 16-bit heightmap** (`0.5 m/px`, `504m x 504m` centered on hero anchor `(3049.4802, 2346.6019, 6249.7935)`): live `pct-region-0029` + `procgen-hydrology` carved channel (`max_carve_m = 1.35m`) + `procgen-terrain` high-frequency geomorphic detail. |
| `heightmap_2017.png` / `.raw` | 1.90 MB / 8.14 MB | **Full-tile 2017x2017 16-bit heightmap** (`0.5 m/px`, `1008m x 1008m` centered on hero anchor). |
| `heightmap_bridge_frame_1009.png` / `.raw` | 0.91 MB / 2.04 MB | **Bridge-aligned 1009x1009 16-bit heightmap** (`0.25 m/px`, `252m x 252m`) oriented directly in the `reset/unreal/CAMERAS.json` / `gen.py` coordinate frame (`+X` along creek axis, `+Y_local`/`-Y_ue` along bridge axis). |
| `heightmap_procgen_3dep_1009.png` / `.raw` | 0.92 MB / 2.04 MB | **Pure USGS 3DEP 4m + 12-iter eroded 1009x1009 16-bit heightmap** (`0.5 m/px`, `504m x 504m`) from `reset/procgen-terrain/generated-v2`. |
| `geomorphology_mask_1009.png` | 237 KB | 1009x1009 8-bit RGB terrain splat mask aligned with `heightmap_1009`: `R` = creek bed & wet bank, `G` = PCT trail tread dust, `B` = `procgen-terrain` inferred rock/scree. |
| `geomorphology_mask_bridge_frame_1009.png` | 150 KB | 1009x1009 8-bit RGB terrain splat mask aligned with `heightmap_bridge_frame_1009` (drop-in replacement for `T_TerrainMask.png` in `gen.py` / `ue_main.py`). |
| `creek_spline.json` | 168 KB | 95-point continuous creek spline (`nhd-5e02f9e3f66982ec7e5e-0`, `358.37 m` total length, `width = 2.5 m`, `depth = 0.3976 m`, `flow_speed = 1.1343 m/s` at crossing) + 2 secondary tributary creeks within 400m. |
| `placements.json` & `placements.csv` | 2.49 MB / 526 KB | **1,528 procedural object placements** (`1` wooden footbridge, `138` `ArgonHeroCreek` boulders/ferns/willows/pines, `362` `pct_rock_scatter` cobbles/boulders, `1,027` `pct_vegetation` conifers/logs/foliage/slabs) with transforms in all 3 coordinate frames + wet/dry state (`submerged`, `wet_slick`, `splash_zone`, `dry_dusty`). |
| `trail_spline.json` | 198 KB | High-res `0.5 m` Catmull-Rom hero crossing trail spline (`route-hero-after.json`), canonical `pct-region-0029` route within 600m (`58` points), and `73` recorded 30fps walkthrough keyframes (`1080` frames total). |
| `cameras.json` | 13.5 KB | All 5 still cameras (`hero_low`, `wet_stones`, `trail`, `wide`, `hiker`), `hiker_still`, `walk_clip`, and `time_of_day` cross-checked against `reset/unreal/CAMERAS.json` (`< 1 mm` discrepancy), plus `real_dem_draped` coordinates preserving exact height above real Godot water/ground. |
| `ue_landscape_loader.py` | 2.4 KB | Drop-in Python helper for loading heightmaps, splines, placements, and cameras in `gen.py` or `ue_main.py`. |

---

## 2. Coordinate Frames (All 3 Included in Every File)

Every JSON and CSV row carries coordinates in **three frames** so you can either drop data straight into the existing `gen.py` / `ue_main.py` scene OR import an unrotated UE5 `Landscape`:

1. **`ue_bridge_frame` (Matches `reset/unreal/CAMERAS.json` and `gen.py` / `ue_main.py` directly)**:
   - Origin in Godot `pct-region-0029`: Bridge crossing `(3049.482, 2347.261, 6249.796)` (where bridge deck `2348.281 m` sits at `z_local = +1.02 m` = `+102.0 cm`, and ground at anchor `2346.602 m` sits at `z_local = -0.659 m` = `-65.9 cm`).
   - `+X_local` (`m`) / `+X_ue` (`cm`): Along creek axis `CAX = (0.503, 0, 0.865)`.
   - `+Y_local` (`m`) / `-Y_ue` (`cm`): Along bridge axis `BAX = (0.865, 0, -0.503)` (`Y_ue_cm = -y_local_m * 100.0` matching `AX["sy"] = -1.0` in `ue_main.py`).
   - `+Z_local` (`m`) / `+Z_ue` (`cm`): Up (`Z_ue_cm = (Y_godot_m - 2347.261) * 100.0`).

2. **`ue_anchor_cm` (Canonical Unrotated Godot Y-up metres -> UE Z-up centimetres)**:
   - Origin at hero anchor ground `(3049.4802, 2346.6019, 6249.7935)`:
   - `X_ue_cm = (X_godot_m - 3049.4802) * 100.0` (East)
   - `Y_ue_cm = (Z_godot_m - 6249.7935) * 100.0` (South; left-handed Z-up)
   - `Z_ue_cm = (Y_godot_m - 2346.6019) * 100.0` (Up)

3. **`godot_m` (Raw Godot `pct-region-0029` Local Frame)**:
   - Right-handed Y-up metres `(X_m, Y_m, Z_m)` projected via AEQD from region anchor `(-119.114577, 37.710140)`.

---

## 3. Verified Creek Flow Direction (`CAMERAS.json` Cross-Check)

`reset/unreal/CAMERAS.json` noted `"flow direction unverified"`. We verified the flow direction from both USGS NHD flowline `nhd-5e02f9e3f66982ec7e5e-0` (`pct_region_hydrology.gd`) and D8 DEM accumulation (`procgen-hydrology/flow.json`):
- At the bridge crossing `(3049.48, 6249.79)`, water flows along Godot vector `(0.8651, 0.0021, 0.5016)` (D8 vector `(0.8610, 0.5086)`) at `1.1343 m/s`.
- In `CAMERAS.json` (`ue_bridge_frame`), the flow direction vector is `(+0.8685, +0.4957, +0.0021)` in `local_m` (`(+0.8685, -0.4957, +0.0021)` in `ue_cm`) — i.e., **flowing toward `+X`**.

---

## 4. Quick Usage in Python (`gen.py` / `ue_main.py`)

```python
from ue_landscape_loader import (
    load_heightmap_metres,
    load_creek_spline,
    load_placements,
    load_trail_and_cameras,
)

# 1. Load 1009x1009 heightmap in CAMERAS.json bridge-aligned frame (or 'heightmap_1009' for unrotated):
Z_m, h_meta = load_heightmap_metres("heightmap_bridge_frame_1009")

# 2. Load creek spline points in CAMERAS.json frame:
creek_doc, creek_pts = load_creek_spline("ue_bridge_frame")

# 3. Load the 138 ArgonHeroCreek procedural placements (or all 1,528 placements):
_, hero_items = load_placements(frame="ue_bridge_frame", source_layer="argon_hero_creek")

# 4. Load trail spline and cross-checked cameras:
trail_doc, cameras_doc = load_trail_and_cameras()
```
