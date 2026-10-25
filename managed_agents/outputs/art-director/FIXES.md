# THRU — Art Director Photoreal Critique & Technical Action Plan
**Project:** *THRU* (Photoreal Co-Op Pacific Crest Trail Thru-Hike)  
**Target Engine:** Unreal Engine 5.6.1 (Lumen GI & Reflections, Nanite Foliage & Geometry, Subsurface Profile Shading)  
**Target Biome & Setting:** High Sierra subalpine zone (~8,500–9,500 ft ASL) in late summer; JMT/PCT creek crossing at golden hour.  
**Deliverable File:** `FIXES.md`  

---

## 1. Photorealism Scores & Summary Table

| Render Still | Iteration & Shot Identifier | Score (/10) | One-Line Critique |
|---|---|---|---|
| Still 1 | `1505_hero_low_iter2-dense-route-hiker-pack-trees.png` | **2.5 / 10** | Suburban brown bridge with planar tile-textured abutments, noisy conifer cards, houseplant foliage, and a naked mannequin over opaque canal water. |
| Still 2 | `1505_wide_iter2-dense-route-hiker-pack-trees.png` | **2.8 / 10** | Airbrushed orange clay trail through a uniform yellow straw-mulch carpet; conifer trunks lack root flare, while stream channel resembles a man-made paved ditch. |
| Still 3 | `1505_hiker_iter2-dense-route-hiker-pack-trees.png` | **2.0 / 10** | Extreme close-up exposes untextured nude mannequin, sharp 90° unweathered bridge slats, stretched abutment UVs, and an untextured faceted polygon background mountain. |
| Still 4 | `1440_wide_iter1-first-render.png` | **1.2 / 10** | Stylized blockout with stacked green polygon cone trees, smooth orange clay terrain, and uniform orange soup fog; zero photoreal material response. |

*Scoring calibrated such that a raw 35mm / digital RAW photograph from Kings Canyon/Yosemite backcountry = 10.0.*

---

## 2. Real High Sierra Reference Gallery (Wikimedia Commons)

All reference photographs are verified Creative Commons (CC0, CC-BY, CC-BY-SA) assets documenting authentic late-summer High Sierra granite hydrology, subalpine conifers, rustic trail infrastructure, and PCT backpackers.

| Ref # | Scene / Subject | Wikimedia Commons File Page URL | Author / Credit | Licence | Technical Takeaway for THRU |
|---|---|---|---|---|---|
| **REF-01** | Authentic JMT Timber Footbridge (Thousand Island Lake outlet, Ansel Adams Wilderness) | [File:Thousand Island Lake bridge.jpg](https://commons.wikimedia.org/wiki/File:Thousand_Island_Lake_bridge.jpg) | Kaitymh | CC BY-SA 4.0 | Rough-hewn unpainted weathered grey timber stringers; split-log decking; dry-stacked granite slab rock cribbing/abutments; natural jointed granite bedrock integration. |
| **REF-02** | Backcountry Stream Crossing & Rustic Timber Footbridge (Bridalveil Creek, Pohono Trail, Yosemite) | [File:Bridge over Bridalveil Creek along the Pohono Trail - panoramio.jpg](https://commons.wikimedia.org/wiki/File:Bridge_over_Bridalveil_Creek_along_the_Pohono_Trail_-_panoramio.jpg) | Richard Wood | CC BY-SA 3.0 | Heavy round-log stringers with peeled-pole rustic handrail; boulder-strewn streambed; organic lodgepole needle duff bank transition; damp waterline staining on granite. |
| **REF-03** | Subalpine Creek, Boulders & Lodgepole Pine (Lyell Fork of the Tuolumne River, Tuolumne Meadows) | [File:Tuolumne Meadows - Lyell Fork of the Tuolumne River - 06.JPG](https://commons.wikimedia.org/wiki/File:Tuolumne_Meadows_-_Lyell_Fork_of_the_Tuolumne_River_-_06.JPG) | Jarek Tuszyński | CC BY 4.0 | Light-grey Sierra granodiorite (albedo sRGB 0.48–0.52); shallow, crystal-clear snowmelt over sorted gravel; late-summer golden-amber subalpine sedge (*Carex*) turf. |
| **REF-04** | Whitewater Flow, Granodiorite & Conifer Forest (Dana Fork Tuolumne River, Tioga Pass) | [File:Tuolumne River Dana Fork2.jpg](https://commons.wikimedia.org/wiki/File:Tuolumne_River_Dana_Fork2.jpg) | Starlingjon | CC BY-SA 3.0 | Glacially rounded granite boulders choking stream channel; turbulent aerated whitewater chits and foam lips; wet rock specular sheen (Roughness 0.15–0.25). |
| **REF-05** | PCT Thru-Hikers Silhouette & Full Ultralight Backpacking Kit (Alpine Lakes / PCT) | [File:PCT Thru-Hikers (5038335800).jpg](https://commons.wikimedia.org/wiki/File:PCT_Thru-Hikers_(5038335800).jpg) | Jason Hollinger | CC BY 2.0 | 45–55L technical roll-top pack; closed-cell foam pad; dual trekking poles with wrist wraps; dusty trail running footwear; technical sun-hoody & running shorts. |
| **REF-06** | Glacial Granite Bedrock, Talus & Subalpine Forest Margins (Ansel Adams Wilderness River) | [File:Ansel Adams Wilderness River.JPG](https://commons.wikimedia.org/wiki/File:Ansel_Adams_Wilderness_River.JPG) | Eric T Gunther | CC BY 3.0 | Massive exfoliation sheets with orthogonal joint fractures; decomposed granite (DG) sand bars; dark brown needle litter deposits in bedrock depressions. |

---

## 3. Detailed Per-Still Visual Analysis

### Still 1: `1505_hero_low_iter2-dense-route-hiker-pack-trees.png` (Score: 2.5)
- **Framing & Composition:** Low camera angle placed just above the stream surface looking toward the bridge span. Intended as a hero dramatic crossing shot.
- **Critical Flaws:**
  1. *Bridge Architecture:* The bridge looks like a pre-fabricated brown-painted steel/lumber footbridge from a municipal park or suburban greenway. It has clean, machine-planed rectangular 2x4 posts and dimensional lumber railings with flat uniform brown paint. It completely shatters the wilderness immersion of the High Sierra backcountry.
  2. *Bridge Abutments:* The bridge sits on two perfectly vertical, razor-edged planar piers textured with what appears to be vertically stretched flagstone wall cladding or interior tile siding. Real backcountry footbridges rest on dry-stacked granite rock cribbing or natural bedrock shelves.
  3. *Water Shader & Riverbanks:* The water has uniform horizontal wave troughs with zero directional flow momentum or velocity curls around the piers. The riverbanks are textured with a repeating decorative paving stone texture at a 45-degree angle.
  4. *Foliage & Assets:* Several giant broadleaved tropical houseplant / monstera-like broadleaf clusters are stuck onto the granite and bridge footing. Conifers behind the bridge are noisy, low-resolution alpha cards with burnt-brown coloring and telephone-pole trunks.
  5. *Hiker:* A completely naked, stylized low-poly mannequin is captured in a frozen stride on the bridge deck.
  6. *Sky / Mountain Backdrop:* Behind the trees sits a low-poly faceted sphere/dome with light grey and white polygon facets, looking like a raw blockout mountain mesh or default grid sphere.

### Still 2: `1505_wide_iter2-dense-route-hiker-pack-trees.png` (Score: 2.8)
- **Framing & Composition:** High-angle establishing wide shot overlooking the entire clearing, creek corridor, and approaching trail tread.
- **Critical Flaws:**
  1. *Ground Cover:* The entire forest floor is mapped with a uniform, repetitive texture resembling chopped straw, yellow hay, or hamster bedding. There is no decomposed granite (DG), no pine needle duff layer, no weathered granite grus, and no native alpine bunchgrass.
  2. *Trail Tread:* The trail is an airbrushed swath of saturated, reddish-orange clay (sRGB ~`0.78, 0.42, 0.18`). High Sierra trails are decomposed light grey/buff granite sand and crushed gravel (DG).
  3. *Hydrology:* The creek looks like a dual-stage man-made canal. The lower channel has paved flagstone retaining edges, while the upstream portion abruptly narrows into a weak trickle with smooth brown potato-shaped boulders sitting loosely on top of the straw texture.
  4. *Tree Placement & Anatomy:* The conifers are evenly spaced like tree farm saplings. Trunks are straight vertical cylinders with no root flares, no moss or lichen collar, and needle cards that appear desiccated and sparse.

### Still 3: `1505_hiker_iter2-dense-route-hiker-pack-trees.png` (Score: 2.0)
- **Framing & Composition:** Medium eye-level tracking shot focusing on the hiker traversing the bridge span.
- **Critical Flaws:**
  1. *Character Model & Animation:* The character is a completely untextured, low-poly nude beige mannequin (Quaternius style) with stylized polygon hair and bare feet. Despite the build note mentioning "pack PBR", the character carries zero backpack, zero trekking poles, wears no clothes, and lacks any trail gear.
  2. *Bridge Structural Details:* The camera proximity reveals zero wood grain, zero weathering, zero bolt/pin fasteners, and unrealistically razor-sharp bevels on the handrail timbers.
  3. *Foreground & Terrain Texture:* The foreground embankment shows severe vertical texture stretching on the cut bank. An isolated broadleaf plant sits unnaturally on the bare surface.
  4. *Background Mesh:* The faceted polygon mountain dome in the upper left is blatantly visible with hard-edged polygon triangles, destroying any illusion of scale or natural geology.

### Still 4: `1440_wide_iter1-first-render.png` (Score: 1.2)
- **Framing & Composition:** Iteration 1 wide blockout render of the creek and forest corridor.
- **Critical Flaws:**
  1. *Foliage Blockout:* Trees are stylized video game cones consisting of stacked green polygon pyramids on bright yellow-orange wooden cylinders.
  2. *Terrain & Material:* Terrain is faceted orange clay polygons; boulders are smooth, untextured brown rubber blobs.
  3. *Atmosphere:* Heavy, suffocating orange atmospheric fog washes out the background with zero rayleigh/mie separation or volumetric scattering nuance.

---

## 4. Deep Comparative Critique: Render vs. Real High Sierra

### A. Terrain & Granite Geology
- **Current Render:** Employs saturated orange clay soil, vertically stretched stone siding textures on vertical abutments, and paved flagstone shorelines. Boulders look like smooth, dark-brown river stones dropped arbitrarily on the surface.
- **Real Reference (REF-01, REF-03, REF-06):** High Sierra bedrock belongs to the Sierra Nevada Batholith, dominated by light-grey granodiorite and quartz monzonite.
  - *Color & Tone:* Base albedo is a cool, desaturated light grey: sRGB `(0.48, 0.49, 0.47)`, Linear `(0.19, 0.20, 0.18)` with dark biotite mica flakes and white plagioclase feldspar phenocrysts.
  - *Geomorphology:* Characterized by glacially polished exfoliation slabs, stepped horizontal sheet fractures, sharp orthogonal joints, and angular frost-shattered talus blocks.
  - *Lichen Colonization:* 15–35% surface coverage by crustose lichens, primarily vibrant chartreuse *Rhizocarpon geographicum* (sRGB `0.38, 0.44, 0.16`) and slate-black *Umbilicaria* / *Xanthoparmelia* (sRGB `0.12, 0.12, 0.11`).
  - *Trail Tread:* Composed entirely of decomposed granite (DG) gravel, coarse sand, and pulverized quartz/feldspar grus (sRGB `0.42, 0.38, 0.33`), never red clay.

### B. Conifer Species & Silhouettes
- **Current Render:** Low-poly conical pine skirts (iter1) or messy, noisy brown/khaki twig card brushes with dark telephone-pole trunks (iter2).
- **Real Reference (REF-02, REF-03, REF-04):** The riparian subalpine corridor (8,000–9,500 ft) is defined by three distinct conifer species:
  - *Lodgepole Pine (Pinus contorta subsp. murrayana):* Slender, upright trunks (DBH 0.3–0.7m, height 18–28m) with thin, scaly orange-grey "cornflake" bark (albedo sRGB `0.30, 0.26, 0.22`, Roughness `0.85`). Branching occurs in compact horizontal tiers with short, paired yellow-olive needles (Hue 88–94°, albedo sRGB `0.22, 0.26, 0.14`).
  - *Jeffrey Pine (Pinus jeffreyi):* Massive, majestic trees with thick cinnamon-red puzzle-piece bark plates separated by deep dark charcoal crevices (plate albedo sRGB `0.38, 0.24, 0.16`). Needles are long (8–10 in), bundled in threes, drooping in soft rounded tufts.
  - *Red Fir (Abies magnifica):* Narrow, spire-like crowns with stiff, tiered horizontal boughs and blue-green needles curving upward like bristles.
  - *Deadfall & Snags:* 10–15% of forest volume consists of weathered grey snags, lightning-struck spires, and fallen nurse logs bridging the creek or decaying on the banks.

### C. Ground Cover & Riparian Flora
- **Current Render:** Uniform straw-thatch mulch across all upland terrain, paired with isolated tropical broadleaf houseplant assets stuck onto granite rock faces.
- **Real Reference (REF-02, REF-03):** 
  - *Subalpine Sedges & Grasses:* Riparian borders feature dense, clumpy tufts of *Carex* sedges (*Carex heteroneura*, *Carex spectabilis*) and alpine tufted hairgrass (*Deschampsia cespitosa*). By late August, tips cure to golden straw-amber (sRGB `0.46, 0.38, 0.18`), while bases retain olive-green chlorophyll (sRGB `0.25, 0.32, 0.14`).
  - *Subalpine Willows (Salix eastwoodiae / Salix orestera):* Dense, low-growing riparian scrub (0.6–1.5m tall) hugging the water margin with silvery-green lanceolate foliage.
  - *Forest Floor Duff:* Under pine canopies, ground cover transitions to a 1–3cm thick carpet of decomposed lodgepole/Jeffrey needles (sRGB `0.22, 0.16, 0.11`), weathered wood fragments, fallen Jeffrey pine cones (15–25cm length), and granite grus. Zero broadleaf tropical plants exist in the subalpine Sierra Nevada.

### D. Water Hydrology & Shading
- **Current Render:** Flat, viscous brown plane with artificial sinusoidal ripples, zero water clarity, zero underwater bed visibility, and paved cobblestone edges.
- **Real Reference (REF-03, REF-04):**
  - *Snowmelt Optical Properties:* High Sierra stream water is oligotrophic and exceptionally transparent. Shallow margins (<0.4m) are 100% clear, revealing submerged granite pebbles and golden sand bars. Deeper pools (1.0–2.5m) exhibit cyan-teal rayleigh absorption (Transmission sRGB `0.10, 0.38, 0.44`).
  - *Hydraulic Dynamics:* Fast snowmelt flow creates standing waves, eddy currents behind boulders, and aerated whitewater chits where water crests over rock ledges.
  - *Capillary Wetline:* Waterline on granite boulders exhibits a distinct 10–25cm dark damp perimeter (BaseColor multiplier `0.45`, Roughness `0.18–0.25`) caused by splash and capillary rise.

### E. Lighting, Air & Atmosphere
- **Current Render:** Iter1 uses dense orange smog; iter2 has flat, low-contrast ambient shadows, washed-out backdrops, and an untextured polygonal sky dome.
- **Real Reference (REF-01, REF-03):** High Sierra atmosphere at 9,000 ft is extremely thin and dry:
  - *Direct Golden Hour Sun:* Deep low-angle sunlight (elevation 12–16°) with high direct illuminance (~70,000–80,000 Lux) and low color temperature (~4,000–4,200 K).
  - *Clear Sky & Thin Air:* Minimal aerosol haze. Distant granite peaks maintain sharp contrast and crisp silhouettes; shadows are illuminated by a deep blue skylight (6,500–7,500 K ambient fill).
  - *Volumetric Light:* Warm sun rays (god rays) should emerge specifically through tree canopies via localized moisture or needle dust, not uniform scene smog.

### F. Bridge Scale & Backcountry Construction
- **Current Render:** Municipal suburban pedestrian overpass with painted dimensional brown 2x4 lumber, wide roadway, and vertical quarry-tile abutments.
- **Real Reference (REF-01, REF-02):** USFS / Wilderness Act construction mandates rustic native materials:
  - *Log Stringer Footbridge:* 2 to 3 debarked lodgepole pine or Douglas fir log stringers (diameter 40–55 cm) spanning the creek.
  - *Decking:* Split-log half-rounds or heavy rough-sawn dimensional timbers (3x10 inch or 4x12 inch unplaned planks), weathered to a silvery-grey patina (sRGB `0.40, 0.38, 0.35`, Roughness `0.85`), fastened with rusted steel drift pins.
  - *Railing:* A single-sided rustic peeled pole handrail (post diameter 12–15 cm, rail diameter 10 cm, height 1.05m), or simple log curbs without railings.
  - *Abutments:* Dry-stacked granite masonry cribbing using local granite slabs, interlocking seamlessly into native bedrock shelves.

### G. Hiker Model & Backpacking Gear
- **Current Render:** Low-poly nude beige mannequin running barefoot across the bridge without clothes, pack, or boots.
- **Real Reference (REF-05):** A late-summer Pacific Crest Trail thru-hiker is an ultra-endurance athlete carrying specialized technical ultralight gear:
  - *Pack:* 45–55L ultralight frameless or internal-frame roll-top pack (Hyperlite Mountain Gear DCF white/grey or Osprey Exos ripstop nylon).
  - *Bear Canister:* Mandatory High Sierra bear-resistant canister (BearVault BV500 translucent blue cylinder or Garcia black poly canister) strapped or packed.
  - *Sleeping Pad:* Therm-a-Rest Z Lite accordion closed-cell foam pad (yellow/silver) strapped externally.
  - *Trekking Poles:* Pair of adjustable carbon/aluminum trekking poles with natural cork grips and tungsten carbide tips.
  - *Apparel:* Lightweight UPF 50+ sun hoody (light grey, faded sage, or teal), technical running shorts (5 in inseam), dusty trail running shoes (Altra Lone Peak / Hoka Speedgoat style), dirty mini-gaiters, trucker hat or sun cape.

---

## 5. Prioritized Fix List (Engine-Actionable)

*Note: Per art-direction mandate, no Evermotion, Archmodels, HyperGrass, or CGTrader assets are permitted. All assets must use photogrammetric Nanite meshes (Megascans/Fab), procedural Houdini/PCG pipelines, or custom in-engine shaders.*

### Priority P0: Critical Immersion Breakers (Immediate Action)

1. **Delete Suburban Bridge & Build Authentic USFS Log Stringer Footbridge:**
   - Remove the brown-painted 2x4 municipal railing bridge and the planar tile-faced abutments.
   - Replace bridge deck with two 45cm-diameter debarked lodgepole pine log stringers spanned by 4x10-inch rough-sawn rustic weathered timber planks (UE Material: unpainted weathered silver-grey timber; Albedo sRGB `(0.40, 0.38, 0.35)`, Roughness `0.82–0.90`, Normal map with heavy grain fissures and split ends).
   - Install a single-sided peeled lodgepole log handrail (rail diameter 10cm, post diameter 14cm, top rail height 105cm above deck) fastened with oxidized iron lag bolts (Metallic `0.9`, Roughness `0.65`, Albedo sRGB `0.15, 0.14, 0.13`).
   - Replace vertical abutments with dry-stacked Nanite granite slab masonry cribbing anchored directly onto native bedrock shelves.

2. **Purge Tropical Broadleaf Assets & Spawn Native High Sierra Ground Cover:**
   - Delete all broadleaf houseplant / tropical monstera/fern meshes from stream edges and rock faces.
   - Author PCG (Procedural Content Generation) graph / Foliage Type for subalpine stream margins:
     - Clustered *Carex* sedge (*Carex heteroneura* / *Carex spectabilis*) with late-summer two-sided foliage material (Tip Albedo sRGB `0.46, 0.38, 0.18`, Base Albedo sRGB `0.25, 0.32, 0.14`, Subsurface Profile color `(0.38, 0.42, 0.16)`, Opacity `0.45`). Density: 25–40 clumps/m² along water margin (0–1.5m buffer), fading to 0 in dry zones.
     - Subalpine willow shrubs (*Salix eastwoodiae*): 0.8–1.4m height, clustered along stream banks (Density: 0.15 instances/m²).

3. **Replace Stylized Mannequin with Full Thru-Hiker MetaHuman & Ultralight Kit:**
   - Swap the nude Quaternius mesh for a fully rigged athletic MetaHuman thru-hiker.
   - Outfit character with:
     - Technical UPF sun hoody (Cloth Shading Model, Fuzz tint, Albedo sRGB `0.52, 0.58, 0.54`).
     - Ripstop nylon trail shorts (5-inch inseam, charcoal grey).
     - Trail running shoes with lugged Vibram soles; add DG dust vertex-color / decal layer over lower legs and shoes (Albedo sRGB `0.45, 0.40, 0.34`, Roughness `0.95`).
     - 50L ultralight backpack with roll-top closure, external side mesh holding 1L Smartwater bottle + Sawyer filter, strapped yellow/silver accordion foam sleeping pad.
     - Dual carbon trekking poles held in hands with wrist straps worn.
   - Set animation state to a brisk hiking traverse stride with pole plants, not a barefoot sprint.

4. **Fix Background Mountain Geometry & Sky Dome Artifacts:**
   - Eliminate the visible low-poly faceted dome mesh in the background.
   - Generate high-fidelity Nanite background mountain terrain (using USGS 1m LiDAR / DEM data of the Ritter Range or Cathedral Range), surfaced with light granodiorite rock and talus scree.

---

### Priority P1: Core Photorealism Upgrades (Materials, Hydrology & Lighting)

5. **Physically-Based Snowmelt Water Shader:**
   - Material Blend Mode: Translucent, Lighting Mode: *Surface Forward Shading* (UE 5.6 Lumen High Quality Translucency enabled).
   - Refraction Index (IOR): `1.333`.
   - Single Scattering Albedo / Water Color: Absorption coefficient `(0.45, 0.12, 0.04)`, Scattering coefficient `(0.08, 0.32, 0.40)`. Result: crystal-clear shallows (<0.5m) transitioning to rich alpine teal in 1.5m deep pools.
   - Flow Normal & Waves: Two panning normal maps driven by stream vector flow-map (Broad swell: Scale `250`, Speed `0.06`; Micro-chatter: Scale `40`, Speed `0.22`).
   - Distance Field Boulder Foam: Sample `DistanceToNearestSurface`; generate dynamic white foam lips and wake trails extending 0.3–0.8m downstream of granite boulders and bridge footings (Foam Albedo sRGB `0.94, 0.95, 0.95`, Roughness `0.25`, Opacity `0.85`).
   - Waterline Wetness Decal / RVT: Darken granite boulders and wood stringers within 20cm of the water plane (BaseColor * `0.42`, Roughness * `0.30`).

6. **Sierra Nevada Granite Material Calibration:**
   - Base Color: Desaturated light grey granodiorite, sRGB `(0.48, 0.49, 0.47)`, Linear `(0.19, 0.20, 0.18)`.
   - Roughness: `0.75 – 0.85`.
   - Detail Normal: Multi-scale micro-normal blending 1mm biotite/feldspar grain texture with 10cm exfoliation sheet peeling normal.
   - Lichen Biome Blend Layer: Tri-planar projection for crustose lichen:
     - Map Chartreuse *Rhizocarpon* (Albedo sRGB `0.36, 0.42, 0.15`, Roughness `0.92`) to upward-facing rock surfaces using World Normal Z clamped between `0.4` and `0.95`.
     - Map Dark Slate Lichen (Albedo sRGB `0.11, 0.11, 0.11`) to sheltered vertical crevices.

7. **Landscape Material & Trail Tread Rework:**
   - Replace the uniform yellow straw mulch with a multi-layer RVT landscape material:
     - **Layer 1: Decomposed Granite (DG) Soil:** Coarse sand and angular quartz grus (Albedo sRGB `0.44, 0.39, 0.33`, Roughness `0.88`, Normal with embedded 5–15mm gravel).
     - **Layer 2: Conifer Needle Duff:** Lodgepole pine needle litter (Albedo sRGB `0.22, 0.16, 0.11`, Roughness `0.92`), distributed heavily under conifer canopy projections via distance-to-tree mask.
     - **Layer 3: PCT Trail Tread:** Compacted DG gravel path (Albedo sRGB `0.40, 0.36, 0.30`, Roughness `0.82`) with subtle central foot-wear depression (10–15cm trail cup) and loose scree berms along edges. Eliminate all orange clay paint.

8. **Conifer Asset Replacement (Nanite Lodgepole & Jeffrey Pines):**
   - Replace low-poly card trees with Nanite conifer assets (50k–120k polygons per tree, zero alpha-card cutout overdraw):
     - **Lodgepole Pine:** Straight, slender trunks with orange-grey scaly bark (Albedo sRGB `0.30, 0.26, 0.22`, Roughness `0.85`). High crown of tiered branchlets; paired short needles with Subsurface Scattering (Color sRGB `0.32, 0.40, 0.16`).
     - **Jeffrey Pine:** Large specimen trees (DBH 1.2–1.8m) on upland terraces; jigsaw cinnamon bark plates with dark charcoal fissures; drooping 3-needle clusters.
     - **Trunk-Ground Integration:** Add 3D Nanite root collars extending into the DG soil; place contact ambient occlusion decals and needle duff rings around every tree base.

---

### Priority P2: Polish, Storytelling & Micro-Atmosphere

9. **Golden Hour Sun & High-Altitude Atmosphere Tuning:**
   - **Directional Light (Sun):**
     - Source Elevation: `14.5°`, Azimuth: `242°`.
     - Direct Illuminance: `75,000 Lux`.
     - Color Temperature: `4,200 K` (warm golden light).
     - Source Angle: `0.545°` (accurate solar disk penumbra).
     - Enable Contact Shadows: Length `0.12` (sharp contact grounding for boots, pebbles, sedge bases).
   - **Sky Atmosphere:**
     - Rayleigh Scattering: `(0.175, 0.409, 1.0)`, Scale Height `8.5 km`.
     - Mie Scattering: `0.0018` (crisp, razor-sharp High Sierra thin air).
     - Mie Absorption: `0.0004`, Anisotropy: `0.82`.
   - **Exponential Height Fog & Volumetrics:**
     - Fog Density: `0.0006` (very low global fog to preserve mountain clarity).
     - Fog Inscattering Color: sRGB `(1.0, 0.82, 0.64)`.
     - Volumetric Fog: Enabled, Grid Resolution: `128x128x64`, Scattering Distribution: `0.78`, Extinction Scale: `1.0`. Creates subtle sunbeams piercing conifer canopies without clouding the scene.
   - **Post-Process & Color Grading:**
     - ACES Tonemapping.
     - Auto Exposure EV100: Min `11.5`, Max `14.5`.
     - White Balance Temp: `6,100 K` (preserves golden sunlight warmth while keeping sky rich alpine cobalt).
     - Lumen Scene Detail: `2.0`, Final Gather Quality: `2.0`, Max Trace Distance: `25,000`.

10. **Micro-Foliage, Deadfall & Environmental Storytelling:**
    - Scatter 3–5 fallen, weathered grey lodgepole pine logs (diameter 25–40cm) along the stream bank and in the water.
    - Spawn fallen Jeffrey pine cones (15–20cm) and lodgepole pine cones (4–6cm) on needle duff beds.
    - Scatter fine granite grus, loose stones (1–5cm), and dry twigs along the PCT trail margin.
    - Add subtle wet footprints on the bridge timber decking leading in the direction of the hiker's path.

---

## 6. Implementation Verification Checklist

- [ ] All tropical broadleaf / houseplant meshes deleted from project level.
- [ ] Municipal brown bridge deleted; rustic log-stringer footbridge with peeled log railing installed.
- [ ] Quaternius nude mannequin replaced with fully clothed MetaHuman thru-hiker (backpack, poles, trail runners).
- [ ] Faceted polygon mountain dome replaced with USGS 1m LiDAR Nanite mountain geometry.
- [ ] Granite albedo tuned to sRGB `(0.48, 0.49, 0.47)`, Roughness `0.75–0.85`, with *Rhizocarpon* chartreuse lichen.
- [ ] Trail tread re-painted to decomposed granite (DG) sand/gravel; all bright orange clay removed.
- [ ] Straw/hay mulch replaced with duff and native *Carex* sedge turf.
- [ ] Water material upgraded to Lumen Forward Shading translucency with distance-field foam and clear snowmelt absorption.
- [ ] Sun tuned to 75,000 Lux @ 4,200 K; Mie scattering dropped to 0.0018 for authentic 9,000 ft High Sierra air.