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
| **Arnklit Cliffs & Rocks Pack 1** (`arnklit_boulder1-3`, etc.) | Royalty-free, commercial use OK, no redistribution | **Royalty-Free Commercial License**<br>[Arnklit Godot Rock Pack 1](https://arnklit.itch.io/godot-rock-asset-pack1)<br>[Arnklit Gumroad Store](https://arnklit.gumroad.com/l/godotcliffandrockspack1) | **YES** | Requested by author in project credits: `Godot Cliffs & Rocks Asset Pack 1 by Kasper Arnklit (https://arnklit.itch.io/godot-rock-asset-pack1)`. | Add attribution to YouTube description and project credits. Do not distribute raw model/shader files. |
| **Evermotion AM283 (Archmodels vol. 283)** (6 tree species, 40k GLBs) | Evermotion AM283 EULA (purchased €120), renders only, no redistribution | **Evermotion Commercial EULA** (§2, §3, §4)<br>[Evermotion EULA](https://evermotion.org/static/show/5/eula)<br>[Evermotion Shop EULA](https://evermotion.org/static/show/22/eula-shop) | **YES** | Courtesy credit recommended: `Archmodels vol. 283 © Evermotion (https://evermotion.org)`. (Mandatory only in game producer credits). | Cleared for monetized video renders (§2 permitted commercial field of exploitation: movies, animations, advertisements). Raw files must NOT be redistributed or fed to AI/ML tools. Delete raw assets from cloud pods after hackathon per internal ledger note. |
| **`namaqualand_boulder_02/03` (LOD0)** | CC0-1.0 | **CC0-1.0**<br>[Namaqualand Boulder 02](https://polyhaven.com/a/namaqualand_boulder_02)<br>[Namaqualand Boulder 03](https://polyhaven.com/a/namaqualand_boulder_03)<br>[Poly Haven License](https://polyhaven.com/license) | **YES** | None legally required under CC0. (Courtesy credit: *Namaqualand Boulders by Poly Haven*). | Cleared for monetized video. |
| **`manzanita_shrub, chamise_shrub, needlegrass_cured_large, mature_cedar_14m, coulter_pine_mature`** | THRU original | **THRU Proprietary** | **YES** | None. | Cleared for monetized video. |
| **CGTrader Packs (17 packs: `sword-fern-khalifeh`, `douglas-fir-forest-khalifeh`, `ponderosa-pine-nordiccanopy`, etc.)** | Royalty Free License (no AI) - EXCLUDED | **CGTrader Royalty Free License (No AI)** & Subscription Policy<br>[CGTrader Terms](https://www.cgtrader.com/pages/terms-and-conditions)<br>[CGTrader Fair Use](https://www.cgtrader.com/pages/subscription-fair-use-policy) | **NO** *(If used with AI)* / **EXCLUDED** | N/A | **Enforce Exclusion:** Keep all 17 CGTrader packs excluded from the scene. The "No AI" restriction and subscription project-completion limits conflict with the team's automated/AI toolchain. |
| **Kenney / KayKit / GobKit Low-Poly Nature** | CC0-1.0 - EXCLUDED (Artistic Choice) | **CC0-1.0**<br>[Kenney License](https://kenney.nl/assets/license) | **YES** *(If used)* / **EXCLUDED** | N/A | Excluded due to low-poly visual style. Clean provenance if needed later. |
| **Ceanothus (394 MB) & Scrub Oak Large (194 MB)** | THRU Original - EXCLUDED (Technical Constraint) | **THRU Proprietary** | **YES** *(If used)* / **EXCLUDED** | N/A | Excluded due to mesh density and conversion deadline. Clean provenance. |

---

## 3. In-Depth Legal & Operational Risk Analysis

### 3.1 Creative Commons Attribution 3.0: Kurt's "Stream Sounds"
- **Provenance & Status:** The sound file `stream3_kurt` was uploaded by user `kurt` to OpenGameArt under CC-BY 3.0. This file forms the acoustic core of `creek_medium.wav`, mixed into `ambience_62s.wav` and `unreal_hero_36s_16lufs.wav`.
- **Legal Requirement:** CC-BY 3.0 is a binding copyright license. Under Section 4(b), the licensee must provide:
  1. The name or pseudonym of the author (`kurt`).
  2. The title of the work (`Stream Sounds`).
  3. The Uniform Resource Identifier (URI) for the work (`https://opengameart.org/content/stream-sounds`).
  4. The URI or text of the CC-BY 3.0 license (`https://creativecommons.org/licenses/by/3.0/`).
  5. A notice indicating that modifications were made (derivative mixing).
- **Enforcement & Risk:** On YouTube, automated and manual copyright claims can be initiated if CC-BY attribution is missing. Omitting this attribution converts authorized use into actionable copyright infringement. Including the attribution block in the YouTube description fully satisfies the license.

### 3.2 ArtStation Standard EULA: HyperGrass Vol. 1 Wild Green (Greg Zdunek)
- **View Cap Limitation:** ArtStation's Standard Use License for Stock Assets provides rights for personal use and "one commercial Work, with up to a maximum of, as applicable, 2,000 sales of the Work or 20,000 monthly views of the Work" (ArtStation Help Center, *EULA: End User License Agreements*).
- **Public Video Impact:** A promotional trailer posted to YouTube is categorized under "commercial Work" supporting the THRU project. If the video garners more than 20,000 views within any single calendar month, THRU breaches the Standard EULA.
- **AI Clause:** Greg Zdunek's package documentation stipulates that raw meshes and textures must not be ingested into generative AI services. Using the meshes directly in Unreal Engine to render rasterized video frames is permitted, but the raw geometry and textures must remain excluded from generative model training or neural reconstruction pipelines.
- **Action Required:**
  1. Audit current YouTube view analytics upon release.
  2. If the video reaches 15,000 views within a 30-day window, immediately purchase the **ArtStation Extended Commercial License** ($100–$250 tier) to lift all view and unit caps.

### 3.3 Generative AI Score: `music_sierra_conifer.wav` (Google DeepMind Lyria 3.5)
- **Licence Terms:** Google's Gemini API Additional Terms of Service govern outputs from the Lyria 3.5 audio model. Google explicitly stipulates: *"Google won't claim ownership over that content."* (Section *Use of Generated Content*).
- **YouTube Policy on Synthetic Media:** Since March 2024, YouTube requires creators to disclose realistic synthetic content (content generated or substantially modified with AI that could be mistaken for real people, real places, or authentic recordings). Audio tracks that sound like an authentic orchestral/acoustic recording fall under this disclosure guidance.
- **SynthID & Watermarking:** Lyria generates audio with imperceptible SynthID acoustic watermarks. YouTube and Google systems detect these watermarks automatically. If an uploader fails to disclose AI generation, YouTube may apply an automated synthetic media label or penalize the channel.
- **Content ID Vulnerability:** Generative AI audio cannot be copyrighted under current US Copyright Office guidance (compendium on works lacking human authorship) and must NOT be submitted to YouTube's Content ID system. Additionally, third-party rights holders have occasionally filed false positive Content ID matches against AI-generated musical phrases. The production team should retain prompt logs, model timestamps, and seed parameters to dispute any spurious claims.

### 3.4 Evermotion AM283 EULA Compliance
- **Permitted Fields of Exploitation:** Section 2 and Section 4 of the Evermotion EULA expressly permit the incorporation of 3D models into rendered animations, films, advertisements, and video productions for commercial gain worldwide.
- **Strict Prohibitions:**
  1. *No Redistribution:* Raw geometry (`.glb`, `.fbx`, `.blend`) and source texture files cannot be publicly shared, sublicensed, or distributed.
  2. *Strict No-AI Clause:* Evermotion EULA §3 and §4 explicitly prohibit using Evermotion Products in any generative artificial intelligence system or machine learning model, whether as input training data, fine-tuning data, or prompt augmentation.
  3. *Homogeneous Backgrounds:* Single tree models cannot be rendered on an isolated plain background and sold as stock illustrations.
- **Audit Verdict:** The usage in THRU satisfies all Evermotion terms: models are placed in a complex environment scene, rendered as video frames, and the raw source files reside only on internal secure development pods scheduled for deletion post-hackathon.

### 3.5 Excluded CGTrader Assets: Sound Legal Strategy
- **Audit of CGTrader "Royalty Free License (no AI)":** CGTrader enforces strict terms forbidding the ingestion of assets into neural network training pipelines or generative AI environments. Furthermore, models acquired under CGTrader subscriptions cannot be introduced into new commercial projects once the subscription lapses.
- **Audit Verdict:** Paul's decision to exclude all 17 CGTrader packs (including `sword-fern-khalifeh`, `douglas-fir-forest-khalifeh`, `ponderosa-pine-nordiccanopy`) was correct and eliminates cross-contamination risks with THRU's generative review and procedural pipelines.

---

## 4. YouTube Upload Pre-Flight Checklist

Before making the video public and enabling monetization on YouTube Studio:

- [ ] **Description Field:** Copy and paste the complete text from `ATTRIBUTION.txt` into the video description box.
- [ ] **Altered or Synthetic Content Checkbox:** In YouTube Studio under **Details > Altered content**, select **"Yes"** to: *"Do any of the following describe your content? Makes a real person appear to say or do something they didn't do, alters footage of a real event, or generates a realistic-looking scene that didn't actually occur."* (Noting AI-assisted musical score via Lyria 3.5).
- [ ] **Content ID Registration:** Do NOT submit the audio track to any digital music distributor (DistroKid, TuneCore, CD Baby) with Content ID monetization turned on, as `music_sierra_conifer.wav` contains AI-generated audio and `ambience_62s.wav` contains CC-BY/CC0 elements.
- [ ] **View Metric Monitoring (HyperGrass):** Set a calendar reminder to check trailer view counts at 7 days and 30 days. If monthly views approach 20,000, purchase the ArtStation Extended Commercial License.
- [ ] **Storage Hygiene:** Verify that raw Evermotion AM283 archives and files on pod `thru-unreal-1` remain non-public and are cleared after production renders are complete.