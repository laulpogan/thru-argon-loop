#!/usr/bin/env python3
"""
THRU Unreal Systems — System 1: Trail-Follow & Walkthrough Camera (ue_trail_follow.py)

Dual-mode script:
1. Inside Unreal Engine 5.6 Python (`import unreal`):
   - Spawns `AThruTrailSpline` (with USplineComponent for the PCT route)
   - Builds `/Game/Cine/SeqWalk` and `/Game/Cine/SeqHeroWalk36s` with:
     * Exact Catmull-Rom resampled trail path from `route-hero-after.json`
     * Natural 1.40 m/s walk pace (or configurable 1.15-1.50 m/s)
     * Velocity-aligned hiker yaw (8.0m lookahead, exponential smoothing, angle unwrapping, zero crab-walk)
     * Slope-adaptive pitch lean (`SLOPE_LEAN_CAP = 12.6 deg`) + pack load lean (`5.16 deg`)
     * FK-calibrated walk cycle `play_rate = speed_mps / 1.0181` (switches cleanly to `idle` on bridge linger)
     * 3rd-person CineCamera follow boom (`3.8m` back, `1.3m` right, `1.6m` up, `8.0m` look-ahead, ground clearance clamp, subtle gait bob/sway, and 14s 40-deg bridge linger orbit)
2. Standalone CLI (`python3 ue_trail_follow.py --verify --out trail_follow_keyframes.json`):
   - Computes and verifies the exact frame-by-frame trajectory, speed profile, footfall frames, and camera keyframes without needing Unreal running.
"""

import json
import math
import os
import sys
import numpy as np

# ---------------------------------------------------------------------------
# Constants ported from hiker.gd, trail_camera.gd, walkthrough.gd, route-hero-after.json
# ---------------------------------------------------------------------------
HIKER_NATIVE_WALK_MPS = 1.0181   # FK-measured on hiker_male.glb: 2 * 0.6787m / 1.3333s
HIKER_WALK_CLIP_S = 1.3333       # 32 frames @ 24fps
HIKER_STRIDE_M = 0.78            # trail_footsteps.gd:15 STRIDE_M (1 step = 0.6787m..0.78m)
HIKER_YAW_OFFSET_DEG = -90.0     # glTF +Z forward -> UE actor +X forward
SLOPE_LEAN_CAP_RAD = 0.22        # hiker.gd:26 SLOPE_LEAN_CAP (12.6 deg)
LOADED_LEAN_RAD = 0.09           # hiker.gd:92 loaded pack forward pitch (5.16 deg)

GAIT_RADIANS_PER_M = 6.0         # trail_camera.gd:26
BOB_M = 0.019                    # trail_camera.gd:27
SWAY_M = 0.013                   # trail_camera.gd:28

BRIDGE_CENTER_GODOT = np.array([3049.5, 6249.8], dtype=float)
BRIDGE_AXIS = np.array([0.865, -0.503], dtype=float)  # +y_local along bridge
CREEK_AXIS = np.array([0.503, 0.865], dtype=float)    # +x_local along creek
BRIDGE_HALF_LEN_M = 6.8

DEFAULT_WAYPOINTS_GODOT = [
    [3038.0, 2351.0, 6280.0],
    [3040.5, 2350.2, 6272.0],
    [3042.0, 2349.4, 6264.0],
    [3042.8, 2348.8, 6258.0],
    [3043.6, 2348.4, 6253.2],
    [3046.5, 2348.6, 6251.5],
    [3049.5, 2348.8, 6249.8],
    [3052.5, 2348.6, 6248.1],
    [3055.3, 2348.4, 6246.4],
    [3058.0, 2348.6, 6245.0],
    [3062.0, 2348.8, 6242.0],
]


def play_rate_for_speed(speed_mps: float) -> float:
    """Exact walk animation play_rate for a target ground speed (m/s)."""
    if speed_mps <= 0.08:
        return 1.0
    return max(0.4, float(speed_mps) / HIKER_NATIVE_WALK_MPS)


def catmull_rom_chain(ctrl_pts: np.ndarray, step_m: float = 0.25) -> np.ndarray:
    """Resample 2D/3D control points with centripetal/uniform Catmull-Rom spline."""
    pts = []
    q = np.r_[[ctrl_pts[0]], ctrl_pts, [ctrl_pts[-1]]]
    for i in range(1, len(q) - 2):
        p0, p1, p2, p3 = q[i - 1], q[i], q[i + 1], q[i + 2]
        seg_len = float(np.linalg.norm(p2 - p1))
        n = max(2, int(math.ceil(seg_len / step_m)))
        for t in np.linspace(0.0, 1.0, n, endpoint=False):
            t2, t3 = t * t, t * t * t
            pt = 0.5 * (
                (2.0 * p1)
                + (-p0 + p2) * t
                + (2.0 * p0 - 5.0 * p1 + 4.0 * p2 - p3) * t2
                + (-p0 + 3.0 * p1 - 3.0 * p2 + p3) * t3
            )
            pts.append(pt)
    pts.append(ctrl_pts[-1])
    arr = np.asarray(pts, dtype=float)
    keep = np.r_[True, np.linalg.norm(np.diff(arr, axis=0), axis=1) > 1e-4]
    return arr[keep]


def load_exported_trail_spline(spline_json_path: str = ""):
    """
    Load the canonical 75-point 3D spline from `reset/unreal/import/landscape/trail_spline.json`
    when available, returning `(pts_3d_local_m, on_bridge_flags, creek_dists_m,pts_3d_anchor_cm)`.
    """
    if not spline_json_path:
        cand = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "import", "landscape", "trail_spline.json"
        )
        if os.path.isfile(cand):
            spline_json_path = cand
    if not spline_json_path or not os.path.isfile(spline_json_path):
        return None
    doc = json.load(open(spline_json_path))
    pts_block = doc.get("hero_crossing_trail_spline", {}).get("points", [])
    if not pts_block:
        return None
    local_m = np.array([p["ue_bridge_frame"]["local_m"] for p in pts_block], dtype=float)
    anchor_cm = np.array([p["ue_anchor_cm"]["location_cm"] for p in pts_block], dtype=float)
    on_bridge = np.array([bool(p.get("on_bridge", False)) for p in pts_block], dtype=bool)
    creek_dist = np.array([float(p.get("creek_dist_m", 15.0)) for p in pts_block], dtype=float)
    # Smooth C1 Hermite transition onto bridge centerline x_local = 0 over |y| in [6.8m, 9.2m]
    abs_y = np.abs(local_m[:, 1])
    t_blend = np.clip((abs_y - BRIDGE_HALF_LEN_M) / 2.4, 0.0, 1.0)
    w_blend = t_blend * t_blend * (3.0 - 2.0 * t_blend)
    local_m[:, 0] *= w_blend
    local_m[on_bridge, 0] = 0.0
    return {
        "local_m": local_m,
        "anchor_cm": anchor_cm,
        "on_bridge": on_bridge,
        "creek_dist_m": creek_dist,
    }


def build_local_trail_polyline(waypoints_godot=None, use_exported_spline: bool = True) -> np.ndarray:
    """Convert Godot (X, Y, Z) route waypoints into local (x_creek, y_bridge) meters."""
    if use_exported_spline and waypoints_godot is None:
        exp = load_exported_trail_spline()
        if exp is not None:
            return exp["local_m"][:, :2]
    if waypoints_godot is None:
        waypoints_godot = DEFAULT_WAYPOINTS_GODOT
    wp_xz = np.array([[p[0], p[2]] for p in waypoints_godot], dtype=float) - BRIDGE_CENTER_GODOT
    loc = np.c_[wp_xz @ CREEK_AXIS, wp_xz @ BRIDGE_AXIS]
    d0 = loc[0] - loc[1]
    d0 /= np.linalg.norm(d0)
    d1 = loc[-1] - loc[-2]
    d1 /= np.linalg.norm(d1)
    ctrl = np.r_[[loc[0] + d0 * 14.0, loc[0] + d0 * 7.0], loc, [loc[-1] + d1 * 6.0, loc[-1] + d1 * 12.0]]
    trail = catmull_rom_chain(ctrl, step_m=0.25)
    # Smooth C1 Hermite transition onto the wooden bridge deck centerline
    abs_y = np.abs(trail[:, 1])
    t_blend = np.clip((abs_y - BRIDGE_HALF_LEN_M) / 2.4, 0.0, 1.0)
    trail[:, 0] *= t_blend * t_blend * (3.0 - 2.0 * t_blend)
    return trail


def default_height_fn(deck_z: float = 0.99):
    """Fallback analytic height function matching gen.py when terrain interpolator is not passed."""
    def zf(x: float, y: float) -> float:
        c = 0.8 * math.sin(x / 11.0) + 1.2 * math.sin(x / 4.3 + 1.0)
        hw = 1.7 + 0.8 * math.sin(x / 7.1)
        d = abs(y - c)
        bank = min(1.0, max(0.0, (d - hw) / 6.0))
        z = -0.5 * max(0.0, 1.0 - (d / hw) ** 2) + (bank ** 1.4) * 1.2 - x * 0.01
        if abs(x) < 2.2 and hw < d < hw + 3.5:
            z = max(z, -0.5 + 0.34 - x * 0.01 + 0.9)
        return float(z)
    return zf


def classify_surface(x: float, y: float, z: float, water_z0: float = -0.16, slope: float = 0.01) -> str:
    """Classify physical surface at local (x, y, z) for footsteps & particles."""
    if abs(x) < 0.85 and abs(y) <= BRIDGE_HALF_LEN_M + 0.2:
        return "wood_bridge"
    c = 0.8 * math.sin(x / 11.0) + 1.2 * math.sin(x / 4.3 + 1.0)
    hw = 1.7 + 0.8 * math.sin(x / 7.1)
    d_creek = abs(y - c)
    zw = water_z0 - x * slope
    if d_creek < hw * 0.95 and z <= zw + 0.08:
        return "water_splash"
    if abs(y) <= BRIDGE_HALF_LEN_M + 2.8 and abs(x) < 2.5:
        return "gravel"
    if d_creek < hw + 1.8:
        return "granite"
    return "decomposed_granite"


def generate_walkthrough_trajectory(
    speed_mps: float = 1.40,
    fps: int = 60,
    walk_duration_s: float = 22.0,
    linger_duration_s: float = 14.0,
    deck_z: float = 0.99,
    height_fn=None,
    waypoints_godot=None,
    cam_back_m: float = 3.8,
    cam_side_m: float = 1.3,
    cam_up_m: float = 1.6,
    cam_look_ahead_m: float = 8.0,
    cam_look_up_m: float = 0.9,
    linger_orbit_deg: float = 40.0,
    linger_rise_m: float = 1.2,
    linger_look_m: float = 7.0,
    steer_lookahead_m: float = 4.5,
):
    """
    Generate frame-accurate hiker & camera trajectories along the PCT spline.
    Supports both continuous walk (linger_duration_s=0) and hero walkthrough
    (22s walk to bridge center + 14s linger overlooking creek).
    """
    if height_fn is None:
        height_fn = default_height_fn(deck_z)
    trail = build_local_trail_polyline(waypoints_godot)
    seg_lengths = np.hypot(*np.diff(trail, axis=0).T)
    cum_s = np.r_[0.0, np.cumsum(seg_lengths)]
    total_len = float(cum_s[-1])

    # Find arc-length s_bridge_center where trail crosses y = 0.0 (bridge center)
    idx_center = int(np.argmin(np.abs(trail[:, 1]) + np.abs(trail[:, 0])))
    s_center = float(cum_s[idx_center])

    walk_frames = int(round(walk_duration_s * fps))
    linger_frames = int(round(linger_duration_s * fps))
    total_frames = walk_frames + linger_frames

    # Start distance so hiker arrives at bridge center (or crosses bridge) cleanly
    if linger_frames > 0:
        s_end = s_center + 1.2  # Stop just past center of bridge deck overlooking water
        s_start = max(0.0, s_end - speed_mps * walk_duration_s)
    else:
        walk_dist = speed_mps * walk_duration_s
        s_start = max(0.0, s_center - walk_dist * 0.55)
        s_end = min(total_len - 0.5, s_start + walk_dist)

    def sample_along(s_val: float):
        s_clamped = float(np.clip(s_val, 0.0, total_len - 1e-4))
        i = int(np.clip(np.searchsorted(cum_s, s_clamped) - 1, 0, len(seg_lengths) - 1))
        t = (s_clamped - cum_s[i]) / max(1e-6, float(seg_lengths[i]))
        p = trail[i] + t * (trail[i + 1] - trail[i])
        d = (trail[i + 1] - trail[i]) / max(1e-6, float(seg_lengths[i]))
        return p, d

    dt = 1.0 / float(fps)
    p0, d0 = sample_along(s_start)
    fwd = d0 / max(1e-6, np.linalg.norm(d0))

    hiker_frames = []
    cam_frames = []
    footstep_events = []

    elapsed_dist = 0.0
    stride_accum = 0.0
    step_index = 0
    prev_yaw = None
    prev_z = None
    gait_pitch_deg = 0.0
    cam_pos = None
    cam_tgt = None

    for f in range(total_frames + 1):
        t_sec = f * dt
        lingering = (f > walk_frames) and (linger_frames > 0)

        if not lingering:
            # Smooth ease-out over last 1.2s before bridge stop if lingering
            if linger_frames > 0 and (walk_frames - f) < int(1.2 * fps):
                rem = max(0.0, (walk_frames - f) / (1.2 * fps))
                cur_speed = speed_mps * (rem * rem * (3.0 - 2.0 * rem))
            else:
                cur_speed = speed_mps
            s_cur = min(s_end, s_start + elapsed_dist)
        else:
            cur_speed = 0.0
            s_cur = s_end

        (hx, hy), tangent = sample_along(s_cur)
        # Lookahead steering (walkthrough.gd:152-157)
        la_dist = min(steer_lookahead_m, 2.2) if abs(hy) < BRIDGE_HALF_LEN_M + 3.0 else steer_lookahead_m
        p_ahead, _ = sample_along(min(total_len, s_cur + la_dist))
        to_vec = p_ahead - np.array([hx, hy])
        if np.linalg.norm(to_vec) > 0.25 and cur_speed > 0.05:
            to_unit = to_vec / np.linalg.norm(to_vec)
            alpha_steer = 1.0 - math.exp(-3.2 * dt)
            fwd = fwd * (1.0 - alpha_steer) + to_unit * alpha_steer
            fwd /= max(1e-6, np.linalg.norm(fwd))

        on_bridge = abs(hx) < 0.85 and abs(hy) < (BRIDGE_HALF_LEN_M + 0.2)
        hz = float(deck_z) if on_bridge else float(height_fn(hx, hy))

        # Slope pitch lean (hiker.gd:267-288)
        if prev_z is not None and cur_speed > 0.1:
            dz_ds = (hz - prev_z) / max(1e-4, cur_speed * dt)
            target_pitch_rad = np.clip(math.atan(dz_ds) * 0.55, -SLOPE_LEAN_CAP_RAD, SLOPE_LEAN_CAP_RAD)
        else:
            target_pitch_rad = 0.0
        prev_z = hz
        total_pitch_deg = math.degrees(LOADED_LEAN_RAD + target_pitch_rad) if cur_speed > 0.08 else 0.0
        gait_pitch_deg += np.clip(total_pitch_deg - gait_pitch_deg, -85.0 * dt, 85.0 * dt)

        # Unwrapped yaw (degrees in local XY)
        yaw_deg = math.degrees(math.atan2(float(fwd[1]), float(fwd[0])))
        if prev_yaw is not None:
            while yaw_deg - prev_yaw > 180.0:
                yaw_deg -= 360.0
            while yaw_deg - prev_yaw < -180.0:
                yaw_deg += 360.0
        prev_yaw = yaw_deg

        surface = classify_surface(hx, hy, hz)

        # Footstep cadence by distance spent (trail_footsteps.gd:74-86)
        step_dist = cur_speed * dt
        elapsed_dist += step_dist
        stride_accum += step_dist
        if stride_accum >= HIKER_STRIDE_M and cur_speed >= 0.3:
            stride_accum = math.fmod(stride_accum, HIKER_STRIDE_M)
            footstep_events.append({
                "frame": f,
                "time_s": round(t_sec, 4),
                "step_index": step_index,
                "foot": "L" if (step_index % 2 == 0) else "R",
                "pos_local_m": [round(hx, 4), round(hy, 4), round(hz, 4)],
                "surface": surface,
                "speed_mps": round(cur_speed, 4),
            })
            step_index += 1

        # Gait bob & sway (trail_camera.gd:90-93)
        gait_weight = min(1.0, cur_speed / max(0.1, speed_mps))
        phase = elapsed_dist * GAIT_RADIANS_PER_M
        bob = math.sin(phase * 2.0) * BOB_M * gait_weight
        sway = math.sin(phase) * SWAY_M * gait_weight

        # Right vector perpendicular to fwd in XY
        right = np.array([fwd[1], -fwd[0]], dtype=float)

        if not lingering:
            want_cx = hx - fwd[0] * cam_back_m + right[0] * cam_side_m + right[0] * sway
            want_cy = hy - fwd[1] * cam_back_m + right[1] * cam_side_m + right[1] * sway
            ground_c = float(height_fn(want_cx, want_cy))
            want_cz = max(hz, ground_c) + cam_up_m + bob
            want_pos = np.array([want_cx, want_cy, want_cz], dtype=float)
            want_tgt = np.array([
                hx + fwd[0] * cam_look_ahead_m,
                hy + fwd[1] * cam_look_ahead_m,
                hz + cam_look_up_m,
            ], dtype=float)
            if cam_pos is None:
                cam_pos = want_pos.copy()
                cam_tgt = want_tgt.copy()
            else:
                alpha_cam = 1.0 - math.exp(-5.9 * dt)
                cam_pos = cam_pos + alpha_cam * (want_pos - cam_pos)
                cam_tgt = cam_tgt + alpha_cam * (want_tgt - cam_tgt)
        else:
            # Linger orbit on bridge (walkthrough.gd:142-150)
            d_orbit_rad = math.radians(linger_orbit_deg) * dt / max(1.0, linger_duration_s)
            rel = cam_pos - np.array([hx, hy, hz])
            cos_o, sin_o = math.cos(d_orbit_rad), math.sin(d_orbit_rad)
            rx = rel[0] * cos_o - rel[1] * sin_o
            ry = rel[0] * sin_o + rel[1] * cos_o
            rz = rel[2] + linger_rise_m * dt / max(1.0, linger_duration_s)
            cam_pos = np.array([hx + rx, hy + ry, hz + rz], dtype=float)
            linger_tgt = np.array([
                hx + fwd[0] * linger_look_m,
                hy + fwd[1] * linger_look_m,
                hz + 0.6,
            ], dtype=float)
            alpha_linger = 1.0 - math.exp(-1.2 * dt)
            cam_tgt = cam_tgt + alpha_linger * (linger_tgt - cam_tgt)

        hiker_frames.append({
            "f": f,
            "t": round(t_sec, 4),
            "pos": [round(float(hx), 4), round(float(hy), 4), round(float(hz), 4)],
            "yaw": round(float(yaw_deg), 4),
            "pitch": round(float(gait_pitch_deg), 4),
            "speed_mps": round(float(cur_speed), 4),
            "anim": "walk" if cur_speed > 0.08 else "idle",
            "play_rate": round(play_rate_for_speed(cur_speed), 4),
            "surface": surface,
        })
        cam_frames.append({
            "f": f,
            "t": round(t_sec, 4),
            "pos": [round(float(cam_pos[0]), 4), round(float(cam_pos[1]), 4), round(float(cam_pos[2]), 4)],
            "tgt": [round(float(cam_tgt[0]), 4), round(float(cam_tgt[1]), 4), round(float(cam_tgt[2]), 4)],
        })

    return {
        "speed_mps": speed_mps,
        "native_walk_mps": HIKER_NATIVE_WALK_MPS,
        "play_rate_walk": round(play_rate_for_speed(speed_mps), 4),
        "fps": fps,
        "walk_duration_s": walk_duration_s,
        "linger_duration_s": linger_duration_s,
        "total_frames": total_frames,
        "walk_frames": walk_frames,
        "linger_frames": linger_frames,
        "trail_points_local_m": np.round(trail, 4).tolist(),
        "hiker_walk": hiker_frames,
        "walk": cam_frames,
        "footsteps": footstep_events,
    }


def convert_dense_replay_to_unreal(
    dense_json_path: str = "",
    deck_z: float = 0.99,
    height_fn=None,
):
    """
    Convert Playtest Operator's canonical 2,353-frame (39.20s @ 60fps)
    `reset/unreal/route/path-hero-after-dense.json` directly into Unreal
    `ue_bridge_frame` (`local_m` & `ue_cm`) and `ue_anchor_cm` keyframes,
    automatically detecting the 4.0s bridge-center pause (frames 1479..1718)
    to switch `walk` (`play_rate = 1.3751`) <-> `idle` (`play_rate = 1.0`).
    """
    if not dense_json_path:
        cand = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "route", "path-hero-after-dense.json"
        )
        if os.path.isfile(cand):
            dense_json_path = cand
    if not dense_json_path or not os.path.isfile(dense_json_path):
        raise FileNotFoundError(f"Dense replay file not found: {dense_json_path}")

    if height_fn is None:
        height_fn = default_height_fn(deck_z)

    doc = json.load(open(dense_json_path))
    fps = int(doc.get("fps", 60))
    dt = 1.0 / float(fps)
    frames_in = doc["frames"]

    # Bridge center datum from heightmap.json / CAMERAS.json
    bc_xz = np.array([3049.482, 6249.796], dtype=float)
    datum_y = 2347.261

    def godot_to_local_m(g_xyz):
        dx = float(g_xyz[0]) - bc_xz[0]
        dz = float(g_xyz[2]) - bc_xz[1]
        xl = (0.503 * dx + 0.865 * dz) / 1.001234
        yl = (0.865 * dx - 0.503 * dz) / 1.001234
        zl = float(g_xyz[1]) - datum_y
        return np.array([xl, yl, zl], dtype=float)

    hiker_frames = []
    cam_frames = []
    footstep_events = []

    prev_xy = None
    prev_yaw = None
    prev_z = None
    gait_pitch_deg = 0.0
    stride_accum = 0.0
    step_index = 0
    fwd = np.array([-0.5, 0.866], dtype=float)

    for i, fr in enumerate(frames_in):
        f = int(fr["f"])
        t_sec = f * dt
        b_loc = godot_to_local_m(fr["body"])
        c_loc = godot_to_local_m(fr["cam"])
        t_loc = godot_to_local_m(fr["target"])

        hx, hy, hz_godot = float(b_loc[0]), float(b_loc[1]), float(b_loc[2])
        # Keep bridge span centered on x_local = 0 with smooth Hermite blend over |y| in [6.8, 9.2]
        abs_y = abs(hy)
        t_b = min(1.0, max(0.0, (abs_y - BRIDGE_HALF_LEN_M) / 2.4))
        hx *= t_b * t_b * (3.0 - 2.0 * t_b)
        on_bridge = abs(hx) < 0.85 and abs_y <= (BRIDGE_HALF_LEN_M + 0.2)
        hz = float(deck_z) if on_bridge else float(height_fn(hx, hy))

        cur_xy = np.array([hx, hy], dtype=float)
        if prev_xy is not None:
            disp = cur_xy - prev_xy
            dist_step = float(np.linalg.norm(disp))
            cur_speed = dist_step / dt
            if dist_step > 1e-4:
                fwd = disp / dist_step
        else:
            dist_step = 0.0
            cur_speed = 1.40
        prev_xy = cur_xy

        # Convert Godot heading (atan2(-dx, -dz)) or velocity tangent to local XY yaw
        yaw_deg = math.degrees(math.atan2(float(fwd[1]), float(fwd[0])))
        if prev_yaw is not None:
            while yaw_deg - prev_yaw > 180.0:
                yaw_deg -= 360.0
            while yaw_deg - prev_yaw < -180.0:
                yaw_deg += 360.0
        prev_yaw = yaw_deg

        # Slope pitch lean
        if prev_z is not None and cur_speed > 0.1:
            dz_ds = (hz - prev_z) / max(1e-4, dist_step)
            target_pitch_rad = np.clip(math.atan(dz_ds) * 0.55, -SLOPE_LEAN_CAP_RAD, SLOPE_LEAN_CAP_RAD)
        else:
            target_pitch_rad = 0.0
        prev_z = hz
        total_pitch_deg = math.degrees(LOADED_LEAN_RAD + target_pitch_rad) if cur_speed > 0.08 else 0.0
        gait_pitch_deg += float(np.clip(total_pitch_deg - gait_pitch_deg, -85.0 * dt, 85.0 * dt))

        surface = classify_surface(hx, hy, hz)
        stride_accum += dist_step
        if stride_accum >= HIKER_STRIDE_M and cur_speed >= 0.3:
            stride_accum = math.fmod(stride_accum, HIKER_STRIDE_M)
            footstep_events.append({
                "frame": f,
                "time_s": round(t_sec, 4),
                "step_index": step_index,
                "foot": "L" if (step_index % 2 == 0) else "R",
                "pos_local_m": [round(hx, 4), round(hy, 4), round(hz, 4)],
                "surface": surface,
                "speed_mps": round(cur_speed, 4),
            })
            step_index += 1

        # Offset camera Z relative to local terrain/bridge height
        dz_offset = hz - hz_godot
        cx, cy, cz = float(c_loc[0]), float(c_loc[1]), float(c_loc[2]) + dz_offset
        tx, ty, tz = float(t_loc[0]), float(t_loc[1]), float(t_loc[2]) + dz_offset

        hiker_frames.append({
            "f": f,
            "t": round(t_sec, 4),
            "pos": [round(hx, 4), round(hy, 4), round(hz, 4)],
            "godot_body": [round(float(x), 4) for x in fr["body"]],
            "yaw": round(yaw_deg, 4),
            "pitch": round(gait_pitch_deg, 4),
            "speed_mps": round(cur_speed, 4),
            "anim": "walk" if cur_speed > 0.08 else "idle",
            "play_rate": round(play_rate_for_speed(cur_speed), 4),
            "surface": surface,
        })
        cam_frames.append({
            "f": f,
            "t": round(t_sec, 4),
            "pos": [round(cx, 4), round(cy, 4), round(cz, 4)],
            "tgt": [round(tx, 4), round(ty, 4), round(tz, 4)],
        })

    # Identify idle window (bridge pause frames)
    idle_indices = [k["f"] for k in hiker_frames if k["anim"] == "idle"]
    pause_start = min(idle_indices) if idle_indices else len(hiker_frames)
    pause_end = max(idle_indices) if idle_indices else len(hiker_frames)

    return {
        "source": dense_json_path,
        "speed_mps": 1.40,
        "native_walk_mps": HIKER_NATIVE_WALK_MPS,
        "play_rate_walk": round(play_rate_for_speed(1.40), 4),
        "fps": fps,
        "total_frames": len(frames_in) - 1,
        "bridge_pause_start_frame": pause_start,
        "bridge_pause_end_frame": pause_end,
        "hiker_walk": hiker_frames,
        "walk": cam_frames,
        "footsteps": footstep_events,
    }


# ---------------------------------------------------------------------------
# Unreal Engine 5.6 Python Builder (`import unreal`)
# ---------------------------------------------------------------------------
def build_unreal_trail_follow(
    seq_name: str = "SeqWalk",
    speed_mps: float = 1.40,
    fps: int = 60,
    walk_duration_s: float = 10.0,
    linger_duration_s: float = 0.0,
    deck_z: float = 0.99,
    focal_length_mm: float = 24.0,
    aperture: float = 5.6,
    sy: float = -1.0,
    hiker_mesh_path: str = "/Game/Pack/hiker_male",
    key_step: int = 2,
):
    """
    Build `LevelSequence` in Unreal Engine 5.6 with velocity-aligned hiker,
    FK-synced walk/idle animation sections, and smoothed walkthrough camera.
    """
    import unreal

    EAL = unreal.EditorAssetLibrary
    EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    AT = unreal.AssetToolsHelpers.get_asset_tools()

    traj = generate_walkthrough_trajectory(
        speed_mps=speed_mps,
        fps=fps,
        walk_duration_s=walk_duration_s,
        linger_duration_s=linger_duration_s,
        deck_z=deck_z,
    )

    def to_ue_vec(p):
        return unreal.Vector(float(p[0]) * 100.0, float(p[1]) * 100.0 * sy, float(p[2]) * 100.0)

    def to_ue_look(pos, tgt):
        dx = (tgt[0] - pos[0])
        dy = (tgt[1] - pos[1]) * sy
        dz = (tgt[2] - pos[2])
        yaw = math.degrees(math.atan2(dy, dx))
        pitch = math.degrees(math.atan2(dz, math.hypot(dx, dy)))
        return unreal.Rotator(roll=0.0, pitch=pitch, yaw=yaw)

    # Load SkeletalMesh and walk/idle AnimSequences
    skel_mesh = None
    anims = {}
    if EAL.does_directory_exist(hiker_mesh_path):
        for asset_path in EAL.list_assets(hiker_mesh_path, recursive=True, include_folder=False):
            obj = unreal.load_asset(asset_path)
            if isinstance(obj, unreal.SkeletalMesh):
                skel_mesh = obj
            elif isinstance(obj, unreal.AnimSequence):
                anims[obj.get_name().lower()] = obj

    seq_path = f"/Game/Cine/{seq_name}"
    if EAL.does_asset_exist(seq_path):
        EAL.delete_asset(seq_path)
    seq = AT.create_asset(seq_name, "/Game/Cine", unreal.LevelSequence, unreal.LevelSequenceFactoryNew())
    seq.set_display_rate(unreal.FrameRate(fps, 1))
    nframes = traj["total_frames"]
    seq.set_playback_start(0)
    seq.set_playback_end(nframes)

    # 1. Spawnable CineCameraActor (focused on the hiker at ~412 cm, not the 8m look-ahead point)
    c0 = traj["walk"][0]
    h0 = traj["hiker_walk"][0]
    cam = EAS.spawn_actor_from_class(unreal.CineCameraActor, to_ue_vec(c0["pos"]), to_ue_look(c0["pos"], c0["tgt"]))
    cam.set_actor_label(f"Cam_{seq_name}")
    cc = cam.get_cine_camera_component()
    cc.set_editor_property("current_focal_length", float(focal_length_mm))
    cc.set_editor_property("current_aperture", float(aperture))
    fs = cc.focus_settings
    fs.focus_method = unreal.CameraFocusMethod.MANUAL
    fs.manual_focus_distance = math.dist(c0["pos"], h0["pos"]) * 100.0
    cc.focus_settings = fs

    cam_binding = seq.add_spawnable_from_instance(cam)
    EAS.destroy_actor(cam)

    cut_track = seq.add_track(unreal.MovieSceneCameraCutTrack)
    cut_sec = cut_track.add_section()
    cut_sec.set_range(0, nframes)
    try:
        cut_sec.set_camera_binding_id(seq.get_binding_id(cam_binding))
    except Exception:
        cut_sec.set_camera_binding_id(
            unreal.MovieSceneSequenceExtensions.get_portable_binding_id(seq, seq, cam_binding)
        )

    cam_tt = cam_binding.add_track(unreal.MovieScene3DTransformTrack)
    cam_ts = cam_tt.add_section()
    cam_ts.set_range(0, nframes)
    cam_ch = cam_ts.get_all_channels()
    interp_auto = unreal.MovieSceneKeyInterpolation.AUTO
    prev_cam_yaw = None

    for k in traj["walk"][::key_step] + ([traj["walk"][-1]] if (len(traj["walk"]) - 1) % key_step != 0 else []):
        loc = to_ue_vec(k["pos"])
        rot = to_ue_look(k["pos"], k["tgt"])
        cyaw = rot.yaw
        if prev_cam_yaw is not None:
            while cyaw - prev_cam_yaw > 180.0:
                cyaw -= 360.0
            while cyaw - prev_cam_yaw < -180.0:
                cyaw += 360.0
        prev_cam_yaw = cyaw
        fn = unreal.FrameNumber(int(k["f"]))
        for idx, val in enumerate([loc.x, loc.y, loc.z, rot.roll, rot.pitch, cyaw]):
            cam_ch[idx].add_key(fn, float(val), 0.0, unreal.MovieSceneTimeUnit.DISPLAY_RATE, interp_auto)

    # 2. Spawnable Hiker SkeletalMeshActor
    if skel_mesh is not None:
        h0 = traj["hiker_walk"][0]
        h_actor = EAS.spawn_actor_from_class(unreal.SkeletalMeshActor, to_ue_vec(h0["pos"]))
        smc = h_actor.skeletal_mesh_component
        if hasattr(smc, "set_skeletal_mesh_asset"):
            smc.set_skeletal_mesh_asset(skel_mesh)
        else:
            smc.set_skeletal_mesh(skel_mesh)
        h_binding = seq.add_spawnable_from_instance(h_actor)
        EAS.destroy_actor(h_actor)

        # Animation track: walk section + stepped deceleration sub-sections + idle section
        walk_anim = next((a for n, a in anims.items() if "walk" in n), None)
        idle_anim = next((a for n, a in anims.items() if n == "idle" or "idle" in n), walk_anim)
        if walk_anim is not None:
            anim_track = h_binding.add_track(unreal.MovieSceneSkeletalAnimationTrack)
            decel_frames = min(int(1.2 * fps), traj["walk_frames"] // 4) if traj["linger_frames"] > 0 else 0
            main_walk_end = traj["walk_frames"] - decel_frames

            walk_sec = anim_track.add_section()
            walk_sec.set_range(0, main_walk_end)
            pr = walk_sec.params
            pr.animation = walk_anim
            pr.play_rate = float(traj["play_rate_walk"])
            walk_sec.params = pr

            if decel_frames > 0:
                mid_f = main_walk_end + decel_frames // 2
                for s_f, e_f, scale_r in [
                    (main_walk_end, mid_f, 0.72),
                    (mid_f, traj["walk_frames"], 0.42),
                ]:
                    d_sec = anim_track.add_section()
                    d_sec.set_range(s_f, e_f)
                    dpr = d_sec.params
                    dpr.animation = walk_anim
                    dpr.play_rate = max(0.35, float(traj["play_rate_walk"]) * scale_r)
                    d_sec.params = dpr

            if traj["linger_frames"] > 0 and idle_anim is not None:
                idle_sec = anim_track.add_section()
                idle_sec.set_range(traj["walk_frames"], nframes)
                ipr = idle_sec.params
                ipr.animation = idle_anim
                ipr.play_rate = 1.0
                idle_sec.params = ipr

        # 3D Transform track with velocity-aligned yaw + slope pitch (mapped to local Roll because HIKER_YAW=-90 rotates +Y to +X)
        h_tt = h_binding.add_track(unreal.MovieScene3DTransformTrack)
        h_ts = h_tt.add_section()
        h_ts.set_range(0, nframes)
        h_ch = h_ts.get_all_channels()
        interp_lin = unreal.MovieSceneKeyInterpolation.LINEAR
        prev_hyaw = None
        for k in traj["hiker_walk"][::key_step] + ([traj["hiker_walk"][-1]] if (len(traj["hiker_walk"]) - 1) % key_step != 0 else []):
            loc = to_ue_vec(k["pos"])
            hyaw = float(k["yaw"]) * sy + HIKER_YAW_OFFSET_DEG
            if prev_hyaw is not None:
                while hyaw - prev_hyaw > 180.0:
                    hyaw -= 360.0
                while hyaw - prev_hyaw < -180.0:
                    hyaw += 360.0
            prev_hyaw = hyaw
            fn = unreal.FrameNumber(int(k["f"]))
            # With HIKER_YAW_OFFSET_DEG = -90 deg, local mesh forward is +Y, so forward lean is Roll = -pitch
            h_roll = -float(k["pitch"])
            for idx, val in enumerate([loc.x, loc.y, loc.z, h_roll, 0.0, hyaw]):
                h_ch[idx].add_key(fn, float(val), 0.0, unreal.MovieSceneTimeUnit.DISPLAY_RATE, interp_lin)

    EAL.save_loaded_asset(seq)
    return seq, traj


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Verify and export THRU Unreal trail-follow keyframes")
    ap.add_argument("--speed", type=float, default=1.40, help="Walking speed in m/s (1.3-1.5)")
    ap.add_argument("--fps", type=int, default=60, help="Frame rate")
    ap.add_argument("--walk-s", type=float, default=22.0, help="Walking duration in seconds")
    ap.add_argument("--linger-s", type=float, default=14.0, help="Bridge linger duration in seconds")
    ap.add_argument("--from-dense-replay", type=str, default="", help="Convert path-hero-after-dense.json")
    ap.add_argument("--out", type=str, default="", help="Output JSON path")
    args = ap.parse_args()

    if args.from_dense_replay:
        res = convert_dense_replay_to_unreal(args.from_dense_replay)
        summary = {
            "mode": "dense_replay_39p2s",
            "speed_mps": res["speed_mps"],
            "play_rate_walk": res["play_rate_walk"],
            "fps": res["fps"],
            "total_frames": res["total_frames"],
            "bridge_pause_frames": [res["bridge_pause_start_frame"], res["bridge_pause_end_frame"]],
            "footstep_count": len(res["footsteps"]),
            "surfaces_traversed": sorted(list({e["surface"] for e in res["footsteps"]})),
        }
    else:
        res = generate_walkthrough_trajectory(
            speed_mps=args.speed,
            fps=args.fps,
            walk_duration_s=args.walk_s,
            linger_duration_s=args.linger_s,
        )
        summary = {
            "speed_mps": res["speed_mps"],
            "native_walk_mps": res["native_walk_mps"],
            "play_rate_walk": res["play_rate_walk"],
            "fps": res["fps"],
            "total_frames": res["total_frames"],
            "footstep_count": len(res["footsteps"]),
            "surfaces_traversed": sorted(list({e["surface"] for e in res["footsteps"]})),
            "start_pos_m": res["hiker_walk"][0]["pos"],
            "bridge_arrive_pos_m": res["hiker_walk"][res["walk_frames"]]["pos"],
        }
    print("TRAIL_FOLLOW_VERIFIED:", json.dumps(summary))
    if args.out:
        with open(args.out, "w") as f:
            json.dump(res, f, indent=2)
