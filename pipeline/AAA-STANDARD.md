# THRU AAA QUALITY BAR (Trailboss, 2:24 PM PT Oct 25; Paul: "build with AAA asset quality including textures maps etc")
Applies to EVERY lane, orchestrator, critic loop and pod job. Quality beats quantity: one asset that passes beats ten that do not.

## Every asset ships with
- Real geometry: silhouette-correct, no blobs; bevels/chips on rock edges; LOD0 + LOD1/LOD2 (+ impostor for trees); clean UVs, texel density ~1024 px/m hero, 512 px/m mid.
- FULL PBR map set, not flat colors: albedo (no baked lighting), normal (OpenGL/Godot convention), roughness, AO, height/displacement; metallic only if metal. 2K default, 4K for hero/close-up. Tileable where used as terrain/ground.
- Material states: dry / wet (darker albedo ~0.7x, roughness ~0.2-0.3, clearcoat) / dusty / snow where relevant, driven by waterline mask and global_wetness.
- Detail: micro-normal or detail texture for close-ups; moss/lichen/dirt masks on rocks; bark with height-blend; foliage with alpha-to-coverage, subsurface/translucency and wind sway.
- Placement rules (biome, elevation, slope, aspect, moisture, distance to water, density, clustering) and growth stages/variants.
- Reference-driven: compare against real Sierra/PCT photos; match scale (meters) and color (no oversaturation).

## Every scene/render uses
- Physically based lighting: directional sun with soft shadows, sky + ambient GI (SDFGI/VoxelGI or baked lightmaps in Godot; Cycles path tracing in Blender), volumetric fog, ACES/AgX tonemap, correct exposure.
- Water: reflection (SSR + reflection probe), refraction, depth fade showing streambed, caustics, riffle foam, flow normals.
- Post: SSAO/SSIL, TAA/FSR, subtle bloom; no flat uniform light.

## Gate
- Argon critic scores REFLECTION, WETNESS, DUST/ROUGHNESS, LIGHT QUALITY, GEOMETRY, TEXTURE each 0-10 against reference photos. Below 7 = iterate (fix list -> rerender -> recritique). Only >=7 goes to Trailboss for Paul review. Paul accepts assets; nothing counts until he does.
- Real renders only (Godot/Blender/UE). No image-gen repaints.
- Bulk/filler critique on gemini-3.8-flash; Argon reserved for hero creek, AFTER walkthrough, Unreal and final verdicts.
