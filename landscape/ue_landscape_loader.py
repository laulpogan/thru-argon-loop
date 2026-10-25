"""
Drop-in loader for ~/cs-audit/gemini-hackathon/reset/unreal/import/landscape/
Works in both standard NumPy (gen.py) and Unreal Engine 5.6 Python (ue_main.py).
"""
import json
from pathlib import Path
import numpy as np

LANDSCAPE_DIR = Path(__file__).resolve().parent


def load_heightmap_metres(variant: str = "heightmap_1009", directory: Path = LANDSCAPE_DIR):
    """
    Load 16-bit RAW heightmap and decode to float64 elevation in metres.
    Variants:
      - 'heightmap_1009' (1009x1009, 0.5m/px, 504m span, unrotated anchor frame)
      - 'heightmap_2017' (2017x2017, 0.5m/px, 1008m span, unrotated anchor frame)
      - 'heightmap_bridge_frame_1009' (1009x1009, 0.25m/px, 252m span, CAMERAS.json bridge-aligned frame)
      - 'heightmap_procgen_3dep_1009' (1009x1009, 0.5m/px, pure USGS 3DEP + 12-iter thermal/hydraulic erosion)
    Returns (heights_m, meta_dict).
    """
    meta_all = json.loads((directory / "heightmap.json").read_text())
    meta = meta_all["variants"][variant]
    n_h, n_w = meta["resolution_px"]
    u16 = np.frombuffer((directory / meta["raw_file"]).read_bytes(), dtype="<u2").reshape(n_h, n_w)
    h_min = float(meta["min_height_m"])
    h_range = float(meta["height_range_m"])
    heights_m = h_min + (u16.astype(np.float64) / 65535.0) * h_range
    return heights_m, meta


def load_creek_spline(frame: str = "ue_bridge_frame", directory: Path = LANDSCAPE_DIR):
    """
    Load creek_spline.json.
    frame: 'ue_bridge_frame' | 'ue_anchor_cm' | 'godot_m'
    """
    doc = json.loads((directory / "creek_spline.json").read_text())
    pts = [p[frame] for p in doc["points"]]
    return doc, pts


def load_placements(frame: str = "ue_bridge_frame", category: str = None, source_layer: str = None, directory: Path = LANDSCAPE_DIR):
    """
    Load placements.json filtered optionally by category ('rock', 'cobble', 'tree', 'foliage', 'log', 'bridge')
    or source_layer ('argon_hero_creek', 'pct_region_hydrology', 'pct_rock_scatter', 'pct_vegetation').
    """
    doc = json.loads((directory / "placements.json").read_text())
    items = doc["placements"]
    if category is not None:
        items = [x for x in items if x["category"] == category]
    if source_layer is not None:
        items = [x for x in items if x["source_layer"] == source_layer]
    return doc, items


def load_trail_and_cameras(directory: Path = LANDSCAPE_DIR):
    """Load trail_spline.json and cameras.json."""
    trail = json.loads((directory / "trail_spline.json").read_text())
    cameras = json.loads((directory / "cameras.json").read_text())
    return trail, cameras
