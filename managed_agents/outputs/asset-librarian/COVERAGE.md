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

Below is the complete inventory of all 652 assets receiving an Argon critic score below 5.0, organized by region to assist the modeling lane in prioritization and remediation.

### SoCal desert (251 low scorers)
| Asset Name | Argon Critic Score | Remediation Priority |
| :--- | :---: | :--- |
| `socal-oak-leaf-litter-dry-curled-spiny-oak-leaves-and-acorn-caps` | 0.0 | Immediate Re-bake / Re-mesh |
| `california-juniper--young` | 1.0 | Immediate Re-bake / Re-mesh |
| `beavertail-prickly-pear--young` | 1.5 | Immediate Re-bake / Re-mesh |
| `socal-buckwheat-mature-autumn-deep-rust-dry` | 1.5 | Immediate Re-bake / Re-mesh |
| `socal-granite-outcrop-montane-snow-crevice-granite-outcrop` | 1.5 | Immediate Re-bake / Re-mesh |
| `california-sycamore` | 2.0 | Immediate Re-bake / Re-mesh |
| `chamise-dead-stem-kit` | 2.0 | Immediate Re-bake / Re-mesh |
| `laurel-sumac--establishment` | 2.0 | Immediate Re-bake / Re-mesh |
| `lemonade-berry--establishment` | 2.0 | Immediate Re-bake / Re-mesh |
| `manzanita-shrub` | 2.0 | Immediate Re-bake / Re-mesh |
| `oak-root-flare-litter` | 2.0 | Immediate Re-bake / Re-mesh |
| `singleleaf-pinyon--sapling` | 2.0 | Immediate Re-bake / Re-mesh |
| `socal-beavertail` | 2.0 | Immediate Re-bake / Re-mesh |
| `socal-beavertail-cactus-young-two-pad-glaucous-sprout` | 2.0 | Immediate Re-bake / Re-mesh |
| `socal-buckwheat-young-spring-vegetative` | 2.0 | Immediate Re-bake / Re-mesh |
| `socal-chamise-mature-autumn-cured` | 2.0 | Immediate Re-bake / Re-mesh |
| `socal-chamise-mature-summer-dry-dusty` | 2.0 | Immediate Re-bake / Re-mesh |
| `socal-chamise-mature-winter-rain-wet` | 2.0 | Immediate Re-bake / Re-mesh |
| `socal-creosote-drought-pruned-skeletal-branches` | 2.0 | Immediate Re-bake / Re-mesh |
| `socal-creosote-old-clonal-ring-segment-dead-center` | 2.0 | Immediate Re-bake / Re-mesh |
| `socal-granite-corestone-exfoliating-grus-apron-spalled-corestones` | 2.0 | Immediate Re-bake / Re-mesh |
| `socal-granite-scree-dry-dusty-slope-talus-fan` | 2.0 | Immediate Re-bake / Re-mesh |
| `socal-joshua-tree-old-multi-armed-desert-patriarch` | 2.0 | Immediate Re-bake / Re-mesh |
| `socal-oak-leaf-litter-rain-matted-dark-decomposing-oak-duff` | 2.0 | Immediate Re-bake / Re-mesh |
| `socal-ocotillo-old-wide-flaring-40-cane-funnel` | 2.0 | Immediate Re-bake / Re-mesh |
| `socal-our-lords-candle-young-compact-spiny-rosette` | 2.0 | Immediate Re-bake / Re-mesh |
| `socal-pine-needle-duff-rain-soaked-dark-compressed-needle-litter` | 2.0 | Immediate Re-bake / Re-mesh |
| `socal-prickly-pear-mature-winter-rain-glossy-wet-pads` | 2.0 | Immediate Re-bake / Re-mesh |
| `socal-prickly-pear-young-spiny-cladode-cluster` | 2.0 | Immediate Re-bake / Re-mesh |
| `socal-scrub-oak-young-spring-flush` | 2.0 | Immediate Re-bake / Re-mesh |
| `socal-silver-cholla-bleached-tabular-cholla-skeleton` | 2.0 | Immediate Re-bake / Re-mesh |
| `tafoni-boulders` | 2.0 | Immediate Re-bake / Re-mesh |
| `white-bursage--young` | 2.0 | Immediate Re-bake / Re-mesh |
| `california-juniper` | 2.5 | Immediate Re-bake / Re-mesh |
| `california-quail-roadrunner` | 2.5 | Immediate Re-bake / Re-mesh |
| `california-sycamore--sapling` | 2.5 | Immediate Re-bake / Re-mesh |
| `canyon-liveforever-dudleya--juvenile` | 2.5 | Immediate Re-bake / Re-mesh |
| `coast-live-oak--young` | 2.5 | Immediate Re-bake / Re-mesh |
| `coulter-pine` | 2.5 | Immediate Re-bake / Re-mesh |
| `desert-scrub-oak--young` | 2.5 | Immediate Re-bake / Re-mesh |
| `fremont-cottonwood` | 2.5 | Immediate Re-bake / Re-mesh |
| `hollyleaf-redberry` | 2.5 | Immediate Re-bake / Re-mesh |
| `interior-live-oak` | 2.5 | Immediate Re-bake / Re-mesh |
| `julian-mica-schist-outcrop` | 2.5 | Immediate Re-bake / Re-mesh |
| `laurel-sumac` | 2.5 | Immediate Re-bake / Re-mesh |
| `purple-sage` | 2.5 | Immediate Re-bake / Re-mesh |
| `red-rock-tuff-hoodoo-cliff` | 2.5 | Immediate Re-bake / Re-mesh |
| `socal-beavertail-cactus-mature-rain-turgid-blue-grey-pads` | 2.5 | Immediate Re-bake / Re-mesh |
| `socal-beavertail-cactus-mature-spring-magenta-cup-bloom` | 2.5 | Immediate Re-bake / Re-mesh |
| `socal-beavertail-cactus-mature-summer-wrinkled-violet-stressed-pads` | 2.5 | Immediate Re-bake / Re-mesh |
| `socal-big-sagebrush` | 2.5 | Immediate Re-bake / Re-mesh |
| `socal-california-barrel` | 2.5 | Immediate Re-bake / Re-mesh |
| `socal-california-juniper-mature-winter-frost-dusted-crown` | 2.5 | Immediate Re-bake / Re-mesh |
| `socal-decomposed-granite-rain-darkened-compacted-rill-grus` | 2.5 | Immediate Re-bake / Re-mesh |
| `socal-desert-willow` | 2.5 | Immediate Re-bake / Re-mesh |
| `socal-dg-tread` | 2.5 | Immediate Re-bake / Re-mesh |
| `socal-drywash-cobble-sun-baked-imbricated-arroyo-cobbles` | 2.5 | Immediate Re-bake / Re-mesh |
| `socal-granite-corestone-dry-warm-feldspar-lichen-corestone-cluster` | 2.5 | Immediate Re-bake / Re-mesh |
| `socal-granite-corestone-rain-slick-darkened-granite-boulder-pile` | 2.5 | Immediate Re-bake / Re-mesh |
| `socal-granite-outcrop-rain-seep-dark-streak-granite-outcrop` | 2.5 | Immediate Re-bake / Re-mesh |
| `socal-granite-scree-rain-wet-low-roughness-scree-scatter` | 2.5 | Immediate Re-bake / Re-mesh |
| `socal-hedgehog-cactus-mature-summer-contracted-spiny-cushion` | 2.5 | Immediate Re-bake / Re-mesh |
| `socal-joshua-tree-mature-forked-spring-panicles` | 2.5 | Immediate Re-bake / Re-mesh |
| `socal-ocotillo-mature-postrain-emerald-bark-leaf-flush` | 2.5 | Immediate Re-bake / Re-mesh |
| `socal-our-lords-candle-mature-vegetative-glaucous-rosette` | 2.5 | Immediate Re-bake / Re-mesh |
| `socal-pinyon-pine` | 2.5 | Immediate Re-bake / Re-mesh |
| `socal-scrub-oak-postfire-basal-resprout` | 2.5 | Immediate Re-bake / Re-mesh |
| `socal-silver-cholla-mature-rain-wet-darkened-epidermis` | 2.5 | Immediate Re-bake / Re-mesh |
| `socal-silver-cholla-mature-summer-dense-silver-spination` | 2.5 | Immediate Re-bake / Re-mesh |
| `socal-white-sage-postfire-silver-seedling` | 2.5 | Immediate Re-bake / Re-mesh |
| `southern-pacific-diamondback-rattlesnake` | 2.5 | Immediate Re-bake / Re-mesh |
| `sun-bleached-cattle-skull-ribcage` | 2.5 | Immediate Re-bake / Re-mesh |
| `toyon-christmasberry--establishment` | 2.5 | Immediate Re-bake / Re-mesh |
| `western-fence-lizard-horned-lizard` | 2.5 | Immediate Re-bake / Re-mesh |
| `white-sage--young` | 2.5 | Immediate Re-bake / Re-mesh |
| `yerba-santa` | 2.5 | Immediate Re-bake / Re-mesh |
| `big-sagebrush` | 3.0 | Refine Shaders & LODs |
| `coulter-pine--young` | 3.0 | Refine Shaders & LODs |
| `redshank-ribbonwood--young` | 3.0 | Refine Shaders & LODs |
| `singleleaf-pinyon` | 3.0 | Refine Shaders & LODs |
| `socal-buckwheat-mature-summer-rust-seedheads` | 3.0 | Refine Shaders & LODs |
| `socal-creosote-mature-summer-olive-amber-resinous-dry` | 3.0 | Refine Shaders & LODs |
| `socal-decomposed-granite-dry-dusty-trail-shoulder-grus-with-bootprint` | 3.0 | Refine Shaders & LODs |
| `socal-desert-willow-old-winter-leafless-leaning-wash-trunk` | 3.0 | Refine Shaders & LODs |
| `socal-drywash-cobble-receding-flow-damp-sand-rimmed-cobble-bar` | 3.0 | Refine Shaders & LODs |
| `socal-drywash-cobble-waterline-slick-clearcoat-wet-cobbles` | 3.0 | Refine Shaders & LODs |
| `socal-granite-outcrop-jointed-dry-granite-tor-outcrop` | 3.0 | Refine Shaders & LODs |
| `socal-granite-pile` | 3.0 | Refine Shaders & LODs |
| `socal-joshua-tree-mature-monsoon-rain-dark-fibrous-bark` | 3.0 | Refine Shaders & LODs |
| `socal-joshua-tree-weathered-skeleton-standing-snag` | 3.0 | Refine Shaders & LODs |
| `socal-manzanita-mature-montane-rime-frost` | 3.0 | Refine Shaders & LODs |
| `socal-mojave-yucca-mature-spring-cream-bell-cluster` | 3.0 | Refine Shaders & LODs |
| `socal-ocotillo` | 3.0 | Refine Shaders & LODs |
| `socal-ocotillo-mature-summer-drought-leafless-spiny-canes` | 3.0 | Refine Shaders & LODs |
| `socal-ocotillo-young-few-cane-rosette` | 3.0 | Refine Shaders & LODs |
| `socal-teddy-bear-cholla-old-gnarled-blackened-base-fallen-joints` | 3.0 | Refine Shaders & LODs |
| `sugar-bush` | 3.0 | Refine Shaders & LODs |
| `yerba-santa--young` | 3.0 | Refine Shaders & LODs |
| `pelona-blueschist-greenstone` | 3.2 | Refine Shaders & LODs |
| `arroyo-willow-mulefat` | 3.5 | Refine Shaders & LODs |
| `big-sagebrush--establishment` | 3.5 | Refine Shaders & LODs |
| `bigcone-douglas-fir--sapling` | 3.5 | Refine Shaders & LODs |
| `bigcone-douglas-fir--young` | 3.5 | Refine Shaders & LODs |
| `buckhorn-cholla` | 3.5 | Refine Shaders & LODs |
| `california-buckwheat--establishment` | 3.5 | Refine Shaders & LODs |
| `california-coffeeberry--young` | 3.5 | Refine Shaders & LODs |
| `california-juniper--sapling` | 3.5 | Refine Shaders & LODs |
| `california-sagebrush--establishment` | 3.5 | Refine Shaders & LODs |
| `canyon-live-oak--young` | 3.5 | Refine Shaders & LODs |
| `canyon-liveforever-dudleya--young` | 3.5 | Refine Shaders & LODs |
| `coast-live-oak` | 3.5 | Refine Shaders & LODs |
| `coast-live-oak--young` | 3.5 | Refine Shaders & LODs |
| `coffee-fern-pellaea` | 3.5 | Refine Shaders & LODs |
| `desert-scrub-oak` | 3.5 | Refine Shaders & LODs |
| `desert-scrub-oak--establishment` | 3.5 | Refine Shaders & LODs |
| `engelmann-prickly-pear--juvenile` | 3.5 | Refine Shaders & LODs |
| `engelmann-prickly-pear--young` | 3.5 | Refine Shaders & LODs |
| `flannelbush-fremontia--young` | 3.5 | Refine Shaders & LODs |
| `fremont-cottonwood--sapling` | 3.5 | Refine Shaders & LODs |
| `goldenbush-deerweed` | 3.5 | Refine Shaders & LODs |
| `hollyleaf-cherry` | 3.5 | Refine Shaders & LODs |
| `honey-mesquite` | 3.5 | Refine Shaders & LODs |
| `joshua-tree--sapling` | 3.5 | Refine Shaders & LODs |
| `lemonade-berry--young` | 3.5 | Refine Shaders & LODs |
| `manzanita-shrub--establishment` | 3.5 | Refine Shaders & LODs |
| `mormon-tea-ephedra--establishment` | 3.5 | Refine Shaders & LODs |
| `oak-mistletoe-woodrat` | 3.5 | Refine Shaders & LODs |
| `pancake-prickly-pear` | 3.5 | Refine Shaders & LODs |
| `prickly-poppy-argemone` | 3.5 | Refine Shaders & LODs |
| `smoke-tree` | 3.5 | Refine Shaders & LODs |
| `socal-beavertail-cactus-mature-autumn-dry-fruit-remnants` | 3.5 | Refine Shaders & LODs |
| `socal-buckwheat` | 3.5 | Refine Shaders & LODs |
| `socal-buckwheat-mature-late-spring-white-umbels` | 3.5 | Refine Shaders & LODs |
| `socal-buckwheat-mature-winter-rain-darkened` | 3.5 | Refine Shaders & LODs |
| `socal-california-barrel-cactus-mature-autumn-yellow-scaly-fruit-ring` | 3.5 | Refine Shaders & LODs |
| `socal-california-barrel-cactus-mature-spring-yellow-crown-ring` | 3.5 | Refine Shaders & LODs |
| `socal-california-barrel-cactus-old-tall-basal-corking-multi-headed` | 3.5 | Refine Shaders & LODs |
| `socal-california-juniper-mature-winter-rain-saturated-fibrous-bark` | 3.5 | Refine Shaders & LODs |
| `socal-california-juniper-old-twisted-strip-bark-dead-spire` | 3.5 | Refine Shaders & LODs |
| `socal-chamise` | 3.5 | Refine Shaders & LODs |
| `socal-chamise-burl-resprout-postfire` | 3.5 | Refine Shaders & LODs |
| `socal-creosote-bush` | 3.5 | Refine Shaders & LODs |
| `socal-creosote-mature-rain-wet-glossy-resinous-foliage` | 3.5 | Refine Shaders & LODs |
| `socal-creosote-mature-spring-yellow-flowers-fuzzy-globes` | 3.5 | Refine Shaders & LODs |
| `socal-creosote-young-open-v-stemmed-shrub` | 3.5 | Refine Shaders & LODs |
| `socal-desert-willow-mature-flash-flood-after-rain-wet` | 3.5 | Refine Shaders & LODs |
| `socal-desert-willow-mature-late-spring-orchid-trumpet-bloom` | 3.5 | Refine Shaders & LODs |
| `socal-desert-willow-mature-summer-narrow-hanging-leaves-pods` | 3.5 | Refine Shaders & LODs |
| `socal-dry-wash` | 3.5 | Refine Shaders & LODs |
| `socal-granite-scree-coarse-chute-sorted-scree-debris` | 3.5 | Refine Shaders & LODs |
| `socal-hedgehog-cactus-mature-rain-swollen-plump-ribs` | 3.5 | Refine Shaders & LODs |
| `socal-hedgehog-cactus-old-many-stemmed-hemispheric-colony` | 3.5 | Refine Shaders & LODs |
| `socal-joshua-tree-mature-summer-dry-shaggy-thatch` | 3.5 | Refine Shaders & LODs |
| `socal-juniper` | 3.5 | Refine Shaders & LODs |
| `socal-manzanita-mature-rain-slick-redbark` | 3.5 | Refine Shaders & LODs |
| `socal-mojave-yucca` | 3.5 | Refine Shaders & LODs |
| `socal-oak-leaf-litter-thick-canyon-draw-drift-with-bark-twigs` | 3.5 | Refine Shaders & LODs |
| `socal-ocotillo-mature-spring-scarlet-tip-panicles-leafy` | 3.5 | Refine Shaders & LODs |
| `socal-prickly-pear-mature-late-summer-burgundy-tunas` | 3.5 | Refine Shaders & LODs |
| `socal-prickly-pear-mature-spring-yellow-blossoms` | 3.5 | Refine Shaders & LODs |
| `socal-prickly-pear-mature-summer-dusty-shrunken-pads` | 3.5 | Refine Shaders & LODs |
| `socal-prickly-pear-old-sprawling-lignified-corky-base` | 3.5 | Refine Shaders & LODs |
| `socal-scrub-oak-mature-autumn-acorn-mast` | 3.5 | Refine Shaders & LODs |
| `socal-scrub-oak-old-dense-interlocking-crown` | 3.5 | Refine Shaders & LODs |
| `socal-silver-cholla` | 3.5 | Refine Shaders & LODs |
| `socal-silver-cholla-young-low-branching-silver-joints` | 3.5 | Refine Shaders & LODs |
| `socal-teddy-bear-cholla-mature-rain-wet-translucent-spines` | 3.5 | Refine Shaders & LODs |
| `socal-teddy-bear-cholla-mature-spring-yellow-green-apical-buds` | 3.5 | Refine Shaders & LODs |
| `socal-white-sage-mature-spring-tall-panicles` | 3.5 | Refine Shaders & LODs |
| `socal-white-sage-mature-summer-drought-curled` | 3.5 | Refine Shaders & LODs |
| `white-sage--establishment` | 3.5 | Refine Shaders & LODs |
| `yerba-santa--establishment` | 3.5 | Refine Shaders & LODs |
| `california-buckwheat` | 4.0 | Refine Shaders & LODs |
| `california-sycamore--young` | 4.0 | Refine Shaders & LODs |
| `chamise-shrub` | 4.0 | Refine Shaders & LODs |
| `desert-tarantula-harvester-ant-mound` | 4.0 | Refine Shaders & LODs |
| `scrub-oak--establishment` | 4.0 | Refine Shaders & LODs |
| `singleleaf-pinyon--young` | 4.0 | Refine Shaders & LODs |
| `socal-hedgehog-cactus-young-few-stem-compact-mound` | 4.0 | Refine Shaders & LODs |
| `socal-manzanita-old-sculpted-half-deadwood` | 4.0 | Refine Shaders & LODs |
| `socal-our-lords-candle-mature-rain-wet-rosette` | 4.0 | Refine Shaders & LODs |
| `socal-scrub-oak-mature-winter-rain-wet` | 4.0 | Refine Shaders & LODs |
| `yucca-rosette` | 4.0 | Refine Shaders & LODs |
| `beavertail-prickly-pear--juvenile` | 4.2 | Refine Shaders & LODs |
| `big-sagebrush--young` | 4.2 | Refine Shaders & LODs |
| `black-sage--young` | 4.2 | Refine Shaders & LODs |
| `blue-oak--young` | 4.2 | Refine Shaders & LODs |
| `buckhorn-cholla--juvenile` | 4.2 | Refine Shaders & LODs |
| `buckhorn-cholla--young` | 4.2 | Refine Shaders & LODs |
| `california-coffeeberry--establishment` | 4.2 | Refine Shaders & LODs |
| `california-sagebrush--young` | 4.2 | Refine Shaders & LODs |
| `canyon-liveforever-dudleya` | 4.2 | Refine Shaders & LODs |
| `catclaw-acacia--young` | 4.2 | Refine Shaders & LODs |
| `chamise-shrub--young` | 4.2 | Refine Shaders & LODs |
| `coast-live-oak--sapling` | 4.2 | Refine Shaders & LODs |
| `creosote-bush` | 4.2 | Refine Shaders & LODs |
| `creosote-bush--young` | 4.2 | Refine Shaders & LODs |
| `desert-lavender--young` | 4.2 | Refine Shaders & LODs |
| `engelmann-oak--young` | 4.2 | Refine Shaders & LODs |
| `hollyleaf-redberry--establishment` | 4.2 | Refine Shaders & LODs |
| `hollyleaf-redberry--young` | 4.2 | Refine Shaders & LODs |
| `joshua-tree` | 4.2 | Refine Shaders & LODs |
| `joshua-tree--young` | 4.2 | Refine Shaders & LODs |
| `laurel-sumac--young` | 4.2 | Refine Shaders & LODs |
| `manzanita-shrub--young` | 4.2 | Refine Shaders & LODs |
| `mojave-yucca--establishment` | 4.2 | Refine Shaders & LODs |
| `mojave-yucca--young` | 4.2 | Refine Shaders & LODs |
| `ocotillo-coachwhip--establishment` | 4.2 | Refine Shaders & LODs |
| `redshank-ribbonwood` | 4.2 | Refine Shaders & LODs |
| `redshank-ribbonwood--establishment` | 4.2 | Refine Shaders & LODs |
| `scrub-oak--young` | 4.2 | Refine Shaders & LODs |
| `smoke-tree--sapling` | 4.2 | Refine Shaders & LODs |
| `socal-beavertail-cactus-old-prostrate-corky-basal-mat` | 4.2 | Refine Shaders & LODs |
| `socal-buckwheat-old-woody-dry-mound` | 4.2 | Refine Shaders & LODs |
| `socal-chamise-old-grey-dieback` | 4.2 | Refine Shaders & LODs |
| `socal-desert-willow-mature-autumn-splitting-cigar-seed-capsules` | 4.2 | Refine Shaders & LODs |
| `socal-hedgehog-cactus-mature-spring-magenta-funnels` | 4.2 | Refine Shaders & LODs |
| `socal-jeffrey-pine-fallen-jeffrey-bark-sloughing-log` | 4.2 | Refine Shaders & LODs |
| `socal-joshua-tree` | 4.2 | Refine Shaders & LODs |
| `socal-manzanita` | 4.2 | Refine Shaders & LODs |
| `socal-manzanita-charred-silver-skeleton` | 4.2 | Refine Shaders & LODs |
| `socal-manzanita-mature-summer-dry-bark` | 4.2 | Refine Shaders & LODs |
| `socal-manzanita-young-spring-urn-bloom` | 4.2 | Refine Shaders & LODs |
| `socal-mojave-yucca-old-twin-trunk-clustered-rosettes` | 4.2 | Refine Shaders & LODs |
| `socal-ocotillo-mature-autumn-dry-seed-capsules-bare-canes` | 4.2 | Refine Shaders & LODs |
| `socal-pine-needle-duff-patchy-spring-snowmelt-needle-and-cone-bed` | 4.2 | Refine Shaders & LODs |
| `socal-pine-needle-duff-sun-warmed-copper-needle-carpet-with-jeffrey-cones` | 4.2 | Refine Shaders & LODs |
| `socal-prickly-pear` | 4.2 | Refine Shaders & LODs |
| `socal-scrub-oak-mature-summer-spiny-leathery` | 4.2 | Refine Shaders & LODs |
| `socal-silver-cholla-old-spreading-candelabra-dry-fruit` | 4.2 | Refine Shaders & LODs |
| `socal-teddy-bear-cholla` | 4.2 | Refine Shaders & LODs |
| `socal-white-sage-mature-autumn-dry-flower-wands` | 4.2 | Refine Shaders & LODs |
| `socal-white-sage-young-silver-rosette` | 4.2 | Refine Shaders & LODs |
| `sugar-bush--young` | 4.2 | Refine Shaders & LODs |
| `toyon-christmasberry` | 4.2 | Refine Shaders & LODs |
| `toyon-christmasberry--young` | 4.2 | Refine Shaders & LODs |
| `white-bursage--establishment` | 4.2 | Refine Shaders & LODs |
| `yucca-rosette--young` | 4.2 | Refine Shaders & LODs |
| `california-buckwheat--young` | 4.5 | Refine Shaders & LODs |
| `socal-chamise-young-spring-bloom` | 4.5 | Refine Shaders & LODs |
| `white-bursage` | 4.5 | Refine Shaders & LODs |

### Sierra (120 low scorers)
| Asset Name | Argon Critic Score | Remediation Priority |
| :--- | :---: | :--- |
| `hs-v2-rock-granite-slab-whaleback-broad` | 0.0 | Immediate Re-bake / Re-mesh |
| `hs-v2-extra-010` | 1.5 | Immediate Re-bake / Re-mesh |
| `hs-v2-extra-011` | 1.5 | Immediate Re-bake / Re-mesh |
| `hs-v2-extra-021` | 1.0 | Immediate Re-bake / Re-mesh |
| `hs-v2-extra-055` | 1.5 | Immediate Re-bake / Re-mesh |
| `socal-jeffrey-pine-mature-tall-puzzle-bark-summer-canopy` | 1.5 | Immediate Re-bake / Re-mesh |
| `yellow-bellied-marmot-american-pika` | 1.5 | Immediate Re-bake / Re-mesh |
| `high-sierra-sedge-clump-v1` | 2.0 | Immediate Re-bake / Re-mesh |
| `hs-v2-extra-001` | 2.0 | Immediate Re-bake / Re-mesh |
| `hs-v2-extra-014` | 2.0 | Immediate Re-bake / Re-mesh |
| `hs-v2-extra-019` | 2.0 | Immediate Re-bake / Re-mesh |
| `hs-v2-extra-038` | 2.0 | Immediate Re-bake / Re-mesh |
| `hs-v2-extra-050` | 2.0 | Immediate Re-bake / Re-mesh |
| `hs-v2-extra-062` | 2.0 | Immediate Re-bake / Re-mesh |
| `hs-v2-tree-whitebark-burned-ridge-snag` | 2.0 | Immediate Re-bake / Re-mesh |
| `hs-v2-tree-whitebark-veteran-prostrate-banner` | 2.0 | Immediate Re-bake / Re-mesh |
| `moss-crust-set` | 2.0 | Immediate Re-bake / Re-mesh |
| `mule-deer-bighorn-sheep` | 2.0 | Immediate Re-bake / Re-mesh |
| `rock-lichen-varnish` | 2.0 | Immediate Re-bake / Re-mesh |
| `white-fir` | 2.0 | Immediate Re-bake / Re-mesh |
| `whitebark-pine` | 2.0 | Immediate Re-bake / Re-mesh |
| `aplite-pegmatite-dike-slab` | 2.5 | Immediate Re-bake / Re-mesh |
| `burn-snags-stumps-logs` | 2.5 | Immediate Re-bake / Re-mesh |
| `foxtail-pine` | 2.5 | Immediate Re-bake / Re-mesh |
| `hs-v2-extra-002` | 2.5 | Immediate Re-bake / Re-mesh |
| `hs-v2-extra-003` | 2.5 | Immediate Re-bake / Re-mesh |
| `hs-v2-extra-006` | 2.5 | Immediate Re-bake / Re-mesh |
| `hs-v2-extra-008` | 2.5 | Immediate Re-bake / Re-mesh |
| `hs-v2-extra-013` | 2.5 | Immediate Re-bake / Re-mesh |
| `hs-v2-extra-015` | 2.5 | Immediate Re-bake / Re-mesh |
| `hs-v2-extra-016` | 2.5 | Immediate Re-bake / Re-mesh |
| `hs-v2-extra-024` | 2.5 | Immediate Re-bake / Re-mesh |
| `hs-v2-extra-051` | 2.5 | Immediate Re-bake / Re-mesh |
| `hs-v2-extra-057` | 2.5 | Immediate Re-bake / Re-mesh |
| `hs-v2-extra-060` | 2.5 | Immediate Re-bake / Re-mesh |
| `hs-v2-tree-lodgepole-burned-standing` | 2.5 | Immediate Re-bake / Re-mesh |
| `hs-v2-tree-lodgepole-snag-barkless` | 2.5 | Immediate Re-bake / Re-mesh |
| `hs-v2-tree-red-fir-young-gap-grown` | 2.5 | Immediate Re-bake / Re-mesh |
| `mountain-mahogany` | 2.5 | Immediate Re-bake / Re-mesh |
| `snow-suncups-penitentes-drift` | 2.5 | Immediate Re-bake / Re-mesh |
| `socal-jeffrey-pine-mature-winter-snow-mantled-sky-island` | 2.5 | Immediate Re-bake / Re-mesh |
| `socal-jeffrey-pine-old-growth-flat-top-basal-fire-catface` | 2.5 | Immediate Re-bake / Re-mesh |
| `stellers-jay-clark-nutcracker` | 2.5 | Immediate Re-bake / Re-mesh |
| `western-juniper` | 2.5 | Immediate Re-bake / Re-mesh |
| `western-white-pine` | 2.5 | Immediate Re-bake / Re-mesh |
| `whitebark-pine--sapling` | 2.5 | Immediate Re-bake / Re-mesh |
| `grus-tread-soil` | 3.0 | Refine Shaders & LODs |
| `high-sierra-lodgepole-detail-v1` | 3.0 | Refine Shaders & LODs |
| `hs-v2-extra-017` | 3.0 | Refine Shaders & LODs |
| `hs-v2-extra-022` | 3.0 | Refine Shaders & LODs |
| `hs-v2-extra-059` | 3.0 | Refine Shaders & LODs |
| `hs-v2-extra-069` | 3.0 | Refine Shaders & LODs |
| `hs-v2-tree-lodgepole-sapling-snowbent` | 3.0 | Refine Shaders & LODs |
| `hs-v2-tree-lodgepole-veteran-slab-anchored` | 3.0 | Refine Shaders & LODs |
| `hs-v2-tree-lodgepole-young-grove` | 3.0 | Refine Shaders & LODs |
| `hs-v2-tree-red-fir-fallen-log-shattered` | 3.0 | Refine Shaders & LODs |
| `jeffrey-pine` | 3.0 | Refine Shaders & LODs |
| `mountain-mahogany--establishment` | 3.2 | Refine Shaders & LODs |
| `staghorn-wolf-lichen` | 3.2 | Refine Shaders & LODs |
| `andesite-breccia-hoodoo-pinnacle` | 3.5 | Refine Shaders & LODs |
| `high-sierra-whitebark-krummholz-v1` | 3.5 | Refine Shaders & LODs |
| `hs-v2-extra-007` | 3.5 | Refine Shaders & LODs |
| `hs-v2-extra-009` | 3.5 | Refine Shaders & LODs |
| `hs-v2-extra-020` | 3.5 | Refine Shaders & LODs |
| `hs-v2-extra-033` | 3.5 | Refine Shaders & LODs |
| `hs-v2-extra-034` | 3.5 | Refine Shaders & LODs |
| `hs-v2-extra-035` | 3.5 | Refine Shaders & LODs |
| `hs-v2-extra-045` | 3.5 | Refine Shaders & LODs |
| `hs-v2-extra-046` | 3.5 | Refine Shaders & LODs |
| `hs-v2-extra-063` | 3.5 | Refine Shaders & LODs |
| `hs-v2-extra-066` | 3.5 | Refine Shaders & LODs |
| `hs-v2-tree-lodgepole-mature-straight` | 3.5 | Refine Shaders & LODs |
| `hs-v2-tree-lodgepole-veteran-creek-leaner` | 3.5 | Refine Shaders & LODs |
| `hs-v2-tree-lodgepole-young-open` | 3.5 | Refine Shaders & LODs |
| `hs-v2-tree-red-fir-burned-hollow-bole` | 3.5 | Refine Shaders & LODs |
| `hs-v2-tree-red-fir-sapling-snowskirt` | 3.5 | Refine Shaders & LODs |
| `hs-v2-tree-whitebark-fallen-branch-cluster` | 3.5 | Refine Shaders & LODs |
| `hs-v2-tree-whitebark-snag-bleached` | 3.5 | Refine Shaders & LODs |
| `indian-paintbrush-penstemon` | 3.5 | Refine Shaders & LODs |
| `pinemat-manzanita` | 3.5 | Refine Shaders & LODs |
| `quaking-aspen` | 3.5 | Refine Shaders & LODs |
| `sierra-bush-chinquapin` | 3.5 | Refine Shaders & LODs |
| `sierra-mule-ears` | 3.5 | Refine Shaders & LODs |
| `socal-jeffrey-pine-mature-rain-wet-dark-cinnamon-plates` | 3.5 | Refine Shaders & LODs |
| `socal-jeffrey-pine-young-pole-stage-dense-needles` | 3.5 | Refine Shaders & LODs |
| `western-juniper--young` | 3.5 | Refine Shaders & LODs |
| `western-white-pine--sapling` | 3.5 | Refine Shaders & LODs |
| `white-fir--young` | 3.5 | Refine Shaders & LODs |
| `california-black-oak` | 4.0 | Refine Shaders & LODs |
| `hs-v2-extra-018` | 4.0 | Refine Shaders & LODs |
| `hs-v2-extra-032` | 4.0 | Refine Shaders & LODs |
| `hs-v2-extra-049` | 4.0 | Refine Shaders & LODs |
| `hs-v2-extra-058` | 4.0 | Refine Shaders & LODs |
| `hs-v2-extra-061` | 4.0 | Refine Shaders & LODs |
| `california-black-oak--young` | 4.2 | Refine Shaders & LODs |
| `california-red-fir--young` | 4.2 | Refine Shaders & LODs |
| `foxtail-pine--young` | 4.2 | Refine Shaders & LODs |
| `glacial-moraine-erratic-till` | 4.2 | Refine Shaders & LODs |
| `hs-v2-extra-005` | 4.2 | Refine Shaders & LODs |
| `hs-v2-extra-041` | 4.2 | Refine Shaders & LODs |
| `hs-v2-extra-053` | 4.2 | Refine Shaders & LODs |
| `hs-v2-extra-054` | 4.2 | Refine Shaders & LODs |
| `hs-v2-extra-067` | 4.2 | Refine Shaders & LODs |
| `hs-v2-extra-068` | 4.2 | Refine Shaders & LODs |
| `hs-v2-tree-lodgepole-sapling-sheltered` | 4.2 | Refine Shaders & LODs |
| `hs-v2-tree-red-fir-snag-broken-top` | 4.2 | Refine Shaders & LODs |
| `idaho-green-fescue` | 4.2 | Refine Shaders & LODs |
| `incense-cedar--young` | 4.2 | Refine Shaders & LODs |
| `mountain-misery-kitkitdizze` | 4.2 | Refine Shaders & LODs |
| `pine-needle-duff` | 4.2 | Refine Shaders & LODs |
| `ponderosa-pine` | 4.2 | Refine Shaders & LODs |
| `riparian-juncus-sedge` | 4.2 | Refine Shaders & LODs |
| `sierra-roof-pendant-marble-hornfels` | 4.2 | Refine Shaders & LODs |
| `sky-pilot-polemonium` | 4.2 | Refine Shaders & LODs |
| `western-juniper--sapling` | 4.2 | Refine Shaders & LODs |
| `western-white-pine--young` | 4.2 | Refine Shaders & LODs |
| `whitebark-pine--young` | 4.2 | Refine Shaders & LODs |

### NorCal (72 low scorers)
| Asset Name | Argon Critic Score | Remediation Priority |
| :--- | :---: | :--- |
| `norcal-basalt` | 0.0 | Immediate Re-bake / Re-mesh |
| `norcal-gen-manzanita-burned-resprout` | 1.0 | Immediate Re-bake / Re-mesh |
| `snowbrush-ceanothus` | 1.0 | Immediate Re-bake / Re-mesh |
| `black-cottonwood--young` | 1.5 | Immediate Re-bake / Re-mesh |
| `norcal-gen-andesite-boulder` | 1.5 | Immediate Re-bake / Re-mesh |
| `norcal-gen-basalt-wet-cobble` | 1.5 | Immediate Re-bake / Re-mesh |
| `norcal-gen-ponderosa-old` | 1.5 | Immediate Re-bake / Re-mesh |
| `norcal-serpentinite` | 1.5 | Immediate Re-bake / Re-mesh |
| `white-alder--young` | 1.5 | Immediate Re-bake / Re-mesh |
| `bigleaf-maple` | 2.0 | Immediate Re-bake / Re-mesh |
| `norcal-gen-basalt-talus` | 2.0 | Immediate Re-bake / Re-mesh |
| `norcal-gen-incense-cedar-fallen` | 2.0 | Immediate Re-bake / Re-mesh |
| `pacific-yew--young` | 2.0 | Immediate Re-bake / Re-mesh |
| `bigleaf-maple--sapling` | 2.2 | Immediate Re-bake / Re-mesh |
| `bigleaf-maple--young` | 2.5 | Immediate Re-bake / Re-mesh |
| `giant-chinquapin` | 2.5 | Immediate Re-bake / Re-mesh |
| `norcal-douglas-fir` | 2.5 | Immediate Re-bake / Re-mesh |
| `norcal-gen-andesite-wet-cobble` | 2.5 | Immediate Re-bake / Re-mesh |
| `norcal-gen-basalt-boulder` | 2.5 | Immediate Re-bake / Re-mesh |
| `norcal-gen-douglas-fir-mature` | 2.5 | Immediate Re-bake / Re-mesh |
| `norcal-gen-douglas-fir-young` | 2.5 | Immediate Re-bake / Re-mesh |
| `norcal-gen-incense-cedar-burned` | 2.5 | Immediate Re-bake / Re-mesh |
| `norcal-gen-incense-cedar-old` | 2.5 | Immediate Re-bake / Re-mesh |
| `norcal-gen-manzanita-mature` | 2.5 | Immediate Re-bake / Re-mesh |
| `norcal-gen-manzanita-young` | 2.5 | Immediate Re-bake / Re-mesh |
| `norcal-gen-ponderosa-snag` | 2.5 | Immediate Re-bake / Re-mesh |
| `norcal-gen-sugar-pine-fallen` | 2.5 | Immediate Re-bake / Re-mesh |
| `norcal-gen-sugar-pine-old` | 2.5 | Immediate Re-bake / Re-mesh |
| `norcal-sugar-pine` | 2.5 | Immediate Re-bake / Re-mesh |
| `pacific-yew--sapling` | 2.5 | Immediate Re-bake / Re-mesh |
| `white-alder` | 2.5 | Immediate Re-bake / Re-mesh |
| `white-alder--sapling` | 2.5 | Immediate Re-bake / Re-mesh |
| `giant-chinquapin--sapling` | 3.0 | Refine Shaders & LODs |
| `incense-cedar` | 3.0 | Refine Shaders & LODs |
| `norcal-gen-andesite-dry-cobble` | 3.0 | Refine Shaders & LODs |
| `norcal-gen-douglas-fir-snag` | 3.0 | Refine Shaders & LODs |
| `norcal-gen-incense-cedar-young` | 3.0 | Refine Shaders & LODs |
| `norcal-gen-manzanita-dead` | 3.0 | Refine Shaders & LODs |
| `norcal-gen-ponderosa-burned` | 3.0 | Refine Shaders & LODs |
| `norcal-gen-ponderosa-mature` | 3.0 | Refine Shaders & LODs |
| `norcal-gen-sugar-pine-mature` | 3.0 | Refine Shaders & LODs |
| `poison-oak--establishment` | 3.0 | Refine Shaders & LODs |
| `poison-oak--young` | 3.0 | Refine Shaders & LODs |
| `norcal-gen-douglas-fir-fallen` | 3.2 | Refine Shaders & LODs |
| `coast-douglas-fir` | 3.5 | Refine Shaders & LODs |
| `coast-douglas-fir--young` | 3.5 | Refine Shaders & LODs |
| `greenleaf-manzanita` | 3.5 | Refine Shaders & LODs |
| `greenleaf-manzanita--young` | 3.5 | Refine Shaders & LODs |
| `klamath-serpentinite-peridotite` | 3.5 | Refine Shaders & LODs |
| `mountain-whitethorn` | 3.5 | Refine Shaders & LODs |
| `norcal-gen-basalt-dry-cobble` | 3.5 | Refine Shaders & LODs |
| `norcal-gen-douglas-fir-burned` | 3.5 | Refine Shaders & LODs |
| `norcal-gen-douglas-fir-old` | 3.5 | Refine Shaders & LODs |
| `norcal-gen-manzanita-bloom` | 3.5 | Refine Shaders & LODs |
| `norcal-gen-manzanita-fallen-branch` | 3.5 | Refine Shaders & LODs |
| `norcal-gen-manzanita-old` | 3.5 | Refine Shaders & LODs |
| `norcal-gen-manzanita-seedling` | 3.5 | Refine Shaders & LODs |
| `norcal-gen-ponderosa-sapling` | 3.5 | Refine Shaders & LODs |
| `norcal-gen-sugar-pine-burned` | 3.5 | Refine Shaders & LODs |
| `norcal-gen-sugar-pine-sapling` | 3.5 | Refine Shaders & LODs |
| `pacific-madrone--sapling` | 3.5 | Refine Shaders & LODs |
| `sadler-oak--establishment` | 3.5 | Refine Shaders & LODs |
| `norcal-manzanita` | 4.0 | Refine Shaders & LODs |
| `coast-douglas-fir--sapling` | 4.2 | Refine Shaders & LODs |
| `norcal-gen-douglas-fir-sapling` | 4.2 | Refine Shaders & LODs |
| `norcal-gen-incense-cedar-snag` | 4.2 | Refine Shaders & LODs |
| `norcal-gen-ponderosa-young` | 4.2 | Refine Shaders & LODs |
| `norcal-gen-sugar-pine-snag` | 4.2 | Refine Shaders & LODs |
| `norcal-gen-sugar-pine-young` | 4.2 | Refine Shaders & LODs |
| `norcal-ponderosa` | 4.2 | Refine Shaders & LODs |
| `sugar-pine` | 4.2 | Refine Shaders & LODs |
| `sugar-pine--young` | 4.2 | Refine Shaders & LODs |

### Oregon (12 low scorers)
| Asset Name | Argon Critic Score | Remediation Priority |
| :--- | :---: | :--- |
| `oregon-huckleberry-01` | 2.0 | Immediate Re-bake / Re-mesh |
| `oregon-mazama-pumice-01` | 2.0 | Immediate Re-bake / Re-mesh |
| `oregon-white-oak` | 2.0 | Immediate Re-bake / Re-mesh |
| `arrowleaf-balsamroot` | 2.5 | Immediate Re-bake / Re-mesh |
| `oregon-three-sided-log-shelter` | 2.5 | Immediate Re-bake / Re-mesh |
| `oregon-white-oak--young` | 2.5 | Immediate Re-bake / Re-mesh |
| `oregon-lungwort-lobaria` | 3.0 | Refine Shaders & LODs |
| `oregon-oxalis-twinflower` | 3.0 | Refine Shaders & LODs |
| `aa-basalt-lava-clinker` | 3.5 | Refine Shaders & LODs |
| `oregon-grape--young` | 3.5 | Refine Shaders & LODs |
| `oregon-white-oak--sapling` | 4.2 | Refine Shaders & LODs |
| `pacific-rhododendron--young` | 4.2 | Refine Shaders & LODs |

### Washington (156 low scorers)
| Asset Name | Argon Critic Score | Remediation Priority |
| :--- | :---: | :--- |
| `noble-fir--young` | 1.0 | Immediate Re-bake / Re-mesh |
| `washington-cascade-volcanic-basalt-andesite-v06` | 1.0 | Immediate Re-bake / Re-mesh |
| `washington-mountain-hemlock-v03` | 1.0 | Immediate Re-bake / Re-mesh |
| `old-mans-beard-usnea` | 1.5 | Immediate Re-bake / Re-mesh |
| `washington-douglas-fir-v04` | 1.5 | Immediate Re-bake / Re-mesh |
| `washington-douglas-fir-v07` | 1.5 | Immediate Re-bake / Re-mesh |
| `washington-pacific-silver-fir-v01` | 1.5 | Immediate Re-bake / Re-mesh |
| `washington-vine-maple-v01` | 1.5 | Immediate Re-bake / Re-mesh |
| `washington-vine-maple-v08` | 1.5 | Immediate Re-bake / Re-mesh |
| `washington-western-redcedar-v04` | 1.5 | Immediate Re-bake / Re-mesh |
| `thimbleberry--establishment` | 2.0 | Immediate Re-bake / Re-mesh |
| `vine-maple` | 2.0 | Immediate Re-bake / Re-mesh |
| `vine-maple--establishment` | 2.0 | Immediate Re-bake / Re-mesh |
| `washington-cascade-volcanic-basalt-andesite-v01` | 2.0 | Immediate Re-bake / Re-mesh |
| `washington-devils-club-v04` | 2.0 | Immediate Re-bake / Re-mesh |
| `washington-douglas-fir-v03` | 2.0 | Immediate Re-bake / Re-mesh |
| `washington-forest-mossy-boulder-v04` | 2.0 | Immediate Re-bake / Re-mesh |
| `washington-red-alder-v03` | 2.0 | Immediate Re-bake / Re-mesh |
| `washington-vine-maple-v06` | 2.0 | Immediate Re-bake / Re-mesh |
| `washington-western-redcedar-v02` | 2.0 | Immediate Re-bake / Re-mesh |
| `washington-western-redcedar-v05` | 2.0 | Immediate Re-bake / Re-mesh |
| `washington-white-mountain-heather-v06` | 2.0 | Immediate Re-bake / Re-mesh |
| `western-hemlock` | 2.0 | Immediate Re-bake / Re-mesh |
| `washington-forest-mossy-boulder-v05` | 2.1 | Immediate Re-bake / Re-mesh |
| `alaska-yellow-cedar` | 2.5 | Immediate Re-bake / Re-mesh |
| `avalanche-glacier-lily` | 2.5 | Immediate Re-bake / Re-mesh |
| `cascades-root-step-mud-wallow` | 2.5 | Immediate Re-bake / Re-mesh |
| `red-huckleberry--establishment` | 2.5 | Immediate Re-bake / Re-mesh |
| `thinleaf-huckleberry--establishment` | 2.5 | Immediate Re-bake / Re-mesh |
| `washington-cascade-volcanic-basalt-andesite-v03` | 2.5 | Immediate Re-bake / Re-mesh |
| `washington-cascade-volcanic-basalt-andesite-v08` | 2.5 | Immediate Re-bake / Re-mesh |
| `washington-forest-mossy-boulder-v01` | 2.5 | Immediate Re-bake / Re-mesh |
| `washington-forest-mossy-boulder-v08` | 2.5 | Immediate Re-bake / Re-mesh |
| `washington-mountain-hemlock-v02` | 2.5 | Immediate Re-bake / Re-mesh |
| `washington-mountain-hemlock-v05` | 2.5 | Immediate Re-bake / Re-mesh |
| `washington-mountain-hemlock-v07` | 2.5 | Immediate Re-bake / Re-mesh |
| `washington-pacific-silver-fir-v05` | 2.5 | Immediate Re-bake / Re-mesh |
| `washington-pacific-silver-fir-v07` | 2.5 | Immediate Re-bake / Re-mesh |
| `washington-pnw-sword-fern-v05` | 2.5 | Immediate Re-bake / Re-mesh |
| `washington-red-alder-v02` | 2.5 | Immediate Re-bake / Re-mesh |
| `washington-subalpine-fir-v03` | 2.5 | Immediate Re-bake / Re-mesh |
| `washington-subalpine-fir-v05` | 2.5 | Immediate Re-bake / Re-mesh |
| `washington-subalpine-lupine-v05` | 2.5 | Immediate Re-bake / Re-mesh |
| `washington-subalpine-lupine-v08` | 2.5 | Immediate Re-bake / Re-mesh |
| `washington-western-redcedar-v01` | 2.5 | Immediate Re-bake / Re-mesh |
| `washington-western-redcedar-v06` | 2.5 | Immediate Re-bake / Re-mesh |
| `washington-western-redcedar-v07` | 2.5 | Immediate Re-bake / Re-mesh |
| `washington-western-redcedar-v08` | 2.5 | Immediate Re-bake / Re-mesh |
| `washington-white-mountain-heather-v05` | 2.5 | Immediate Re-bake / Re-mesh |
| `western-redcedar` | 2.5 | Immediate Re-bake / Re-mesh |
| `western-serviceberry--young` | 2.5 | Immediate Re-bake / Re-mesh |
| `alaska-yellow-cedar--young` | 3.0 | Refine Shaders & LODs |
| `cascades-cedar-stump-springboard` | 3.0 | Refine Shaders & LODs |
| `devils-club--establishment` | 3.0 | Refine Shaders & LODs |
| `glacier-peak-dacite-tephra-bank` | 3.0 | Refine Shaders & LODs |
| `sitka-alder--establishment` | 3.0 | Refine Shaders & LODs |
| `subalpine-fir--sapling` | 3.0 | Refine Shaders & LODs |
| `washington-black-alpine-sedge-v07` | 3.0 | Refine Shaders & LODs |
| `washington-cascade-volcanic-basalt-andesite-v04` | 3.0 | Refine Shaders & LODs |
| `washington-cascade-volcanic-basalt-andesite-v05` | 3.0 | Refine Shaders & LODs |
| `washington-douglas-fir-v01` | 3.0 | Refine Shaders & LODs |
| `washington-forest-mossy-boulder-v03` | 3.0 | Refine Shaders & LODs |
| `washington-mountain-hemlock-v01` | 3.0 | Refine Shaders & LODs |
| `washington-pacific-silver-fir-v03` | 3.0 | Refine Shaders & LODs |
| `washington-red-alder-v06` | 3.0 | Refine Shaders & LODs |
| `western-redcedar--sapling` | 3.0 | Refine Shaders & LODs |
| `western-skunk-cabbage` | 3.0 | Refine Shaders & LODs |
| `sitka-alder--young` | 3.2 | Refine Shaders & LODs |
| `alaska-yellow-cedar--sapling` | 3.5 | Refine Shaders & LODs |
| `devils-club` | 3.5 | Refine Shaders & LODs |
| `engelmann-spruce` | 3.5 | Refine Shaders & LODs |
| `engelmann-spruce--sapling` | 3.5 | Refine Shaders & LODs |
| `noble-fir` | 3.5 | Refine Shaders & LODs |
| `nurse-log-hemlock-seedlings` | 3.5 | Refine Shaders & LODs |
| `salal-gaultheria--young` | 3.5 | Refine Shaders & LODs |
| `salmonberry--establishment` | 3.5 | Refine Shaders & LODs |
| `subalpine-larch--sapling` | 3.5 | Refine Shaders & LODs |
| `thimbleberry` | 3.5 | Refine Shaders & LODs |
| `washington-cascade-huckleberry-v05` | 3.5 | Refine Shaders & LODs |
| `washington-cascade-huckleberry-v06` | 3.5 | Refine Shaders & LODs |
| `washington-cascade-volcanic-basalt-andesite-v02` | 3.5 | Refine Shaders & LODs |
| `washington-cascade-volcanic-basalt-andesite-v07` | 3.5 | Refine Shaders & LODs |
| `washington-devils-club-v03` | 3.5 | Refine Shaders & LODs |
| `washington-devils-club-v05` | 3.5 | Refine Shaders & LODs |
| `washington-devils-club-v06` | 3.5 | Refine Shaders & LODs |
| `washington-devils-club-v07` | 3.5 | Refine Shaders & LODs |
| `washington-devils-club-v08` | 3.5 | Refine Shaders & LODs |
| `washington-douglas-fir-v02` | 3.5 | Refine Shaders & LODs |
| `washington-douglas-fir-v06` | 3.5 | Refine Shaders & LODs |
| `washington-douglas-fir-v08` | 3.5 | Refine Shaders & LODs |
| `washington-forest-mossy-boulder-v02` | 3.5 | Refine Shaders & LODs |
| `washington-mountain-hemlock-v04` | 3.5 | Refine Shaders & LODs |
| `washington-pacific-silver-fir-v02` | 3.5 | Refine Shaders & LODs |
| `washington-pacific-silver-fir-v04` | 3.5 | Refine Shaders & LODs |
| `washington-pacific-silver-fir-v06` | 3.5 | Refine Shaders & LODs |
| `washington-pacific-silver-fir-v08` | 3.5 | Refine Shaders & LODs |
| `washington-pink-mountain-heather-v01` | 3.5 | Refine Shaders & LODs |
| `washington-pink-mountain-heather-v02` | 3.5 | Refine Shaders & LODs |
| `washington-pink-mountain-heather-v04` | 3.5 | Refine Shaders & LODs |
| `washington-pink-mountain-heather-v05` | 3.5 | Refine Shaders & LODs |
| `washington-pnw-sword-fern-v04` | 3.5 | Refine Shaders & LODs |
| `washington-red-alder-v05` | 3.5 | Refine Shaders & LODs |
| `washington-subalpine-fir-v01` | 3.5 | Refine Shaders & LODs |
| `washington-subalpine-lupine-v01` | 3.5 | Refine Shaders & LODs |
| `washington-subalpine-lupine-v04` | 3.5 | Refine Shaders & LODs |
| `washington-subalpine-lupine-v07` | 3.5 | Refine Shaders & LODs |
| `washington-vine-maple-v02` | 3.5 | Refine Shaders & LODs |
| `washington-vine-maple-v04` | 3.5 | Refine Shaders & LODs |
| `washington-western-pasqueflower-v04` | 3.5 | Refine Shaders & LODs |
| `washington-western-pasqueflower-v06` | 3.5 | Refine Shaders & LODs |
| `washington-western-pasqueflower-v07` | 3.5 | Refine Shaders & LODs |
| `washington-western-redcedar-v03` | 3.5 | Refine Shaders & LODs |
| `washington-white-mountain-heather-v07` | 3.5 | Refine Shaders & LODs |
| `western-hemlock--sapling` | 3.5 | Refine Shaders & LODs |
| `western-serviceberry--establishment` | 3.5 | Refine Shaders & LODs |
| `western-sword-fern` | 3.5 | Refine Shaders & LODs |
| `fireweed-chamaenerion` | 4.0 | Refine Shaders & LODs |
| `oceanspray-holodiscus` | 4.0 | Refine Shaders & LODs |
| `washington-black-alpine-sedge-v06` | 4.0 | Refine Shaders & LODs |
| `washington-black-alpine-sedge-v08` | 4.0 | Refine Shaders & LODs |
| `washington-pink-mountain-heather-v06` | 4.0 | Refine Shaders & LODs |
| `washington-red-alder-v08` | 4.0 | Refine Shaders & LODs |
| `washington-subalpine-fir-v04` | 4.0 | Refine Shaders & LODs |
| `washington-subalpine-lupine-v02` | 4.0 | Refine Shaders & LODs |
| `western-serviceberry` | 4.0 | Refine Shaders & LODs |
| `devils-club--young` | 4.2 | Refine Shaders & LODs |
| `engelmann-spruce--young` | 4.2 | Refine Shaders & LODs |
| `mountain-hemlock` | 4.2 | Refine Shaders & LODs |
| `noble-fir--sapling` | 4.2 | Refine Shaders & LODs |
| `north-cascades-migmatite-gneiss` | 4.2 | Refine Shaders & LODs |
| `pacific-silver-fir--young` | 4.2 | Refine Shaders & LODs |
| `salal-gaultheria--establishment` | 4.2 | Refine Shaders & LODs |
| `thimbleberry--young` | 4.2 | Refine Shaders & LODs |
| `washington-black-alpine-sedge-v01` | 4.2 | Refine Shaders & LODs |
| `washington-black-alpine-sedge-v03` | 4.2 | Refine Shaders & LODs |
| `washington-cascade-huckleberry-v03` | 4.2 | Refine Shaders & LODs |
| `washington-cascade-huckleberry-v08` | 4.2 | Refine Shaders & LODs |
| `washington-devils-club-v02` | 4.2 | Refine Shaders & LODs |
| `washington-douglas-fir-v05` | 4.2 | Refine Shaders & LODs |
| `washington-mountain-hemlock-v06` | 4.2 | Refine Shaders & LODs |
| `washington-mountain-hemlock-v08` | 4.2 | Refine Shaders & LODs |
| `washington-pink-mountain-heather-v03` | 4.2 | Refine Shaders & LODs |
| `washington-pink-mountain-heather-v08` | 4.2 | Refine Shaders & LODs |
| `washington-pnw-sword-fern-v06` | 4.2 | Refine Shaders & LODs |
| `washington-pnw-sword-fern-v08` | 4.2 | Refine Shaders & LODs |
| `washington-red-alder-v04` | 4.2 | Refine Shaders & LODs |
| `washington-subalpine-fir-v02` | 4.2 | Refine Shaders & LODs |
| `washington-subalpine-fir-v06` | 4.2 | Refine Shaders & LODs |
| `washington-subalpine-fir-v07` | 4.2 | Refine Shaders & LODs |
| `washington-subalpine-lupine-v03` | 4.2 | Refine Shaders & LODs |
| `washington-vine-maple-v03` | 4.2 | Refine Shaders & LODs |
| `washington-vine-maple-v07` | 4.2 | Refine Shaders & LODs |
| `washington-western-pasqueflower-v03` | 4.2 | Refine Shaders & LODs |
| `washington-white-mountain-heather-v08` | 4.2 | Refine Shaders & LODs |
| `western-pasqueflower` | 4.2 | Refine Shaders & LODs |
| `white-mountain-heather` | 4.2 | Refine Shaders & LODs |
| `washington-devils-club-v01` | 4.5 | Refine Shaders & LODs |
| `washington-white-mountain-heather-v02` | 4.5 | Refine Shaders & LODs |

### trail towns/roads/vehicles/gear (41 low scorers)
| Asset Name | Argon Critic Score | Remediation Priority |
| :--- | :---: | :--- |
| `prop_boots_1990s_full_grain_leather_vibram_sole` | 1.5 | Immediate Re-bake / Re-mesh |
| `prop_junction_signpost_routed_cedar_three_blade` | 1.5 | Immediate Re-bake / Re-mesh |
| `prop_puncheon_bridge_split_cedar_deck` | 1.5 | Immediate Re-bake / Re-mesh |
| `bedrock-granite-milling-mortars` | 2.0 | Immediate Re-bake / Re-mesh |
| `prop_pack_external_frame_three_pocket_canvas_70s80s` | 2.0 | Immediate Re-bake / Re-mesh |
| `usgs-brass-benchmark-triangulation` | 2.0 | Immediate Re-bake / Re-mesh |
| `boxed-spring-pipe-trough` | 2.5 | Immediate Re-bake / Re-mesh |
| `katadyn-pur-hiker-pump-filter` | 2.5 | Immediate Re-bake / Re-mesh |
| `prop_boots_1990s_trail_scuffed_mud_caked_pair` | 2.5 | Immediate Re-bake / Re-mesh |
| `prop_boots_split_suede_nylon_panel_midweight` | 2.5 | Immediate Re-bake / Re-mesh |
| `granite-dry-stone-retaining-wall` | 2.8 | Immediate Re-bake / Re-mesh |
| `1990s-internal-frame-expedition-pack` | 3.0 | Refine Shaders & LODs |
| `prop_cold_fire_ring_granite_circle` | 3.0 | Refine Shaders & LODs |
| `prop_trail_kiosk_cascades_moss_gabled` | 3.0 | Refine Shaders & LODs |
| `split-cedar-puncheon-turnpike` | 3.0 | Refine Shaders & LODs |
| `1980s-usfs-chevy-k10-ranger-truck` | 3.5 | Refine Shaders & LODs |
| `garcia-black-bear-canister-hang-bag` | 3.5 | Refine Shaders & LODs |
| `prop_cookware_nested_two_pot_mess_kit_strap` | 3.5 | Refine Shaders & LODs |
| `prop_mat_accordion_zfold_foam_strapped` | 3.5 | Refine Shaders & LODs |
| `prop_mat_rolled_foam_compact_three_quarter` | 3.5 | Refine Shaders & LODs |
| `prop_pack_external_frame_trail_worn_field_repaired` | 3.5 | Refine Shaders & LODs |
| `prop_stove_brass_packed_in_aluminum_cup_lid` | 3.5 | Refine Shaders & LODs |
| `prop_water_jug_hdpe_duct_tape_marked_cache` | 3.5 | Refine Shaders & LODs |
| `ranch-range-kit` | 3.5 | Refine Shaders & LODs |
| `single-log-flattened-footbridge` | 3.5 | Refine Shaders & LODs |
| `stacked-granite-duck-cairn` | 3.5 | Refine Shaders & LODs |
| `usfs-signs-register` | 3.5 | Refine Shaders & LODs |
| `water-cache-fire-ring` | 3.5 | Refine Shaders & LODs |
| `prop_mat_rolled_foam_trail_chewed_edges` | 4.0 | Refine Shaders & LODs |
| `prop_stove_remote_bottle_liquid_fuel_pump_90s` | 4.0 | Refine Shaders & LODs |
| `wooden-step-stile-fence-crossing` | 4.0 | Refine Shaders & LODs |
| `a-frame-nylon-tarp-bivy` | 4.2 | Refine Shaders & LODs |
| `camp-scatter-gear-kit` | 4.2 | Refine Shaders & LODs |
| `newspaper-rack-hiker-laundry-basket` | 4.2 | Refine Shaders & LODs |
| `northern-terminus-monument-boundary-obelisk` | 4.2 | Refine Shaders & LODs |
| `prop_trail_kiosk_sierra_heavy_snow_brace` | 4.2 | Refine Shaders & LODs |
| `prop_trail_register_wooden_gable_box` | 4.2 | Refine Shaders & LODs |
| `prop_water_jug_hdpe_1998_desert_cache` | 4.2 | Refine Shaders & LODs |
| `steel-pipe-stock-pass-chicane` | 4.2 | Refine Shaders & LODs |
| `prop_picnic_table_heavy_plank_bolted_frame` | 4.5 | Refine Shaders & LODs |

## 3. Top Missing Visually Signature PCT Objects: Ranking & Rationale

Thru-hiking the PCT is defined by unmistakable milestones, geological transformations, and navigation monuments. After auditing the 832 built assets against real-world PCT trail logs, USFS documentation, and hiker survey data, here are the top 10 most critical missing objects ranked by impact:

### 1. John Muir Memorial Shelter (Muir Hut) [P0] - Sierra
Situated at the 11,955-foot summit of Muir Pass in Kings Canyon National Park, this 1930 beehive granite hut (built by the Sierra Club and designed by Henry Gutterson) is the most famous high-alpine sanctuary in the Sierra Nevada. Thru-hikers climb through miles of barren granite and snowcups to reach it. While the inventory contains the low-elevation 'muir-trail-ranch-stone-hut' in the forest, the actual high-pass stone monument is completely absent.

### 2. Dee Wright Observatory [P0] - Oregon
Built by the CCC in 1935 atop McKenzie Pass (Mile 1983) entirely out of black vesicular aa basalt lava clinkers. Oregon is in a catastrophic deficit with only 16 assets in the library. Hikers traverse the grueling 65-square-mile Belknap Crater lava field under blazing sun; this fortress-like volcanic stone structure with viewing apertures framing the Three Sisters and Mt. Washington is the definitive visual anchor of Oregon Section E.

### 3. Devils Postpile Columnar Basalt Cliff & Talus [P0] - Sierra
Located at Mile 907 near Mammoth Lakes, this 60-foot vertical cliff of geometrically perfect 6-sided hexagonal and 5-sided pentagonal basalt columns (formed 82,000 years ago) with a sprawling columnar scree apron is one of the premier geological wonders of the trail. The inventory has generic basalt talus, but lacks this iconic geological marvel.

### 4. Vasquez Rocks Tilted Sandstone Hogback [P0] - SoCal desert
At Mile 451 in Agua Dulce, the PCT cuts directly through the iconic 45-to-50-degree tilted arkosic sandstone fins of the Mint Canyon Formation (famous from Star Trek and countless films). It marks the transition into the Sierra Pelona and is the definitive geological photo milestone of Southern California Section D.

### 5. Official PCT National Scenic Trail Crest Marker & Cedar Post [P0] - All Sections / Props
The official 9-inch triangular shield emblem (white baked enamel, green conifer silhouette, blue sky, snow peak) mounted on a 4x4 routed cedar post. While the inventory includes generic junction signs and kiosks, the official triangular PCT shield—the single most recognized navigational icon along all 2,650 miles—does not exist as a dedicated hero prop.

### 6. Pacific Crest Trail Midpoint Monument Sign [P1] - NorCal
Located at Mile 1325 near Chester and Highway 36, marking the exact geometric halfway point between Mexico and Canada (1,325 miles in each direction). A two-way wooden signboard with directional arrows and hiker register box where 100% of thru-hikers stop for celebration photographs.

### 7. Forester Pass Crest Elevation Sign & Chiseled Trail Shelf [P1] - Sierra
At 13,153 feet, Forester Pass is the absolute highest elevation on the Pacific Crest Trail. The sheer shelf blasted into the granite wall and the rustic Forest Service wooden elevation marker are unforgettable emotional milestones.

### 8. Timberline Lodge Historic Entrance & Trail Kiosk [P1] - Oregon
At Mile 2097 on the slopes of Mt. Hood, Timberline Lodge (1937 WPA masterpiece) is the only National Historic Landmark lodge sitting directly on the PCT tread, famous for thru-hiker breakfast buffets and iconic stone/timber architecture.

### 9. Goat Rocks Knife's Edge Route Cairn & Arête Spine [P1] - Washington
The narrow shattered andesite knife-edge ridge in the Goat Rocks Wilderness between Old Snowy Mountain and Gilbert Peak, legendary for precipitous drop-offs and sweeping views of Mt. Rainier, Mt. Adams, and Mt. St. Helens.

### 10. San Gorgonio Pass Water Cache Shaded Lean-To [P2] - SoCal desert
The iconic shade shelter and communal water container depot beneath the Interstate 10 underpass near Cabazon/Whitewater, representing the lifesaving trail-angel culture of the desert.

## 4. Emitted Asset Specs

The 5 highest priority assets (Ranked 1 through 5, all P0) have been fully researched with confirmed public domain/CC-licensed photographic references and emitted as validated asset specifications in `/workspace/specs/`:

1. `specs/muir_pass_stone_shelter.json` (Sierra - Architecture/Structures, 48k tris LOD0)
2. `specs/dee_wright_observatory.json` (Oregon - Architecture/Structures, 62k tris LOD0)
3. `specs/devils_postpile_columnar_basalt.json` (Sierra - Geology/Hero Rock, 68k tris LOD0)
4. `specs/vasquez_rocks_sandstone_hogback.json` (SoCal desert - Geology/Hero Rock, 58k tris LOD0)
5. `specs/pct_trail_marker_shield_post.json` (Trail-wide / Props - Hero Signage, 14.5k tris LOD0)