# Port Note: celestial_sim

## 1. Overview
The `celestial_sim` module ports astronomical coordinate transformations, topocentric horizontal projections, IAU 1976 precession, USNO apparent sidereal time, and tabular NASA/JPL Sun and Moon ephemeris sampling from Godot GDScript (`godot/scripts/celestial_math.gd` and `godot/scripts/celestial_ephemeris.gd`) to engine-agnostic C++17 (`thru::CelestialMath`, `thru::CelestialEphemeris`) and Unreal Engine 5.6 wrappers (`UThruCelestialMathLibrary`, `UThruCelestialEphemeris`).

## 2. GDScript file:line -> C++ Symbol Mapping

### `godot/scripts/celestial_math.gd`
| GDScript File:Line | GDScript Symbol | C++ Symbol | Notes |
| :--- | :--- | :--- | :--- |
| `celestial_math.gd:4` | `const J2000: float = 2451545.0` | `thru::CelestialMath::J2000` | `constexpr double` |
| `celestial_math.gd:5` | `const EARTH_EQUATORIAL_RADIUS_AU: float = 4.263521e-5` | `thru::CelestialMath::EARTH_EQUATORIAL_RADIUS_AU` | `constexpr double` |
| `celestial_math.gd:6` | `const EARTH_FLATTENING_RATIO: float = 0.99664719` | `thru::CelestialMath::EARTH_FLATTENING_RATIO` | `constexpr double` |
| `celestial_math.gd:9` | `static func equatorial_vector(ra_degrees, dec_degrees)` | `thru::CelestialMath::equatorial_vector(double, double)` | Converts RA/Dec to unit `Vector3` |
| `celestial_math.gd:17` | `static func horizontal_direction(equatorial, jd, lat, lon)` | `thru::CelestialMath::horizontal_direction(Vector3, double, double, double)` | Horizon frame direction vector |
| `celestial_math.gd:21` | `static func j2000_horizontal_basis(jd, lat, lon)` | `thru::CelestialMath::j2000_horizontal_basis(double, double, double)` | Combined horizon * precession |
| `celestial_math.gd:25` | `static func horizon_basis(jd, lat, lon)` | `thru::CelestialMath::horizon_basis(double, double, double)` | Topocentric horizontal `Basis` |
| `celestial_math.gd:37` | `static func precession_basis(jd)` | `thru::CelestialMath::precession_basis(double)` | IAU 1976 orthonormalized precession |
| `celestial_math.gd:47` | `static func apparent_sidereal_degrees(jd)` | `thru::CelestialMath::apparent_sidereal_degrees(double)` | USNO sidereal rotation in [0, 360) |
| `celestial_math.gd:69` | `static func topocentric_equatorial(geocentric, dist_au, jd, lat, lon, elev)` | `thru::CelestialMath::topocentric_equatorial(...)` | Diurnal parallax displacement |
| `celestial_math.gd:97` | `static func _precess_vector(source, jd)` | `thru::CelestialMath::precess_vector(...)` | Private static precession helper |
| - | - | `thru::CelestialMath::azimuth(Vector3)` | Azimuth helper (from `atmosphere_check.gd:120`) |
| - | - | `thru::CelestialMath::altitude(Vector3)` | Altitude helper (from `atmosphere_check.gd:124`) |
| - | - | `thru::CelestialMath::fposmod(double, double)` | Positive float modulo helper |

### `godot/scripts/celestial_ephemeris.gd`
| GDScript File:Line | GDScript Symbol | C++ Symbol | Notes |
| :--- | :--- | :--- | :--- |
| `celestial_ephemeris.gd:4` | `const DEFAULT_PATH: String` | `thru::CelestialEphemeris::DEFAULT_PATH` | `"data/celestial/sun_moon_2026.tsv"` |
| `celestial_ephemeris.gd:6` | `var _jds: PackedFloat64Array` | `thru::CelestialEphemeris::jds_` | `std::vector<double>` |
| `celestial_ephemeris.gd:7` | `var _sun: PackedVector3Array` | `thru::CelestialEphemeris::sun_` | `std::vector<Vector3>` |
| `celestial_ephemeris.gd:8` | `var _sun_distance: PackedFloat64Array` | `thru::CelestialEphemeris::sun_distance_` | `std::vector<double>` |
| `celestial_ephemeris.gd:9` | `var _moon: PackedVector3Array` | `thru::CelestialEphemeris::moon_` | `std::vector<Vector3>` |
| `celestial_ephemeris.gd:10` | `var _moon_distance: PackedFloat64Array` | `thru::CelestialEphemeris::moon_distance_` | `std::vector<double>` |
| `celestial_ephemeris.gd:11` | `var _problem: String` | `thru::CelestialEphemeris::problem_` | `std::string` |
| `celestial_ephemeris.gd:15` | `static func load_default()` | `thru::CelestialEphemeris::load_default(DataSource*)` | Loads from DataSource/disk or embedded default |
| `celestial_ephemeris.gd:19` | `static func load_path(path)` | `thru::CelestialEphemeris::load_path(std::string, DataSource*)` | Loads specific file path |
| `celestial_ephemeris.gd:25` | `func is_valid()` | `thru::CelestialEphemeris::is_valid()` | Checks if `problem_` is empty |
| `celestial_ephemeris.gd:29` | `func problem()` | `thru::CelestialEphemeris::problem()` | Returns problem description string |
| `celestial_ephemeris.gd:33` | `func sample(body, julian_day)` | `thru::CelestialEphemeris::sample(std::string, double)` | Returns `thru::CelestialSample` |
| `celestial_ephemeris.gd:47` | `func _load(path)` | `thru::CelestialEphemeris::load(std::string, DataSource*)` | Parses TSV or JSON data |
| `celestial_ephemeris.gd:84` | `func _upper_bound(julian_day)` | `thru::CelestialEphemeris::upper_bound_jd(double)` | Binary search via `std::upper_bound` |
| `celestial_ephemeris.gd:95` | `func _sample_at(body, index, interpolated)` | `thru::CelestialEphemeris::sample_at(...)` | Knot sample extraction |
| - | - | `thru::CelestialEphemeris::moon_to_sun_direction(...)` | Relative vector helper (from `geo_atmosphere.gd:511`) |
| - | - | `thru::CelestialEphemeris::moon_illuminated_fraction(...)` | Moon phase helper (from `geo_atmosphere.gd:515`) |

### Unreal Engine 5.6 Wrappers
- `Unreal/ThruGame/Source/ThruGame/Public/ThruCelestialMathLibrary.h` & `Private/ThruCelestialMathLibrary.cpp`
  - `FThruBasis`: Blueprint struct holding `X`, `Y`, `Z` column vectors.
  - `UThruCelestialMathLibrary : public UBlueprintFunctionLibrary`: exposes `EquatorialVector`, `HorizontalDirection`, `J2000HorizontalBasis`, `HorizonBasis`, `PrecessionBasis`, `ApparentSiderealDegrees`, `TopocentricEquatorial`, `Azimuth`, `Altitude`.
- `Unreal/ThruGame/Source/ThruGame/Public/ThruCelestialEphemeris.h` & `Private/ThruCelestialEphemeris.cpp`
  - `FThruCelestialSample`: Blueprint struct holding `Equatorial`, `DistanceAu`, `bInterpolated`, `bValid`.
  - `UThruCelestialEphemeris : public UObject`: wraps `thru::CelestialEphemeris` and exposes `LoadDefault`, `LoadPath`, `LoadString`, `IsValid`, `GetProblem`, `GetSampleCount`, `Sample`, `MoonToSunDirection`, `MoonIlluminatedFraction`.

## 3. Deliberate Deviations
1. **Strongly-Typed Sample Struct**: In GDScript, `sample()` returns a dynamic `Dictionary` (`{"equatorial": Vector3, "distance_au": float, "interpolated": bool}`). In C++, `thru::CelestialSample` and `FThruCelestialSample` provide type safety, deterministic semantics, and a `valid` flag for out-of-range/error handling.
2. **Embedded Minimal Default Ephemeris**: To satisfy the core requirement for standalone testing and runtime resilience without hard disk path assumptions, `thru::CelestialEphemeris` embeds 16 JPL Horizons samples spanning March 1, 2026 to February 1, 2027. If no external TSV file is present at `DEFAULT_PATH`, `load_default()` automatically loads the embedded samples.
3. **Flexible Format Ingestion (TSV + JSON)**: In addition to reading the tab-delimited TSV format produced by `build_celestial_data.py`, `thru::CelestialEphemeris` also supports JSON array and JSON object formats via `nlohmann::json`, allowing data-source independence.
4. **`fposmod` Boundary Guard**: In double precision, small negative numbers like `-1e-16` can evaluate `-1e-16 + 360.0 == 360.0` due to floating-point rounding. `fposmod` guards `if (y > 0.0 && r >= y) r = 0.0;` so that angles are strictly inside `[0, y)`.

## 4. What Was Left Out and Why
- `godot/scripts/celestial_sphere.gd`: Excluded as specified in `MODULE_MAP.md`. It contains Godot rendering code (`MultiMeshInstance3D` star field instances and custom celestial quad shader materials) which is owned by Unreal Engine's Sky Atmosphere and directional lights.

## 5. Test Suite
- Test file: `tests/test_celestial_sim.cpp`
- Test framework: doctest 2.4.11
- Test cases:
  1. `Vector3 and Basis basic operations`: vector arithmetic, cross product, slerp, basis transformation.
  2. `CelestialMath::equatorial_vector cardinal transforms`: verifies vernal equinox, celestial poles, and unit norm.
  3. `CelestialMath::apparent_sidereal_degrees USNO algorithm`: verifies J2000 epoch and April 15 2026 campaign noon against USNO expressions.
  4. `CelestialMath::precession_basis IAU 1976 precession`: verifies identity matrix at J2000 and orthonormal basis in 2026.
  5. `CelestialMath::horizon_basis and horizontal_direction topocentric geometry`: verifies NCP points to Zenith at North Pole and northern horizon at Equator.
  6. `CelestialMath::topocentric_equatorial parallax correction`: verifies sub-radius bypass, lunar parallax shift at Mount Whitney, and minimal solar parallax.
  7. `CelestialEphemeris loading, problems, and error handling`: verifies uninitialized state, missing file error (`missing_ephemeris`), malformed file error (`malformed_ephemeris`), unordered dates (`unordered_ephemeris`), and empty file error (`empty_ephemeris`).
  8. `CelestialEphemeris embedded default and sampling`: verifies knot date coverage (March 2026 to February 2027), boundary clamping, and midpoint slerp/lerp interpolation.
  9. `CelestialEphemeris DataSource integration (TSV and JSON)`: verifies loading via `MemoryDataSource` for both TSV and JSON ephemeris tables.
  10. `CelestialEphemeris Moon illumination and phase geometry`: verifies full moon, new moon, and quarter moon fraction calculations.
- Module assertions: 122 assertions (all passing)
- Full test runner: 23 test cases, 11,979 assertions passing warning-free across both GCC and Clang (`-Wall -Wextra -Werror`).

MODULE_DONE
