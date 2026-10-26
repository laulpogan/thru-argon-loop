# THRU asset DREAMLIST (full)

Owner: Paul Logan. Consumer: Pitcrew → gemini-4-argon writes **one Blender Python modeling script per item** (LODs, UVs, procedural PBR, glTF export), run headless on RunPod pods, turntable render.
Written 2026-10-25 (PT). Supersedes the first cut; same structure, more detail.

## Ground rules
- Everything original and CC0-style. Procedural generators (seed + species/type + age + season params) that emit LOD sets, not one-off sculpts.
- **Never** derive from, or cite as reference, Evermotion AM283, CGTrader, TurboSquid, ArtStation, Textures.com, Poliigon or any other purchased pack. Do not name pack files as generator references. References below are described in words from real PCT places.
- No logos, brand names or readable brand text on any item (gear, vehicles, signs).
- Order = priority. Ranked ID = `T<tier>-<nn>` (lower is sooner). Sub-variants share the ID with a letter suffix.

## Delivery spec (verbatim)
glTF 2.0 .glb with embedded PBR (baseColor/ORM/normal), metres, real-world scale, origin at base center, LOD0–2 as separate meshes named _LOD0/_LOD1/_LOD2, collision hull UCX_<name> for solid props. Drop into /mnt/models/thru-assets/<set>/<name>/ with <name>.glb, a turntable, and provenance.json (prompt, script hash, model, license CC0). Never overwrite in place; write <name>_v2 instead, because my Unreal lane imports new folders by hash and overwrites crash the live editor.

Field key per item: **Section/biome · Size (m) · Polys LOD0/LOD1/LOD2 (tris) · Materials · Variants · Visual reference.**
Foliage = masked (alpha-clip) two-sided cards with translucency in ORM-adjacent mask or baseColor alpha; bark/rock = opaque one-sided.

---

## TIER 1 — Hero scene: Sierra, Middle Fork San Joaquin creek crossing, wooden footbridge, golden hour
Set name: `hero-sierra`. The camera sits at the bridge looking up-canyon into low warm sun.

### T1-01 Distant Sierra ridgeline + granite skyline silhouettes (replaces grey ridge.glb blocks)
- **Hard rule: there must never be a visible map edge.** Ridges must close the full 360° horizon around the hero bowl, layered.
- T1-01a Near ridge wall (0.5–2 km): 800 × 300 × 400 m, 60k/20k/6k, baseColor/ORM/normal, granite with snow-free summer gullies, sparse conifer speckle baked into albedo. 4 variants.
- T1-01b Mid skyline (2–8 km): 3000 × 600 × 1200 m, 30k/10k/3k, low-frequency normal + aerial-perspective-friendly albedo (desaturated blue-grey). 6 variants that tile end to end.
- T1-01c Far crest silhouettes (8–30 km): 8000 × 1500 × 2500 m cards/shells, 8k/3k/1k, flat albedo with height-gradient haze; jagged Ritter/Banner-style volcanic-dark peaks and white Minarets-like spires. 4 variants.
- T1-01d Horizon ring skirt: closed 360° low-poly ring under the far layer, 10k/4k/1.5k, so no gap exists at any yaw or from any reachable point.
- Reference: Middle Fork San Joaquin canyon near Devils Postpile/Reds Meadow — glacially polished domes and steep side walls, jagged dark Ritter Range on the horizon, warm orange rim light on west faces, blue shadow on east faces at golden hour.

### T1-02 Footbridge variants
- T1-02a Single-log flattened stringer bridge with one handrail: 12 × 1.2 × 1.6 m, 18k/6k/2k, weathered silver-grey adzed top, bark remnants on underside, iron drift pins; baseColor/ORM/normal; UCX. 3 variants (span 8/12/16 m).
- T1-02b Twin-stringer plank deck bridge with log abutments and rock-filled cribs: 14 × 1.5 × 1.8 m, 30k/10k/3k, UCX. 2 variants (new boards / sun-checked).
- T1-02c Abutment kits: rock-filled timber crib and dry-laid granite abutment, 2 × 2 × 1.5 m, 8k/3k/1k, UCX. 2 each.
- Reference: USFS backcountry log bridges in the Ansel Adams Wilderness — grey sun-checked log, a single pole handrail, mossy wet ends, granite blocks bedded under the ends.

### T1-03 Creek streambed set
- T1-03a Submerged rounded cobbles: 0.1–0.4 m, 1.5k/500/150, wet-darkened albedo + low roughness, algae tint on top faces. 12 variants.
- T1-03b Emergent creek boulders with wet waterline band: 0.8–2.5 m, 6k/2k/600, UCX. 8 variants.
- T1-03c Gravel bar / point-bar decal meshes: 4 × 3 × 0.2 m, 4k/1.5k/400. 4 variants.
- T1-03d Bank undercut pieces with exposed roots and sod lip: 3 × 1 × 1 m, 8k/3k/1k, masked root cards. 4 variants.
- T1-03e Wet log / driftwood jam pieces: 2–6 m, 6k/2k/600, UCX. 5 variants.
- T1-03f Riffle foam/splash cards (mesh only, shader-ready flowmap UVs): 1 × 0.5 m, 200/100/50. 6 variants.
- Reference: clear shallow Sierra creek over granite — tan/grey cobbles, gold sun caustics, dark wet stone at the waterline, sedge tufts on bank.

### T1-04 Granite boulders and scree
- T1-04a Exfoliating rounded granite boulders: 1–4 m, 8k/2.5k/800, salt-and-pepper biotite flecks, lichen patches (green/orange crustose), UCX. 10 variants.
- T1-04b Glacier-polished slab outcrops (whaleback): 6 × 4 × 1.5 m, 12k/4k/1.2k, glossy polish patches + chatter marks in normal, UCX. 5 variants.
- T1-04c Angular talus blocks: 0.3–1.5 m, 2k/700/200, UCX. 12 variants.
- T1-04d Scree/grus fan meshes: 5 × 5 × 1 m, 6k/2k/600. 4 variants.
- T1-04e Glacial erratic perched on slab: 3 m, 10k/3k/1k, UCX. 2 variants.
- Reference: Yosemite/Ansel Adams granite — pale grey with warm iron staining, black water streaks, exfoliation sheets peeling like onion skin.

### T1-05 Sierra conifers (each species: young, mature, snag)
- T1-05a Jeffrey pine: young 6 m / mature 35 m / snag 25 m; 40k/12k/3k (mature), plus billboard impostor LOD2; orange-cinnamon jigsaw-puzzle bark plates, long needles in bundles of 3, large prickly cones; bark opaque, needles masked two-sided. 3 each = 9.
- T1-05b Lodgepole pine: 5 / 25 / 18 m; thin scaly grey-tan bark, twisted 2-needle bundles, straight narrow crown. 3 each = 9.
- T1-05c Red fir: 5 / 40 / 28 m; deep red-brown furrowed bark, tiered short branches, dense spire. 3 each = 9.
- T1-05d Western white pine: 5 / 35 / 25 m; checkered grey bark, long slim curved cones, horizontal long branches. 3 each = 9.
- Shared: fallen log and stump per species (2 each), 6k/2k/600, UCX.
- Reference: mixed-conifer slopes above the Middle Fork — open stands, warm-lit trunks, silver snags with broken tops.

### T1-06 Understory
- T1-06a Greenleaf manzanita: 1.5 × 2 m, 12k/4k/1k, smooth mahogany-red bark, bright green upright leaves. 4.
- T1-06b Huckleberry oak: 1 × 1.5 m mat, 10k/3k/800, small grey-green leathery leaves. 4.
- T1-06c Willow (creekside thicket): 3 × 3 m, 15k/5k/1.2k, narrow leaves, red-brown stems. 4.
- T1-06d **Bracken fern (NOT sword fern)**: 0.8–1.2 m, 4k/1.2k/300, triangular tri-pinnate fronds on upright stalks, late-summer yellowing variant. 5.
- T1-06e Corn lily (Veratrum californicum): 1.5 m, 3k/1k/250, broad pleated leaves, white flower plume variant. 4.
- T1-06f Sedge and grass cards: 0.3–0.6 m clumps, 1.2k/400/100, masked. 8.
- T1-06g Lupine: 0.5 m, 2k/700/200, blue-violet spikes, palmate leaves. 4.
- T1-06h Indian paintbrush: 0.4 m, 1.5k/500/150, scarlet bracts. 3.
- All foliage: masked two-sided, translucency, wind vertex color (R=trunk, G=branch, B=leaf flutter).
- Reference: Sierra creekside meadow edge in late July — corn lily and willow along water, lupine and paintbrush in dry pockets, bracken on forest edge.

### T1-07 Trail kit (no logos, no brand text)
- T1-07a Tread edge rocks (borrow-pit set stones): 0.2–0.5 m, 1k/350/100, UCX. 10.
- T1-07b Rock water bar (angled, half buried): 2 × 0.4 × 0.3 m, 4k/1.5k/400, UCX. 3.
- T1-07c Log water bar with pin stakes: 2.5 m, 3k/1k/300, UCX. 2.
- T1-07d Rock and log steps: 1.2 × 0.4 × 0.25 m per step, 3k/1k/300, UCX. 4.
- T1-07e Cairns (duck stack, tall cairn): 0.3–1.2 m, 3k/1k/300, UCX. 4.
- T1-07f Generic trail junction sign: 4×4 timber post with routed board, generic arrows and blank/neutral placeholder text area, 1.8 m, 3k/1k/300, UCX. 3.
- T1-07g Generic trail marker: small diamond/post marker with neutral emblem, 1.2 m, 1k/400/100. 3.
- Reference: well-built Sierra trail through DG tread — fitted granite edge stones, angled drains, routed brown-stained wood signs gone grey.

### T1-08 Hiker gear props (generic, unbranded)
- T1-08a Internal-frame pack (full / dropped on ground): 0.75 × 0.35 × 0.25 m, 12k/4k/1k, nylon weave normal, UCX. 3.
- T1-08b Trekking poles pair (leaning / dropped): 1.3 m, 2k/700/200. 2.
- T1-08c Water bottles and soft flask: 0.25 m, 1.5k/500/150. 3.
- T1-08d Canister stove + pot: 0.15 m, 3k/1k/300. 2.
- T1-08e Bear canister: 0.3 m, 2k/700/200, UCX. 2.
- T1-08f Rolled foam pad, stuff sacks: 0.6 m, 2k/700/200. 3.
- T1-08g Boots/camp shoes on a rock: 0.3 m, 4k/1.5k/400. 2.
- Reference: a thru-hiker's break at a creek — pack against a boulder, poles across it, bottle being filled, faded saturated colors, dust on everything.

---

## TIER 2 — Rest of the trail by section
Same field rules; polys given LOD0/LOD1/LOD2 tris.

### Desert / SoCal (set `socal-desert`)
- T2-01 Chamise + mixed chaparral clumps · 1–2.5 m · 10k/3k/800 · masked two-sided · 6 · dense grey-green brush on Laguna-area slopes.
- T2-02 Chaparral yucca (rosette + bloom stalk) · 1–3 m · 6k/2k/500 · masked · 4 · glaucous spiky ball with tall cream panicle.
- T2-03 Joshua tree · 4–8 m · 25k/8k/2k + impostor · bark opaque, leaf clusters masked · 5 · shaggy branching trunks near Mojave crossing.
- T2-04 Cholla, barrel, beavertail cacti · 0.3–1.5 m · 6k/2k/500 · spines as masked cards · 6 · gold back-lit spines at sunset.
- T2-05 Creosote and sagebrush · 1–2 m · 6k/2k/500 · masked · 6 · olive shrubs on flat desert floor.
- T2-06 Peninsular granite tors and grus boulders · 2–8 m · 15k/5k/1.5k · UCX · 6 · weathered rounded corestones stacked on ridges.
- T2-07 Desert wash cobble and sand bar meshes · 5 m · 5k/1.5k/400 · 4 · dry braided wash.
- T2-08 Wind turbine silhouettes (generic, unbranded, distant) · 120 m · 4k/1.5k/400 · 3 · San Gorgonio Pass turbine rows.
- T2-09 Water cache (stacked jugs, crate) · 1 m · 4k/1.5k/400 · UCX · 3 · roadside desert water cache under shade.

### Sierra high country (set `sierra-high`)
- T2-10 Whitebark and foxtail pine (krummholz, mature, snag) · 2–15 m · 25k/8k/2k · 9 · twisted silver trees on windy passes.
- T2-11 Mountain hemlock · 5/25 m · 30k/10k/2.5k · 4 · drooping leaders near treeline.
- T2-12 Alpine lake shore kit (rock shelf, shoreline cobbles) · 10 m · 10k/3k/1k · UCX · 4 · deep blue tarn under a granite cirque.
- T2-13 Snowfields and suncups patches · 10 × 6 m · 6k/2k/500 · 4 · late-season dirty snow in north-facing gullies.
- T2-14 High pass switchback walls (dry-laid granite) · 6 × 1.5 m · 8k/3k/800 · UCX · 3 · Forester/Muir-pass-style stonework.
- T2-15 Alpine meadow turf and willow carpet · 5 m · 6k/2k/500 · masked · 4 · emerald meadow with meandering creek.

### NorCal / Oregon / Washington forest (set `pnw-forest`)
- T2-16 Douglas fir (young/mature/snag) · 8/50/35 m · 40k/12k/3k + impostor · 9 · thick corky bark, dense PNW stands.
- T2-17 Western hemlock and western red cedar · 8/45 m · 40k/12k/3k · 6 · droopy tops and stringy red bark.
- T2-18 Shasta red fir and ponderosa pine · 8/40 m · 40k/12k/3k · 6 · open NorCal ridges.
- T2-19 PNW understory: sword fern, salal, Oregon grape, vine maple, devils club · 0.5–3 m · 6k/2k/500 · masked · 10 · lush green Washington understory.
- T2-20 Moss-covered nurse logs and stumps · 4–10 m · 10k/3k/800 · UCX · 6 · rotting logs with seedlings.
- T2-21 Volcanic rocks: basalt columns, andesite talus, red scoria · 0.3–4 m · 6k/2k/600 · UCX · 10 · Lassen / Oregon Cascades lava terrain.
- T2-22 Huckleberry and beargrass patches · 0.5–1 m · 4k/1.2k/300 · masked · 6 · Washington subalpine ridges.
- T2-23 Distant volcano silhouettes (Shasta-, Hood-, Rainier-like generic cones, not exact replicas) · 3–5 km · 20k/6k/2k · 3 · snow-capped cone floating over forest haze.
- T2-24 Timber truss trail bridge (generic) · 20 m · 30k/10k/3k · UCX · 2 · Cascades footbridge over a glacial stream.

### Trail towns and highway crossings (set `towns`) — generic vehicles, no badges
- T2-25 Generic 1990s pickup (4x4) · 5.2 × 2 × 1.9 m · 30k/10k/3k · UCX · 3 colors.
- T2-26 Generic sedan and hatchback · 4.5 m · 25k/8k/2.5k · UCX · 4.
- T2-27 Generic forest-service-style utility truck (unmarked, no shield) · 5.5 m · 30k/10k/3k · UCX · 2.
- T2-28 Highway crossing kit: guardrail, culvert, postmile paddle (blank), trailhead pullout · 4–20 m · 6k/2k/500 · UCX · 6.
- T2-29 Small-town storefront modules (general store, post office, motel, diner) · 10–20 m · 30k/10k/3k · UCX · 6 · false-front wood buildings like Idyllwild/Sierra City.
- T2-30 Gas pump (generic), picnic table, trash/bear-proof bin, hiker box shelf · 1–2 m · 4k/1.5k/400 · UCX · 6.
- T2-31 Trailhead info kiosk (blank panels) · 3 m · 6k/2k/500 · UCX · 2.

### Camp (set `camp`)
- T2-32 Generic tents (dome, trekking-pole shelter, tarp) pitched + packed · 2.2 × 1.4 × 1.1 m · 10k/3k/800 · two-sided fabric · 6.
- T2-33 Sleeping bag, pad, ground sheet · 2 m · 4k/1.2k/300 · 4.
- T2-34 Fire ring (rock), small campfire logs (mesh only, VFX separate) · 1 m · 4k/1.2k/300 · UCX · 3.
- T2-35 Food bag hang line, bear box (generic) · 1.2 m · 4k/1.2k/300 · UCX · 3.
- T2-36 Camp clutter: socks on line, headlamp, mug, spoon, food wrappers (no brands) · 0.05–1 m · 1k/400/100 · 10.

---

## TIER 3 — Wildlife silhouettes and weather props
Wildlife = non-rigged or simple pose-set silhouettes for mid/far distance; 1–3 poses each.
- T3-01 Mule deer (doe, buck) · 1.0 m shoulder · 15k/5k/1.2k · 3 poses.
- T3-02 Black bear · 0.9 m · 15k/5k/1.2k · 3 poses.
- T3-03 Marmot and pika on rocks · 0.2–0.5 m · 5k/1.5k/400 · 2 each.
- T3-04 Steller's jay, Clark's nutcracker, raven (perched + flying) · 0.3 m · 3k/1k/250 · 2 each.
- T3-05 Rattlesnake coiled, horned lizard · 0.3–1 m · 4k/1.2k/300 · 2 each.
- T3-06 Bighorn sheep silhouette on ridge · 0.9 m · 12k/4k/1k · 2.
- T3-07 Hawk soaring silhouette · 1.2 m span · 2k/600/150 · 2.
- T3-08 Weather: cumulus/cloud cards and thunderhead billboards · 0.5–3 km · 500/200/50 · 8.
- T3-09 Weather: rain streak and snow flurry card meshes, mist/fog sheets for creek · 2–20 m · 200/100/50 · 6.
- T3-10 Weather: wind-blown dust devil mesh, lightning-struck snag · 2–25 m · 6k/2k/500 · 3.
- T3-11 Seasonal swaps: snow-loaded conifer crowns (shells for T1-05 species), frost on meadow · per species · 3 each.

---

## AUDIO SETS (last)
Delivered as 48 kHz 24-bit WAV, loop-points marked, CC0 provenance.json alongside, under /mnt/models/thru-assets/audio/<set>/.
- A-01 Footsteps per surface: decomposed-granite tread, granite slab, wood bridge deck, gravel/cobble, wet creek stones, shallow water wade, pine-needle duff, snow, sand, asphalt. 12 one-shots each, walk + run.
- A-02 Creek near (bridge position, 0–5 m) loop, 2 min, plus 6 splash/burble one-shots.
- A-03 Creek far (50–200 m) loop, 2 min.
- A-04 Wind in pines: light, moderate, gusting loops; separate needle-hiss and trunk-creak layers.
- A-05 Sierra birds: Steller's jay, mountain chickadee, Clark's nutcracker, hermit thrush (dusk), robin, woodpecker drum; 8+ one-shots each.
- A-06 Evening bed: golden-hour to dusk ambience loop (soft wind, distant creek, crickets onset), 3 min.

---

## SKIP LIST (do not generate)
1. Clothed women's PCT hiker rig — done today (2026-10-25). (`/workspace/argon/unreal/assetfix/` women turntables)
2. Clothed men's PCT hiker rig — done today. (same folder)
3. Anything already accepted by Paul — **search found zero assets with a recorded Paul acceptance.** Searched: /workspace/Thru-2 (no asset ledger or accepted-assets list; `docs/ASSET_PACKS.md` is a purchase shortlist only, `art/pct-reconstruction/acceptance.json` is gates/thresholds with no accepted items), /workspace/argon/*.md notes, and Dell `~/cs-audit/gemini-hackathon/` (no `assets/RESULT.md` and no `swarm/SUMMARY.md` exist; all 1,120 rows in `assets/MANIFEST.csv` are `review_required` 790 / `building` 288 / `failed` 42; asset cards say "counts only after Paul accepts it"). The "APPROVED & ACCEPTED FOR PRODUCTION" note in `reset/model3-trailsign/RESULT.md` is a Gemini critic verdict, not Paul's, so it is **not** skipped (listed below as existing).
4. Anything derived from Evermotion AM283, CGTrader or other purchased packs — never requested.

Skip list size: **2 assets** (plus the two standing rules: Paul-accepted items, currently 0, and no purchased-pack derivatives).

## EXISTING BUT NOT ACCEPTED (Pitcrew decides remake vs improve)
Source: Dell `~/cs-audit/gemini-hackathon/assets/MANIFEST.csv` (status | critic score /10) and `assets/built/<id>/`. Low scores (<3) → remake; ≥4 → consider improving.
- Footbridge (T1-02): single-log-flattened-footbridge review_required 3.5; cascades-timber-truss-trail-bridge 5.0; bridge-of-the-gods-truss-span 5.5 (named landmark — don't reuse for generic bridge).
- Granite/scree (T1-04): granite-boulders-tors failed; granite-slabs-glaciated failed; talus-cobble-wash failed; tafoni-boulders 2.0; hs-v2-rock-granite-slab-whaleback-broad 0.0; socal-granite-scree-dry-dusty-slope-talus-fan (built, see RESULT.md); Godot `owned_granite_a`, `sierra_granite_slab`, `boulder_a`, `sierra_mossy_rock` (procgen-scatter instances).
- Conifers (T1-05): jeffrey-pine 3.0 (+sapling/young building); sierra-lodgepole-pine 5.0 and ~15 hs-v2-tree-lodgepole-* variants 2.5–4.2; california-red-fir building (young 4.2) and hs-v2-tree-red-fir-* 2.5–4.2; western-white-pine 2.5 (sapling 3.5, young 4.2); whitebark burned snag 2.0.
- Understory (T1-06): greenleaf-manzanita 3.5, manzanita-shrub 2.0 (young 4.2), pinemat-manzanita 3.5; huckleberry-oak 5.0 (young 4.2); arroyo-willow-mulefat 3.5; bracken-fern building; california-corn-lily building; high-sierra-sedge-clump-v1 2.0; riparian-juncus-sedge 4.2; wildflower-lupine-poppy 4.0; indian-paintbrush-penstemon 3.5.
- Trail kit (T1-07): granite-rock-water-bar 5.5; peeled-log-water-bar-check-dam failed; stacked-granite-duck-cairn 3.5; granite-dry-stone-retaining-wall 2.8; usfs-signs-register 3.5; reset/model3-trailsign junction sign + cairn (critic 9.1, contains period/agency text — strip text before reuse).
- Gear (T1-08/T2-32): 1990s-internal-frame-expedition-pack 3.0; external-frame-pack 5.5; trekking poles 5.0; 1980s-geodesic-dome-tent failed; a-frame tarp bivy, camp-scatter-gear-kit, PUR filter review_required (several reference brand names — strip brands).
- Towns/vehicles (T2-25..31): 1980s USFS K10 ranger truck review_required (has agency decal — make generic); roadside-town-props review_required; campground picnic table review_required.
- Desert (T2-01..09): mojave-yucca 5.5, joshua-tree 4.2, ocotillo, creosote, sagebrush, cholla variants review_required; beavertail/engelmann/barrel cactus failed; scrub-oak failed.
- PNW (T2-16..24): norcal-douglas-fir, norcal-gen-* basalt/andesite rocks 1.5–3.5, oregon-huckleberry 2.0, pacific-silver-fir sapling, salmonberry (see assets/built/*/RESULT.md).
- Wildlife (T3): mule-deer-bighorn-sheep, california-quail-roadrunner review_required.
- Also present: Thru-2 `godot/assets/` folders (conifers, sierra_vegetation, rock_dressing, bridge_surfaces, gear, vehicles, wildlife, camp_props, towns). Note `paid_nature/` and `packs/` there — do **not** use as references or sources.

---

## Counts
- Tier 1: 8 items (T1-01..T1-08), 44 sub-items.
- Tier 2: 36 items (T2-01..T2-36).
- Tier 3: 11 items (T3-01..T3-11).
- Audio: 6 sets (A-01..A-06).
- Skip list: 2 assets.
