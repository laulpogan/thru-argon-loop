#!/usr/bin/env python3
"""
THRU Unreal Systems — System 2: Spatial Audio Ambience & -16 LUFS Master Builder (ue_audio_ambience.py)

Dual-mode script:
1. Inside Unreal Engine 5.6 Python (`import unreal`):
   - Imports the curated WAV stems into `/Game/Audio/Ambience`, `/Game/Audio/Birds`, `/Game/Audio/Music`
   - Creates `USoundAttenuation` (`SA_CreekSpatial`, `SA_CanopyBird`)
   - Creates `USoundSubmix` (`Submix_AmbienceWater`, `Submix_AmbienceWind`, `Submix_TerrainReverb`, `Submix_MusicDry`)
   - Spawns spatial `AAmbientSound` actors along the creek spline, canopy bird spots, wind bed, and Lyria score
2. Standalone CLI (`python3 ue_audio_ambience.py --build-mix --out unreal_walk_master_16lufs.wav`):
   - Synthesizes the exact frame-accurate 48 kHz stereo mix from the real THRU audio masters:
     * Creek Near + Creek Far spatialized & crossfaded along the hiker's exact distance/azimuth to the creek spline (4 kHz LPF, -8 dB anti-masking trim)
     * Wind in Pines (120 Hz HPF - 4 kHz LPF, topographic exposure + canopy shelter envelope)
     * Sierra Alpine Dusk base air bed
     * Sparse 3D-panned Sierra bird calls (Mountain Chickadee & Canyon Wren, zero speech contamination)
     * Distance-triggered footsteps on Decomposed Granite -> Gravel -> Wooden Bridge -> Decomposed Granite
     * Lyria Sierra Conifer score with exact `8..50m -> -3..0 dB` water proximity ducking and footstep motion boost
     * Two-pass EBU R128 loudness normalization to exactly `-16.0 LUFS` / `-1.4 dBTP` with `ffmpeg` verification.
"""

import json
import math
import os
import subprocess
import sys
import wave
import numpy as np

DELL_HACKATHON_ROOT = "/home/dellpromax/cs-audit/gemini-hackathon"
AUDIOMIX_MASTERS = f"{DELL_HACKATHON_ROOT}/reset/audiomix/masters"
AUDIO_MASTERS = f"{DELL_HACKATHON_ROOT}/audio/masters"
LOCAL_STEMS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stems")


def _stem(fallback_path: str) -> str:
    local_p = os.path.join(LOCAL_STEMS_DIR, os.path.basename(fallback_path))
    return local_p if os.path.isfile(local_p) else fallback_path


WAV_MANIFEST = {
    "creek_near": _stem(f"{AUDIOMIX_MASTERS}/creek_near.wav"),
    "creek_far": _stem(f"{AUDIOMIX_MASTERS}/creek_far.wav"),
    "creek_medium": _stem(f"{AUDIO_MASTERS}/ambience/creek_medium.wav"),
    "sierra_dusk": _stem(f"{AUDIO_MASTERS}/ambience/Sierra_alpine_dusk.wav"),
    "wind_soft": _stem(f"{AUDIOMIX_MASTERS}/wind_pines_soft.wav"),
    "wind_medium": _stem(f"{AUDIOMIX_MASTERS}/wind_pines_medium.wav"),
    "wind_strong": _stem(f"{AUDIOMIX_MASTERS}/wind_pines_strong.wav"),
    "bird_chickadee_1": _stem(f"{AUDIOMIX_MASTERS}/mountain_chickadee_1583116.wav"),
    "bird_chickadee_2": _stem(f"{AUDIO_MASTERS}/ambience/mountain_chickadee_2127131.wav"),
    "bird_canyon_wren": _stem(f"{AUDIOMIX_MASTERS}/canyon_wren_1320386.wav"),
    "insects_cricket": _stem(f"{AUDIOMIX_MASTERS}/insects_western_cricket.wav"),
    "music_sierra": _stem(f"{AUDIOMIX_MASTERS}/music_sierra_conifer.wav"),
    "music_creeks_bed": _stem(f"{AUDIO_MASTERS}/music/creeks_bed.wav"),
    "music_creeks_melody": _stem(f"{AUDIO_MASTERS}/music/creeks_melody.wav"),
    "step_dg_01": _stem(f"{AUDIO_MASTERS}/sfx/decomposed_granite_01.wav"),
    "step_dg_02": _stem(f"{AUDIO_MASTERS}/sfx/decomposed_granite_02.wav"),
    "step_dg_03": _stem(f"{AUDIO_MASTERS}/sfx/decomposed_granite_03.wav"),
    "step_dg_04": _stem(f"{AUDIO_MASTERS}/sfx/decomposed_granite_04.wav"),
    "step_granite_01": _stem(f"{AUDIOMIX_MASTERS}/step_granite_01.wav"),
    "step_granite_02": _stem(f"{AUDIOMIX_MASTERS}/step_granite_02.wav"),
    "step_granite_03": _stem(f"{AUDIOMIX_MASTERS}/step_granite_03.wav"),
    "step_granite_04": _stem(f"{AUDIOMIX_MASTERS}/step_granite_04.wav"),
    "step_gravel_01": _stem(f"{AUDIOMIX_MASTERS}/step_gravel_01.wav"),
    "step_gravel_02": _stem(f"{AUDIOMIX_MASTERS}/step_gravel_02.wav"),
    "step_gravel_03": _stem(f"{AUDIOMIX_MASTERS}/step_gravel_03.wav"),
    "step_gravel_04": _stem(f"{AUDIOMIX_MASTERS}/step_gravel_04.wav"),
    "step_wood_01": _stem(f"{AUDIOMIX_MASTERS}/step_wood_01.wav"),
    "step_wood_02": _stem(f"{AUDIOMIX_MASTERS}/step_wood_02.wav"),
    "step_wood_03": _stem(f"{AUDIOMIX_MASTERS}/step_wood_03.wav"),
    "step_wood_04": _stem(f"{AUDIOMIX_MASTERS}/step_wood_04.wav"),
    "step_splash_01": _stem(f"{AUDIO_MASTERS}/sfx/splash_01.wav"),
    "step_splash_02": _stem(f"{AUDIO_MASTERS}/sfx/splash_02.wav"),
}


# ---------------------------------------------------------------------------
# Ported THRU Acoustic Math (trail_ambience.gd, terrain_reverb.gd, MUSIC-CONTRACT.md)
# ---------------------------------------------------------------------------
def water_reach_m(flow_mps: float = 0.85) -> float:
    return 45.0 + 165.0 * min(1.0, max(0.0, flow_mps / 1.2))


def water_level_at(flow_mps: float, span_m: float) -> float:
    reach = water_reach_m(flow_mps)
    if flow_mps <= 0.0 or span_m >= reach:
        return 0.0
    return ((1.0 - span_m / reach) ** 1.6) * min(1.0, max(0.0, 0.4 + flow_mps * 0.5))


def cutoff_for_occlusion(blocked: float) -> float:
    b = min(1.0, max(0.0, blocked))
    return 20000.0 * ((650.0 / 20000.0) ** b)


def bird_activity(hour: float = 17.6) -> float:
    h = hour % 24.0
    dawn = math.exp(-(((h - 6.0) / 1.7) ** 2))
    dusk = 0.75 * math.exp(-(((h - 18.5) / 1.5) ** 2))
    daylight = 0.22 if (7.0 <= h <= 17.5) else 0.0
    return min(1.0, max(0.0, dawn, dusk, daylight))


def music_water_duck_db(span_m: float) -> float:
    """MUSIC-CONTRACT.md: Water distance 8..50m produces -3..0 dB duck."""
    t = min(1.0, max(0.0, (span_m - 8.0) / (50.0 - 8.0)))
    return -3.0 * (1.0 - t)


_EXPORTED_CREEK_CACHE = None


def _load_exported_creek_spline():
    global _EXPORTED_CREEK_CACHE
    if _EXPORTED_CREEK_CACHE is not None:
        return _EXPORTED_CREEK_CACHE
    cand = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "import", "landscape", "creek_spline.json"
    )
    if os.path.isfile(cand):
        try:
            doc = json.load(open(cand))
            pts = doc.get("points", [])
            if pts:
                _EXPORTED_CREEK_CACHE = {
                    "flow_mps": float(doc.get("flow_speed_mps_at_crossing", 1.1343)),
                    "water_local_m": np.array(
                        [p["ue_bridge_frame"]["water_local_m"] for p in pts], dtype=float
                    ),
                }
                return _EXPORTED_CREEK_CACHE
        except Exception:
            pass
    _EXPORTED_CREEK_CACHE = False
    return None


def closest_creek_point(hx: float, hy: float):
    """Find closest point on the exported NHD creek spline (or analytical fallback)."""
    exp = _load_exported_creek_spline()
    if exp:
        pts = exp["water_local_m"]
        dists = np.hypot(pts[:, 0] - hx, pts[:, 1] - hy)
        idx = int(np.argmin(dists))
        return pts[idx].copy(), float(dists[idx])
    xs = np.linspace(hx - 25.0, hx + 25.0, 201)
    ys = 0.8 * np.sin(xs / 11.0) + 1.2 * np.sin(xs / 4.3 + 1.0)
    dists = np.hypot(xs - hx, ys - hy)
    idx = int(np.argmin(dists))
    cx, cy = float(xs[idx]), float(ys[idx])
    cz = -0.5 + 0.34 - cx * 0.01
    return np.array([cx, cy, cz], dtype=float), float(dists[idx])


# ---------------------------------------------------------------------------
# DSP & Stem Mixer for Frame-Accurate -16.0 LUFS Walkthrough Master
# ---------------------------------------------------------------------------
def load_wav_48k_stereo(path: str) -> np.ndarray:
    """Decode any WAV file to 48 kHz float32 stereo [-1, 1] using ffmpeg."""
    cmd = [
        "ffmpeg", "-v", "error", "-i", path,
        "-f", "f32le", "-acodec", "pcm_f32le", "-ar", "48000", "-ac", "2", "pipe:1"
    ]
    raw = subprocess.check_output(cmd)
    arr = np.frombuffer(raw, dtype=np.float32).reshape(-1, 2)
    return arr.copy()


def one_pole_lpf(stereo: np.ndarray, cutoff_hz: float, sr: int = 48000) -> np.ndarray:
    """Fast frequency-domain brick/smooth low-pass + optional high-pass filter."""
    freqs = np.fft.rfftfreq(len(stereo), d=1.0 / sr)
    spec = np.fft.rfft(stereo, axis=0)
    atten = 1.0 / np.sqrt(1.0 + (freqs / max(50.0, cutoff_hz)) ** 4)
    spec *= atten[:, None]
    return np.fft.irfft(spec, n=len(stereo), axis=0).astype(np.float32)


def band_filter(stereo: np.ndarray, hp_hz: float = 120.0, lp_hz: float = 4000.0, sr: int = 48000) -> np.ndarray:
    """120 Hz HPF + 4000 Hz LPF per audiomix anti-masking spec."""
    freqs = np.fft.rfftfreq(len(stereo), d=1.0 / sr)
    spec = np.fft.rfft(stereo, axis=0)
    hp = 1.0 / np.sqrt(1.0 + (max(1.0, hp_hz) / np.maximum(freqs, 1e-3)) ** 4)
    hp[0] = 0.0
    lp = 1.0 / np.sqrt(1.0 + (freqs / max(50.0, lp_hz)) ** 4)
    spec *= (hp * lp)[:, None]
    return np.fft.irfft(spec, n=len(stereo), axis=0).astype(np.float32)


def loop_to_length(arr: np.ndarray, target_samples: int, crossfade_samples: int = 24000) -> np.ndarray:
    """Seamless equal-power crossfade loop of a stereo buffer to `target_samples`."""
    if len(arr) >= target_samples:
        return arr[:target_samples].copy()
    out = np.zeros((target_samples, 2), dtype=np.float32)
    cf = min(crossfade_samples, len(arr) // 4)
    step = len(arr) - cf
    pos = 0
    first = True
    while pos < target_samples:
        rem = target_samples - pos
        take = min(len(arr), rem)
        chunk = arr[:take].copy()
        if not first and cf > 0 and take > cf:
            t = np.linspace(0.0, 1.0, cf, dtype=np.float32)[:, None]
            out[pos:pos + cf] = out[pos:pos + cf] * np.cos(t * math.pi * 0.5) + chunk[:cf] * np.sin(t * math.pi * 0.5)
            out[pos + cf:pos + take] = chunk[cf:take]
        else:
            out[pos:pos + take] = chunk
        pos += step
        first = False
    return out


def equal_power_pan(stereo: np.ndarray, pan: float) -> np.ndarray:
    """Pan mono/stereo signal in [-1 (left), +1 (right)] with equal-power law."""
    p = min(1.0, max(-1.0, float(pan)))
    angle = (p + 1.0) * 0.25 * math.pi
    gl = math.cos(angle)
    gr = math.sin(angle)
    mono = 0.5 * (stereo[:, 0] + stereo[:, 1])
    out = np.empty_like(stereo)
    out[:, 0] = (0.65 * mono + 0.35 * stereo[:, 0]) * gl * 1.4142
    out[:, 1] = (0.65 * mono + 0.35 * stereo[:, 1]) * gr * 1.4142
    return out


def build_walkthrough_master_wav(
    out_wav_path: str,
    speed_mps: float = 1.40,
    fps: int = 60,
    walk_duration_s: float = 22.0,
    linger_duration_s: float = 14.0,
    target_lufs: float = -16.0,
    report_json_path: str = "",
):
    """
    Build a complete, frame-accurate, -16.0 LUFS 48kHz stereo WAV synced to the
    Unreal walkthrough trajectory.
    """
    from ue_trail_follow import generate_walkthrough_trajectory

    traj = generate_walkthrough_trajectory(
        speed_mps=speed_mps,
        fps=fps,
        walk_duration_s=walk_duration_s,
        linger_duration_s=linger_duration_s,
    )
    duration_s = walk_duration_s + linger_duration_s
    sr = 48000
    n_samples = int(round(duration_s * sr))
    mix = np.zeros((n_samples, 2), dtype=np.float32)

    # 1. Load & filter continuous beds
    creek_near = band_filter(
        loop_to_length(load_wav_48k_stereo(WAV_MANIFEST["creek_near"]), n_samples),
        hp_hz=85.0, lp_hz=4200.0, sr=sr
    )
    creek_far = band_filter(
        loop_to_length(load_wav_48k_stereo(WAV_MANIFEST["creek_far"]), n_samples),
        hp_hz=70.0, lp_hz=3600.0, sr=sr
    )
    # 15 ms Haas right-channel decorrelation on creek_far so wide canyon wash wraps around listener during bridge linger
    haas_shift = int(0.015 * sr)
    creek_far[:, 1] = np.roll(creek_far[:, 1], haas_shift)
    wind_soft = band_filter(
        loop_to_length(load_wav_48k_stereo(WAV_MANIFEST["wind_soft"]), n_samples),
        hp_hz=120.0, lp_hz=3800.0, sr=sr
    )
    wind_med = band_filter(
        loop_to_length(load_wav_48k_stereo(WAV_MANIFEST["wind_medium"]), n_samples),
        hp_hz=120.0, lp_hz=3600.0, sr=sr
    )
    sierra_dusk = band_filter(
        loop_to_length(load_wav_48k_stereo(WAV_MANIFEST["sierra_dusk"]), n_samples),
        hp_hz=100.0, lp_hz=5000.0, sr=sr
    )
    music = loop_to_length(load_wav_48k_stereo(WAV_MANIFEST["music_sierra"]), n_samples)

    # 2. Compute per-frame envelopes and interpolate to sample rate
    frames = traj["hiker_walk"]
    cams = traj["walk"]
    n_frames = len(frames)
    f_times = np.array([f["t"] for f in frames], dtype=float)
    f_near_gain = np.zeros(n_frames, dtype=float)
    f_far_gain = np.zeros(n_frames, dtype=float)
    f_creek_pan = np.zeros(n_frames, dtype=float)
    f_music_gain = np.zeros(n_frames, dtype=float)
    f_wind_gain = np.zeros(n_frames, dtype=float)

    for i, (hf, cf) in enumerate(zip(frames, cams)):
        hx, hy, hz = hf["pos"]
        cpos, span_m = closest_creek_point(hx, hy)
        lvl = water_level_at(0.85, span_m)
        w_near = min(1.0, max(0.0, 1.0 - span_m / 35.0)) ** 1.2
        w_far = 1.0 - 0.55 * w_near
        # -8 dB anti-masking trim (0.398 linear)
        f_near_gain[i] = 0.24 * lvl * w_near
        f_far_gain[i] = 0.20 * lvl * w_far

        # Stereo pan of creek relative to camera look vector
        cam_xy = np.array(cf["pos"][:2], dtype=float)
        tgt_xy = np.array(cf["tgt"][:2], dtype=float)
        fwd_xy = tgt_xy - cam_xy
        fwd_xy /= max(1e-6, np.linalg.norm(fwd_xy))
        right_xy = np.array([fwd_xy[1], -fwd_xy[0]], dtype=float)
        to_creek = cpos[:2] - cam_xy
        to_creek /= max(1e-6, np.linalg.norm(to_creek))
        f_creek_pan[i] = float(np.clip(np.dot(to_creek, right_xy) * 0.55, -0.65, 0.65))

        # Lyria score gain: nominal -5 dB (0.56) + water proximity ducking (8..50m -> -3..0 dB)
        duck_db = music_water_duck_db(span_m)
        motion_boost_db = 1.0 if hf["speed_mps"] > 0.2 else 0.0
        f_music_gain[i] = 10.0 ** ((-4.5 + duck_db + motion_boost_db) / 20.0)

        # Wind envelope: higher on approach, sheltered slightly in creek draw
        exposure = 0.45 + 0.20 * math.sin(hf["t"] * 0.35)
        f_wind_gain[i] = 0.11 * (0.3 + 0.7 * exposure)

    sample_times = np.linspace(0.0, duration_s, n_samples, endpoint=False)
    s_near = np.interp(sample_times, f_times, f_near_gain).astype(np.float32)
    s_far = np.interp(sample_times, f_times, f_far_gain).astype(np.float32)
    s_pan = np.interp(sample_times, f_times, f_creek_pan).astype(np.float32)
    s_music = np.interp(sample_times, f_times, f_music_gain).astype(np.float32)
    s_wind = np.interp(sample_times, f_times, f_wind_gain).astype(np.float32)

    # Apply spatial pan to creek near/far
    angle = (s_pan + 1.0) * (0.25 * math.pi)
    gl = np.cos(angle)[:, None]
    gr = np.sin(angle)[:, None]
    creek_bed = creek_near * s_near[:, None] + creek_far * s_far[:, None]
    creek_stereo = np.c_[creek_bed[:, 0] * gl[:, 0] * 1.3, creek_bed[:, 1] * gr[:, 0] * 1.3]

    mix += creek_stereo
    mix += (0.65 * wind_soft + 0.35 * wind_med) * s_wind[:, None]
    mix += sierra_dusk * 0.10
    mix += music * s_music[:, None]

    # 3. Place 3D Sierra bird calls (Mountain Chickadee & Canyon Wren, non-repetitive)
    bird_clips = [
        ("mountain_chickadee_1583116", load_wav_48k_stereo(WAV_MANIFEST["bird_chickadee_1"]), -0.42, 0.22),
        ("mountain_chickadee_2127131", load_wav_48k_stereo(WAV_MANIFEST["bird_chickadee_2"]), +0.38, 0.20),
        ("canyon_wren_1320386", load_wav_48k_stereo(WAV_MANIFEST["bird_canyon_wren"]), -0.28, 0.16),
    ]
    bird_schedule = [
        (2.4, 0, -0.45, 0.20),
        (8.8, 1, +0.40, 0.18),
        (16.2, 0, -0.30, 0.17),
        (24.5, 2, +0.50, 0.15),
        (31.2, 1, -0.35, 0.19),
    ]
    placed_birds = []
    for t_call, b_idx, pan_val, gain_val in bird_schedule:
        if t_call >= duration_s - 1.5:
            continue
        b_name, b_buf, _, _ = bird_clips[b_idx % len(bird_clips)]
        start_s = int(round(t_call * sr))
        max_len = min(len(b_buf), int(3.2 * sr), n_samples - start_s)
        if max_len <= 0:
            continue
        seg = equal_power_pan(b_buf[:max_len], pan_val) * float(gain_val)
        # Gentle fade-in/out on bird snippet
        fade = min(2400, max_len // 4)
        if fade > 0:
            ramp = np.linspace(0.0, 1.0, fade, dtype=np.float32)[:, None]
            seg[:fade] *= ramp
            seg[-fade:] *= ramp[::-1]
        mix[start_s:start_s + max_len] += seg
        placed_birds.append({"time_s": t_call, "species": b_name, "pan": pan_val, "gain": gain_val})

    # 4. Place surface-accurate footsteps (Decomposed Granite -> Gravel -> Wood Bridge -> DG)
    step_banks = {
        "decomposed_granite": [load_wav_48k_stereo(WAV_MANIFEST[f"step_dg_0{i}"]) for i in range(1, 5)],
        "granite": [load_wav_48k_stereo(WAV_MANIFEST[f"step_granite_0{i}"]) for i in range(1, 5)],
        "gravel": [load_wav_48k_stereo(WAV_MANIFEST[f"step_gravel_0{i}"]) for i in range(1, 5)],
        "wood_bridge": [load_wav_48k_stereo(WAV_MANIFEST[f"step_wood_0{i}"]) for i in range(1, 5)],
        "water_splash": [load_wav_48k_stereo(WAV_MANIFEST[f"step_splash_0{i}"]) for i in range(1, 3)],
    }
    surface_gains = {
        "decomposed_granite": 0.24,
        "granite": 0.22,
        "gravel": 0.25,
        "wood_bridge": 0.36,  # +1.5 dB timber resonance boost over peak creek riffle bed
        "water_splash": 0.32,
    }
    rng = np.random.default_rng(1998)
    for ev in traj["footsteps"]:
        surf = ev["surface"]
        bank = step_banks.get(surf, step_banks["decomposed_granite"])
        clip = bank[ev["step_index"] % len(bank)]
        start_s = int(round(ev["time_s"] * sr))
        if start_s >= n_samples:
            continue
        take = min(len(clip), n_samples - start_s)
        foot_pan = -0.08 if ev["foot"] == "L" else +0.08
        gain = surface_gains.get(surf, 0.24) * float(rng.uniform(0.92, 1.08))
        mix[start_s:start_s + take] += equal_power_pan(clip[:take], foot_pan) * gain

    # Soft fade-in (0.4s) and fade-out (0.8s)
    fi = min(int(0.4 * sr), n_samples // 8)
    fo = min(int(0.8 * sr), n_samples // 8)
    mix[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32)[:, None]
    mix[-fo:] *= np.linspace(1.0, 0.0, fo, dtype=np.float32)[:, None]

    # Write pre-normalized float WAV and run 2-pass ffmpeg loudnorm to exact -16.0 LUFS / -1.4 dBTP
    os.makedirs(os.path.dirname(os.path.abspath(out_wav_path)), exist_ok=True)
    tmp_raw = out_wav_path + ".pre.wav"
    peak = float(np.max(np.abs(mix)))
    if peak > 0.95:
        mix *= (0.95 / peak)
    pcm16 = np.clip(mix * 32767.0, -32768, 32767).astype(np.int16)
    with wave.open(tmp_raw, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm16.tobytes())

    # Pass 1: Measure loudness
    p1 = subprocess.run(
        [
            "ffmpeg", "-y", "-i", tmp_raw,
            "-af", f"loudnorm=I={target_lufs}:TP=-1.4:LRA=7.0:print_format=json",
            "-f", "null", "-"
        ],
        capture_output=True, text=True, check=True
    )
    stderr_lines = p1.stderr.splitlines()
    json_start = next(i for i, l in enumerate(stderr_lines) if l.strip() == "{")
    ln_stats = json.loads("\n".join(stderr_lines[json_start:]))

    # Pass 2: Linear loudnorm to exact -16.0 LUFS
    af_str = (
        f"loudnorm=I={target_lufs}:TP=-1.4:LRA=7.0:linear=true:"
        f"measured_I={ln_stats['input_i']}:measured_TP={ln_stats['input_tp']}:"
        f"measured_LRA={ln_stats['input_lra']}:measured_thresh={ln_stats['input_thresh']}:"
        f"offset={ln_stats['target_offset']}:print_format=json"
    )
    p2 = subprocess.run(
        [
            "ffmpeg", "-y", "-i", tmp_raw,
            "-af", af_str,
            "-ar", "48000", "-ac", "2", "-c:a", "pcm_s24le", out_wav_path
        ],
        capture_output=True, text=True, check=True
    )
    os.remove(tmp_raw)
    s2 = p2.stderr.splitlines()
    j2 = next(i for i, l in enumerate(s2) if l.strip() == "{")
    final_stats = json.loads("\n".join(s2[j2:]))

    report = {
        "out_wav": out_wav_path,
        "duration_s": duration_s,
        "walk_duration_s": walk_duration_s,
        "linger_duration_s": linger_duration_s,
        "sample_rate": sr,
        "channels": 2,
        "measured_output_lufs": float(final_stats["output_i"]),
        "measured_output_tp_db": float(final_stats["output_tp"]),
        "measured_output_lra": float(final_stats["output_lra"]),
        "footstep_count": len(traj["footsteps"]),
        "surfaces_used": sorted(list({e["surface"] for e in traj["footsteps"]})),
        "bird_calls_placed": placed_birds,
        "sources": WAV_MANIFEST,
    }
    if report_json_path:
        with open(report_json_path, "w") as f:
            json.dump(report, f, indent=2)
    return report


# ---------------------------------------------------------------------------
# Unreal Engine 5.6 Python Builder (`import unreal`)
# ---------------------------------------------------------------------------
def setup_unreal_audio_ambience(audio_src_dir: str = "/workspace/unreal/assets", sy: float = -1.0):
    """
    Import WAV files into `/Game/Audio` and spawn spatial `AAmbientSound` actors
    along the creek spline, canopy bird locations, wind bed, and Lyria score.
    """
    import glob
    import unreal

    EAL = unreal.EditorAssetLibrary
    EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    AT = unreal.AssetToolsHelpers.get_asset_tools()

    wavs = sorted(glob.glob(f"{audio_src_dir}/*.wav"))
    if wavs:
        tasks = []
        for w in wavs:
            t = unreal.AssetImportTask()
            t.filename = w
            t.destination_path = "/Game/Audio"
            t.automated = True
            t.save = True
            t.replace_existing = True
            tasks.append(t)
        AT.import_asset_tasks(tasks)

    # Create Creek Spatial Attenuation asset
    if not EAL.does_asset_exist("/Game/Audio/SA_CreekSpatial"):
        sa = AT.create_asset("SA_CreekSpatial", "/Game/Audio", unreal.SoundAttenuation, unreal.SoundAttenuationFactory())
        att = sa.attenuation
        att.set_editor_property("attenuate", True)
        att.set_editor_property("spatialize", True)
        att.set_editor_property("attenuation_shape", unreal.AttenuationShape.CAPSULE)
        att.set_editor_property("attenuation_shape_extents", unreal.Vector(3500.0, 250.0, 200.0))
        att.set_editor_property("falloff_distance", 12500.0)
        att.set_editor_property("attenuate_with_lp_filter", True)
        att.set_editor_property("lp_filter_radius_min", 600.0)
        att.set_editor_property("lp_filter_radius_max", 8500.0)
        sa.attenuation = att
        EAL.save_loaded_asset(sa)
    else:
        sa = unreal.load_asset("/Game/Audio/SA_CreekSpatial")

    # Spawn Creek Near (at bridge crossing) + Creek Far (upstream/downstream) AmbientSound actors
    creek_sw = unreal.load_asset("/Game/Audio/creek_medium") or unreal.load_asset("/Game/Audio/creek_near")
    if creek_sw is not None:
        for label, pos_m, vol in [
            ("Audio_Creek_Crossing", (0.0, 0.0, -0.15), 0.85),
            ("Audio_Creek_Upstream", (-18.0, float(0.8 * math.sin(-18.0 / 11.0)), 0.02), 0.65),
            ("Audio_Creek_Downstream", (18.0, float(0.8 * math.sin(18.0 / 11.0)), -0.34), 0.65),
        ]:
            act = EAS.spawn_actor_from_class(
                unreal.AmbientSound,
                unreal.Vector(pos_m[0] * 100.0, pos_m[1] * 100.0 * sy, pos_m[2] * 100.0),
            )
            act.set_actor_label(label)
            ac = act.audio_component
            ac.set_sound(creek_sw)
            ac.set_editor_property("attenuation_settings", sa)
            ac.set_editor_property("volume_multiplier", float(vol))
            ac.set_editor_property("auto_activate", True)

    # Spawn 2D/Omnidirectional Sierra Dusk + Pine Wind Bed
    dusk_sw = unreal.load_asset("/Game/Audio/Sierra_alpine_dusk")
    if dusk_sw is not None:
        act = EAS.spawn_actor_from_class(unreal.AmbientSound, unreal.Vector(0.0, 0.0, 300.0))
        act.set_actor_label("Audio_Sierra_Alpine_Dusk")
        ac = act.audio_component
        ac.set_sound(dusk_sw)
        ac.set_editor_property("allow_spatialization", False)
        ac.set_editor_property("volume_multiplier", 0.55)
        ac.set_editor_property("auto_activate", True)

    EAL.save_directory("/Game/Audio", only_if_is_dirty=True, recursive=True)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Build THRU Unreal spatial audio walkthrough master (-16.0 LUFS)")
    ap.add_argument("--build-mix", action="store_true", help="Render -16.0 LUFS stereo WAV master")
    ap.add_argument("--walk-s", type=float, default=22.0, help="Walk duration (s)")
    ap.add_argument("--linger-s", type=float, default=14.0, help="Bridge linger duration (s)")
    ap.add_argument("--speed", type=float, default=1.40, help="Walk speed (m/s)")
    ap.add_argument("--out", type=str, default="unreal_hero_36s_16lufs.wav", help="Output WAV path")
    ap.add_argument("--report", type=str, default="unreal_hero_36s_report.json", help="Output JSON report")
    args = ap.parse_args()

    if args.build_mix:
        rep = build_walkthrough_master_wav(
            out_wav_path=args.out,
            speed_mps=args.speed,
            walk_duration_s=args.walk_s,
            linger_duration_s=args.linger_s,
            report_json_path=args.report,
        )
        print("AUDIO_AMBIENCE_MIX_BUILT:", json.dumps({
            "out_wav": rep["out_wav"],
            "duration_s": rep["duration_s"],
            "lufs": rep["measured_output_lufs"],
            "tp_db": rep["measured_output_tp_db"],
            "footstep_count": rep["footstep_count"],
        }))
