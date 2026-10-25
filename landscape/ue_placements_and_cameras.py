#!/usr/bin/env python3
"""
Drop-in Unreal Engine 5.6 & standalone Python loader/spawner for
`unreal-landscape-export-w3` (Placements, Trail Spline & Cameras).

Works in:
  1. Standalone Python / `gen.py` (loads JSON/CSV placements, cameras, trail spline).
  2. Unreal Engine 5.6 Editor Python (`import unreal`; spawns HISM / StaticMeshActors,
     CineCameraActors for all 5 shots + 6 Godot views, and USplineComponent trail).
"""

import json
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent


def _resolve_file(filename: str, directory: Optional[Path] = None) -> Path:
    base = Path(directory) if directory else HERE
    cand = base / filename
    if cand.exists():
        return cand
    parent_cand = base.parent / filename
    if parent_cand.exists():
        return parent_cand
    raise FileNotFoundError(f"Cannot locate {filename} in {base}")


def load_placements(
    frame: str = "ue_bridge_frame",
    category: Optional[str] = None,
    source_layer: Optional[str] = None,
    wet_dry_state: Optional[str] = None,
    max_dist_m: Optional[float] = None,
    directory: Optional[Path] = None,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Load placements.json with optional filtering by:
      - frame: 'ue_bridge_frame' | 'ue_anchor_centered' | 'ue_anchor_cm' | 'godot_transform' | 'godot_m'
      - category: 'rock' | 'cobble' | 'tree' | 'foliage' | 'log' | 'bridge' | 'trail'
      - source_layer: 'argon_hero_creek' | 'argon_hero_creek_waterline' | 'pct_rock_scatter'
                      | 'pct_vegetation' | 'pct_trail_bridges' | 'pct_region_hydrology' | 'pct_trail_tread'
      - wet_dry_state: 'submerged' | 'wet_slick' | 'splash_zone' | 'dry_dusty'
      - max_dist_m: maximum horizontal distance (m) from the hero bridge anchor
    """
    doc = json.loads(_resolve_file("placements.json", directory).read_text())
    items = doc["placements"]
    if category is not None:
        items = [x for x in items if x.get("category") == category]
    if source_layer is not None:
        items = [x for x in items if x.get("source_layer") == source_layer or x.get("source") == source_layer]
    if wet_dry_state is not None:
        items = [x for x in items if x.get("wet_dry_state") == wet_dry_state]
    if max_dist_m is not None:
        items = [
            x for x in items
            if float(x.get("placement_metadata", {}).get("dist_to_anchor_m", 0.0)) <= float(max_dist_m)
        ]
    return doc, items


def load_cameras(directory: Optional[Path] = None) -> Dict[str, Any]:
    """Load cameras.json (5 UE spike shots, hiker_still, 6 Godot hero views, and walk sequences)."""
    return json.loads(_resolve_file("cameras.json", directory).read_text())


def load_trail_spline(directory: Optional[Path] = None) -> Dict[str, Any]:
    """Load trail_spline.json (Catmull-Rom crossing spline, route-hero-after waypoints, canonical PCT route)."""
    return json.loads(_resolve_file("trail_spline.json", directory).read_text())


# ---------------------------------------------------------------------------
# Unreal Engine 5.6 Editor Python Spawners
# ---------------------------------------------------------------------------
def spawn_cameras_in_ue(
    frame: str = "ue_bridge_frame",
    use_dem_safe: bool = False,
    include_godot_views: bool = True,
    directory: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Spawn CineCameraActors in UE 5.6 for the 5 primary shots (`hero_low`, `wet_stones`,
    `trail`, `wide`, `hiker`) and optionally the 6 Godot `walkthrough.gd` hero views.
    """
    import unreal  # type: ignore

    cam_doc = load_cameras(directory)
    subsys = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    spawned: Dict[str, Any] = {}

    for sh in cam_doc.get("shots", []):
        name = sh["name"]
        if frame == "ue_anchor_centered":
            loc = sh["ue_anchor_centered"]["location_cm"]
            rot = sh["ue_anchor_centered"]["rotation"]
        else:
            if use_dem_safe and "dem_clearance_check" in sh:
                loc = sh["dem_clearance_check"]["dem_safe_ue_location_cm"]
            else:
                loc = sh["ue"]["location_cm"]
            rot = sh["ue"]["rotation"]

        actor = subsys.spawn_actor_from_class(
            unreal.CineCameraActor,
            unreal.Vector(float(loc[0]), float(loc[1]), float(loc[2])),
            unreal.Rotator(float(rot["roll"]), float(rot["pitch"]), float(rot["yaw"])),
        )
        actor.set_actor_label(f"Cam_{name}")
        cc = actor.get_cine_camera_component()
        fb = cc.get_editor_property("filmback")
        fb.sensor_width = 24.0
        fb.sensor_height = 13.5
        cc.set_editor_property("filmback", fb)
        cc.set_editor_property("current_focal_length", float(sh["ue"].get("focal_mm", 28.0)))
        cc.set_editor_property("current_aperture", float(sh["ue"].get("aperture", 5.6)))
        fs = cc.get_editor_property("focus_settings")
        fs.focus_method = unreal.CameraFocusMethod.DISABLE
        cc.set_editor_property("focus_settings", fs)
        spawned[name] = actor

    if include_godot_views:
        for gv in cam_doc.get("godot_walkthrough_hero_views", []):
            vname = f"godot_{gv['name']}"
            tf_block = gv["ue_anchor_centered"] if frame == "ue_anchor_centered" else gv["ue_bridge_frame"]
            loc = tf_block["location_cm"]
            rot = tf_block["rotation"]
            actor = subsys.spawn_actor_from_class(
                unreal.CineCameraActor,
                unreal.Vector(float(loc[0]), float(loc[1]), float(loc[2])),
                unreal.Rotator(float(rot["roll"]), float(rot["pitch"]), float(rot["yaw"])),
            )
            actor.set_actor_label(f"Cam_{vname}")
            cc = actor.get_cine_camera_component()
            fb = cc.get_editor_property("filmback")
            fb.sensor_width = 24.0
            fb.sensor_height = 13.5
            cc.set_editor_property("filmback", fb)
            # vfov 58 deg on 13.5mm sensor -> focal_mm = 6.75 / tan(29 deg) = 12.18mm
            focal_mm = 6.75 / math.tan(math.radians(float(gv.get("fov_vertical_deg", 58.0)) * 0.5))
            cc.set_editor_property("current_focal_length", focal_mm)
            spawned[vname] = actor

    return spawned


def spawn_placements_in_ue(
    mesh_asset_map: Dict[str, Any],
    frame: str = "ue_bridge_frame",
    categories: Optional[List[str]] = None,
    max_dist_m: float = 120.0,
    directory: Optional[Path] = None,
) -> List[Any]:
    """
    Spawn StaticMeshActors in UE 5.6 from placements.json using a mapping from
    `asset_id` or `ue_pack_mesh` -> loaded `unreal.StaticMesh`.
    Tags each actor with its category, species, and wet_dry_state (`submerged`,
    `wet_slick`, `splash_zone`, `dry_dusty`).
    """
    import unreal  # type: ignore

    _, items = load_placements(frame=frame, max_dist_m=max_dist_m, directory=directory)
    if categories is not None:
        cat_set = set(categories)
        items = [x for x in items if x.get("category") in cat_set]

    subsys = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors = []
    tf_key = "ue_anchor_centered" if frame in ("ue_anchor_centered", "ue_anchor_cm") else "ue_bridge_frame"

    for item in items:
        mesh_obj = mesh_asset_map.get(item["asset_id"]) or mesh_asset_map.get(item["ue_pack_mesh"])
        if mesh_obj is None:
            continue
        tf = item[tf_key]
        loc = tf["location_cm"]
        rot = tf["rotation_deg"]
        sc = tf["scale"]
        act = subsys.spawn_actor_from_class(
            unreal.StaticMeshActor,
            unreal.Vector(float(loc[0]), float(loc[1]), float(loc[2])),
            unreal.Rotator(float(rot["roll"]), float(rot["pitch"]), float(rot["yaw"])),
        )
        act.set_actor_scale3d(unreal.Vector(float(sc[0]), float(sc[1]), float(sc[2])))
        act.set_actor_label(item["id"])
        smc = act.get_editor_property("static_mesh_component")
        smc.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
        smc.set_static_mesh(mesh_obj)
        act.tags = [
            item["category"],
            item["species"],
            item["wet_dry_state"],
            f"wetness_{item['wetness_dry']:.2f}",
        ]
        actors.append(act)

    return actors


if __name__ == "__main__":
    doc, items = load_placements()
    cams = load_cameras()
    trail = load_trail_spline()
    print(f"Loaded {len(items)} placements, {len(cams['shots'])} primary cameras, {len(trail['hero_crossing_catmull_spline'])} trail points.")
