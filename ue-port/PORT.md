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
| skeleton: rng, data_source | (new) | builds, -Werror | builds, -Werror | 4 cases / 10155 assertions pass |

## Build
```
cmake -S ue-port -B build-gcc -DCMAKE_CXX_COMPILER=g++ && cmake --build build-gcc -j && build-gcc/thru_tests
cmake -S ue-port -B build-clang -DCMAKE_CXX_COMPILER=clang++ && cmake --build build-clang -j && build-clang/thru_tests
```

## Data
The shared world-pack at `/mnt/models/thru-worldpack/v2/` did not exist as of Oct 25 2026, 9:15 PM PT. Tables load through the `thru::DataSource` interface, so that format can be added later.

## Remaining effort
[TBD: updated as modules land]
