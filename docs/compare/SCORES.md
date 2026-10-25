# Hero creek: Godot vs Unreal, Argon six-score AAA critic

Built 15:20 PT. Each set scored with one gemini-4-argon call against AAA-STANDARD.md, 0-10; 7 or above passes. Key: R=REFLECTION W=WETNESS D=DUST/ROUGHNESS L=LIGHT G=GEOMETRY T=TEXTURE.

- Top row: **Godot current best (Pitcrew full dry look-argon capture, 2:49 PM; add-on variant paused at 2:49)** (`godot-dry/`)
- Bottom row: **Unreal iter2** (`unreal/`, from reset/unreal/out/LOOP.md)
- Shots use the Unreal names from reset/unreal/CAMERAS.json. The Godot images are the closest existing framings (low, wet-cobble, detail, overview), not re-rendered from Unreal's cameras. No build has a hiker-in-frame shot yet.

| Shot | Build | R | W | D | L | G | T | Mean |
|---|---|---|---|---|---|---|---|---|
| hero_low | Godot | 2 | 1 | 2 | 3 | 2 | 2 | 2.0 |
| hero_low | Unreal | 3 | 2 | 2 | 3 | 1 | 2 | 2.2 |
| wet_stones | Godot | 1 | 1 | 2 | 2 | 2 | 2 | 1.7 |
| wet_stones | Unreal | 3 | 2 | 2 | 3 | 1 | 2 | 2.2 |
| trail | Godot | 2 | 1 | 2 | 3 | 2 | 2 | 2.0 |
| trail | Unreal | 2 | 1 | 2 | 3 | 1 | 1 | 1.7 |
| wide | Godot | 2 | 1 | 2 | 3 | 2 | 2 | 2.0 |
| wide | Unreal | 2 | 1 | 2 | 3 | 1 | 1 | 1.7 |
| **all** | Godot | 1.8 | 1.0 | 2.0 | 2.8 | 2.0 | 2.0 | **1.9** |
| **all** | Unreal | 2.5 | 1.5 | 2.0 | 3.0 | 1.0 | 1.5 | **1.9** |

## Critic notes
- **Godot / hero_low:** Water is an opaque silver/grey ribbon with harsh polygon/tile seams, zero refraction, no streambed visibility, and a tree growing straight out of the middle of the channel. Rocks are smooth low-poly blobs with a bright yellow artifact on the foreground boulder. No waterline wetness gradient.
- **Godot / wet_stones:** Camera is aimed at the bridge planks and stretched low-res railing texture rather than wet stones at the waterline. Planks are uniform black/charcoal with repetitive bolt placement; railing has severe UV stretching. Background scrub is repetitively stamped with flat lighting.
- **Godot / trail:** Water shader shows extreme rectangular grid tiling and looks like crinkled tin foil rather than flowing water. Creek banks have a visible wireframe/grid artifact and hard straight edges. Boulders lack bevels/chips and sit on top of terrain without contact AO or dirt blending.
- **Godot / wide:** Creek channel is an unnatural straight V-trench cut into the terrain with a tree trunk rooted directly in the water. Trail is a flat painted stripe with a 90-degree turn. Ground clutter and yellow bushes are uniformly scattered without biome clustering, and lighting lacks GI depth and soft shadow falloff.
- **Unreal / hero_low:** Fails AAA bar completely. Trees are primitive stacked cones with crushed black shadows (no GI/subsurface). Rocks are smooth amorphous blobs lacking bevels, chips, or fractures. Water has basic ripples and SSR but looks like murky olive plastic with no streambed refraction, caustics, or riffle foam. Waterline wetness is a thin white/glossy artifact rather than proper darkened albedo + roughness transition.
- **Unreal / wet_stones:** Close-up exposes severe geometry and material flaws. 'Stones' are rounded, melted-looking grey blobs clipped into smooth sand. Waterline has an unnatural bright/glossy fringe instead of physically based wet darkening (0.7x albedo, 0.2 roughness) on both rock and bank. Water is opaque murky green-grey with uniform sine-wave ripples. Background tree trunks sit on bare sand with zero ground cover, roots, or ambient occlusion.
- **Unreal / trail:** Right foreground tree shows paper-thin cone shells with crude alpha-fringe edges and untextured cylinder trunks. Trail/bank is a smooth, featureless tan mesh with repetitive micro-noise and zero pebbles, duff, pine needles, or displacement. Rocks look like grey foam pillows. Lighting has harsh directional shadows, blown-out white horizon, and dark, unlit foliage interiors.
- **Unreal / wide:** Wide angle highlights the blockout/placeholder nature of the scene. Identical low-poly cone trees arranged in a grid-like cluster with cylinder trunks intersecting smooth sand. Rocks are melted grey blobs repeated along the channel. No foliage variants, understory, bark height-blend, moss/lichen masks, or streambed depth fade. Far below the >=7 gate on every metric.

Also scored: Godot after-rain look-argon capture (2:31 PM) per-shot means: hero_low 2.2, wet_stones 1.8, trail 2.0, wide 2.2

Unreal LOOP.md (its own critic):
```
iter1 | overall: 2.0 | hero_low: 1.5, wet_stones: 2.5, trail: 2.0, wide: 2.0 | baseline initial render
iter2 | overall: 3.1 | hero_low: 3.5, wet_stones: 4.0, trail: 2.5, wide: 2.5 | smooth GLB normals, triplanar granite, clear hero_low cam, cobble clusters, dome reposition
```
