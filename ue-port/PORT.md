# THRU Godot to Unreal 5.6 game-logic port: PORT.md

Status: **in progress**. This file is updated as modules land.

## Layout
- `ThruCore/`: an engine-agnostic C++17 core (namespace `thru::`) with no Unreal headers. It is deterministic: time is passed in explicitly and randomness uses a seeded `thru::Rng`, so co-op peers stay in sync.
- `Unreal/ThruGame/Source/ThruGame/`: thin UE 5.6 wrappers (subsystems, components and Blueprint function libraries) that own a core object and forward calls to it.
- `tests/`: doctest unit tests. Each check cites the GDScript `file:line` it encodes.
- `third_party/`: doctest 2.4.11 and nlohmann/json 3.11.3, both MIT, hash-pinned in `PINS.txt`. I picked these off the shelf instead of writing a test harness or JSON parser.

## Module map
See `MODULE_MAP.md`, which maps each GDScript file to its Unreal class, with dependencies and difficulty. The 92 GDScript paths it cites all exist in Thru-2 fleet/thru @ 101a52b4. The port order is in `port-jobs.tsv`: 16 modules, foundations first.

## Ported so far
| Module | GDScript | gcc | clang | tests |
|---|---|---|---|---|
| skeleton: rng, data_source | (new) | builds, -Werror | builds, -Werror | 4 cases (10155 assertions, mostly RNG sampling loops) |
| core_calendar | trail_calendar.gd | builds, no warnings | builds, no warnings | 6 cases / 82 assertions |
| celestial_sim | celestial_math.gd, celestial_ephemeris.gd | builds, no warnings | builds, no warnings | 10 cases / 122 assertions |

Total at this commit: **20 test cases, 10359 assertions, 0 failures under both g++ 11.4 and clang** (-Wall -Wextra -Werror). I re-ran this myself from a clean export of the files at this commit and read the full output (Oct 25 2026, 9:51 PM PT).
The UE 5.6 wrapper sources under `Unreal/` have **not been compiled yet**. They need UnrealHeaderTool and a .uproject, and no UE 5.6 pod is set up.

## Queued or in progress
trail_season_environment, weather_sim, wildfire_smoke, trail_phenology_ecology, hiker_metabolism, hiker_rhythm_fatigue, hiker_cohort_bubble, town_hours_schedule, town_resupply_logistics, town_commerce_services, trail_registers_journal, encounters_promises, campaign_journey_progression, film_camera_logic, campaign_parcels_logic, campaign_encounter_tasks, and review_fix_r1 (the review round 1 fixes). Every worker hits Gemini 429 quota errors, so progress is slow.

## Build
```
cmake -S ue-port -B build-gcc -DCMAKE_CXX_COMPILER=g++ && cmake --build build-gcc -j && build-gcc/thru_tests
cmake -S ue-port -B build-clang -DCMAKE_CXX_COMPILER=clang++ && cmake --build build-clang -j && build-clang/thru_tests
```

## Data
The shared world-pack at `/mnt/models/thru-worldpack/v2/` did not exist as of Oct 25 2026, 9:15 PM PT. Tables load through the `thru::DataSource` interface, so that format can be added later.

## Remaining effort
3 of 19 modules (foundations included) are ported and tested. 16 remain, plus a UE compile check of the wrappers. At the current quota-bound pace of about 1 module per 20-40 minutes with 6 workers, that is several more hours. [TBD: verify once quota frees]
