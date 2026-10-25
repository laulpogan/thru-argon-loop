# THRU UE 5.6 Drop-In Loader: Creek Spline & Wooden Trail Bridge (unreal-landscape-export-w2)
# Compatible with reset/unreal/src-snapshot/src/ue_main.py, ue_trail_follow.py, and ue_audio_ambience.py.

import json
import math
import os

try:
    import unreal
    HAS_UNREAL = True
except ImportError:
    HAS_UNREAL = False

DEFAULT_IMPORT_DIR = os.path.dirname(os.path.abspath(__file__))


def load_creek_spline_data(import_dir=DEFAULT_IMPORT_DIR):
    """Load creek_spline.json from the import directory."""
    path = os.path.join(import_dir, "creek_spline.json")
    with open(path, "r") as f:
        return json.load(f)


def load_bridge_data(import_dir=DEFAULT_IMPORT_DIR):
    """Load bridge.json from the import directory."""
    path = os.path.join(import_dir, "bridge.json")
    with open(path, "r") as f:
        return json.load(f)


class CreekAndBridgeQuery:
    """
    Pure-Python spatial query helper for gen.py / ue_main.py / ue_trail_follow.py / ue_audio_ambience.py.
    Works both inside Unreal Python and standalone offline scripts (numpy/scipy not required).
    """

    def __init__(self, import_dir=DEFAULT_IMPORT_DIR, frame="bridge_aligned"):
        """
        frame:
          - "bridge_aligned": CAMERAS.json / ue_main.py frame (origin at bridge center, cm, Z-up, sy=-1.0)
          - "anchor_centered": Cardinal East/South frame centered at hero anchor ground (cm, Z-up)
          - "local_m": gen.py scene-local metres (origin at bridge center, Z-up)
          - "godot_local": Godot pct-region-0029 metres (Y-up)
        """
        self.creek = load_creek_spline_data(import_dir)
        self.bridge = load_bridge_data(import_dir)
        self.frame = frame
        self.points = self.creek["resampled_1m_points"]

    def _pt_coords(self, pt):
        if self.frame == "bridge_aligned":
            return pt["ue_bridge_aligned_cm"]
        elif self.frame == "anchor_centered":
            return pt["ue_anchor_centered_cm"]
        elif self.frame == "local_m":
            return pt["local_m"]
        else:
            return pt["godot_water_pos_m"]

    def nearest_creek_sample(self, x, y):
        """
        Find the closest point on the resampled 1m creek spline to horizontal (x, y)
        (or (x, z) if frame == 'godot_local').
        Returns dict with: distance, water_elevation, bed_elevation, width, depth, flow_mps, flow_dir, sample.
        """
        best_d = 1e18
        best_pt = None
        for pt in self.points:
            c = self._pt_coords(pt)
            px = c[0]
            py = c[2] if self.frame == "godot_local" else c[1]
            d = math.hypot(x - px, y - py)
            if d < best_d:
                best_d = d
                best_pt = pt
        c = self._pt_coords(best_pt)
        scale = 100.0 if self.frame in ("bridge_aligned", "anchor_centered") else 1.0
        water_z = c[1] if self.frame == "godot_local" else c[2]
        return {
            "distance": best_d,
            "water_elevation": water_z,
            "bed_elevation": water_z - best_pt["depth_m"] * scale,
            "width": best_pt["width_m"] * scale,
            "half_width": 0.5 * best_pt["width_m"] * scale,
            "depth": best_pt["depth_m"] * scale,
            "flow_mps": best_pt["flow_mps"],
            "flow_dir": (
                best_pt["flow_dir_godot"]
                if self.frame == "godot_local"
                else best_pt["flow_dir_local_m"]
            ),
            "sample": best_pt,
        }

    def bridge_deck_elevation_at(self, x_local_m, y_local_m):
        """
        In local_m (gen.py / ue_trail_follow.py), return the walkable Z height (m) on the bridge deck
        or its approach ramps, or None if (x_local_m, y_local_m) is outside the bridge footprint.
        """
        half_w = self.bridge["dimensions"]["walkable_deck_width_m"] * 0.5  # 0.625 m
        if abs(x_local_m) > half_w + 0.15:
            return None
        half_span = self.bridge["dimensions"]["span_m"] * 0.5  # 6.75 m
        deck_z = 1.02
        pitch_grade = 0.0293  # 1.676 deg climbing from -y_local to +y_local
        if abs(y_local_m) <= half_span:
            return deck_z + y_local_m * pitch_grade
        # Check south-west approach ramp (-8.0127 <= y_local_m < -6.75)
        if -8.0127 <= y_local_m < -half_span:
            t = (y_local_m - (-half_span)) / (-8.0127 - (-half_span))
            top_z = deck_z - half_span * pitch_grade
            return top_z + t * (-0.4167)
        # Check north-east approach ramp (+6.75 < y_local_m <= +7.9932)
        if half_span < y_local_m <= 7.9932:
            t = (y_local_m - half_span) / (7.9932 - half_span)
            top_z = deck_z + half_span * pitch_grade
            return top_z + t * (-0.4103)
        return None


# ---------------- Unreal Engine 5.6 Editor Spawner ----------------
if HAS_UNREAL:
    AT = unreal.AssetToolsHelpers.get_asset_tools()
    EAL = unreal.EditorAssetLibrary
    MEL = unreal.MaterialEditingLibrary
    EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

    def _import_files(files, dest_path):
        tasks = []
        for f in files:
            if not os.path.exists(f):
                continue
            t = unreal.AssetImportTask()
            t.filename = f
            t.destination_path = dest_path
            t.automated = True
            t.save = True
            t.replace_existing = True
            tasks.append(t)
        if tasks:
            AT.import_asset_tasks(tasks)

    def import_creek_and_bridge_assets(import_dir=DEFAULT_IMPORT_DIR):
        """Import bridge & water ribbon GLBs and PBR textures into /Game/CreekBridge."""
        tex_dir = os.path.join(import_dir, "textures")
        tex_files = [
            os.path.join(tex_dir, "wood_planks_grey_diff.jpg"),
            os.path.join(tex_dir, "wood_planks_grey_nor_dx.png"),
            os.path.join(tex_dir, "wood_planks_grey_rough.jpg"),
            os.path.join(tex_dir, "rusty_metal_02_diff.jpg"),
            os.path.join(tex_dir, "rusty_metal_02_nor_dx.png"),
            os.path.join(tex_dir, "rusty_metal_02_rough.jpg"),
        ]
        _import_files(tex_files, "/Game/CreekBridge/Textures")
        for n in ["wood_planks_grey_nor_dx", "rusty_metal_02_nor_dx"]:
            t = unreal.load_asset(f"/Game/CreekBridge/Textures/{n}")
            if t:
                t.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP)
                t.set_editor_property("srgb", False)
                EAL.save_loaded_asset(t)
        for n in ["wood_planks_grey_rough", "rusty_metal_02_rough"]:
            t = unreal.load_asset(f"/Game/CreekBridge/Textures/{n}")
            if t:
                t.set_editor_property("srgb", False)
                EAL.save_loaded_asset(t)

        mesh_files = [
            os.path.join(import_dir, "bridge_mesh.glb"),
            os.path.join(import_dir, "bridge_godot_exact.glb"),
            os.path.join(import_dir, "weathered_wooden_footbridge_sect.glb"),
            os.path.join(import_dir, "water_ribbon_mesh.glb"),
            os.path.join(import_dir, "wet_bank_mesh.glb"),
        ]
        for mf in mesh_files:
            stem = os.path.splitext(os.path.basename(mf))[0]
            _import_files([mf], f"/Game/CreekBridge/Meshes/{stem}")

    def spawn_creek_spline_actor(
        import_dir=DEFAULT_IMPORT_DIR,
        frame="bridge_aligned",
        point_set="resampled_1m_points",
        actor_label="HeroCreekSpline",
    ):
        """
        Spawn an Actor in the active UE5 level carrying a USplineComponent populated with
        the exact Middle Fork San Joaquin River spline points, widths, depths, and flow tangents.
        """
        data = load_creek_spline_data(import_dir)
        pts = data[point_set]
        coord_key = "ue_bridge_aligned_cm" if frame == "bridge_aligned" else "ue_anchor_centered_cm"

        actor = EAS.spawn_actor_from_class(unreal.Actor, unreal.Vector(0.0, 0.0, 0.0))
        actor.set_actor_label(actor_label)
        spline = unreal.SplineComponent(actor)
        actor.set_root_component(spline)
        spline.clear_spline_points( False)

        for i, pt in enumerate(pts):
            c = pt[coord_key]
            loc = unreal.Vector(float(c[0]), float(c[1]), float(c[2]))
            spline.add_spline_point(loc, unreal.SplineCoordinateSpace.WORLD, False)
            # Encode channel width (m) in X/Y scale and depth (m) in Z scale
            w_scale = float(pt.get("width_m", 2.5))
            d_scale = float(pt.get("depth_m", 0.3976))
            spline.set_scale_at_spline_point(i, unreal.Vector(w_scale, w_scale, d_scale), False)

        spline.update_spline()
        return actor, spline

    def spawn_bridge_and_water_meshes(
        import_dir=DEFAULT_IMPORT_DIR,
        frame="bridge_aligned",
        water_material=None,
        wood_material=None,
        stone_material=None,
        rail_material=None,
    ):
        """
        Spawn the multi-part Godot TrailSpan_BridgeWood footbridge and the NHD creek water ribbon
        in the active UE5 level.
        """
        import_creek_and_bridge_assets(import_dir)
        bridge_data = load_bridge_data(import_dir)

        spawned = []
        if frame == "bridge_aligned":
            mesh_folder = "/Game/CreekBridge/Meshes/bridge_mesh"
            loc = unreal.Vector(0.0, 0.0, 0.0)
            rot = unreal.Rotator(roll=0.0, pitch=0.0, yaw=0.0)
        else:
            mesh_folder = "/Game/CreekBridge/Meshes/bridge_godot_exact"
            t_info = bridge_data["transforms"]["ue_anchor_centered_cm"]
            loc = unreal.Vector(*t_info["location_cm"])
            r_info = t_info["rotation_deg"]
            rot = unreal.Rotator(roll=r_info["roll"], pitch=r_info["pitch"], yaw=r_info["yaw"])

        for asset_path in EAL.list_assets(mesh_folder, recursive=True, include_folder=False):
            obj = unreal.load_asset(asset_path)
            if isinstance(obj, unreal.StaticMesh):
                a = EAS.spawn_actor_from_object(obj, loc, rot)
                a.set_actor_label(f"HeroBridge_{obj.get_name()}")
                smc = a.static_mesh_component
                name_l = obj.get_name().lower()
                if "stone" in name_l and stone_material:
                    smc.set_material(0, stone_material)
                elif "rail" in name_l and rail_material:
                    smc.set_material(0, rail_material)
                elif wood_material and "wood" in name_l:
                    smc.set_material(0, wood_material)
                spawned.append(a)

        # Spawn water ribbon mesh
        water_folder = "/Game/CreekBridge/Meshes/water_ribbon_mesh"
        for asset_path in EAL.list_assets(water_folder, recursive=True, include_folder=False):
            obj = unreal.load_asset(asset_path)
            if isinstance(obj, unreal.StaticMesh) and "2p5m" in obj.get_name():
                wa = EAS.spawn_actor_from_object(obj, unreal.Vector(0.0, 0.0, 0.0), unreal.Rotator())
                wa.set_actor_label("HeroCreek_WaterRibbon_NHD")
                if water_material:
                    wa.static_mesh_component.set_material(0, water_material)
                spawned.append(wa)

        return spawned
