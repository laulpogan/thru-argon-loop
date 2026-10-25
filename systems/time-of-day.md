# System 4: Time of Day, Golden-Hour Sun, Sky Atmosphere, Volumetric Fog & Exposure (`time-of-day`)

Ported from THRU Godot 4 sources & Unreal SOTA brief:
- `godot/scripts/geo_atmosphere.gd` (Topocentric ephemeris sun/moon solver, `daylight`/`golden`/`twilight` curves, scale-height `altitude_haze`, 72-hour exponential `wetness_at` history, AgX tone mapping & exposure grading)
- `godot/scripts/celestial_ephemeris.gd` & `godot/scripts/celestial_math.gd` (Julian day `SEASON_EPOCH_JD = 2461100.5` + `trail_day` + solar longitude offset)
- `godot/shaders/geo_sky.gdshader` (Zenith `#2e66b5` high-altitude darkening, horizon haze blend, cloud deck transmittance)
- `reset/unreal/CAMERAS.json` & `reset/unreal/SOTA.md` (Hero golden-hour sun `sky_hour = 17.6`, `SingleLayerWater` snowmelt absorption/scattering, Dual-Lobe Beer-Lambert wet granite, Lumen + VSM console variables)

---

## 1. Astronomical & Geographic State for the Hero Scene (`route-hero.json`)

| Parameter | THRU Godot Value (`geo_atmosphere.gd` / `route-hero.json`) | Unreal Engine 5.6 Equivalent |
|---|---|---|
| **Location** | Middle Fork San Joaquin PCT Crossing (`pct-region-0029`) | Scene origin `(0, 0, DECK_Z)` = Bridge Center |
| **Coordinates** | `lat = 37.6538256° N`, `lon = -119.0800196° W` | Topocentric solar azimuth/elevation input |
| **Elevation ($z_{\text{ASL}}$)** | `2348.28 m` (`7,704 ft` High Sierra montane) | `altitude_haze = exp(-(2348.28 - 600) / 2400) = 0.4827` |
| **Calendar Date** | June 29, 1998 (`year = 1998`, `trail_day = 120` from March 1) | Summer solstice + 8 days (snowmelt peak, `snowSWE = 0` at crossing) |
| **Local Solar Hour** | `sky_hour = 17.6` (`17:36` / 5:36 PM local time) | Golden hour (`sun_elevation_deg = +9.0°`) |
| **Julian Day ($JD$)** | `2461100.5 + 120 + (17.6 - (-119.08 / 15.0)) / 24.0 = 2461221.564` | Ephemeris sample timestamp |
| **Sun Elevation / Pitch**| `+9.0°` above horizon ($\sin(\text{elev}) = 0.1564$) | `DirectionalLight` `Pitch = -9.0 deg` |
| **Sun Azimuth / Yaw** | `291.8°` WNW (or `-140.0°` offset from `hero_low` camera look vector) | Backlights creek riffles & wet granite cobbles toward camera |
| **Daylight / Golden Factors** | `daylight = smoothstep(-0.18, 0.22, 0.1564) = 0.903`, `golden = clamp(1 - |0.1564 - 0.10|/0.20, 0, 1) = 0.718` | Drives color temperature (`4100 K`), fog inscattering, and exposure |

---

## 2. Exact Unreal Engine 5.6 Actor & Component Settings

### 2.1 `ADirectionalLight` (`UDirectionalLightComponent` — Golden Hour Sun)
- **Mobility**: `EComponentMobility::Movable`
- **Rotation**: `Pitch = -9.0 deg`, `Yaw = atan2(hero_cam_dy, hero_cam_dx) - 140.0 deg` (`+24.6 deg` in `ue_main.py` scene space so sun backlights the water toward `hero_low` and `trail` cameras).
- **Intensity**: `10.0 lux` (`IntensityUnits = ELightUnits::Lux`, matching `CAMERAS.json`; or `6.5` if SkyAtmosphere transmittance is pre-multiplied).
- **Color & Temperature**:
  - `bUseTemperature = true`, `Temperature = 4100.0 K` (warm golden-hour amber).
  - `LightColor = LinearColor(1.0, 0.88, 0.74)` (blending Godot `_base_sun_color = #fff0d3` toward `GOLDEN_SUN = #ff9d52` by `golden * 0.75 = 0.538`).
- **Atmosphere & Volumetric Couplings**:
  - `bAtmosphereSunLight = true`, `AtmosphereSunLightIndex = 0`
  - `VolumetricScatteringIntensity = 1.35` (boosts god rays through Jeffrey pine trunks)
  - `bEnableLightShaftBloom = true`, `LightShaftBloomScale = 0.28`, `LightShaftBloomThreshold = 0.9`
  - `bEnableLightShaftOcclusion = true`, `OcclusionMaskDarkness = 0.45`
  - `LightSourceAngle = 0.535 deg` (realistic soft solar penumbra on Virtual Shadow Maps)

### 2.2 `ASkyAtmosphere` (`USkyAtmosphereComponent` — High-Altitude Sierra Air)
Ported from `geo_atmosphere.gd:74-86, 756-772` (`CLEAR_ZENITH = #2e66b5`, `thin_air = smoothstep(1500, 4000, 2348.28) = 0.339`):
- **Ground Radius**: `6360.0 km`, **Atmosphere Height**: `60.0 km`
- **MultiScatteringFactor**: `1.0`
- **RayleighScatteringScale**: `0.0331` (default) with **RayleighScattering**: `LinearColor(0.180, 0.400, 0.710, 1.0)` (`#2e66b5` deep Sierra zenith blue, avoiding milky cyan washout).
- **RayleighExponentialDistribution**: `8.0 km`
- **MieScatteringScale**: `0.003996 * altitude_haze = 0.00193` (clean high-altitude Sierra air at `2,348 m`).
- **MieAbsorptionScale**: `0.00044 * altitude_haze = 0.00021`
- **MieAnisotropy**: `0.82` (strong forward-scattering solar aureole over the creek canyon).
- **MieExponentialDistribution**: `1.2 km`
- **AerialPerspectiveViewDistanceScale**: `1.15`

### 2.3 `ASkyLight` (`USkyLightComponent`)
- **Mobility**: `EComponentMobility::Movable`
- **bRealTimeCapture**: `true` (captures `SkyAtmosphere` + `VolumetricCloud` + distant granite domes every frame).
- **IntensityScale**: `1.05` (balanced with `10.0 lux` sun so shadow side of granite boulders retains cool sky fill without flattening contrast).
- **bLowerHemisphereIsBlack**: `true`, `LowerHemisphereColor = LinearColor(0.04, 0.035, 0.03, 1.0)` (matches `geo_atmosphere.gd:557` `ground_bottom_color = top.darkened(0.3)`).

### 2.4 `AExponentialHeightFog` (`UExponentialHeightFogComponent` — Volumetric God Rays & Valley Haze)
Ported from `geo_atmosphere.gd:83-86, 610-616`:
$$\text{altitude\_haze} = \text{clamp}\!\left(e^{-(z_{\text{ASL}} - 600)/2400},\; 0.35,\; 1.35\right) = 0.4827$$
- **FogDensity**: `0.0035` (reduced from `0.006` so distant domes and sky remain crisp rather than milky, per iter1/iter2 critic feedback).
- **FogHeightFalloff**: `0.22` (concentrates mist in the cold-air pool along the creek channel).
- **FogInscatteringLuminance**: `LinearColor(0.85, 0.68, 0.48, 1.0)` (warm golden-hour haze).
- **DirectionalInscatteringExponent**: `12.0`, **DirectionalInscatteringColor**: `LinearColor(1.0, 0.72, 0.42, 1.0)`.
- **bEnableVolumetricFog**: `true`
- **VolumetricFogScatteringDistribution**: `0.68` (forward scattering for visible golden-hour shafts between conifer trunks).
- **VolumetricFogAlbedo**: `Color(245, 220, 185, 255)`
- **VolumetricFogExtinctionScale**: `1.15`
- **VolumetricFogDistance**: `8000.0 cm` (`80 m`)

### 2.5 `APostProcessVolume` (`FPostProcessSettings` — Exposure, Tonemap & Grade)
Ported from `GeoAtmosphere.grade()` (`geo_atmosphere.gd:136-163`):
- **bUnbound**: `true`
- **Exposure**:
  - `MeteringMode = EAutoExposureMethod::AEM_Histogram` (or `AEM_Manual` with `AutoExposureBias = -0.35` to lock exposure across the 5 stills and walkthrough).
  - `AutoExposureBias = -0.35`
  - `AutoExposureMinBrightness = 0.45`, `AutoExposureMaxBrightness = 1.65` (prevents sky blowout while keeping dark wet granite readable).
- **Color Grading (`AGX_CONTRAST = 1.3`, `SATURATION = 1.1` mapped to UE5 ACES Filmic)**:
  - `WhiteTemp = 6100.0`
  - `ColorSaturation = Vector4(1.06, 1.06, 1.06, 1.0)`
  - `ColorContrast = Vector4(1.12, 1.12, 1.12, 1.0)`
  - `FilmSlope = 0.88`, `FilmToe = 0.55`, `FilmShoulder = 0.26` (rolls off sunlit granite & water glints smoothly like Godot AgX `tonemap_agx_white = 3.5`).
- **Bloom & Glints (`GLOW_INTENSITY = 0.22`, `GLOW_THRESHOLD = 1.05`)**:
  - `BloomIntensity = 0.38`, `BloomThreshold = 1.05` (crisp sun glints on water riffles without milky full-screen haze).
  - `VignetteIntensity = 0.25`

---

## 3. Continuous Time-of-Day & Surface State Equations (`geo_atmosphere.gd`)

When driving the level dynamically across any `sky_hour` $\in [0, 24)$:
1. **Solar Altitude Factor**:
   $$\alpha = \sin(\text{sun\_elevation\_rad}), \qquad \text{daylight} = \text{smoothstep}(-0.18,\, 0.22,\, \alpha)$$
   $$\text{golden} = \text{clamp}\!\left(1.0 - \frac{|\alpha - 0.10|}{0.20},\; 0.0,\; 1.0\right), \qquad \text{twilight} = \max(0.0,\, 1.0 - 3.2|\alpha|)$$
2. **72-Hour Replayable Ground Wetness (`wetness_at`, `geo_atmosphere.gd:655-688`)**:
   - Constants: `WETNESS_HISTORY_HOURS = 72.0`, `WETNESS_STEP_HOURS = 0.5`, `WETNESS_SOAK_HOURS = 2.0`, `WETNESS_DRY_HOURS = 10.0`.
   - Per half-hour step:
     $$w_{k+1} = \begin{cases} \text{lerp}(w_k,\, 1.0,\, 1 - e^{-0.5 / 2.0}) & \text{if raining} \\ w_k \cdot e^{-0.5 / 10.0} & \text{otherwise} \end{cases}$$
3. **Waterline Wetness Mask & Dual-Lobe Wet Slick Granite (`SOTA.md` #3 + `AAA-STANDARD.md`)**:
   - Height above creek water surface: $\Delta z = z_{\text{world}} - z_{\text{water}}(x)$.
   - Capillary/splash zone mask (`wet_band = 0.42 m` = `42 cm`):
     $$W(\mathbf{x}) = \text{saturate}\!\left(\frac{42.0\text{ cm} - \Delta z_{\text{cm}}}{42.0\text{ cm}} + 0.18 \cdot \text{noise}(\mathbf{x}_{xy})\right)$$
   - **Beer-Lambert Albedo Darkening (`SOTA.md` #3)**:
     $$\text{Albedo}_{\text{wet}} = \text{pow}(\text{Albedo}_{\text{dry}},\, 1.8) \times 0.35$$
   - **Roughness & Specular Transition**:
     $$\text{Roughness} = \text{lerp}(\text{Roughness}_{\text{dry}},\, 0.04,\, W), \qquad \text{Specular} = \text{lerp}(0.50,\, 0.58,\, W)$$
   - **Water Film Normal Flattening**:
     $$\mathbf{N}_{\text{final}} = \text{normalize}\!\left(\text{lerp}(\mathbf{N}_{\text{granite}},\, (0, 0, 1),\, 0.85\,W)\right)$$

---

## 4. Required Console Variables (`MoviePipelineConsoleVariableSetting`)

```ini
r.Lumen.TranslucencyReflections.FrontLayer.Enable=1
r.Lumen.Reflections.ScreenTraces=1
r.Lumen.Reflections.DownsampleFactor=1
r.Lumen.TraceMeshSDFs=1
r.Lumen.Scene.SurfaceCache.CardResolutionMultiplier=2.0
r.LumenScene.Radiosity.ProbeSpacing=2
r.Lumen.ScreenProbeGather.ScreenTraces.HZBTraversal.FullResDepth=1
r.Nanite.MaxNodesPerFrame=524288
r.Nanite.MaxCandidateClusters=4194304
r.Shadow.Virtual.ResolutionLodBiasDirectional=-1.5
r.Shadow.Virtual.SMRT.RayCountDirectional=16
r.Shadow.Virtual.Cache.MaxPageAge=128
r.VolumetricFog.GridPixelSize=4
r.VolumetricFog.GridSizeZ=128
r.MotionBlurQuality=0
r.DepthOfFieldQuality=4
r.Tonemapper.Sharpen=0.6
```

See **`reset/unreal/systems/ue_time_of_day.py`** for the copy-ready UE 5.6 Python script that spawns and configures the entire golden-hour lighting/atmosphere stack and provides the mathematical solver for any `(lat, lon, elevation_m, trail_day, sky_hour)`.
