# THRU x Gemini Managed Agents: SHOWCASE (final, generated 15:52 PT)

> **How we used Managed Agents (submission blurb):** THRU runs three persisted Gemini Managed Agents: an art director that critiques every new Unreal render against real CC-licensed Sierra photos and feeds a scored fix list back into the render loop from one persistent sandbox that remembers past critiques, an asset librarian that fanned out across the whole Pacific Crest Trail in parallel sandboxes to write build-ready asset specs for our Blender lane, and a licence auditor that checks credits for YouTube safety. Each agent is defined once with its own instructions and mounted skills, then invoked by ID, so research, critique and compliance run as hosted jobs instead of on our overloaded workstation.

Gemini 4 Argon hackathon, category "best use of managed agents". Built and run on Oct 25 2026 (PT) from Paul Logan's Dell workstation with the
Interactions API (`google-genai` 2.33.0), base agent `antigravity-preview-09-2026`, model `gemini-3.8-flash`.

**THRU** is a photoreal co-op Pacific Crest Trail hiking game (UE 5.6, Lumen). It needs three kinds of grind work done all the time:
art critique against reality, research for thousands of real-world assets, and licence hygiene before anything goes on YouTube.
Each one is now a **named, persisted managed agent**, each with its own system instruction, mounted `.agents/AGENTS.md` and a mounted `SKILL.md`.

## The agents (persisted by ID)

| Agent ID | Role | Mounted skill | Runs | Completed | Tokens |
|---|---|---|---|---|---|
| `thru-art-director` | THRU photoreal art director: compares Unreal stills to real High Sierra/PCT reference photos and writes FIXES.md | `.agents/skills/*/SKILL.md` | 3 | 3 | 3,291,958 |
| `thru-asset-librarian` | THRU asset librarian: researches real PCT section visuals and emits structured Blender asset specs | `.agents/skills/*/SKILL.md` | 19 | 19 | 51,768,148 |
| `thru-license-auditor` | THRU licence auditor: checks audio credits and asset-pack lists for YouTube/public-video safety | `.agents/skills/*/SKILL.md` | 1 | 1 | 1,511,147 |

## Why managed agents fit THRU
- **A hosted Linux sandbox per job.** Each critique, research or audit job gets its own Google-hosted VM with Python, web search and URL fetch, so the agent can
  actually download reference thumbnails, compute colour stats, validate JSON with `json.loads`, and hold intermediate files. Nothing runs on, or fills, the Dell (its disk is ~99% full).
- **Persistent environments.** The art director's 2nd turn reuses the same `environment_id`: it re-opens its own `FIXES.md` and saved reference photos
  from turn 1 and turns them into a machine-readable UE5 task list. That's a stateful art-review loop, not a stateless chat.
- **Fan-out at scale.** The asset librarian ran **18 parallel interactions** (8 at a time, with 429 backoff), one per PCT section/theme from Campo to the Canadian border, plus 1 gap-analysis job over the Blender lane's 832-asset inventory,
  each in its own sandbox, producing **80 asset-spec JSON files** that the Blender lane picks up directly.
- **Config as code.** Agents are defined once (`setup_agents.py`) with `agents.create`, invoked by ID, and the model is locked per agent.
- **Secrets stay out.** The API key is sourced only in the calling shell; no key appears in prompts, sandboxes, files or git.

## Totals
- Interactions run: **23** (23 completed), distinct sandboxes (environments): **21**
- Tokens: total 56,571,253 (input 55,827,678, output 513,440, cached 52,195,919, thinking 230,135)
- Wall time per agent (sum of interactions): thru-art-director 11.5 min, thru-asset-librarian 103.5 min, thru-license-auditor 7.1 min
- Full log: `managed-agents/RUNS.jsonl` (one row per interaction: interaction_id, environment_id, prompt, output_text, files, usage, seconds)

## 1. thru-art-director: Unreal stills vs the real High Sierra
Input: 4 real UE 5.6 render stills from `reset/unreal/PROGRESSION/` (iter1 + iter2) sent as inline images. No Blender turntables existed yet.

### FIXES.md (excerpt)
```markdown
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
```

### Turn 2 in the same environment: JUDGE-SUMMARY.md
```markdown
# THRU Photoreal Critique: Executive Summary
Biggest Gap: The scene displays manicured municipal assets (a brown-painted suburban footbridge, glowing orange clay, potted houseplants, and a nude mannequin) instead of raw High Sierra granodiorite geology, native lodgepole ecology, and authentic backcountry trailcraft.
Fast Win 1: Replace the suburban bridge and tiled piers with a rustic USFS peeled-log stringer footbridge on dry-stacked granite slab cribbing.
Fast Win 2: Overhaul the terrain materials from straw mulch and orange clay to decomposed granite (DG) sand, pine duff, and native Carex sedge clusters.
Fast Win 3: Swap the untextured nude mannequin for a fully geared MetaHuman thru-hiker carrying an ultralight pack, bear canister, and trekking poles.
```

## 2. thru-asset-librarian: 18-way fan-out across the PCT + Blender-inventory gap analysis
Output: `reset/unreal-models/specs-from-managed-agent/` (80 files). Sample spec:
```json
{
 "name": "bigberry_manzanita_shrub",
 "category": "vegetation",
 "pct_section": "Southern California (Campo to Mt Laguna, Mile 0-42)",
 "description": "Arctostaphylos glauca (Bigberry Manzanita), dominant chaparral shrub with twisted sculptural branches, smooth mahogany-red bark, glaucous grey-green ovate leaves, and clusters of sticky berry drupes.",
 "real_world_references": [
  {
   "url": "https://commons.wikimedia.org/wiki/File:Bigberrymanzanita.jpg",
   "title": "Arctostaphylos glauca at Pine Valley in the Cuyamaca Mountains",
   "author": "Dionysia",
   "license": "CC BY-SA 3.0"
  },
  {
   "url": "https://commons.wikimedia.org/wiki/File:Arctostaphylos_glauca_-_Flickr_-_brewbooks.jpg",
   "title": "Arctostaphylos glauca bigberry manzanita",
   "author": "brewbooks",
   "license": "CC BY 2.0"
  }
 ],
 "dimensions_m": {
  "height": 2.4,
  "width": 2.8,
  "depth": 2.6
 },
 "materials": [
  {
   "slot": "mat_manzanita_bark",
   "description": "Smooth mahogany-red bark with peeling strips revealing olive underlayers.",
   "pbr_hints": "BaseColor #5C1D18, Roughness 0.38, Specular 0.55, Subsurface Scattering 0.15"
  },
  {
   "slot": "mat_manzanita_foliage",
   "description": "Leathery glaucous grey-green leaves with waxy cuticle on two-sided cards.",
   "pbr_hints": "BaseColor #7A8E7D, Roughness 0.48, Subsurface Scattering 0.25 pale olive"
  },
  {
   "slot": "mat_manzanita_berries",
   "description": "Viscid spherical drupes (12-15mm) maturing from sage green to dull red-brown.",
   "pbr_hints": "BaseColor #8C4738, Roughness 0.40, Specular 0.5"
  }
 ],
 "lod_targets": {
  "lod0_tris": 48000,
  "lod1_tris": 18000,
  "lod2_tris": 4500,
```
### Gap analysis of the Blender lane's real output (COVERAGE.md excerpt)
```markdown
# THRU Pacific Crest Trail Blender Asset Lane: Gap Analysis & Coverage Report

This report audits all 832 built Blender assets in the THRU model library, analyzing regional coverage, quality ratings (Argon critic score /10), identifying under-performing assets (<5.0/10), and evaluating critical visually signature objects required for authentic photoreal immersion.

## 1. Regional Coverage & Quality Summary Table

| PCT Region / Bucket | Total Assets | Scored Assets | Mean Score (/10) | Low Scorers (<5.0) | Low Scorer % | Unscored Assets | Coverage Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **SoCal desert** | 319 | 307 | 3.64 | 251 | 81.8% | 12 | Heavy coverage (319 assets), but plagued by low quality (81.8% < 5.0). |
| **Sierra** | 136 | 130 | 3.27 | 120 | 92.3% | 6 | Moderate coverage (136 assets), severe quality crisis (92.3% < 5.0). |
| **NorCal** | 84 | 80 | 3.14 | 72 | 90.0% | 4 | Sparse coverage (84 assets), very low mean score (3.14/10; 90.0% < 5.0). |
| **Oregon** | 16 | 15 | 3.59 | 12 | 80.0% | 1 | CRITICAL GAP: Extreme deficit (16 assets for 455 trail miles). |
| **Washington** | 188 | 182 | 3.50 | 156 | 85.7% | 6 | Moderate coverage (188 assets), highly repetitive variations, low mean score (3.50/10). |
| **trail towns/roads/vehicles/gear** | 89 | 76 | 4.24 | 41 | 53.9% | 13 | Solid foundation (89 assets), highest mean score (4.24/10), lacks hero trail crest signage. |
| **TOTAL / OVERALL** | **832** | **790** | **3.55** | **652** | **82.5%** | **42** | **Portfolio-wide refactor required for low-scoring generative variants** |

### Key Takeaways from Bucket Analysis:
1. **The Oregon Void**: Oregon accounts for ~455 miles (17% of the entire trail), yet has only **16 assets** (1.9% of inventory). Signature landmarks of the Central Oregon Cascades (lava beds, observatories, obsidian flows, volcanic crags) are almost entirely absent.
2. **Argon Score Deficit**: 652 out of 790 scored assets (**82.5%**) score below the 5.0 acceptability threshold. The vast majority of programmatic shrub and tree variations (`hs-v2-extra-*`, `norcal-gen-*`, `washington-*-v0*`) suffer from repetitive geometry, unnatural branching, and flat procedural shaders.
3. **Missing Hero Waypoints**: While the lane generated dozens of generic conifer and shrub lod variations, key landmark structures and geological features that thru-hikers navigate by are absent.

## 2. Low-Scorer Audit (< 5.0 / 10)
```
All specs:
- `00_bigberry_manzanita_shrub.json`
- `00_california_buckwheat_shrub.json`
- `00_chaparral_yucca_cluster.json`
- `00_pct_southern_terminus_monument.json`
- `01_ganders_cholla_cylindropuntia.json`
- `01_highway_78_underpass_bridge.json`
- `01_ocotillo_fouquieria_splendens.json`
- `01_scissors_crossing_water_cache.json`
- `02_joshua_tree_mature.json`
- `02_la_aqueduct_pipe_walk.json`
- `02_mojave_dirt_service_road.json`
- `02_tehachapi_wind_turbine.json`
- `03_black_mountain_road_closure_gate.json`
- `03_fuller_ridge_snow_patch.json`
- `03_pinus_jeffreyi_mature.json`
- `03_san_jacinto_granite_boulder.json`
- `04_bear_canister_bearvault_bv500.json`
- `04_great_basin_big_sagebrush_shrub.json`
- `04_kms_general_store_porch_bench.json`
- `04_south_fork_kern_river_granite_boulder.json`
- `05_forester_pass_switchback_cribbing.json`
- `05_high_sierra_talus_boulder_cluster.json`
- `05_muir_hut_stone_shelter.json`
- `05_sky_pilot_cushion.json`
- `06_evolution_creek_ford_stepping_stones.json`
- `06_krummholz_whitebark_pine.json`
- `06_sierra_lodgepole_pine.json`
- `06_subalpine_meadow_grass_clump.json`
- `07_sierra_alpine_trail_cairn.json`
- `07_sierra_bear_proof_food_locker.json`
- `07_sierra_log_stringer_footbridge.json`
- `07_sierra_pct_junction_sign.json`
- `07_sierra_wilderness_boundary_sign.json`
- `08_nps_ranger_patrol_truck.json`
- `08_sonora_pass_summit_sign.json`
- `08_tuolumne_general_store_tent.json`
- `08_yosemite_bear_proof_food_locker.json`
- `09_fire_scarred_ponderosa_pine.json`
- `09_greenleaf_manzanita_shrub.json`
- `09_hat_creek_vesicular_basalt_boulder.json`
- `09_subway_cave_lava_tube_portal.json`
- `10_burney_falls_basalt_cliff.json`
- `10_castella_i5_crossing_underpass.json`
- `10_castle_crags_granite_spire.json`
- `10_douglas_fir_mature.json`
- `11_mazama_pumice_boulder_cluster.json`
- `11_mount_thielsen_horn_pinnacle.json`
- `11_mountain_hemlock_mature.json`
- `11_rim_village_rustic_promenade_wall.json`
- `12_dee_wright_observatory.json`
- `12_dee_wright_peak_finder.json`
- `12_obsidian_falls_boulder_cluster.json`
- `12_vesicular_basalt_lava_boulder.json`
- `13_bridge_of_the_gods_cantilever_span.json`
- `13_columbia_gorge_columnar_basalt.json`
- `13_timberline_lodge_main_entrance.json`
- `13_timberline_lodge_trailhead_sign.json`
- `14_alpine_glacier_ice_serac.json`
- `14_knifes_edge_andesite_talus_cluster.json`
- `14_subalpine_fir_krummholz.json`
- `14_western_pasqueflower_seedhead_cluster.json`
- `15_harts_pass_guard_station.json`
- `15_pct_northern_terminus_monument.json`
- `15_stehekin_bakery_cabin.json`
- `15_stehekin_red_bus.json`
- `16_cascade_locks_post_office.json`
- `16_idyllwild_rustic_storefront.json`
- `16_pct_hiker_box.json`
- `16_sierra_city_country_store_porch.json`
- `16_trail_angel_water_cache.json`
- `17_pct_highway_crossing_sign.json`
- `17_rangeland_cattle_guard.json`
- `17_subaru_outback_trailhead_wagon.json`
- `17_trail_angel_shuttle_van.json`
- `17_usfs_patrol_pickup.json`
- `gap_dee_wright_observatory.json`
- `gap_devils_postpile_columnar_basalt.json`
- `gap_muir_pass_stone_shelter.json`
- `gap_pct_trail_marker_shield_post.json`
- `gap_vasquez_rocks_sandstone_hogback.json`

## 3. thru-license-auditor: YouTube safety
```markdown
# LICENSE-AUDIT: THRU Public YouTube Trailer & Commercial Video Audit

**Audit Date:** October 25, 2026  
**Auditor:** THRU Licence Audit Lane  
**Target Exploitation:** Public Monetized Video on YouTube (Cinematic Trailer & Gameplay Renders)  
**Input Manifests Audited:** `/workspace/inputs/CREDITS.md` & `/workspace/inputs/ASSET-PACKS.md`

---

## 1. Executive Summary

This audit evaluates all audio, 3D geometry, material textures, and procedural assets used in the THRU Unreal Engine spike and Godot hero lane for public distribution in a monetized YouTube trailer.

### Key Audit Findings:
1. **Mandatory Attribution (CC-BY-3.0):** The creek audio in master audio mixes (`ambience_62s.wav`, `unreal_hero_36s_16lufs.wav`) derives from **"Stream Sounds" by kurt** (OpenGameArt). Attribution is **legally mandatory** under Creative Commons Attribution 3.0 Unported. Failing to include attribution in the YouTube video description would invalidate the license and expose the trailer to copyright strikes.
2. **Commercial View Cap Alert (CHECK - HyperGrass Vol. 1 Wild Green):** Purchased under an ArtStation **Standard Use License**, which caps commercial exploitation at **20,000 monthly views** (or 2,000 sales). If the public YouTube trailer exceeds 20,000 views in any calendar month, the license must be upgraded to an **Extended Commercial License**. Additionally, Greg Zdunek's terms prohibit feeding raw mesh/texture data into generative AI tools (the current render-only workflow complies).
3. **Generative AI Audio Compliance (CHECK - `music_sierra_conifer.wav` via Lyria 3.5):** Generated using Google DeepMind's Lyria 3.5 model. Under Google's Gemini API terms, Google does not claim ownership over outputs; however, YouTube's platform policy **strictly mandates disclosure of realistic synthetic/AI-generated media** during upload. The video upload must toggle the "Altered or synthetic content" checkbox.
4. **Commercial EULA & AI Restrictions (Evermotion AM283):** Evermotion EULA (§2–§4) grants full commercial rights for rendered video/film/commercials, but strictly forbids raw file redistribution or using assets as training/input data in generative AI pipelines. The project's workflow (rendering only, raw files isolated on pod, deleting after hackathon) is compliant.
5. **Verified CC0-1.0 Audio & Visuals:** All 5 iNaturalist bird calls, 6 Freesound audio files, 4 Poly Haven nature/rock assets, and the Quaternius base characters were verified against their original database and license records as dedicated **CC0 1.0 (Public Domain)** or royalty-free no-attribution licenses.
6. **Excluded Assets Confirmed:** The 17 CGTrader packs carrying "Royalty Free License (no AI)" and subscription reuse limitations remain correctly **excluded** from the build, mitigating AI-clause conflicts.

---

## 2. Comprehensive Licence Audit Table

| Item | Claimed Licence | Verified Licence + URL | YouTube OK (YES/NO/CHECK) | Required Attribution Text | Action |
|---|---|---|---|---|---|
| **`ambience_62s.wav` & `unreal_hero_36s_16lufs.wav`** (Audio Master Mixes) | CC-BY-3.0 / CC0 / Original mix | Composite Master Audio Mix containing CC-BY-3.0, CC0-1.0, procedural, and AI audio | **YES** *(Conditional)* | Contains CC-BY-3.0 audio; requires "Stream Sounds" attribution in video description (see row below). | Provide full attribution block in YouTube description. Ensure YouTube AI disclosure box is checked for Lyria score. |
| **"Stream Sounds" by kurt** (`creek_medium.wav` / `stream3_kurt`) | CC-BY-3.0 | **CC-BY-3.0**<br>[OpenGameArt Stream Sounds](https://opengameart.org/content/stream-sounds)<br>[CC BY 3.0 Legal Code](https://creativecommons.org/licenses/by/3.0/) | **YES** | `"Stream Sounds" by kurt (https://opengameart.org/content/stream-sounds), licensed under Creative Commons Attribution 3.0 (https://creativecommons.org/licenses/by/3.0/). Modified for trailer mix.` | **Mandatory Action:** Paste verbatim attribution into the YouTube video description. |
| **`mountain_chickadee_1583116.wav`** (Sound ID 1583116) | iNaturalist CC0-1.0 | **CC0-1.0** (No rights reserved)<br>[iNaturalist Obs 301369695](https://www.inaturalist.org/observations/301369695)<br>Observer: `whiteoak` | **YES** | None legally required under CC0. (Courtesy credit: *Mountain Chickadee sound by whiteoak via iNaturalist, CC0*). | Cleared for monetized video. Include optional courtesy credit. |
| **`mountain_chickadee_2127131.wav`** (Sound ID 2127131) | iNaturalist CC0-1.0 | **CC0-1.0** (No rights reserved)<br>[iNaturalist Obs 392928456](https://www.inaturalist.org/observations/392928456)<br>Observer: `sardinemachine` | **YES** | None legally required under CC0. (Courtesy credit: *Mountain Chickadee sound by sardinemachine via iNaturalist, CC0*). | Cleared for monetized video. Include optional courtesy credit. |
| **`canyon_wren_1320386.wav`** (Sound ID 1320386) | iNaturalist CC0-1.0 | **CC0-1.0** (No rights reserved)<br>[iNaturalist Obs 263552965](https://www.inaturalist.org/observations/263552965)<br>Observer: `caitlincornwall` | **YES** | None legally required under CC0. (Courtesy credit: *Canyon Wren sound by caitlincornwall via iNaturalist, CC0*). | Cleared for monetized video. Include optional courtesy credit. |
| **`stellers_jay_2197823.wav`** (Sound ID 2197823) | iNaturalist CC0-1.0 | **CC0-1.0** (No rights reserved)<br>[iNaturalist Obs 408572176](https://www.inaturalist.org/observations/408572176)<br>Observer: `ben142` | **YES** | None legally required under CC0. (Courtesy credit: *Steller's Jay sound by ben142 via iNaturalist, CC0*). | Cleared for monetized video. Include optional courtesy credit. |
| **`stellers_jay_2191937.wav`** (Sound ID 2191937) | iNaturalist CC0-1.0 | **CC0-1.0** (No rights reserved)<br>[iNaturalist Obs 407317418](https://www.inaturalist.org/observations/407317418)<br>Observer: `saintaardvark` | **YES** | None legally required under CC0. (Courtesy credit: *Steller's Jay sound by saintaardvark via iNaturalist, CC0*). | Cleared for monetized video. Include optional courtesy credit. |
| **`wind_pines_soft/medium.wav`** (Freesound ID 81797) | CC0-1.0 | **CC0-1.0**<br>[Freesound Sound 81797](https://freesound.org/people/silencyo/sounds/81797/)<br>Author: `silencyo` | **YES** | None legally required under CC0. (Courtesy credit: *Wind Mistral Pine Trees by silencyo via Freesound.org*). | Cleared for monetized video. |
| **`wind_pines_soft/medium.wav`** (Freesound ID 843927) | CC0-1.0 | **CC0-1.0**<br>[Freesound Sound 843927](https://freesound.org/people/nicotep/sounds/843927/)<br>Author: `nicotep` | **YES** | None legally required under CC0. (Courtesy credit: *Dry Wind Pine Trees by nicotep via Freesound.org*). | Cleared for monetized video. |
| **`decomposed_granite_01..04.wav`** (Freesound ID 384880) | CC0-1.0 | **CC0-1.0**<br>[Freesound Sound 384880](https://freesound.org/people/Ali_6868/sounds/384880/)<br>Author: `Ali_6868` | **YES** | None legally required under CC0. | Cleared for monetized video. |
| **`decomposed_granite_01..04.wav`** (Freesound ID 556002) | CC0-1.0 | **CC0-1.0**<br>[Freesound Sound 556002](https://freesound.org/people/Nox_Sound/sounds/556002/)<br>Author: `Nox_Sound` | **YES** | None legally required under CC0. | Cleared for monetized video. |
| **`step_gravel_01..04.wav` / `step_wood_01..04.wav`** (Freesound ID 148802) | CC0-1.0 | **CC0-1.0**<br>[Freesound Sound 148802](https://freesound.org/people/SpliceSound/sounds/148802/)<br>Author: `SpliceSound` | **YES** | None legally required under CC0. | Cleared for monetized video. |
| **`step_gravel_01..04.wav` / `step_wood_01..04.wav`** (Freesound ID 369838) | CC0-1.0 | **CC0-1.0**<br>[Freesound Sound 369838](https://freesound.org/people/SpliceSound/sounds/369838/)<br>Author: `SpliceSound` | **YES** | None legally required under CC0. | Cleared for monetized video. |
| **`Sierra_alpine_dusk.wav`** | THRU Original | **THRU Proprietary** (Procedural audio bed, project-authored) | **YES** | None. | Cleared for monetized video. |
| **`music_sierra_conifer.wav`** (`lyria-3.5` Sierra conifer score) | THRU Original | **Generative AI Audio**<br>[Google DeepMind Lyria 3.5](https://deepmind.google/models/lyria/)<br>[Gemini API Terms of Service](https://ai.google.dev/gemini-api/terms) | **CHECK** | None required by Google API terms. Recommended disclosure: *Music generated with Google DeepMind Lyria 3.5*. | **Mandatory Action:** Check YouTube's "Altered or synthetic content" disclosure checkbox during upload. Do NOT register audio with YouTube Content ID. Retain prompt records. |
| **`jeffrey_open, fir_white_tall, fir_red_mature` (LOD0)** | Project geometry; embedded Poly Haven CC0 textures | **THRU Proprietary Geometry + CC0-1.0 Textures**<br>[Poly Haven License](https://polyhaven.com/license) | **YES** | None legally required. | Cleared for monetized video. |
| **`hero_granite_a/b/c`** | THRU original | **THRU Proprietary** (`generate_granite.py` seed1998) | **YES** | None. | Cleared for monetized video. |
| **`polyhaven_fern_02 a-d`** | CC0-1.0 | **CC0-1.0**<br>[Poly Haven Fern 02](https://polyhaven.com/a/fern_02)<br>Authors: Rob Tuytel & Rico Cilliers | **YES** | None legally required under CC0. (Courtesy credit: *Fern 02 by Rob Tuytel & Rico Cilliers via Poly Haven*). | Cleared for monetized video. |
| **`polyhaven_grass_medium_01 a-d`** | CC0-1.0 | **CC0-1.0**<br>[Poly Haven Grass Medium 01](https://polyhaven.com/a/grass_medium_01)<br>Authors: Rob Tuytel & Rico Cilliers | **YES** | None legally required under CC0. (Courtesy credit: *Grass Medium 01 by Rob Tuytel & Rico Cilliers via Poly Haven*). | Cleared for monetized video. |
| **`hiker_male` (+ walk anim)** | CC0-1.0 (License_Standard.txt / Quaternius Asset License) | **CC0-1.0 & Quaternius Asset License (QAL)**<br>[Universal Base Characters on itch.io](https://quaternius.itch.io/universal-base-characters)<br>[Quaternius Asset License](https://quaternius.com/license.html) | **YES** | None legally required under CC0 / QAL. (Courtesy credit: *Universal Base Characters by Quaternius*). | Cleared for monetized video. |
| **`granite-boulders-tors, talus-cobble-wash, pine-needle-duff PBR`** | THRU original | **THRU Proprietary** (Procedural PBR textures) | **YES** | None. | Cleared for monetized video. |
| **Procedural creek terrain, water, cobbles, bridge, domes** | THRU original | **THRU Proprietary** (`gen.py` code) | **YES** | None. | Cleared for monetized video. |
| **HyperGrass Vol. 1 Wild Green** (Primary Grass: 8 variations) | Purchased: Standard Use Licence (sales cap) | **ArtStation Standard EULA (Stock Asset)**<br>[ArtStation EULA](https://help.artstation.com/en/articles/16155014-eula-end-user-license-agreements)<br>[HyperGrass Vol. 1 Store Page](https://www.artstation.com/marketplace/p/qDv3/hypergrass-vol-1-wild-green-realistic-3d-grass-collection) | **CHECK** *(Conditional)* | None legally required under ArtStation EULA. (Courtesy credit: *HyperGrass Vol. 1 Wild Green by Greg Zdunek*). | **Risk Action:** Standard license limits commercial work to **20,000 monthly views**. Monitor YouTube view metrics. If video approaches/exceeds 20,000 views in a month, upgrade to Extended Commercial License immediately. Do NOT feed raw assets into generative AI tools. |
```

## Live loop hook: managed critic inside the render loop
`managed-agents/ma_critic_hook.py` watches `reset/unreal/PROGRESSION/` for new render stills, sends each new batch to `thru-art-director` in the SAME
persistent environment (chained with `previous_interaction_id`), and the agent keeps `/workspace/memory/critiques.jsonl` in its sandbox so every critique says what improved
or regressed since the last iteration. Output is critic.sh-compatible JSON (`scores`, `overall`, `top_issues`, `param_changes` keyed to the loop's `params.json`), written to
`reset/unreal/out/managed-critic/` and `reset/unreal/MANAGED-CRITIC.md`, with a pointer appended to `reset/unreal/STEER.md` so the next render iteration applies it.

Latest hook output:
```markdown
# Managed art-director critique (live hook) 15:46 PT
- agent `thru-art-director`, interaction `v1_ChdFb1RlYXFxREhxWDQtc0FQcWVxZGdBSRIXZFliZWF0dkFIOUsxMU1rUG9xN1dzUWM`
- persistent environment `935b320c904cc3c5537fbb9468d869ee` (iteration 1 of the memory chain)
- stills: 1505_hero_low_iter2-dense-route-hiker-pack-trees.png, 1505_hiker_iter2-dense-route-hiker-pack-trees.png, 1505_wide_iter2-dense-route-hiker-pack-trees.png
- overall: 2.4  scores: {"1505_hero_low_iter2-dense-route-hiker-pack-trees.png": 2.5, "1505_hiker_iter2-dense-route-hiker-pack-trees.png": 2.0, "1505_wide_iter2-dense-route-hiker-pack-trees.png": 2.8}
- delta vs previous: Improved vs 1440 blockout: transitioned from stacked green cone trees to branched pine meshes and added character path traversal. Critical regressions: character is an untextured nude mannequin without pack/gear; bridge is an urban municipal 2x4 railing on planar tile abutments; terrain is covered in uniform straw thatch and glowing orange clay.

## Top issues
- Bridge architecture is an urban/park brown-painted 2x4 railing on planar tile-faced vertical piers instead of a rustic USFS peeled-log stringer bridge on dry-stacked granite cribbing.
- Hiker character is an untextured low-poly nude mannequin running barefoot without clothes, backpack, or trekking poles.
- Ground cover is a repetitive yellow straw/hay mulch carpet, paired with glowing orange clay trail paint instead of decomposed granite (DG) sand and pine needle duff.
- Stream banks have vertical geometric shear faces with stretched textures, and streambed lacks snowmelt water clarity and dynamic boulder foam.
- Vegetation includes out-of-place tropical broadleaf houseplant meshes; conifers have noisy brown alpha cards and telephone-pole trunks without root flare.
- Lighting has excessive milky fog density (0.011) washing out background mountain geometry, while ambient fill lacks directional contrast.

## param_changes (params.json keys)
```json
{
 "light": {
  "sun_pitch": -13.5,
  "sun_lux": 26.0,
  "sun_temp": 4250,
  "sky_int": 1.65,
  "fog_density": 0.0028,
  "exposure_bias": 0.1
 },
 "water": {
  "tint": [
   0.18,
   0.36,
   0.4
  ],
  "opacity": 0.22,
  "roughness": 0.08,
  "normal_strength": 0.65,
  "flow_speed": 0.48
 },
 "granite": {
  "rough": 0.78,
  "wet_band": 0.22,
```

## Interaction ledger
| label | agent | status | interaction_id | environment_id | sec | tokens |
|---|---|---|---|---|---|---|
| librarian/fanout-04 | thru-asset-librarian | completed | `v1_ChdFb1RlYXFLcEU1elUtc0FQbWRqSy1RRRIXRW9UZWFxS3BFNXpVLXNBUG1kakstUUU` | `86447dd59a2c43f898a663d8be04d174` | 136.6 | 574,470 |
| librarian/fanout-06 | thru-asset-librarian | completed | `v1_ChZFb1RlYXVUekpkMmM5TW9Qam83ZFNBEhZFb1RlYXVUekpkMmM5TW9Qam83ZFNB` | `b2be555c5e0bcd2ed2e7ea0ce0dcd273` | 246.5 | 2,574,221 |
| librarian/fanout-02 | thru-asset-librarian | completed | `v1_ChdFb1RlYXVtSUlmanYtOFlQeXNmNzhBZxIXRW9UZWF1bUlJZmp2LThZUHlzZjc4QWc` | `5f3686e089333ca4afc81ff64e529496` | 247.8 | 1,887,066 |
| librarian/fanout-07 | thru-asset-librarian | completed | `v1_ChdFb1RlYXF2a0tQZlRfUFVQOU5fYi1BNBIXRW9UZWFxdmtLUGZUX1BVUDlOX2ItQTQ` | `e9de7d30ed3c4f26cd001f1fb77fa2d9` | 306.3 | 5,554,462 |
| librarian/fanout-05 | thru-asset-librarian | completed | `v1_ChdFb1RlYXBhUEVOSzExTWtQb3E3V3NRYxIXRW9UZWFwYVBFTksxMU1rUG9xN1dzUWM` | `24ded07974068f652cc88a7eb797e477` | 322.8 | 2,360,284 |
| librarian/fanout-08 | thru-asset-librarian | completed | `v1_ChdsNFRlYXFqS0FfeXg5TW9QaXQ3RndBYxIXbDRUZWFxaktBX3l4OU1vUGl0N0Z3QWM` | `7331dcde3754687cf662a1725203a33a` | 234.4 | 1,416,601 |
| librarian/fanout-03 | thru-asset-librarian | completed | `v1_ChdFb1RlYXBtQUY5SzExTWtQb3E3V3NRYxIXRW9UZWFwbUFGOUsxMU1rUG9xN1dzUWM` | `d659a3971f7e895191095e0b5aea74e0` | 380.4 | 1,936,658 |
| librarian/fanout-01 | thru-asset-librarian | completed | `v1_ChdFWVRlYXJiM041ZVZfdU1QOEt1YjZRaxIXRVlUZWFyYjNONWVWX3VNUDhLdWI2UWs` | `92ea2511ff9f328ee1e36a9719257088` | 380.7 | 2,372,959 |
| librarian/fanout-00 | thru-asset-librarian | completed | `v1_ChdFb1RlYXVIMExNN2Utc0FQcnFTWnVRRRIXRW9UZWF1SDBMTTdlLXNBUHJxU1p1UUU` | `70aabd4f77910e900f5a73160866e722` | 414.4 | 4,393,275 |
| license-auditor/turn1 | thru-license-auditor | completed | `v1_ChdFb1RlYXJINUdjUzE5TW9QNU5tUXFRYxIXRW9UZWFySDVHY1MxOU1vUDVObVFxUWM` | `1874318d61e4b757bc132c6bbb25d575` | 426.9 | 1,511,147 |
| librarian/fanout-09 | thru-asset-librarian | completed | `v1_ChdCSVhlYW8tRE9yWGUtc0FQcjVDQXFRSRIXQklYZWFvLURPclhlLXNBUHI1Q0FxUUk` | `addf1e104fbf9867c67a57e2003bd0ee` | 192.4 | 974,955 |
| art-director/turn1 | thru-art-director | completed | `v1_ChdFb1RlYXFxREhxWDQtc0FQcWVxZGdBSRIXRW9UZWFxcURIcVg0LXNBUHFlcWRnQUk` | `935b320c904cc3c5537fbb9468d869ee` | 462.0 | 1,602,820 |
| librarian/fanout-11 | thru-asset-librarian | completed | `v1_ChdRSVhlYXAtekk2ZXYxTWtQaXViaW9RYxIXUUlYZWFwLXpJNmV2MU1rUGl1YmlvUWM` | `3487643442f60e8e7b2d49c93f00e1a7` | 215.6 | 2,052,354 |
| librarian/fanout-12 | thru-asset-librarian | completed | `v1_ChdVWVhlYXJ5U0Q2cXkxTWtQMHVqYWlBOBIXVVlYZWFyeVNENnF5MU1rUDB1amFpQTg` | `5b491f012cb5f8c551f5628ae6945e0b` | 235.6 | 2,117,199 |
| librarian/fanout-10 | thru-asset-librarian | completed | `v1_ChZCb1hlYXREU0RQbWI5TW9QaHN6cVFREhZCb1hlYXREU0RQbWI5TW9QaHN6cVFR` | `3284957ddde7db723565a49972c29dbb` | 328.3 | 4,159,582 |
| art-director/turn2-same-env | thru-art-director | completed | `v1_ChdFb1RlYXFxREhxWDQtc0FQcWVxZGdBSRIXMjRYZWF1ektFYkdBMU1rUDhmdUFvQWM` | `935b320c904cc3c5537fbb9468d869ee` | 147.6 | 1,062,276 |
| librarian/fanout-13 | thru-asset-librarian | completed | `v1_ChdnWVhlYXNPX0Y4djctc0FQNWNxNS1RZxIXZ1lYZWFzT19GOHY3LXNBUDVjcTUtUWc` | `f379a36a0f20ce0a92c079c11b466513` | 255.4 | 1,425,664 |
| librarian/fanout-14 | thru-asset-librarian | completed | `v1_Chdpb1hlYXUtR05JaVkxTWtQNXZ5UnNBYxIXaW9YZWF1LUdOSWlZMU1rUDV2eVJzQWM` | `60a715c70332a89e99bfa9baa051d11e` | 254.5 | 1,803,411 |
| librarian/fanout-17 | thru-asset-librarian | completed | `v1_Chd4WVhlYXRUUkRZTFNfUFVQanFpNjhBOBIXeFlYZWF0VFJEWUxTX1BVUGpxaTY4QTg` | `9e236486675d8cea16a760b12ce14fdf` | 255.1 | 1,307,306 |
| art-director/live-hook-iter1505 | thru-art-director | completed | `v1_ChdFb1RlYXFxREhxWDQtc0FQcWVxZGdBSRIXZFliZWF0dkFIOUsxMU1rUG9xN1dzUWM` | `935b320c904cc3c5537fbb9468d869ee` | 82.5 | 626,862 |
| librarian/gap-analysis-blender-inventory | thru-asset-librarian | completed | `v1_Chc3NFRlYXE3RkFvTFNfUFVQdzZxNjhBOBIXNzRUZWFxN0ZBb0xTX1BVUHc2cTY4QTg` | `f25944c6786d2940cc0acbaafbb05e06` | 654.1 | 2,399,149 |
| librarian/fanout-16 | thru-asset-librarian | completed | `v1_ChdySVhlYXVPTE5MV0kxTWtQaWRyVTZROBIXcklYZWF1T0xOTFdJMU1rUGlkclU2UTg` | `5d28f58d36a4b2646217f423a3a951f0` | 490.9 | 3,700,946 |
| librarian/fanout-15 | thru-asset-librarian | completed | `v1_ChdpNFhlYW83NUJPejQtc0FQMWEyb2lBTRIXaTRYZWFvNzVCT3o0LXNBUDFhMm9pQU0` | `a1583eee557a509c4243da5edab612bc` | 659.7 | 8,757,586 |

## What worked, what did not
{open(NOTES).read() if os.path.exists(NOTES) else '(pending)'}
