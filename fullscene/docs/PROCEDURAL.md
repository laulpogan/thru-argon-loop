# Procedural scene and regeneration

## Live producer and caller

`src/generate.py` consumes the section heightmap/trail, `config/sierra.json`, and exported Godot library. It emits recentered terrain tiles, placements, life anchors, camera paths, surface steps, and a v2 placement chunk. `src/build_scene.py`, launched by Unreal's Python startup script, imports that chunk and places native foliage/HISM, library meshes, animated actors, Niagara systems and spatial audio. No unattached queue, scheduler or service is required.

Python data-driven scatter → Unreal InstancedFoliageActor/HISM is the chosen PCG equivalent. It permits deterministic headless regeneration, inspectable rule results, and direct schema integration without interactive graph authoring. The saved map contains native Unreal components; it is not a picture composited outside the engine.

## Coordinates and terrain checks

Generator coordinates are meters, X/Y horizontal and Z up, relative to 2347.261 m section elevation. Sixteen recentered 65×65 tiles cover 120×80 m of the section; a blended skirt carries the distant forest. GLB conversion and an axis probe determine Unreal handedness; engine units are centimeters. Imported tile bounds must match source within 1 cm. Five known source-grid vertices are collision traced against placed terrain before water, bridge or scatter; errors must stay below 3 cm. A missed trace aborts the build before art output.

The current input is the existing section DEM plus creek and trail data. The creek banks/trail are locally regraded for a traversable bridge, not an untouched survey reconstruction. Bridge and trail alignment are the only authored scene anchors. Cameras and all life/props derive from the generated section.

## Data rules

Every core stratum specifies elevation and slope ranges, signed water distance, trail distance, canopy shade, aspect bias, cluster strength, scale and optional age mixture. The generator samples source heights, gradients and downhill aspect. Shade is an analytic canopy-distance estimate, not ray-traced light. Cluster density is a seeded spatial field. Counts are targets with bounded rejection sampling; actual/requested counts and attempts are written to generation.json.

Jeffrey 90, red fir 65, white fir 55 targets; 18–22% saplings, minimum 3.7 m trunk separation, at least 3 m from trail, species-specific water/elevation/aspect limits. Outer forest uses the same terrain/skirt height producer, with 650 candidates and a dedicated broad forest envelope. This outer layer does not apply every core species filter.

Grass 42,000: eight HyperGrass species/variants, outside water and trail, scale 0.65–1.25 with variable height. These are HyperGrass, not the 5–32 cm Poly Haven tufts requiring >1 scaling. Understory 950: 15 entries including sedge, meadow, herbs, manzanita, shrubs, saplings, snags and deadfall; 430 granite placements share a single three-plane world material to avoid stretched UVs. Fern source remains unchanged. Camp/marker props use slope and proximity rejection rules.

Butterflies 18: near water, open canopy, limited slope; critters 8: dry banks; birds 12: canopy-shade and height gates; insects 25: open moist meadow. Camera closeups select nearby generated life anchors. Native skeletal clips provide gait/flutter, sequence transforms provide deterministic wander. Niagara meshes add small populations sharing these anchors; pollen near open butterfly habitat, dust near walk path, fireflies only at dusk. Pollen placement approximates sunlit openings via shade gating, not measured sun shafts. The daytime beauty renders do not claim visible fireflies.

Audio: creek anchors follow the moist-life/water corridor, bird/wind use canopy life anchors, insects use meadow insect anchors. Native AmbientSound actors use attenuation and spatialization. Walk footsteps select wood inside bridge envelope, gravel near creek and dirt otherwise; granite recording is available as an explicit stone proxy. Walk mix is offline ffmpeg mux using these path/emitter sidecars, because headless Movie Render Queue does not reliably emit the spatial audio track.

## World-pack adapter and section swap

Chunk conforms to `thru.chunk-placements/v2` from work/tb-worldpack-v2: explicit_instances, integer generator/seed descriptor, meter positions/quaternions/scales and provenance. The format is Y-up; adapter uses [x,z,y], yaw quaternion about Y and corresponding vertical scale. Chunk origin carries section elevation; Unreal works chunk-local and deliberately does not add it again. Upright yaw and equal horizontal scale are supported; unsupported rotations raise errors. scatter_strata is empty: do not imply a different PRNG reproduces encoded distributions. Wildlife positions/scales are consumed from the v2 chunk after identity/count checks; motion/phase remain a scene sidecar. No whole-world pack index or streaming importer is claimed.

On GPU pod, install code under /workspace/fullscene, then `python3 src/generate.py` and launch tools/launch.sh (installed as /workspace/fullscene/launch.sh). Set `SCENE_SEED=19980030` for alternate regeneration; default 19980029. The editor consumes out/worldpack-placements.json and rejects a stale seed. Re-render saved scenes with src/render_existing.py rather than rebuilding assets. Runtime config is run.json. Heightmap/trail inputs and conversion are currently in terrain.py/params.json and real/; swap those section inputs and elevation origin/rule biome config, regenerate, pass terrain gates, then render. Reprojection/regrading are section-specific; this is reusable with configured inputs, not an arbitrary-heightmap one-click claim.

Final art correction adds bridge/trail camera sightline clearance for trees/rocks, rock scale ×0.65, fauna clearance from boulder origins, native hiker idle, and explicit materials for previously untextured Sierra wood/ground. Imported young-pine proxy is omitted from active scatter; winning tree age variants supply saplings. Native marker receives plain wood to avoid insignia.

Niagara cache paths include seed/template/mesh/scale, so regeneration cannot silently reuse a system authored for another seed. Baked static fauna paths include source identity and applied scale.
