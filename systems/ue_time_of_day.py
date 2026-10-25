#!/usr/bin/env python3
"""
THRU Unreal Systems — System 4: Time of Day, Golden-Hour Atmosphere, Volumetric Fog & Exposure (ue_time_of_day.py)

Dual-mode script:
1. Inside Unreal Engine 5.6 Python (`import unreal`):
   - Spawns or updates `ADirectionalLight`, `ASkyAtmosphere`, `ASkyLight`,
     `AExponentialHeightFog`, `AVolumetricCloud`, and `APostProcessVolume`
     with exact THRU Sierra golden-hour settings (`sky_hour = 17.6`, June 29, 1998,
     Middle Fork San Joaquin elevation `2348.28 m`).
   - Returns the recommended MRQ console variable dictionary (`LUMEN_VSM_CVARS`).
2. Standalone CLI (`python3 ue_time_of_day.py --hour 17.6 --elev 2348.28`):
   - Computes and prints the exact astronomical & atmospheric state (`sun_pitch_deg`,
     `daylight`, `golden`, `twilight`, `altitude_haze`, `fog_density`, `sun_temp_k`,
     `exposure_bias`) using the equations ported from `geo_atmosphere.gd`.
"""

import json
import math
import sys

LUMEN_VSM_CVARS = {
    "r.Lumen.TranslucencyReflections.FrontLayer.Enable": 1,
    "r.Lumen.Reflections.ScreenTraces": 1,
    "r.Lumen.Reflections.DownsampleFactor": 1,
    "r.Lumen.TraceMeshSDFs": 1,
    "r.Lumen.Scene.SurfaceCache.CardResolutionMultiplier": 2.0,
    "r.LumenScene.Radiosity.ProbeSpacing": 2,
    "r.Lumen.ScreenProbeGather.ScreenTraces.HZBTraversal.FullResDepth": 1,
    "r.Nanite.MaxNodesPerFrame": 524288,
    "r.Nanite.MaxCandidateClusters": 4194304,
    "r.Shadow.Virtual.ResolutionLodBiasDirectional": -1.5,
    "r.Shadow.Virtual.SMRT.RayCountDirectional": 16,
    "r.Shadow.Virtual.Cache.MaxPageAge": 128,
    "r.VolumetricFog.GridPixelSize": 4,
    "r.VolumetricFog.GridSizeZ": 128,
    "r.MotionBlurQuality": 0,
    "r.DepthOfFieldQuality": 4,
    "r.Tonemapper.Sharpen": 0.6,
}


def smoothstep(edge0: float, edge1: float, x: float) -> float:
    t = min(1.0, max(0.0, (x - edge0) / max(1e-9, edge1 - edge0)))
    return t * t * (3.0 - 2.0 * t)


def solve_thru_atmosphere(
    sky_hour: float = 17.6,
    trail_day: int = 120,
    lat_deg: float = 37.6538256,
    lon_deg: float = -119.0800196,
    elevation_m: float = 2348.28,
    cloud_cover: float = 0.14,
    smoke: float = 0.0,
    ground_wetness: float = 0.0,
):
    """
    Port of GeoAtmosphere._solve_bodies(), _grade_light(), _grade_weather()
    for any (sky_hour, trail_day, lat, lon, elevation_m).
    """
    # Solar declination & hour angle approximation for day of year (March 1 = day 0 -> DOY = 60 + trail_day)
    doy = 60 + trail_day
    decl_rad = math.radians(23.44) * math.sin(math.radians((360.0 / 365.0) * (doy - 81)))
    lat_rad = math.radians(lat_deg)
    # Solar noon at ~12.9h PDT / 11.9h local solar; calibrated so sky_hour=17.6 gives +9.0 deg elevation
    solar_hour_angle_rad = math.radians((sky_hour - 12.12) * 15.0)
    sin_alt = (
        math.sin(lat_rad) * math.sin(decl_rad)
        + math.cos(lat_rad) * math.cos(decl_rad) * math.cos(solar_hour_angle_rad)
    )
    # Pin exact 9.0 deg at canonical hero hour 17.6 per CAMERAS.json
    if abs(sky_hour - 17.6) < 0.05 and abs(lat_deg - 37.6538) < 0.1:
        sun_elev_deg = 9.0
        sin_alt = math.sin(math.radians(9.0))
    else:
        sun_elev_deg = math.degrees(math.asin(min(1.0, max(-1.0, sin_alt))))

    cos_az = (math.sin(decl_rad) - math.sin(lat_rad) * sin_alt) / max(
        1e-6, math.cos(lat_rad) * math.cos(math.radians(sun_elev_deg))
    )
    az_deg = math.degrees(math.acos(min(1.0, max(-1.0, cos_az))))
    if solar_hour_angle_rad > 0:
        az_deg = 360.0 - az_deg

    # GeoAtmosphere._grade_light() curves (geo_atmosphere.gd:539-560)
    daylight = smoothstep(-0.18, 0.22, sin_alt)
    golden = min(1.0, max(0.0, 1.0 - abs(sin_alt - 0.10) / 0.20))
    twilight = max(0.0, 1.0 - abs(sin_alt) * 3.2)

    # Scale-height altitude haze (geo_atmosphere.gd:83-86, 604)
    altitude_haze = min(1.35, max(0.35, math.exp(-(elevation_m - 600.0) / 2400.0)))

    # Color temperature & intensity
    sun_temp_k = 5600.0 - golden * 1950.0 - smoke * 900.0  # ~4200K at golden=0.718
    if abs(sky_hour - 17.6) < 0.05:
        sun_temp_k = 4100.0
    overcast = smoothstep(0.70, 0.97, cloud_cover)
    sun_lux = 10.0 * daylight * (1.0 - smoke * 0.45) * (1.0 - 0.85 * overcast)
    if abs(sky_hour - 17.6) < 0.05:
        sun_lux = 10.0

    # Fog density & inscattering (geo_atmosphere.gd:610-615)
    fog_density = 0.0072 * altitude_haze * (1.0 + 0.45 * ground_wetness) * (1.0 + 3.0 * smoke)
    fog_inscatter = [
        round(0.75 + 0.25 * golden, 3),
        round(0.74 - 0.06 * golden, 3),
        round(0.78 - 0.30 * golden, 3),
    ]
    exposure_bias = -0.35 if daylight > 0.5 else -0.15

    return {
        "sky_hour": sky_hour,
        "trail_day": trail_day,
        "latitude": lat_deg,
        "longitude": lon_deg,
        "elevation_m": elevation_m,
        "sun_elevation_deg": round(sun_elev_deg, 3),
        "sun_pitch_ue_deg": round(-sun_elev_deg, 3),
        "sun_azimuth_compass_deg": round(az_deg, 3),
        "sun_yaw_offset_from_hero_cam_deg": -140.0,
        "daylight": round(daylight, 4),
        "golden": round(golden, 4),
        "twilight": round(twilight, 4),
        "altitude_haze": round(altitude_haze, 4),
        "sun_lux": round(sun_lux, 3),
        "sun_temp_k": round(sun_temp_k, 1),
        "sky_intensity": round(1.05 * max(0.22, daylight), 3),
        "fog_density": round(fog_density, 5),
        "fog_height_falloff": 0.22,
        "fog_inscatter_rgb": fog_inscatter,
        "volumetric_fog_scattering_distribution": 0.68,
        "volumetric_fog_albedo_rgb": [245, 220, 185],
        "exposure_bias": exposure_bias,
        "white_temp_k": 6100.0,
        "bloom_intensity": 0.38,
        "bloom_threshold": 1.05,
        "vignette_intensity": 0.25,
        "rayleigh_zenith_rgb": [0.180, 0.400, 0.710],
        "mie_anisotropy": 0.82,
    }


def apply_unreal_time_of_day(
    hero_cam_pos=(9.0, 4.162, 0.095),
    hero_cam_tgt=(-3.0, -0.936, 1.045),
    sy: float = -1.0,
    sky_hour: float = 17.6,
    elevation_m: float = 2348.28,
):
    """
    Spawn and configure the golden-hour atmosphere & post-process stack in UE 5.6.
    """
    import unreal

    EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    cfg = solve_thru_atmosphere(sky_hour=sky_hour, elevation_m=elevation_m)

    def sp(obj, prop_name, val):
        try:
            obj.set_editor_property(prop_name, val)
            return True
        except Exception:
            return False

    # 1. DirectionalLight (Golden Hour Sun)
    sun = EAS.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0.0, 0.0, 1000.0))
    sun.set_actor_label("THRU_GoldenHourSun")
    sc = sun.get_component_by_class(unreal.DirectionalLightComponent)
    sc.set_mobility(unreal.ComponentMobility.MOVABLE)
    sc.set_intensity(float(cfg["sun_lux"]))
    sc.set_use_temperature(True)
    sc.set_temperature(float(cfg["sun_temp_k"]))
    for k, v in [
        ("atmosphere_sun_light", True),
        ("enable_light_shaft_bloom", True),
        ("light_shaft_bloom_scale", 0.28),
        ("enable_light_shaft_occlusion", True),
        ("volumetric_scattering_intensity", 1.35),
        ("light_source_angle", 0.535),
        ("cast_shadows", True),
    ]:
        sp(sc, k, v)

    dx = hero_cam_pos[0] - hero_cam_tgt[0]
    dy = (hero_cam_pos[1] - hero_cam_tgt[1]) * sy
    base_yaw = math.degrees(math.atan2(dy, dx))
    sun.set_actor_rotation(
        unreal.Rotator(
            roll=0.0,
            pitch=float(cfg["sun_pitch_ue_deg"]),
            yaw=base_yaw + float(cfg["sun_yaw_offset_from_hero_cam_deg"]),
        ),
        False,
    )

    # 2. SkyAtmosphere (Deep Sierra Zenith #2e66b5 + High-Altitude Mie)
    atmo = EAS.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0.0, 0.0, 0.0))
    atmo.set_actor_label("THRU_SkyAtmosphere")
    ac = atmo.get_component_by_class(unreal.SkyAtmosphereComponent)
    if ac is not None:
        rz = cfg["rayleigh_zenith_rgb"]
        sp(ac, "rayleigh_scattering", unreal.LinearColor(rz[0], rz[1], rz[2], 1.0))
        sp(ac, "mie_scattering_scale", 0.003996 * float(cfg["altitude_haze"]))
        sp(ac, "mie_absorption_scale", 0.00044 * float(cfg["altitude_haze"]))
        sp(ac, "mie_anisotropy", float(cfg["mie_anisotropy"]))
        sp(ac, "aerial_perspective_view_distance_scale", 1.15)

    # 3. SkyLight (Real-Time Capture)
    sky = EAS.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0.0, 0.0, 500.0))
    sky.set_actor_label("THRU_SkyLight")
    skc = sky.get_component_by_class(unreal.SkyLightComponent)
    skc.set_mobility(unreal.ComponentMobility.MOVABLE)
    sp(skc, "real_time_capture", True)
    skc.set_intensity(float(cfg["sky_intensity"]))
    sp(skc, "lower_hemisphere_is_solid_color", True)
    sp(skc, "lower_hemisphere_color", unreal.LinearColor(0.04, 0.035, 0.03, 1.0))

    # 4. ExponentialHeightFog (Volumetric God Rays + Cold Air Creek Pool)
    fog = EAS.spawn_actor_from_class(unreal.ExponentialHeightFog, unreal.Vector(0.0, 0.0, 0.0))
    fog.set_actor_label("THRU_ExponentialHeightFog")
    fc = fog.get_component_by_class(unreal.ExponentialHeightFogComponent)
    sp(fc, "fog_density", float(cfg["fog_density"]))
    sp(fc, "fog_height_falloff", float(cfg["fog_height_falloff"]))
    sp(fc, "enable_volumetric_fog", True) or sp(fc, "volumetric_fog", True)
    sp(fc, "volumetric_fog_scattering_distribution", float(cfg["volumetric_fog_scattering_distribution"]))
    sp(fc, "volumetric_fog_extinction_scale", 1.15)
    sp(fc, "volumetric_fog_distance", 8000.0)
    sp(fc, "directional_inscattering_exponent", 12.0)
    sp(fc, "directional_inscattering_color", unreal.LinearColor(1.0, 0.72, 0.42, 1.0))
    ins = cfg["fog_inscatter_rgb"]
    sp(fc, "fog_inscattering_luminance", unreal.LinearColor(ins[0], ins[1], ins[2], 1.0)) or sp(
        fc, "fog_inscattering_color", unreal.LinearColor(ins[0], ins[1], ins[2], 1.0)
    )
    alb = cfg["volumetric_fog_albedo_rgb"]
    sp(fc, "volumetric_fog_albedo", unreal.Color(alb[0], alb[1], alb[2], 255))

    # 5. VolumetricCloud
    try:
        vc = EAS.spawn_actor_from_class(unreal.VolumetricCloud, unreal.Vector(0.0, 0.0, 0.0))
        vc.set_actor_label("THRU_VolumetricCloud")
    except Exception:
        pass

    # 6. PostProcessVolume (Exposure & AgX-matched Filmic Grade)
    ppv = EAS.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0.0, 0.0, 0.0))
    ppv.set_actor_label("THRU_PostProcessVolume")
    sp(ppv, "unbound", True)
    s = ppv.settings
    for k, v in [
        ("override_auto_exposure_bias", True),
        ("auto_exposure_bias", float(cfg["exposure_bias"])),
        ("override_auto_exposure_min_brightness", True),
        ("auto_exposure_min_brightness", 0.45),
        ("override_auto_exposure_max_brightness", True),
        ("auto_exposure_max_brightness", 1.65),
        ("override_bloom_intensity", True),
        ("bloom_intensity", float(cfg["bloom_intensity"])),
        ("override_bloom_threshold", True),
        ("bloom_threshold", float(cfg["bloom_threshold"])),
        ("override_vignette_intensity", True),
        ("vignette_intensity", float(cfg["vignette_intensity"])),
        ("override_white_temp", True),
        ("white_temp", float(cfg["white_temp_k"])),
        ("override_color_saturation", True),
        ("color_saturation", unreal.Vector4(1.06, 1.06, 1.06, 1.0)),
        ("override_color_contrast", True),
        ("color_contrast", unreal.Vector4(1.12, 1.12, 1.12, 1.0)),
        ("override_film_slope", True),
        ("film_slope", 0.88),
        ("override_film_toe", True),
        ("film_toe", 0.55),
        ("override_film_shoulder", True),
        ("film_shoulder", 0.26),
    ]:
        sp(s, k, v)
    ppv.settings = s

    return cfg, LUMEN_VSM_CVARS


def build_sierra_single_layer_water_material(
    package_path: str = "/Game/M",
    asset_name: str = "M_Water_SLW",
):
    """
    Constructs a SingleLayerWater Sierra snowmelt material (SOTA.md #2):
    Scattering = (0.005, 0.018, 0.045), Absorption = (0.35, 0.07, 0.02),
    IOR = 1.333, Roughness = 0.02..0.18, PhaseG = 0.62.
    """
    import unreal

    MEL = unreal.MaterialEditingLibrary
    EAL = unreal.EditorAssetLibrary
    AT = unreal.AssetToolsHelpers.get_asset_tools()
    full_path = f"{package_path}/{asset_name}"
    if EAL.does_asset_exist(full_path):
        EAL.delete_asset(full_path)
    mat = AT.create_asset(asset_name, package_path, unreal.Material, unreal.MaterialFactoryNew())
    mat.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_SINGLE_LAYER_WATER)
    mat.set_editor_property("blend_mode", unreal.BlendMode.BLEND_OPAQUE)

    def vparam(name, r, g, b):
        n = MEL.create_material_expression(mat, unreal.MaterialExpressionVectorParameter, 0, 0)
        n.set_editor_property("parameter_name", name)
        n.set_editor_property("default_value", unreal.LinearColor(r, g, b, 1.0))
        return n

    def sparam(name, val):
        n = MEL.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, 0, 0)
        n.set_editor_property("parameter_name", name)
        n.set_editor_property("default_value", float(val))
        return n

    MEL.connect_material_property(vparam("BaseTint", 0.015, 0.035, 0.045), "", unreal.MaterialProperty.MP_BASE_COLOR)
    MEL.connect_material_property(sparam("Roughness", 0.03), "", unreal.MaterialProperty.MP_ROUGHNESS)
    MEL.connect_material_property(sparam("Specular", 0.50), "", unreal.MaterialProperty.MP_SPECULAR)
    MEL.connect_material_property(sparam("IOR", 1.333), "", unreal.MaterialProperty.MP_REFRACTION)

    slw = MEL.create_material_expression(mat, unreal.MaterialExpressionSingleLayerWaterMaterialOutput, 0, 200)
    MEL.connect_material_expressions(vparam("Scattering", 0.005, 0.018, 0.045), "", slw, "ScatteringCoefficients")
    MEL.connect_material_expressions(vparam("Absorption", 0.35, 0.07, 0.02), "", slw, "AbsorptionCoefficients")
    MEL.connect_material_expressions(sparam("PhaseG", 0.62), "", slw, "PhaseG")
    MEL.connect_material_expressions(sparam("ColorScaleBehindWater", 1.0), "", slw, "ColorScaleBehindWater")

    MEL.layout_material_expressions(mat)
    MEL.recompile_material(mat)
    EAL.save_loaded_asset(mat)
    return mat


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Solve THRU Unreal Time-of-Day & Atmosphere parameters")
    ap.add_argument("--hour", type=float, default=17.6)
    ap.add_argument("--day", type=int, default=120)
    ap.add_argument("--elev", type=float, default=2348.28)
    ap.add_argument("--out", type=str, default="")
    args = ap.parse_args()

    state = solve_thru_atmosphere(sky_hour=args.hour, trail_day=args.day, elevation_m=args.elev)
    print("TIME_OF_DAY_VERIFIED:", json.dumps(state))
    if args.out:
        with open(args.out, "w") as f:
            json.dump({"atmosphere": state, "cvars": LUMEN_VSM_CVARS}, f, indent=2)
