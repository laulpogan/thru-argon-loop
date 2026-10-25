# Creek Spline & Wooden Trail Bridge Export (`unreal-landscape-export-w2`)

Exported from live Godot 4.7.2 (`pct_region_hydrology.gd`, `pct_trail_bridges.gd`, `argon_hero_creek.gd`) and `procgen-hydrology` (`generation-r4/pct-region-0029/flow.json`) for the Middle Fork San Joaquin River PCT crossing (`pct-region-0029`, `37.6538256, -119.0800196`, seed `19980029`, June 29 1998, `sky_hour` 17.6).

---

## 1. Key Findings & Coordinate Verification (Resolving `CAMERAS.json` Note)

`reset/unreal/CAMERAS.json` noted:
> *"Godot mapping is approximate: bridge centre = hero anchor local (3049.482,2348.281,6249.796) at deck height, bridge axis along route-hero-after bridge segment direction (0.865,0,-0.503), creek axis perpendicular (0.503,0,0.865); flow direction unverified."*

Live Godot scene extraction confirms:
1. **Exact Bridge Anchor**:
   - Godot local bridge deck center: `(3049.4802, 2348.3049, 6249.7935)` m (`ground_y = 2346.6019 m`, deck lift above center ground = `1.7030 m`).
   - Bridge span axis (`basis.x`): `(0.8671, 0.0292, -0.4973)` (horizontal unit direction `(0.8675, -0.4975)`, matching `BAX = (0.865, -0.503)` within `0.35°`).
   - Bridge cross axis (`basis.z`): `(0.4975, 0.0, 0.8675)` (matching `CAX = (0.503, 0.865)` within `0.35°`).
2. **Exact Creek Crossing & Flow Direction**:
   - The primary NHD flowline `nhd-5e02f9e3f66982ec7e5e-0` (`Middle Fork San Joaquin River`) passes **0.001 m (1 mm)** horizontally from the bridge center between sample `69` `(3047.350, 2346.792, 6248.558)` and sample `70` `(3050.628, 2346.800, 6250.459)`.
   - **Flow Direction in Godot `(X, Y, Z)`**: `(0.8650, 0.0021, 0.5018)` (flowing ESE/SE down-canyon from upstream elevation `2355.3 m` through `2346.6 m` at the bridge to `2339.4 m` downstream).
   - **Flow Direction in `CAMERAS.json` / `gen.py` `local_m` `(x_local, y_local, z_local)`**: `(+0.8692, +0.4945, +0.0021)`.
     - Flow runs in the **`+x_local` direction** (from `-x_local` upstream toward `+x_local` downstream, matching `gen.py`'s downhill slope `-X * P["slope"]`).
     - The river crosses the bridge at a **`60.1°` angle** (`across = sin(60.1°) = 0.8668`, `30°` skew from perpendicular), which is why Godot sizes the crossing span to `span_m = 13.5 m`.
   - **Continuous 3-Reach Corridor**:
     - `nhd-5e02f9e3f66982ec7e5e-0` (88 pts, upstream & bridge crossing) -> reversed `nhd-721538ecd1f36ffcf697-0` (21 pts, middle connector) -> `nhd-6e160a5a8f3f01008ed2-0` (29 pts, downstream reach) form a single continuous 138-vertex river spline.

---

## 2. Coordinate Frames Provided in Every Record

Every point in `creek_spline.json`, `creek_spline.csv`, and `bridge.json` includes coordinates in all four frames:

| Frame Key | Units & Handedness | Definition |
|---|---|---|
| `godot_local` / `godot_water_pos_m` | Metres, Right-Handed, `+Y` Up (`+X` East, `+Z` South) | Native Godot `pct-region-0029` local coordinates. Anchor ground = `(3049.4802, 2346.6019, 6249.7935)`. |
| `local_m` | Metres, Z-Up (`+x` along `CAX`, `+y` along `BAX`, `+z` Up) | `CAMERAS.json` & `gen.py` scene-local frame. Bridge center deck is `(0, 0, 1.02)`; `z_local = Y_godot - 2347.261`. |
| `ue_bridge_aligned_cm` | Centimetres, Left-Handed, `+Z` Up (`sy = -1.0`) | Direct `CAMERAS.json` & `ue_main.py` UE 5.6 World Space: `[x_local * 100, -y_local * 100, z_local * 100]`. |
| `ue_anchor_centered_cm` | Centimetres, Left-Handed, `+Z` Up (`+X` East, `+Y` South) | Cardinal UE 5.6 Landscape frame centered at anchor ground: `[(X_g - 3049.4802)*100, (Z_g - 6249.7935)*100, (Y_g - 2346.6019)*100]`. |

---

## 3. File Inventory (`reset/unreal/import/creek-spline-and-bridge/`)

| File | Description |
|---|---|
| `creek_spline.json` | Complete hydrology export: `hero_reach_65m_points` (35 pts), `primary_feature_points` (88 pts), `continuous_corridor_points` (138 pts), `resampled_1m_points` (319 pts at 1.0 m spacing from `-160 m` to `+160 m`), `rapids_and_spray_points` (38 rapid/mist emitters with turbulence), hydraulic parameters (`width_m = 2.5`, `hero_crossing_reach_width_m = 7.5`, `depth_m = 0.3976`, `flow_mps = 1.134`), and `gen_py_synthetic_channel_comparison`. |
| `creek_spline.csv` | Flat 138-row CSV table of the continuous river spline in all coordinate frames for UE5 DataTable import. |
| `bridge.json` | Complete specification of `TrailSpan_BridgeWood_nhd-5e02f9e3f66982ec7e5e-0_1462937` (`span_m = 13.5 m`, total length with approach ramps `16.0059 m`, walkable deck width `1.25 m`, 67 planks, 3 stringers, 1 mid-span timber bent, 2 dry-laid granite rock cribs, 2 approach ramps, 3 collision boxes, and exact transforms in all frames). |
| `bridge_mesh.glb` | Full 4-part Godot bridge (`OwnedTimberBridge`, `Part_wood`, `Part_stone`, `Part_rail`) pre-transformed into `gen.py` / `ue_main.py` coordinates (`DECK_Z = 1.02 m` baked). Drop-in replacement for `assets/bridge.glb` at `(0, 0, 0)`. |
| `bridge_godot_exact.glb` | Full 4-part Godot bridge in structure-local frame (`+X` along span, `+Y` up, `+Z` across width, `y = 0` at deck top). |
| `weathered_wooden_footbridge_sect.glb` | Original 961 KB Godot timber footbridge GLB asset (`scale = [3.2419, 1.0, 0.8065]`, `position.y = -0.4004 m`). |
| `water_ribbon_mesh.glb` | 3D draped water surface ribbon meshes (`CreekWaterRibbon_2p5m` and `CreekWaterRibbon_7p5m_HeroCrossing`) along the 1 m resampled spline with flow UVs (`6.0 m/UV`) and vertex colors (`R` = bank foam, `G` = water depth / 6 m, `B` = flow speed, `A` = opacity). |
| `wet_bank_mesh.glb` | 3D wet-bank margin mesh (`4.25 m` total width, `0.875 m` soak margin per bank) along the 1 m resampled spline. |
| `textures/` | CC0 bridge PBR textures (`wood_planks_grey_diff.jpg`, `wood_planks_grey_nor_gl.jpg`, `wood_planks_grey_nor_dx.png` [DirectX flipped-G for UE5], `wood_planks_grey_rough.jpg`, `rusty_metal_02_*`, `CREDITS.md`). |
| `ue_creek_and_bridge.py` | Drop-in UE 5.6 Python loader & spatial query helper (`CreekAndBridgeQuery`, `spawn_creek_spline_actor`, `spawn_bridge_and_water_meshes`). |

---

## 4. Quick Integration in `ue_main.py` / `gen.py`

```python
import sys
sys.path.append("/workspace/unreal/import/creek-spline-and-bridge")
import ue_creek_and_bridge as cb

# 1. Spawn USplineComponent actor for the creek in CAMERAS.json bridge_aligned frame:
creek_actor, creek_spline = cb.spawn_creek_spline_actor(frame="bridge_aligned")

# 2. Spawn the 4-part Godot wooden footbridge + NHD water ribbon with your UE materials:
cb.spawn_bridge_and_water_meshes(
    frame="bridge_aligned",
    water_material=MW,
    wood_material=MWOOD,
    stone_material=MG,
)

# 3. Query creek distance/elevation/flow or bridge deck height anywhere in Python:
q = cb.CreekAndBridgeQuery(frame="local_m")
info = q.nearest_creek_sample(x_local, y_local)
deck_z = q.bridge_deck_elevation_at(x_local, y_local)
```
