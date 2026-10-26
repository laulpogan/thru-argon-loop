# Port Note: core_calendar

## 1. Overview
The `core_calendar` module ports civil calendar date calculations, Pacific daylight/standard time switching, solar noon, daylight duration, sunrise/sunset, astronomical twilight, and clock formatting from Godot GDScript (`godot/scripts/trail_calendar.gd`) to engine-agnostic C++17 (`thru::TrailCalendar`) and an Unreal Engine 5.6 wrapper library (`UThruTrailCalendarLibrary`).

The logic implements Jean Meeus (*Astronomical Algorithms*, ch. 7) for civil calendar conversions from Julian day and NOAA general solar position equations for solar declination, equation of time, solar noon, and horizon crossings.

## 2. GDScript file:line -> C++ Symbol Mapping

| GDScript File:Line | GDScript Symbol | C++ Symbol | Notes |
| :--- | :--- | :--- | :--- |
| `trail_calendar.gd:5` | `const MONTHS: Array[String]` | `thru::TrailCalendar::MONTHS` | `std::array<std::string_view, 12>` |
| `trail_calendar.gd:6` | `const SHORT_MONTHS: Array[String]` | `thru::TrailCalendar::SHORT_MONTHS` | `std::array<std::string_view, 12>` |
| `trail_calendar.gd:7` | `const WEEKDAYS: Array[String]` | `thru::TrailCalendar::WEEKDAYS` | `std::array<std::string_view, 7>` |
| `trail_calendar.gd:9` | `const DST_START_JD: float = 2461107.9166666665` | `thru::TrailCalendar::DST_START_JD` | `constexpr double` |
| `trail_calendar.gd:10` | `const DST_END_JD: float = 2461345.875` | `thru::TrailCalendar::DST_END_JD` | `constexpr double` |
| `trail_calendar.gd:12` | `const HORIZON_DEGREES: float = -0.833` | `thru::TrailCalendar::HORIZON_DEGREES` | Refraction + solar radius |
| `trail_calendar.gd:15` | `const ASTRONOMICAL_DEGREES: float = -18.0` | `thru::TrailCalendar::ASTRONOMICAL_DEGREES` | Astronomical twilight depression |
| `trail_calendar.gd:19` | `static func utc_offset_hours(julian_day)` | `thru::TrailCalendar::utc_offset_hours(double)` | Returns -7.0 (PDT) or -8.0 (PST) |
| `trail_calendar.gd:24` | `static func civil(julian_day)` | `thru::TrailCalendar::civil(double)` | Returns `thru::CivilDate` struct |
| `trail_calendar.gd:47` | `static func label(julian_day)` | `thru::TrailCalendar::label(double)` | Returns `"Mon 20 Apr"` format |
| `trail_calendar.gd:53` | `static func clock_label(julian_day)` | `thru::TrailCalendar::clock_label(double)` | Returns `"HH:MM"` 24-hr clock |
| `trail_calendar.gd:59` | `static func daylight(julian_day, lat, lon)` | `thru::TrailCalendar::daylight(double, double, double)` | Returns `thru::Daylight` struct |
| `trail_calendar.gd:78` | `static func astronomical_twilight(...)` | `thru::TrailCalendar::astronomical_twilight(...)` | Returns `thru::AstronomicalTwilight` |
| `trail_calendar.gd:89` | `static func _horizon_crossing(...)` | `thru::TrailCalendar::horizon_crossing(...)` | Returns `thru::HorizonCrossing` |
| `trail_calendar.gd:125` | `static func hours_label(hours)` | `thru::TrailCalendar::hours_label(double)` | Formats decimal hours to `"HH:MM"` |
| - | - | `thru::TrailCalendar::J2000` | Defined as `2451545.0` to decouple from CelestialMath |
| - | - | `thru::TrailCalendar::weekday_index(std::string_view)` | Convenience helper returning index 0..6 |

### Unreal Engine 5.6 Wrappers
- Header: `Unreal/ThruGame/Source/ThruGame/Public/ThruTrailCalendarLibrary.h`
- Source: `Unreal/ThruGame/Source/ThruGame/Private/ThruTrailCalendarLibrary.cpp`
- USTRUCTs: `FThruCivilDate`, `FThruDaylight`, `FThruAstronomicalTwilight` (mirroring core structs)
- UCLASS: `UThruTrailCalendarLibrary : public UBlueprintFunctionLibrary` exposing pure static functions:
  - `UtcOffsetHours`
  - `Civil`
  - `Label`
  - `ClockLabel`
  - `Daylight`
  - `AstronomicalTwilight`
  - `HoursLabel`

## 3. Deliberate Deviations
1. **Return Types as Strongly-Typed Structs**: In GDScript, `civil()`, `daylight()`, and `astronomical_twilight()` return dynamic `Dictionary`. In C++, these are mapped to strongly-typed plain-old-data structs (`thru::CivilDate`, `thru::Daylight`, `thru::AstronomicalTwilight`, `thru::HorizonCrossing`) for performance, compile-time safety, and zero memory overhead.
2. **Decoupling J2000 Constant**: `trail_calendar.gd:95` in GDScript references `CelestialMath.J2000`. To prevent circular module dependencies (since `CelestialMath` depends on `TrailCalendar`), `thru::TrailCalendar::J2000 = 2451545.0` is declared directly on `thru::TrailCalendar`.
3. **NaN Safety in `hours_label`**: `hours_label` guards against `NaN` inputs (returning `"00:00"`) which can occur when solar crossings do not happen (polar day/night).

## 4. What Was Left Out and Why
Nothing from `godot/scripts/trail_calendar.gd` was left out. All constants, formulas, and formatting functions were completely and faithfully ported.

## 5. Test Suite
- Test file: `tests/test_core_calendar.cpp`
- Test framework: doctest 2.4.11
- Test cases:
  1. `thru::TrailCalendar UTC offset and DST transitions`: verifies 2026 DST boundaries (March 8 start, November 1 end), PST (-8.0) and PDT (-7.0).
  2. `thru::TrailCalendar civil date conversions`: verifies known epoch dates from `godot/tests/town_hours/check.gd` (April 15 2026 noon, April 19 2026 13:30), leap year February 29 handling, and day of year calculations.
  3. `thru::TrailCalendar labels and formatting`: verifies `label`, `clock_label`, and `hours_label` with wrapping past 24h, negative offsets, and NaN guards.
  4. `thru::TrailCalendar daylight calculations`: verifies solar noon, sunrise, sunset, day length, solar declination, polar day, and polar night against NOAA equations.
  5. `thru::TrailCalendar astronomical twilight`: verifies dawn, dusk, polar day (Arctic summer), and polar night (lat 88N Arctic winter).
  6. `thru::TrailCalendar weekday and month lookup tables`: verifies string arrays and `weekday_index`.
- Total test cases: 6
- Total assertions: 82 assertions (all passing)

MODULE_DONE
