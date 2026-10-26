# Godot → Unreal gaps

Source: fleet/thru `81a73b3b504cbb661b87c41ce056c6d244d4890c`; world-pack draft `b96f0632424b2bfd89852c4d199610450668c822`. Unreal baseline main `1c40470`, remote work/ue-port `ea07554`; work/ue-scale is absent. See GODOT_INVENTORY.md for every catalog/reference row and imported Unreal object.

## Closed in this scene

- 317 unique GLB/glTF files import into native Unreal meshes, mapping 351 asset ids, including 39 fauna/insect roster entries. External glTF buffers/textures retain their directory layout. Import success is not a claim that every regional asset appears in this Sierra shot.
- Winning THRU Jeffrey pine + red/white fir use f6_set2 lineage; eight HyperGrass variants, 15 understory/deadfall/snag entries, 15 granite entries, a trail marker, hiker, bridge, creek, and terrain are wired to the scene. Off-biome desert/coastal/urban props remain available in the imported catalog, not scattered into the Sierra.
- Original Godot skeletal idle/move/startled clips are retained. Close wildlife actors use native animation plus wander tracks. Niagara mesh particles add small butterfly/bird/insect swarms; pollen/dust use Niagara template emitters. Firefly systems are authored but gated off in daylight, enabled by dusk configuration.
- Eight licensed real recordings cover creek, wind, bird, insects and four surface footsteps. Unreal spatial ambient emitters and the rendered walk mix share procedural anchors/path data. Geographic and stone-type proxies are labeled in the audio manifest.
- Actual draft v2 explicit-placement schema is exported, independently JSON-schema validated, round-tripped, and consumed by Unreal scatter. Deterministic alternate seed supplies regeneration evidence.

## Deliberate exclusions and limits

- 25 Evermotion catalog/reference rows excluded before reading mesh payloads. Replacement canopy uses THRU trees. No AM283 raw source is staged, imported, or committed. CGTrader sword fern is copied/imported unchanged; granite material overrides occur in Unreal only.
- 13 .tscn references are Godot scene containers, not portable mesh files. Their useful callers/behavior are mapped in the inventory; Godot scene serialization is not executed in Unreal.
- Two unresolved dynamic/evaluation references (`res://assets/landmarks/vvr/%s.glb`, `res://evaluation_assets/wooded_proxy.glb`) are not concrete files at the pinned revision.
- Nine Godot audio references inventoried; eight selected real recordings form the new audio palette. No claim of a full Godot gameplay/audio-engine port.
- Region-specific plant/prop variety is imported broadly but only Sierra-appropriate subsets are active. This is an offline procedural scene/render pipeline, not networked gameplay or a complete PCT streaming implementation.
- Niagara swarms use baked static poses; larger foreground actors retain skeletal motion. Bird paths are coordinated wandering, not a steering/flocking simulation. Particle templates are engine-shipped building blocks, with source meshes and deterministic seed configured by the editor plugin.
- Existing Godot captures cover four comparable views and one creek reference; no matching Godot butterfly/critter capture exists. Contact sheet labels this explicitly. Godot was never run on Dell.
- Mirror `.complete` was absent while preparing assets. SCENE.md/FOLIAGE.md supplied written lessons; mesh inputs came from independently verified winning assets already present on the borrowed pod, not partial mirror files.

## Final observed quality limits

All six primary stills and the 18-second walk rendered, and alternate seed 19980030 changed placements and rendered successfully. Three inspected art passes are exhausted. The butterfly and critter close-ups remain obstructed, so visual acceptance fails despite successful runtime execution. Main views show improved bridge visibility and native hiker idle; remaining problems include oversized foreground plants, straight canal-like creek banks, mixed asset styles and a steep downward walk-camera pitch. Final quality: 4/10. Serialized placement scales retain age variety; explicit age labels are not exported.
