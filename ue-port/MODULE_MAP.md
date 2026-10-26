# THRU Core Game Logic: Module Map & Unreal Engine 5.6 Port Plan

## 1. Architectural Principles & Scope Boundary

THRU is a Pacific Crest Trail co-op hiking game set in 1980–1999. The core game logic is being ported from Godot 4 GDScript (`/work/src`) to Unreal Engine 5.6 C++ (`/work/port`).

### 1.1 Separation of Concerns
1. **Engine-Agnostic Core (`ThruCore/`)**:
   - Resides in namespace `thru::`.
   - C++17 standard, zero Unreal Engine headers.
   - Deterministic and pure: explicit time parameters (Julian day `double`, elapsed seconds, or game minutes), explicit seeded PRNG (`thru::Rng` xoshiro256** / splitmix64), immutable reference tables, pure state transitions.
   - Table loading is decoupled via `thru::DataSource` (interface) and `thru::FileDataSource` / `thru::MemoryDataSource` with `nlohmann::json`.
2. **Unreal Engine 5.6 Wrappers (`Unreal/ThruGame/Source/ThruGame/`)**:
   - Thin UE5 wrappers inheriting from `UGameInstanceSubsystem`, `UWorldSubsystem`, `UActorComponent`, or `UBlueprintFunctionLibrary`.
   - Wrap corresponding `thru::` core classes by value or `TUniquePtr<thru::...>`.
   - Expose `BlueprintCallable` / `BlueprintPure` functions, `UPROPERTY` mirrors, and dynamic multicast delegates for UI and audio notification.
   - Use standard UE 5.6 conventions (`THRUGAME_API`, `GENERATED_BODY()`, `.generated.h` includes).
3. **Automated Doctest Unit Tests (`tests/`)**:
   - Single-header doctest 2.4.11 in `tests/test_<module>.cpp`.
   - Every test encodes GDScript numbers, formulas, and edge conditions, citing exact `file:line` references from `/work/src`.

### 1.2 System Scopes
- **IN SCOPE**:
  1. **Day / Time / Calendar / Season / Weather / Celestial Sim**: Julian days, solar daylight, ephemeris, season snowpack (SWE), synoptic weather fronts, diurnal wind, cold air pooling, lightning acoustic delay, wildfire perimeter risk, smoke index, and phenology (mosquitoes, bloom, fall foliage, poodle-dog bush).
  2. **Player / Hiker State**: Caloric burn and late-season hunger, water carry projections, volunteer water caches, zero/nero pacing rhythm, camp lights-out / quiet hours etiquette, norovirus container contagion, named cohort wear/injury/fatigue.
  3. **Resupply & Towns**: Store/hostel/post office operating schedules, town temporal life, hiker box loot generation, resupply route planning, mail-drop package chains, hitchhiking wait times, town beds, and Kennedy Meadows South arrival applause.
  4. **Journal, Quests, Promises, & Encounters**: Trailhead registration logbooks, closed daily journal records, append-only world event ledger, encounter catalog loading, dinner promises contracts, directed social memory graph, salt-thief gear chewing, and trail dilemma troubles.
  5. **Film Camera Logic**: 1990s 35mm compact/disposable cameras, rolls, exposures, date backs, lab mailing, delivery times, photo albums, and framing composition scoring.
- **OUT OF SCOPE**:
  - Terrain generation, streaming, chunking, and mesh slicing (owned by `work/ue-scale`).
  - Viewport rendering, shaders, materials, sky atmosphere actors, GPU particles, and lighting components.
  - Character mesh binding, bone attachments, animation blending, and visual props.
  - Audio playback, sound cues, and buses (handled by UE audio subsystems).
  - Slate / UMG UI layout and widget trees (logic-only data exposed via wrappers).
  - Godot CI/editor tools and validation scripts.

---

## 2. Master Module Map Table

Below is the complete mapping of candidate files from the port specification, plus discovered domain files.

| GDScript File | Lines | In-Scope? | Unreal Class(es) | Dependencies | Difficulty | Reason / Role |
| :--- | :---: | :---: | :--- | :--- | :---: | :--- |
| `godot/scripts/trail_calendar.gd` | 128 | **YES** | `thru::TrailCalendar`<br>`UThruTrailCalendarLibrary` | None | S | Civil calendar, solar daylight, astronomical twilight, Julian day conversions. |
| `godot/scripts/celestial_math.gd` | 113 | **YES** | `thru::CelestialMath`<br>`UThruCelestialMathLibrary` | `thru::TrailCalendar` | S | Astronomical coordinate frames, equatorial to horizontal vector transforms, J2000 basis. |
| `godot/scripts/celestial_ephemeris.gd` | 98 | **YES** | `thru::CelestialEphemeris`<br>`UThruCelestialEphemeris` | `thru::CelestialMath`, `thru::DataSource` | S | NASA/JPL Sun and Moon positions table interpolation for campaign year. |
| `godot/scripts/celestial_sphere.gd` | 248 | **NO** | `N/A` (UE Sky Atmosphere) | `thru::CelestialMath` | M | Rendering: Star catalog MultiMesh instances and Moon shader quad. |
| `godot/scripts/trail_season.gd` | 625 | **YES** | `thru::TrailSeason`<br>`UThruTrailSeasonSubsystem` | `thru::TrailCalendar`, `thru::DataSource` | M | Historical climate records, snowpack, water availability, travel pace multipliers. |
| `godot/scripts/trail_year.gd` | 508 | **YES** | `thru::TrailYear`<br>`UThruTrailYearSubsystem` | `thru::TrailCalendar`, `thru::DataSource` | M | Modeled snow water equivalent (SWE) per half-mile route bin per calendar day. |
| `godot/scripts/intermittent_water.gd` | 125 | **YES** | `thru::IntermittentWater`<br>`UThruIntermittentWaterSubsystem` | `thru::TrailCalendar`, `thru::DataSource` | S | Intermittent watercourse seasonal flow windows across desert and mountain legs. |
| `godot/scripts/ford_crossings.gd` | 391 | **YES** | `thru::FordCrossings`<br>`UThruFordCrossingsSubsystem` | `thru::TrailCalendar`, `thru::TrailYear`, `thru::DataSource` | M | Snowmelt ford flow speed, water depth, and diurnal crossing hazard calculations. |
| `godot/scripts/weather_front.gd` | 268 | **YES** | `thru::WeatherFront`<br>`UThruWeatherFrontSubsystem` | `thru::TrailCalendar`, `thru::Rng` | M | Synoptic weather front spatial movement, boundary blending, and condition states. |
| `godot/scripts/thunder_delay.gd` | 195 | **YES** | `thru::ThunderDelay`<br>`UThruThunderDelayComponent` | `thru::DataSource` | S | Speed of sound delay and acoustic attenuation for lightning flash-to-bang timing. |
| `godot/scripts/wind_diurnal.gd` | 196 | **YES** | `thru::WindDiurnal`<br>`UThruWindDiurnalComponent` | `thru::TrailCalendar`, `thru::DataSource` | S | Solar-driven diurnal wind speed curve scaling and peak afternoon gust factors. |
| `godot/scripts/cold_air_pool.gd` | 233 | **YES** | `thru::ColdAirPool`<br>`UThruColdAirPoolComponent` | `thru::TrailCalendar`, `thru::DataSource` | S | Night-time cold air drainage, valley pooling deficit, and inversion temperatures. |
| `godot/scripts/geo_precipitation.gd` | 141 | **NO** | `N/A` (UE Niagara / Cascade) | `thru::WeatherFront` | S | Rendering: GPUParticles3D bounding box for local rain streaks and snow flakes. |
| `godot/scripts/fire_risk.gd` | 130 | **YES** | `thru::FireRisk`<br>`UThruFireRiskComponent` | `thru::DataSource` | S | Fine fuel moisture, Keetch-Byram drought index (KBDI), and fire danger rating. |
| `godot/scripts/fire_season.gd` | 210 | **YES** | `thru::FireSeason`<br>`UThruFireSeasonSubsystem` | `thru::DataSource` | S | MTBS historical fire perimeter boundaries and active burn day progression. |
| `godot/scripts/smoke_season.gd` | 395 | **YES** | `thru::SmokeSeason`<br>`UThruSmokeSeasonSubsystem` | `thru::TrailCalendar`, `thru::DataSource` | M | Regional wildfire smoke plume dispersion and atmospheric obscuration index. |
| `godot/scripts/mosquito_season.gd` | 354 | **YES** | `thru::MosquitoSeason`<br>`UThruMosquitoSeasonSubsystem` | `thru::TrailYear`, `thru::DataSource` | M | Post-snowmelt mosquito biting pressure model per route bin. |
| `godot/scripts/wildflower_bloom.gd` | 184 | **YES** | `thru::WildflowerBloom`<br>`UThruWildflowerBloomComponent` | `thru::TrailCalendar`, `thru::DataSource` | S | Regional wildflower phenological bloom timing and ground cover stage. |
| `godot/scripts/fall_colour.gd` | 130 | **YES** | `thru::FallColour`<br>`UThruFallColourComponent` | `thru::TrailCalendar`, `thru::DataSource` | S | Deciduous foliage autumn color turn timing and saturation by species. |
| `godot/scripts/poodle_dog_bush.gd` | 387 | **YES** | `thru::PoodleDogBush`<br>`UThruPoodleDogBushComponent` | `thru::TrailCalendar`, `thru::DataSource` | M | Burn scar chaparral contact dermatitis risk and trailside rash mechanics. |
| `godot/scripts/hiker_hunger.gd` | 175 | **YES** | `thru::HikerHunger`<br>`UThruHikerHungerComponent` | `thru::DataSource` | S | Caloric burn rates per mile and late-season through-hiker hunger curve. |
| `godot/scripts/water_carry_data.gd` | 78 | **YES** | `thru::WaterCarryData`<br>`UThruWaterCarryDatabase` | `thru::DataSource` | S | Hydrology data catalog of mapped drinkable springs, creeks, and caches. |
| `godot/scripts/water_carry.gd` | 110 | **YES** | `thru::WaterCarry`<br>`UThruWaterCarryComponent` | `thru::WaterCarryData`, `thru::IntermittentWater` | S | Look-ahead route projection to nearest viable water source and carry distance. |
| `godot/scripts/water_caches.gd` | 155 | **YES** | `thru::WaterCaches`<br>`UThruWaterCachesSubsystem` | `thru::DataSource`, `thru::Rng` | S | Volunteer-stocked water cache locations, daily draw, and empty chance. |
| `godot/scripts/hiker.gd` | 288 | **NO** | `thru::HikerVitals`<br>`AThruHikerCharacter` | Character pawn | M | CharacterBody3D: Node hierarchy, camera, animation, bottle physics, headlamp. Gameplay vitals logic ported into `thru::HikerVitals`. |
| `godot/scripts/hiker_bed.gd` | 42 | **NO** | `N/A` (Static mesh asset) | None | S | Rendering: Procedural BoxMesh pad and CapsuleMesh sleeping bag creation. |
| `godot/scripts/hiker_dress.gd` | 110 | **NO** | `N/A` (Skeletal mesh component) | None | S | Rendering: BoneAttachment3D cosmetic wardrobe hat and backpack sockets. |
| `godot/scripts/hiker_rhythm.gd` | 380 | **YES** | `thru::HikerRhythm`<br>`UThruHikerRhythmComponent` | `thru::TrailCalendar`, `thru::Rng`, `thru::DataSource` | M | Zero and nero day cadence, physical recovery pacing, and layover scheduling. |
| `godot/scripts/hiker_midnight.gd` | 278 | **YES** | `thru::HikerMidnight`<br>`UThruHikerMidnightComponent` | `thru::TrailCalendar`, `thru::DataSource` | S | 9:00 PM camp lights-out routine, quiet hours etiquette, and standing loss. |
| `godot/scripts/norovirus_outbreak.gd` | 553 lines | **YES** | `thru::NorovirusOutbreak`<br>`UThruNorovirusSubsystem` | `thru::TrailBubble`, `thru::Rng`, `thru::DataSource` | M | Bubble crowd contagion at shared jugs/boxes, sick days, and bunk closures. |
| `godot/scripts/trail_bubble.gd` | 203 | **YES** | `thru::TrailBubble`<br>`UThruTrailBubbleSubsystem` | `thru::TrailCalendar`, `thru::DataSource` | S | Gaussian wave progression of through-hiker density along trail miles. |
| `godot/scripts/trail_cohort.gd` | 430 | **YES** | `thru::TrailCohort`<br>`UThruTrailCohortSubsystem` | `thru::TrailBubble`, `thru::Rng`, `thru::DataSource` | M | Deterministic middle-tier named hiker generation with individual paces and departure dates. |
| `godot/scripts/hiker_cohort.gd` | 808 | **YES** | `thru::HikerCohort`<br>`UThruHikerCohortSubsystem` | `thru::TrailCohort`, `thru::Rng`, `thru::DataSource` | L | Daily wear, fatigue, injury, nutrition deficits, and bailout chance for cohort agents. |
| `godot/scripts/trail_permits.gd` | 193 | **YES** | `thru::TrailPermits`<br>`UThruTrailPermitsComponent` | `thru::TrailCalendar`, `thru::DataSource` | S | PCT inter-agency permit quota calendar, start windows, and quota allocations. |
| `godot/scripts/trail_resources.gd` | 160 | **YES** | `thru::TrailResources`<br>`UThruTrailResourcesSubsystem` | `thru::TrailCohort`, `thru::DataSource` | S | Cohort consumption of trail resources and lunch cache stock depletion. |
| `godot/scripts/town_hours.gd` | 335 | **YES** | `thru::TownHours`<br>`UThruTownHoursSubsystem` | `thru::TrailCalendar`, `thru::DataSource` | M | Resupply stop store, post office, hostel, and service operating hours. |
| `godot/scripts/town_schedule.gd` | 349 | **YES** | `thru::TownSchedule`<br>`UThruTownScheduleSubsystem` | `thru::TownHours`, `thru::DataSource` | M | Instantaneous activity state of town facilities against geographic trail clock. |
| `godot/scripts/trailhead_traffic.gd` | 229 | **YES** | `thru::TrailheadTraffic`<br>`UThruTrailheadTrafficSubsystem` | `thru::TrailCalendar`, `thru::DataSource` | S | Roadside access point vehicle counts, day-use hiker density, and parking pressure. |
| `godot/scripts/hiker_box.gd` | 225 | **YES** | `thru::HikerBox`<br>`UThruHikerBoxComponent` | `thru::TownHours`, `thru::Rng`, `thru::DataSource` | M | Resupply town hiker box inventory generation, deposits, and salvage loot. |
| `godot/scripts/resupply_plan.gd` | 157 | **YES** | `thru::ResupplyPlan`<br>`UThruResupplyPlanSubsystem` | `thru::TownHours`, `thru::TrailSeason` | S | Look-ahead resupply stop milestone planning, carry weights, and estimated arrival. |
| `godot/scripts/pct_box_chain.gd` | 149 | **YES** | `thru::PctBoxChain`<br>`UThruBoxChainSubsystem` | `thru::TownHours`, `thru::DataSource` | S | Postal resupply box chain routing, general delivery hops, and parcel claims. |
| `godot/scripts/kennedy_applause.gd` | 168 | **YES** | `thru::KennedyApplause`<br>`UThruKennedyApplauseComponent` | `thru::DataSource` | S | Milestone porch arrival celebration event at Kennedy Meadows South. |
| `godot/scripts/cash_register.gd` | 35 | **NO** | `N/A` (Static mesh actor) | None | S | Rendering: 3D cash register mesh loader with optical cover material override. |
| `godot/scripts/cash_register_stand.gd` | 42 | **NO** | `N/A` (Static mesh actor) | None | S | Rendering: Outdoor service counter visual stand and static box collision. |
| `godot/scripts/pct_cash_register_counter.gd` | 67 | **NO** | `thru::ServiceCounterPlacement` | None | S | Placement: Authored physical interaction counter spatial offsets. |
| `godot/scripts/snack_vending.gd` | 31 | **NO** | `N/A` (Static mesh actor) | None | S | Rendering: Vending machine mesh asset loader and review candidate. |
| `godot/scripts/snack_vending_site.gd` | 13 | **YES** | `thru::SnackVending`<br>`UThruSnackVendingComponent` | None | S | Authored short-hike shop snack purchasing and host-authoritative economy. |
| `godot/scripts/store_telephone.gd` | 228 | **NO** | `N/A` (Procedural mesh prop) | None | M | Rendering: Procedural CSG/mesh generation of generic desk telephone. |
| `godot/scripts/rural_mailbox.gd` | 28 | **NO** | `N/A` (Static mesh prop) | None | S | Rendering: Mailbox visual prop without rewards or persistence. |
| `godot/scripts/rural_mailbox_site.gd` | 80 | **NO** | `N/A` (Placement actor) | None | S | Placement: Mailbox visual placement seam. |
| `godot/scripts/postal_workbench.gd` | 36 | **NO** | `N/A` (Static mesh prop) | None | S | Rendering: Outdoor mail workbench visual prop at Mount Laguna. |
| `godot/scripts/hitch_wait.gd` | 235 | **YES** | `thru::HitchWait`<br>`UThruHitchWaitComponent` | `thru::TrailheadTraffic`, `thru::Rng`, `thru::DataSource` | M | Hitchhiking ride wait time calculation based on road class and traffic volume. |
| `godot/scripts/town_bed.gd` | 185 | **YES** | `thru::TownBed`<br>`UThruTownBedComponent` | `thru::TrailCalendar`, `thru::DataSource` | S | Resupply stop acoustic environment cues and lodging bed availability. |
| `godot/scripts/pct_towns.gd` | 1217 | **NO** | `N/A` (ue-scale streaming) | Procedural mesh | L | Streaming: Procedural building mesh generation from OSM footprints (owned by ue-scale). |
| `godot/scripts/pct_town_life.gd` | 460 | **NO** | `N/A` (World actor manager) | Node3D | M | World spawning: Store keeper NPC walking, shuttle van timetable, bed slots. |
| `godot/scripts/pct_town_lights.gd` | 388 | **NO** | `N/A` (Distant light renderer) | Node3D | M | Rendering: Distant town night lights billboard rendering. |
| `godot/scripts/pct_town_windows.gd` | 469 | **NO** | `N/A` (Lit window renderer) | Node3D | M | Rendering: Distant lit window quad rendering for settlements after dark. |
| `godot/scripts/pct_trail_hikers.gd` | 851 | **NO** | `N/A` (Crowd renderer) | Node3D | L | Rendering: Distant hiker actor spawning and LOD billboard rendering. |
| `godot/scripts/trail_register.gd` | 640 | **YES** | `thru::TrailRegister`<br>`UThruTrailRegisterSubsystem` | `thru::TrailheadTraffic`, `thru::DataSource` | M | Trailhead registration logbooks, signatures, and page reads/writes. |
| `godot/scripts/trail_journal.gd` | 197 | **YES** | `thru::TrailJournal`<br>`UThruTrailJournalComponent` | `thru::TrailCalendar`, `thru::TrailSeason`, `thru::DataSource` | S | Daily hiker journal entries, trail day summaries, and closed day records. |
| `godot/scripts/world_event_journal.gd` | 211 | **YES** | `thru::WorldEventJournal`<br>`UThruEventJournalSubsystem` | `thru::DataSource` | S | Append-only ledger of expedition events, promises, cache claims, and traces. |
| `godot/scripts/encounter_library.gd` | 230 | **YES** | `thru::EncounterLibrary`<br>`UThruEncounterLibrarySubsystem` | `thru::Rng`, `thru::DataSource` | S | Encounter catalog loading, schema validation, and randomized selection. |
| `godot/scripts/geo_promises.gd` | 985 | **YES** | `thru::GeoPromises`<br>`UThruGeoPromisesComponent` | `thru::WorldEventJournal`, `thru::DataSource` | L | Dinner promises contract state machine, lunch cache claims, and multiplayer sync. |
| `godot/scripts/social_graph.gd` | 209 | **YES** | `thru::SocialGraph`<br>`UThruSocialGraphComponent` | `thru::WorldEventJournal`, `thru::DataSource` | S | Directed NPC memory graph ("observer remembers actor", reputation ledger). |
| `godot/scripts/salt_thieves.gd` | 243 | **YES** | `thru::SaltThieves`<br>`UThruSaltThievesComponent` | `thru::TrailCalendar`, `thru::Rng`, `thru::DataSource` | S | Animal salt-chew damage simulation on unattended salty gear in camp. |
| `godot/scripts/trail_trouble.gd` | 213 | **YES** | `thru::TrailTrouble`<br>`UThruTrailTroubleComponent` | `thru::Rng`, `thru::DataSource` | S | 30-second party voting dilemma social interactions on the trail. |
| `godot/scripts/campaign_content.gd` | 250 | **YES** | `thru::CampaignContent`<br>`UThruCampaignContentSubsystem` | `thru::DataSource` | S | Campaign narrative progression, leg parameters, favor pricing, and outcomes. |
| `godot/scripts/journey_content.gd` | 47 | **YES** | `thru::JourneyContent`<br>`UThruJourneyContentSubsystem` | None | S | Journey progression stages, ridge offers, and hitch stories. |
| `godot/scripts/trail_content.gd` | 80 | **YES** | `thru::TrailContent`<br>`UThruTrailContentSubsystem` | None | S | Trail narrative milestones, delivery objectives, and camp responses. |
| `godot/scripts/pct_checkpoints.gd` | 946 | **YES** | `thru::PctCheckpoints`<br>`UThruCheckpointsSubsystem` | `thru::PctBoxChain`, `thru::DataSource` | L | Host checkpoint milestone validation, resupply, and spending ledger. |
| `godot/scripts/pct_blaze_ledger.gd` | 161 | **YES** | `thru::PctBlazeLedger`<br>`UThruBlazeLedgerComponent` | None | S | Trail blaze traversal tracking, segment coverage, and interval verification. |
| `godot/scripts/campaign_encounters.gd` | 1146 | **NO** | `N/A` (Encounter actor manager) | Node3D | L | Encounter minigame 3D spawning and visual placement (logic in `thru::EncounterLibrary`). |
| `godot/scripts/encounter_person.gd` | 220 | **NO** | `N/A` (NPC character actor) | Node3D | M | Cosmetic 3D NPC wardrobe, mesh rendering, and animation playback. |
| `godot/scripts/geo_encounter_host.gd` | 631 | **NO** | `N/A` (Encounter host actor) | Node3D | L | Geographic 3D encounter scene host (logic delegates to `thru::GeoPromises`). |
| `godot/scripts/campaign_map.gd` | 178 | **NO** | `N/A` (UMG Slate Widget) | Control | S | UI: 2D UI route and map drawing control. |
| `godot/scripts/campaign_parcels.gd` | 194 | **NO** | `N/A` (Item actor) | Node3D | S | 3D physical parcel mesh spawning/handling (logic in `thru::PctBoxChain`). |
| `godot/scripts/campaign_world.gd` | 2788 | **NO** | `N/A` (ue-scale terrain) | Node3D | XL | Authored 3D terrain mesh builder (owned by ue-scale streaming lane). |
| `godot/scripts/journey_world.gd` | 223 | **NO** | `N/A` (ue-scale scenery) | Node3D | M | 3D scenery and traversal mesh builder. |
| `godot/scripts/pct_burney_understory.gd` | 201 | **NO** | `N/A` (Foliage spawner) | RefCounted | M | Procedural vegetation understory placement. |
| `godot/scripts/pct_guidebook.gd` | 274 | **NO** | `N/A` (UMG / 3D Book UI) | Node3D | M | 3D paper tools / guidebook book UI presentation. |
| `godot/scripts/regional_encounters.gd` | 381 | **NO** | `N/A` (Regional manager) | Node3D | M | Regional 3D encounter session manager node. |
| `godot/scripts/minigames/footprints.gd` | 242 | **NO** | `thru::FootprintsMinigame` | Minigame | M | Proximity spatial puzzle minigame logic and node tracking. |
| `godot/scripts/minigames/photo_frame.gd` | 202 | **YES** | `thru::PhotoFrameLogic`<br>`UThruPhotoFrameComponent` | None | S | Photo framing angle diversity scoring and composition evaluator. |
| `godot/scripts/pct_film_camera.gd` | 587 | **YES** | `thru::FilmCamera`<br>`UThruFilmCameraComponent` | `thru::TrailCalendar`, `thru::TownHours`, `thru::DataSource` | L | 35mm film roll state, exposures, lab mailing, delivery, and photo album logic. |
| `godot/scripts/photo_mode.gd` | 398 | **NO** | `N/A` (UE Camera Rig) | Node | M | Camera controller: Free-flying viewport camera and input handler. |
| `godot/scripts/trail_camera.gd` | 144 | **NO** | `N/A` (UE PlayerCameraManager) | Node | S | Camera controller: Player camera follow, bob, and terrain pitch stabilisation. |
| `godot/tools/alive/capture.gd` | 309 | **NO** | `N/A` (Editor tool) | SceneTree | M | Benchmark screenshot capture tool. |
| `godot/tools/placement/metrics_capture.gd` | 303 | **NO** | `N/A` (Editor tool) | RefCounted | M | Metric comparator tool. |
| `godot/tools/terrain_materials/capture.gd` | 97 | **NO** | `N/A` (Editor tool) | SceneTree | S | Material capture tool. |
| `godot/tools/terrain_materials/production_capture.gd` | 222 | **NO** | `N/A` (Editor tool) | SceneTree | M | Terrain material production validation tool. |
| `godot/tools/season/laguna_weather.gd` | 21 | **NO** | `N/A` (Editor tool) | RefCounted | S | Offline weather verification test walk script. |
| `tools/check_slice_landfire_gaps.gd` | 86 | **NO** | `N/A` (Editor tool) | SceneTree | S | Offline Landfire data validation script. |
| `godot/scenes/wildlife/campaign_preview.gd` | 65 | **NO** | `N/A` (Editor scene) | Node3D | S | Wildlife editor preview scene. |

---

## 3. Detailed File Breakdowns (In-Scope Systems)

### Module 1: `core_calendar`
#### `godot/scripts/trail_calendar.gd` (128 lines)
- **Purpose**: Computes civil calendar dates, Daylight Saving Time (1980–1999 rules), solar daylight, sunrise/sunset, civil twilight, and astronomical twilight from a continuous Julian Day number.
- **Key State**: Pure deterministic static math functions. No mutable state.
- **Public Functions**:
  - `utc_offset_hours(julian_day: float) -> float`
  - `civil(julian_day: float) -> Dictionary` (year, month, day, hour, minute, second, weekday)
  - `label(julian_day: float) -> String` ("12 May 1998")
  - `clock_label(julian_day: float) -> String` ("14:32")
  - `daylight(julian_day: float, latitude: float, longitude: float) -> Dictionary` (sunrise, sunset, duration)
  - `astronomical_twilight(julian_day: float, latitude: float, longitude: float) -> Dictionary`
- **Dependencies**: No external files. Pure astronomical mathematics.
- **Logic vs Rendering**: Pure logic.
- **Unreal Mapping**: `thru::TrailCalendar` + `UThruTrailCalendarLibrary` (`UBlueprintFunctionLibrary`).

---

### Module 2: `celestial_sim`
#### `godot/scripts/celestial_math.gd` (113 lines)
- **Purpose**: Low-level astronomical math transformations: right ascension/declination to equatorial vectors, equatorial to topocentric horizontal coordinates (azimuth/altitude), J2000 precession, and apparent sidereal time.
- **Key State**: Pure static functions. Constants for Earth flattening, J2000 epoch.
- **Public Functions**:
  - `equatorial_vector(ra_degrees: float, dec_degrees: float) -> Vector3`
  - `horizontal_direction(equatorial: Vector3, julian_day: float, lat: float, lon: float) -> Vector3`
  - `j2000_horizontal_basis(julian_day: float, lat: float, lon: float) -> Basis`
  - `apparent_sidereal_degrees(julian_day: float) -> float`
- **Dependencies**: None.
- **Logic vs Rendering**: Pure math logic.
- **Unreal Mapping**: `thru::CelestialMath` + `UThruCelestialMathLibrary`.

#### `godot/scripts/celestial_ephemeris.gd` (98 lines)
- **Purpose**: Loads and samples tabular solar and lunar positions interpolated from NASA/JPL ephemeris data.
- **Key State**: `_jds` (array of Julian days), `_sun`, `_moon` coordinates and distances.
- **Public Functions**:
  - `load_default() -> bool`
  - `sample(body: String, julian_day: float) -> Dictionary` (direction, distance AU, phase angle)
  - `is_valid() -> bool`
- **Dependencies**: `thru::DataSource` (reads `data/celestial/ephemeris_1998.json`).
- **Logic vs Rendering**: Pure data interpolation logic.
- **Unreal Mapping**: `thru::CelestialEphemeris` + `UThruCelestialEphemeris` (`UObject`).

---

### Module 3: `trail_season_environment`
#### `godot/scripts/trail_season.gd` (625 lines)
- **Purpose**: Historical climate and travel conditions per PCT route leg. Provides leg bounds, nearest leg lookup, seasonal water availability, snow travel difficulty multipliers, and Washington early-snow deadlines.
- **Key State**: Pre-parsed leg definitions and historical climate records for 1980–1999.
- **Public Functions**:
  - `leg_count() -> int`
  - `leg_info(leg: int) -> Dictionary`
  - `nearest_leg(latitude: float) -> int`
  - `water_on(leg: int, year_id: String, month: int, day: int) -> float`
  - `walk_multiplier(leg: int, year_id: String, month: int, day: int) -> float`
- **Dependencies**: `thru::TrailCalendar`, `thru::DataSource` (`data/season/season_data.json`, `data/season/washington.json`).
- **Logic vs Rendering**: Pure data-driven logic.
- **Unreal Mapping**: `thru::TrailSeason` + `UThruTrailSeasonSubsystem` (`UWorldSubsystem`).

#### `godot/scripts/trail_year.gd` (508 lines)
- **Purpose**: High-resolution snowpack model. Tracks snow water equivalent (SWE in meters) for every 0.5-mile bin of the trail per calendar day (Day 0 = March 1).
- **Key State**: Year selector, seed, 5,300 route bins, daily SWE arrays.
- **Public Functions**:
  - `bind_year(year_id: String) -> void`
  - `season_swe_at(lat: float, lon: float, elevation_m: float, trail_day: int) -> float`
  - `swe_at_bin(bin_index: int, trail_day: int) -> float`
- **Dependencies**: `thru::TrailCalendar`, `thru::DataSource` (`data/season/snow/`).
- **Logic vs Rendering**: Pure simulation data logic.
- **Unreal Mapping**: `thru::TrailYear` + `UThruTrailYearSubsystem`.

#### `godot/scripts/intermittent_water.gd` (125 lines)
- **Purpose**: Models seasonal flow regimes (perennial, early-dry, summer-dry, wet-year-only) for intermittent water sources.
- **Key State**: Regime flow window definitions.
- **Public Functions**:
  - `flow_window(regime: String) -> Dictionary`
  - `flows_on(month: int, day: int, regime: String) -> bool`
  - `flows_for(season: Dictionary) -> bool`
- **Dependencies**: `thru::TrailCalendar`, `thru::DataSource` (`data/water/intermittent.json`).
- **Logic vs Rendering**: Pure logic.
- **Unreal Mapping**: `thru::IntermittentWater` + `UThruIntermittentWaterSubsystem`.

#### `godot/scripts/ford_crossings.gd` (391 lines)
- **Purpose**: Computes creek depth and flow speed at dangerous trail fords (e.g. Evolution Creek, Bear Creek) based on April 1 snowpack ratio and diurnal snowmelt cycle.
- **Key State**: Ford catalog, crossing geometry, ordinary-year baselines.
- **Public Functions**:
  - `fords(leg: int = -1) -> Array<Dictionary>`
  - `ford(ford_id: String) -> Dictionary`
  - `evaluate_flow(ford_id: String, julian_day: float, pack_ratio: float) -> Dictionary` (depth_m, speed_mps, hazard_class)
- **Dependencies**: `thru::TrailCalendar`, `thru::DataSource` (`data/water/ford_flow.json`).
- **Logic vs Rendering**: Pure hydrological simulation logic.
- **Unreal Mapping**: `thru::FordCrossings` + `UThruFordCrossingsSubsystem`.

---

### Module 4: `weather_sim`
#### `godot/scripts/weather_front.gd` (268 lines)
- **Purpose**: Simulates synoptic weather fronts advancing across the geographic trail. Calculates weather condition interpolation (clear, overcast, rain, snow, storm) across boundary blocks.
- **Key State**: Outgoing/incoming weather blocks, speed (km/h), bearing, boundary offset.
- **Public Functions**:
  - `advance(elapsed: float, seed: int, region: int) -> void`
  - `blend_at(point: Vector3) -> Dictionary` (rain_amount, snow_amount, fog_density, wind_vector)
  - `gap_at(point: Vector3) -> float`
- **Dependencies**: `thru::TrailCalendar`, `thru::Rng`.
- **Logic vs Rendering**: Spatial front simulation logic is decoupled from `render()` (which is visual only).
- **Unreal Mapping**: `thru::WeatherFront` + `UThruWeatherFrontSubsystem`.

#### `godot/scripts/thunder_delay.gd` (195 lines)
- **Purpose**: Physics of lightning and thunder: calculates acoustic arrival delay based on speed of sound (343 m/s) and decibel attenuation.
- **Key State**: Speed of sound constants, distance attenuation tables.
- **Public Functions**:
  - `delay_seconds(distance_m: float) -> float`
  - `level_at(distance_m: float) -> float`
- **Dependencies**: `thru::DataSource` (`data/weather/thunder.json`).
- **Logic vs Rendering**: Pure acoustic physics logic.
- **Unreal Mapping**: `thru::ThunderDelay` + `UThruThunderDelayComponent`.

#### `godot/scripts/wind_diurnal.gd` (196 lines)
- **Purpose**: Models diurnal mountain wind patterns, scaling base synoptic winds by daylight fraction to simulate afternoon thermal gusts.
- **Key State**: Diurnal response curve coefficients.
- **Public Functions**:
  - `diurnal_level(julian_day: float, daylight: Dictionary) -> float`
  - `diurnal_level_at(julian_day: float, lat: float, lon: float) -> float`
- **Dependencies**: `thru::TrailCalendar`, `thru::DataSource` (`data/weather/wind.json`).
- **Logic vs Rendering**: Pure mathematical model.
- **Unreal Mapping**: `thru::WindDiurnal` + `UThruWindDiurnalComponent`.

#### `godot/scripts/cold_air_pool.gd` (233 lines)
- **Purpose**: Calculates nocturnal cold air pooling in mountain basins and valley floors when wind is calm (<2.5 m/s).
- **Key State**: Pool elevation thresholds, temperature deficit curves.
- **Public Functions**:
  - `deficit_c(elevation_m: float, floor_m: float, wind_mps: float, julian_day: float) -> float`
  - `calm_wind_max() -> float`
- **Dependencies**: `thru::TrailCalendar`, `thru::DataSource` (`data/weather/cold_pool.json`).
- **Logic vs Rendering**: Pure atmospheric thermodynamic model.
- **Unreal Mapping**: `thru::ColdAirPool` + `UThruColdAirPoolComponent`.

---

### Module 5: `wildfire_smoke`
#### `godot/scripts/fire_risk.gd` (130 lines)
- **Purpose**: Calculates fine fuel moisture cure percentage, Fosberg fire weather index, and USFS fire danger ratings (Low to Extreme).
- **Key State**: Moisture tables, risk thresholds.
- **Public Functions**:
  - `cure(year_id: String, site_leg: int, day: int) -> float`
  - `index(cure_value: float, high_c: float, gust: float, wetness: float) -> float`
  - `danger_class(value: float) -> String`
- **Dependencies**: `thru::DataSource` (`data/season/fire_risk.json`).
- **Logic vs Rendering**: Pure environmental calculation.
- **Unreal Mapping**: `thru::FireRisk` + `UThruFireRiskComponent`.

#### `godot/scripts/fire_season.gd` (210 lines)
- **Purpose**: Historical MTBS (Monitoring Trends in Burn Severity) fire perimeters. Tracks active burn spans and determines if a trail section is closed or impacted by active fire.
- **Key State**: Array of historic fire polygons, ignition days, duration formulas.
- **Public Functions**:
  - `fires() -> Array<Dictionary>`
  - `active_days(fire: Dictionary) -> int`
  - `is_fire_active(fire_id: String, day_of_year: int) -> bool`
- **Dependencies**: `thru::DataSource` (`data/season/burns.json`).
- **Logic vs Rendering**: Pure GIS/temporal query logic.
- **Unreal Mapping**: `thru::FireSeason` + `UThruFireSeasonSubsystem`.

#### `godot/scripts/smoke_season.gd` (395 lines)
- **Purpose**: Simulates regional wildfire smoke drift, PM2.5 particulate loading, and atmospheric visibility reduction per trail mile.
- **Key State**: Smoke dispersion kernels, regional air quality indices.
- **Public Functions**:
  - `in_season(month: int, day: int) -> bool`
  - `smoke_level(mile: float, day_of_year: int) -> float`
  - `air_quality_descriptor(level: float) -> String`
- **Dependencies**: `thru::TrailCalendar`, `thru::DataSource` (`data/season/smoke.json`).
- **Logic vs Rendering**: Pure simulation model.
- **Unreal Mapping**: `thru::SmokeSeason` + `UThruSmokeSeasonSubsystem`.

---

### Module 6: `trail_phenology_ecology`
#### `godot/scripts/mosquito_season.gd` (354 lines)
- **Purpose**: Computes mosquito biting activity based on days elapsed since local snowmelt and ambient temperature.
- **Key State**: Melt trigger dates, biting pressure curves per elevation.
- **Public Functions**:
  - `pressure(mile: float, trail_day: int, swe_m: float, temp_c: float) -> float`
  - `activity_label(pressure: float) -> String`
- **Dependencies**: `thru::TrailYear`, `thru::DataSource` (`data/ecology/mosquitoes.json`).
- **Logic vs Rendering**: Pure ecological formula.
- **Unreal Mapping**: `thru::MosquitoSeason` + `UThruMosquitoSeasonSubsystem`.

#### `godot/scripts/wildflower_bloom.gd` (184 lines)
- **Purpose**: Phenological model of desert and alpine wildflower blooms (poppies, lupine, paintbrush) following winter moisture and warming temperatures.
- **Key State**: Species bloom windows and color signatures.
- **Public Functions**:
  - `bloom_of(season: Dictionary) -> float`
  - `dresses(season: Dictionary) -> Dictionary`
- **Dependencies**: `thru::TrailCalendar`, `thru::DataSource` (`data/ecology/bloom.json`).
- **Logic vs Rendering**: Pure phenological data model.
- **Unreal Mapping**: `thru::WildflowerBloom` + `UThruWildflowerBloomComponent`.

#### `godot/scripts/fall_colour.gd` (130 lines)
- **Purpose**: Models autumn foliage color changes (aspen, oak, larch) across northern California, Oregon, and Washington based on calendar day and elevation.
- **Key State**: Species coloration progress curves.
- **Public Functions**:
  - `turn_color(species: String, region: int, day: int) -> Dictionary`
  - `strength(species: String, region: int, day: int) -> float`
- **Dependencies**: `thru::TrailCalendar`, `thru::DataSource` (`data/ecology/fall_colour.json`).
- **Logic vs Rendering**: Pure state calculation.
- **Unreal Mapping**: `thru::FallColour` + `UThruFallColourComponent`.

#### `godot/scripts/poodle_dog_bush.gd` (387 lines)
- **Purpose**: Models post-fire chaparral poodle-dog bush (*Eriodictyon parryi*) density in recent burn scars and computes contact dermatitis exposure risk when hiking off-trail.
- **Key State**: Burn scar chaparral weighting, rash severity states.
- **Public Functions**:
  - `chaparral_weight(leg_id: String) -> float`
  - `contact_check(mile: float, off_tread_m: float, rng: Rng) -> Dictionary`
- **Dependencies**: `thru::TrailCalendar`, `thru::DataSource` (`data/ecology/poodle_dog.json`).
- **Logic vs Rendering**: Pure gameplay hazard logic.
- **Unreal Mapping**: `thru::PoodleDogBush` + `UThruPoodleDogBushComponent`.

---

### Module 7: `hiker_metabolism`
#### `godot/scripts/hiker_hunger.gd` (175 lines)
- **Purpose**: Simulates through-hiker metabolic energy expenditure. Base burn rate escalates over the season into true "hiker hunger" (needing 5,000+ kcal/day).
- **Key State**: Caloric consumption per mile, appetite onset curve, deficit counter.
- **Public Functions**:
  - `hunger_per_mile(campaign_day: int) -> float`
  - `daily_calorie_target(campaign_day: int, miles_walked: float) -> float`
- **Dependencies**: `thru::DataSource` (`data/season/hiker_hunger.json`).
- **Logic vs Rendering**: Pure physiological logic.
- **Unreal Mapping**: `thru::HikerHunger` + `UThruHikerHungerComponent`.

#### `godot/scripts/water_carry_data.gd` (78 lines)
- **Purpose**: Structured database of all drinkable water sources along the PCT (springs, piped sources, creeks, rivers, cisterns, caches).
- **Key State**: Source catalog keyed by trail mile and leg ID.
- **Public Functions**:
  - `sources() -> Array<Dictionary>`
  - `source(id: String) -> Dictionary`
- **Dependencies**: `thru::DataSource` (`data/water/water_sources.json`).
- **Logic vs Rendering**: Pure data table loader.
- **Unreal Mapping**: `thru::WaterCarryData` + `UThruWaterCarryDatabase` (`UDataAsset`).

#### `godot/scripts/water_carry.gd` (110 lines)
- **Purpose**: Calculates look-ahead water logistics for a hiker at mile $M$ on date $D$. Skips intermittent sources that are dry on that date.
- **Key State**: Cached water features.
- **Public Functions**:
  - `next_reliable_water(mile: float, julian_day: float) -> Dictionary`
  - `carry_miles(mile: float, julian_day: float) -> float`
  - `summary(mile: float, julian_day: float) -> Dictionary`
- **Dependencies**: `thru::WaterCarryData`, `thru::IntermittentWater`.
- **Logic vs Rendering**: Pure algorithmic route lookup.
- **Unreal Mapping**: `thru::WaterCarry` + `UThruWaterCarryComponent`.

#### `godot/scripts/water_caches.gd` (155 lines)
- **Purpose**: Volunteer water caches (e.g. Third Gate, Scissors Crossing). Models volunteer refill intervals, hiker drain rates, and empty cache risks.
- **Key State**: Cache capacities, refill intervals, depletion state.
- **Public Functions**:
  - `caches() -> Array<Dictionary>`
  - `gallons_available(cache_id: String, day_of_year: int, rng: Rng) -> float`
- **Dependencies**: `thru::DataSource` (`data/water/water_caches.json`), `thru::Rng`.
- **Logic vs Rendering**: Pure logistics simulation.
- **Unreal Mapping**: `thru::WaterCaches` + `UThruWaterCachesSubsystem`.

---

### Module 8: `hiker_rhythm_fatigue`
#### `godot/scripts/hiker_rhythm.gd` (380 lines)
- **Purpose**: Pacing of long-distance hiking: models rest days (zeros) and partial rest days (neros) based on cumulative fatigue, trail legs, and weather.
- **Key State**: Fatigue accumulator, consecutive walking days, rest day decisions.
- **Public Functions**:
  - `zero_chance(consecutive_days: int, fatigue: float) -> float`
  - `evaluate_rest_decision(hiker_state: Dictionary, rng: Rng) -> String`
- **Dependencies**: `thru::TrailCalendar`, `thru::Rng`, `thru::DataSource` (`data/season/hiker_rhythm.json`).
- **Logic vs Rendering**: Pure behavioral logic.
- **Unreal Mapping**: `thru::HikerRhythm` + `UThruHikerRhythmComponent`.

#### `godot/scripts/hiker_midnight.gd` (278 lines)
- **Purpose**: Camp etiquette and nocturnal social dynamics. At "hiker midnight" (9:00 PM), hikers must sleep. Talking, playing audio, or shining headlamps into tents damages social standing.
- **Key State**: Hiker midnight hour (21:00), standing loss values, complaint lines.
- **Public Functions**:
  - `is_hiker_midnight(hour: float) -> bool`
  - `evaluate_disturbance(action_kind: String, distance_m: float) -> Dictionary`
- **Dependencies**: `thru::TrailCalendar`, `thru::DataSource` (`data/camp_routine.json`).
- **Logic vs Rendering**: Pure social rule logic.
- **Unreal Mapping**: `thru::HikerMidnight` + `UThruHikerMidnightComponent`.

#### `godot/scripts/norovirus_outbreak.gd` (553 lines)
- **Purpose**: Simulates norovirus epidemics in the hiker bubble. Transmitted via shared water jugs, trail registers, and hostel bunk rooms. Enforces 24–72 hour incapacitation and dehydration penalties.
- **Key State**: Active outbreak clusters, contaminated containers, infected hiker roster.
- **Public Functions**:
  - `touch_container(container_id: String, hiker_id: String, day: int, rng: Rng) -> bool`
  - `sick_day_penalty(infection_day: int, current_day: int) -> Dictionary`
- **Dependencies**: `thru::TrailBubble`, `thru::Rng`, `thru::DataSource` (`data/season/norovirus.json`).
- **Logic vs Rendering**: Pure epidemiological simulation logic.
- **Unreal Mapping**: `thru::NorovirusOutbreak` + `UThruNorovirusSubsystem`.

---

### Module 9: `hiker_cohort_bubble`
#### `godot/scripts/trail_bubble.gd` (203 lines)
- **Purpose**: Mathematical distribution of the through-hiker bubble moving north from Campo to Canada. Determines hiker density per mile on any date.
- **Key State**: Crest departure day, Gaussian spread, dropout decay curve.
- **Public Functions**:
  - `hikers_per_mile(mile: float, julian_day: float) -> float`
  - `track_day(julian_day: float) -> int`
- **Dependencies**: `thru::TrailCalendar`, `thru::DataSource` (`data/season/bubble.json`).
- **Logic vs Rendering**: Pure mathematical distribution.
- **Unreal Mapping**: `thru::TrailBubble` + `UThruTrailBubbleSubsystem`.

#### `godot/scripts/trail_cohort.gd` (430 lines)
- **Purpose**: Deterministically derives individual named virtual hikers from the statistical bubble without storing massive save states.
- **Key State**: Roster seed, trail names generator, pace variations.
- **Public Functions**:
  - `roster_size() -> int`
  - `member(index: int) -> Dictionary` (trail_name, start_day, pace, exit_mile)
  - `near(mile: float, day: int, radius_miles: float) -> Array<Dictionary>`
- **Dependencies**: `thru::TrailBubble`, `thru::Rng`, `thru::DataSource` (`data/season/roster.json`).
- **Logic vs Rendering**: Pure procedural generation logic.
- **Unreal Mapping**: `thru::TrailCohort` + `UThruTrailCohortSubsystem`.

#### `godot/scripts/hiker_cohort.gd` (808 lines)
- **Purpose**: Simulates the daily wear and tear of the trail on named cohort members: gear failure, blister injuries, caloric depletion, zero days, and trail dropout (bailout) risk.
- **Key State**: Agent health, gear wear, morale, injury status.
- **Public Functions**:
  - `simulate_day(member_idx: int, day: int, weather: Dictionary, rng: Rng) -> Dictionary`
  - `active_hikers_at_mile(mile: float, day: int) -> Array<Dictionary>`
- **Dependencies**: `thru::TrailCohort`, `thru::Rng`, `thru::DataSource`.
- **Logic vs Rendering**: Pure agent simulation logic.
- **Unreal Mapping**: `thru::HikerCohort` + `UThruHikerCohortSubsystem`.

#### `godot/scripts/trail_permits.gd` (193 lines)
- **Purpose**: PCT long-distance permit quota system. Limits northbound starts south of Sonora Pass to 50 permits/day between March 1 and May 31.
- **Key State**: Quota limits, permit issue windows.
- **Public Functions**:
  - `permit_ok(julian_day: float, direction: String) -> bool`
  - `daily_quota(julian_day: float) -> int`
- **Dependencies**: `thru::TrailCalendar`, `thru::DataSource` (`data/season/permits.json`).
- **Logic vs Rendering**: Pure game rules.
- **Unreal Mapping**: `thru::TrailPermits` + `UThruTrailPermitsComponent`.

#### `godot/scripts/trail_resources.gd` (160 lines)
- **Purpose**: Simulates through-hiker consumption of caches, trail magic, and trail resources by the passing cohort.
- **Key State**: Cache capacity, consumption rate per passing hiker.
- **Public Functions**:
  - `lunch_cache_stock(mile: float, day: int) -> int`
  - `cache_capacity(cache_id: String) -> int`
- **Dependencies**: `thru::TrailCohort`, `thru::DataSource`.
- **Logic vs Rendering**: Pure deterministic resource model.
- **Unreal Mapping**: `thru::TrailResources` + `UThruTrailResourcesSubsystem`.

---

### Module 10: `town_hours_schedule`
#### `godot/scripts/town_hours.gd` (335 lines)
- **Purpose**: Resupply stop operating hours database. Evaluates whether stores, post offices, and hostels are open at an exact Julian day and civil time.
- **Key State**: Stop database, weekly opening hours, holiday closures.
- **Public Functions**:
  - `is_open(stop_id: String, service: String, julian_day: float) -> bool`
  - `next_open(stop_id: String, service: String, julian_day: float) -> float`
  - `stops() -> Array<Dictionary>`
- **Dependencies**: `thru::TrailCalendar`, `thru::DataSource` (`data/towns/hours.json`, `data/towns/resupply_stops.json`).
- **Logic vs Rendering**: Pure temporal business logic.
- **Unreal Mapping**: `thru::TownHours` + `UThruTownHoursSubsystem`.

#### `godot/scripts/town_schedule.gd` (349 lines)
- **Purpose**: Town life temporal state: evaluates what each town facility and service is doing at any instant (e.g. delivery trucks, clerk present, mail window open).
- **Key State**: Facility activity schedules, host bindings.
- **Public Functions**:
  - `binding_for_host(host: String) -> Dictionary`
  - `instant(elapsed: float, longitude: float) -> Dictionary`
- **Dependencies**: `thru::TownHours`, `thru::DataSource` (`data/towns/schedules.json`).
- **Logic vs Rendering**: Pure scheduling logic.
- **Unreal Mapping**: `thru::TownSchedule` + `UThruTownScheduleSubsystem`.

#### `godot/scripts/trailhead_traffic.gd` (229 lines)
- **Purpose**: Models day-use vehicle counts and day hiker crowds at road crossings, higher on summer weekends.
- **Key State**: Roadside traffic curves, parking capacities.
- **Public Functions**:
  - `traffic_level(trailhead_id: String, julian_day: float) -> float`
  - `parked_cars(trailhead_id: String, julian_day: float) -> int`
- **Dependencies**: `thru::TrailCalendar`, `thru::DataSource` (`data/towns/trailhead_traffic.json`).
- **Logic vs Rendering**: Pure traffic density logic.
- **Unreal Mapping**: `thru::TrailheadTraffic` + `UThruTrailheadTrafficSubsystem`.

---

### Module 11: `town_resupply_logistics`
#### `godot/scripts/hiker_box.gd` (225 lines)
- **Purpose**: Manages hiker box contents at trail stops. Generates discarded items (gas canisters, ramen, instant potatoes, blister tape) based on cohort bubble passage.
- **Key State**: Items list per town box, take/leave operations.
- **Public Functions**:
  - `keeps_box(town_id: String) -> bool`
  - `get_contents(town_id: String, day: int, rng: Rng) -> Array<Dictionary>`
  - `take_item(town_id: String, item_idx: int) -> Dictionary`
  - `deposit_item(town_id: String, item: Dictionary) -> void`
- **Dependencies**: `thru::TownHours`, `thru::Rng`, `thru::DataSource` (`data/towns/hiker_boxes.json`).
- **Logic vs Rendering**: Pure inventory / loot logic.
- **Unreal Mapping**: `thru::HikerBox` + `UThruHikerBoxComponent`.

#### `godot/scripts/resupply_plan.gd` (157 lines)
- **Purpose**: Projects upcoming resupply stops ahead of a hiker based on trail mile, walking pace, and weather slowdowns.
- **Key State**: Projection algorithm, stop sequence.
- **Public Functions**:
  - `plan_ahead(mile: float, julian_day: float, pace: float, season_year: String) -> Array<Dictionary>`
  - `summary(mile: float, julian_day: float) -> Dictionary`
- **Dependencies**: `thru::TownHours`, `thru::TrailSeason`.
- **Logic vs Rendering**: Pure route planning logic.
- **Unreal Mapping**: `thru::ResupplyPlan` + `UThruResupplyPlanSubsystem`.

#### `godot/scripts/pct_box_chain.gd` (149 lines)
- **Purpose**: Mail-drop logistics: sends resupply packages ahead via General Delivery to post offices along the trail; checks post office open hours before pickup.
- **Key State**: Mailed parcels, tracked hops, arrival dates.
- **Public Functions**:
  - `counter_open(key: String, julian_day: float) -> bool`
  - `pickup_box(key: String, hiker_id: int) -> Dictionary`
- **Dependencies**: `thru::TownHours`, `thru::DataSource`.
- **Logic vs Rendering**: Pure postal logistics logic.
- **Unreal Mapping**: `thru::PctBoxChain` + `UThruBoxChainSubsystem`.

#### `godot/scripts/kennedy_applause.gd` (168 lines)
- **Purpose**: Detects hiker arrival at Kennedy Meadows South (mile 702), the gateway to the High Sierra, triggering the traditional porch applause once per season.
- **Key State**: Arrival triggered flag, arrival margin miles.
- **Public Functions**:
  - `check_arrival(mile: float) -> bool`
  - `trigger_welcome() -> Dictionary`
- **Dependencies**: `thru::DataSource` (`data/towns/kennedy_applause.json`).
- **Logic vs Rendering**: Pure milestone event trigger.
- **Unreal Mapping**: `thru::KennedyApplause` + `UThruKennedyApplauseComponent`.

---

### Module 12: `town_commerce_services`
#### `godot/scripts/snack_vending_site.gd` (13 lines)
- **Purpose**: Manages coin/cash transactions for vending machines and small snack counters at road crossings.
- **Key State**: Item prices, stock.
- **Public Functions**:
  - `can_afford(cost_cents: int, player_cash_cents: int) -> bool`
  - `vend_item(item_id: String, player_cash_cents: int) -> Dictionary`
- **Dependencies**: None.
- **Logic vs Rendering**: Pure transaction logic.
- **Unreal Mapping**: `thru::SnackVending` + `UThruSnackVendingComponent`.

#### `godot/scripts/hitch_wait.gd` (235 lines)
- **Purpose**: Calculates wait time (in minutes) when hitchhiking from a trail road crossing into an off-trail resupply town based on road class and hourly traffic.
- **Key State**: Road classes, hitch wait curves, seeded wait roll.
- **Public Functions**:
  - `hitch_point(id: String) -> Dictionary`
  - `roll_wait_minutes(hitch_id: String, julian_day: float, rng: Rng) -> float`
- **Dependencies**: `thru::TrailheadTraffic`, `thru::Rng`, `thru::DataSource` (`data/towns/hitch_wait.json`).
- **Logic vs Rendering**: Pure wait-time math and probability.
- **Unreal Mapping**: `thru::HitchWait` + `UThruHitchWaitComponent`.

#### `godot/scripts/town_bed.gd` (185 lines)
- **Purpose**: Lodging availability and town acoustic environment evaluation (generator hum, distant highway, quiet hours).
- **Key State**: Bed capacity, occupancy states, sound cue time windows.
- **Public Functions**:
  - `is_bunk_available(town_id: String, day: int) -> bool`
  - `active_cues(town_id: String, julian_day: float) -> Array<String>`
- **Dependencies**: `thru::TrailCalendar`, `thru::DataSource` (`data/towns/town_bed.json`).
- **Logic vs Rendering**: Pure state query.
- **Unreal Mapping**: `thru::TownBed` + `UThruTownBedComponent`.

---

### Module 13: `trail_registers_journal`
#### `godot/scripts/trail_register.gd` (640 lines)
- **Purpose**: Trailhead registration logbooks. Hikers record date, trail name, direction, and note. Reads historical signatures of virtual cohort members.
- **Key State**: Register boxes, signature logbook pages.
- **Public Functions**:
  - `sign_register(box_id: String, entry: Dictionary) -> bool`
  - `read_entries(box_id: String, page: int) -> Array<Dictionary>`
- **Dependencies**: `thru::TrailheadTraffic`, `thru::DataSource` (`data/towns/trail_registers.json`).
- **Logic vs Rendering**: Core data logic decoupled from physical 3D box model.
- **Unreal Mapping**: `thru::TrailRegister` + `UThruTrailRegisterSubsystem`.

#### `godot/scripts/trail_journal.gd` (197 lines)
- **Purpose**: Player's daily personal hiking journal. Summarizes each closed campaign day: date, miles walked, weather headline, and camp location.
- **Key State**: Journal entries list, formatting rules.
- **Public Functions**:
  - `close_day_entry(day_summary: Dictionary) -> void`
  - `entries() -> Array<Dictionary>`
- **Dependencies**: `thru::TrailCalendar`, `thru::TrailSeason`, `thru::DataSource`.
- **Logic vs Rendering**: Pure data recording and string formatting.
- **Unreal Mapping**: `thru::TrailJournal` + `UThruTrailJournalComponent`.

#### `godot/scripts/world_event_journal.gd` (211 lines)
- **Purpose**: Append-only deterministic audit log of all significant expedition events: promises made, lunch caches found empty, fires encountered, milestones passed.
- **Key State**: Append-only event sequence, sequence numbers, event origins.
- **Public Functions**:
  - `append(row: Dictionary) -> int`
  - `events_since(seq: int) -> Array<Dictionary>`
  - `save_state() -> Dictionary`
  - `restore(val: Dictionary) -> void`
- **Dependencies**: `thru::DataSource` (`SCHEMA.md`).
- **Logic vs Rendering**: Pure audit ledger.
- **Unreal Mapping**: `thru::WorldEventJournal` + `UThruEventJournalSubsystem`.

---

### Module 14: `encounters_promises`
#### `godot/scripts/encounter_library.gd` (230 lines)
- **Purpose**: Loads and validates authored encounter definitions from JSON catalogs, filtering by region, rarity, and repetition constraints.
- **Key State**: Encounter catalog cache, picked encounter history.
- **Public Functions**:
  - `all() -> Array<Dictionary>`
  - `get_entry(id: String) -> Dictionary`
  - `pick(region: int, spot: String, rng: Rng, used: Dictionary) -> Dictionary`
- **Dependencies**: `thru::Rng`, `thru::DataSource` (`data/encounters/`).
- **Logic vs Rendering**: Pure catalog selector.
- **Unreal Mapping**: `thru::EncounterLibrary` + `UThruEncounterLibrarySubsystem`.

#### `godot/scripts/geo_promises.gd` (985 lines)
- **Purpose**: Contract system for trail dinner promises (e.g. trail angel dinner offer at lunch cache). Manages state transitions: Offered -> Accepted -> Kept / Forfeited / Withdrawn.
- **Key State**: Active promise contract, stock counts, participant commitments.
- **Public Functions**:
  - `perform(player_id: int, action: String) -> bool`
  - `snapshot() -> Dictionary`
  - `apply_snapshot(snap: Dictionary) -> void`
- **Dependencies**: `thru::WorldEventJournal`, `thru::DataSource`.
- **Logic vs Rendering**: Core contract logic cleanly separated from 3D angel/cooler visual meshes.
- **Unreal Mapping**: `thru::GeoPromises` + `UThruGeoPromisesComponent`.

#### `godot/scripts/social_graph.gd` (209 lines)
- **Purpose**: Sparse directed memory graph representing NPC opinions of hikers: "Observer remembers Actor for Action". Retains distinct event counts rather than a simple numeric score.
- **Key State**: Directed edges between stable entity IDs / trail names, evidence counts.
- **Public Functions**:
  - `ingest(event: Dictionary) -> void`
  - `recall(observer: String, actor: String) -> Dictionary`
  - `knows(observer: String, actor: String, fact: String) -> bool`
- **Dependencies**: `thru::WorldEventJournal`, `thru::DataSource`.
- **Logic vs Rendering**: Pure directed graph data structure.
- **Unreal Mapping**: `thru::SocialGraph` + `UThruSocialGraphComponent`.

#### `godot/scripts/salt_thieves.gd` (243 lines)
- **Purpose**: Simulates wildlife (marmots, deer, chipmunks) chewing on sweaty pack straps, trekking pole grips, and boots to obtain salt if left unattended.
- **Key State**: Salt attraction levels, risk thresholds per animal species.
- **Public Functions**:
  - `evaluate_chew_risk(gear_salt_level: float, unattended_minutes: float, rng: Rng) -> Dictionary`
  - `apply_gear_damage(gear_item: Dictionary, damage_severity: float) -> Dictionary`
- **Dependencies**: `thru::TrailCalendar`, `thru::Rng`, `thru::DataSource` (`data/wildlife/salt_thieves.json`).
- **Logic vs Rendering**: Pure gameplay risk calculation.
- **Unreal Mapping**: `thru::SaltThieves` + `UThruSaltThievesComponent`.

#### `godot/scripts/trail_trouble.gd` (213 lines)
- **Purpose**: 30-second social decision loop on the trail. A hiker notices an issue (e.g. shortcut, bees, cold river), the party votes on how to react, and consequences are applied.
- **Key State**: Trouble event catalog, active dilemma, voting timers and tallies.
- **Public Functions**:
  - `walked_by(peer_id: int, meters: float) -> void`
  - `vote(peer_id: int, option_idx: int) -> void`
  - `resolve_vote() -> Dictionary`
- **Dependencies**: `thru::Rng`, `thru::DataSource` (`data/trail_trouble.json`).
- **Logic vs Rendering**: Pure cooperative decision-making logic.
- **Unreal Mapping**: `thru::TrailTrouble` + `UThruTrailTroubleComponent`.

---

### Module 15: `campaign_journey_progression`
#### `godot/scripts/campaign_content.gd` (250 lines)
- **Purpose**: Main campaign storyline, legs, favors, and prices (e.g. Ronald, Switchback).
- **Key State**: Campaign stages, leg configurations, pricing catalogs.
- **Public Functions**:
  - `campaigns() -> Array<Dictionary>`
  - `campaign(id: String) -> Dictionary`
  - `offer(event: String, actor: String, run: Dictionary) -> Dictionary`
  - `outcome(event: String, choice: int, actor: String) -> Dictionary`
- **Dependencies**: `thru::DataSource`.
- **Logic vs Rendering**: Pure narrative branching and economy.
- **Unreal Mapping**: `thru::CampaignContent` + `UThruCampaignContentSubsystem`.

#### `godot/scripts/journey_content.gd` (47 lines)
- **Purpose**: Journey section definitions, ridge challenge dialog, and run end conditions.
- **Key State**: Section name tables, story text.
- **Public Functions**:
  - `section_name(section: int) -> String`
  - `run_ending(days: int, food: int, money: int, history: Array<String>) -> Dictionary`
- **Dependencies**: None.
- **Logic vs Rendering**: Pure narrative definition logic.
- **Unreal Mapping**: `thru::JourneyContent` + `UThruJourneyContentSubsystem`.

#### `godot/scripts/trail_content.gd` (80 lines)
- **Purpose**: Trail milestones, condition rules, and delivery ending objectives.
- **Key State**: Milestone thresholds, supper windows.
- **Public Functions**:
  - `condition_name(condition: int) -> String`
  - `delivery_objective(promise: Dictionary, completed: bool, condition: int, seconds: float) -> Dictionary`
- **Dependencies**: None.
- **Logic vs Rendering**: Pure rule definition.
- **Unreal Mapping**: `thru::TrailContent` + `UThruTrailContentSubsystem`.

#### `godot/scripts/pct_checkpoints.gd` (946 lines)
- **Purpose**: Host-authoritative milestone tracking and resupply checkpoint validation. Tracks section progress, stamps, and cash spent.
- **Key State**: Checkpoint roster, visit stamps, spending balances.
- **Public Functions**:
  - `perform_resupply(checkpoint_id: int) -> bool`
  - `perform_spend(amount_cents: int) -> bool`
  - `is_checkpoint_cleared(checkpoint_id: int) -> bool`
- **Dependencies**: `thru::PctBoxChain`, `thru::DataSource` (`data/trail/checkpoints.json`).
- **Logic vs Rendering**: Core progression authority.
- **Unreal Mapping**: `thru::PctCheckpoints` + `UThruCheckpointsSubsystem`.

#### `godot/scripts/pct_blaze_ledger.gd` (161 lines)
- **Purpose**: Verifies unbroken trail coverage along blazes, calculating low/high chainage bounds without trusting client position reports directly.
- **Key State**: Array of traversal interval tuples `[low_mm, high_mm, mode]`.
- **Public Functions**:
  - `record_motion(id: int, low_mm: int, high_mm: int, mode: String) -> void`
  - `summary(id: int) -> Dictionary` (coverage_percentage, gaps)
- **Dependencies**: None.
- **Logic vs Rendering**: Pure interval-math ledger.
- **Unreal Mapping**: `thru::PctBlazeLedger` + `UThruBlazeLedgerComponent`.

---

### Module 16: `film_camera_logic`
#### `godot/scripts/pct_film_camera.gd` (587 lines)
- **Purpose**: Atlas D2 compact 35mm film camera simulation: 24/27-exposure rolls, shutter frame advancing, date back printing, jammed cameras, mailing rolls to lab, 14-day turnaround to General Delivery, and photo album storage.
- **Key State**: Active rolls, exposures count, lab mailers in transit, prints in album.
- **Public Functions**:
  - `new_roll(kind: String) -> Dictionary`
  - `advance_exposure(roll_id: String, metadata: Dictionary) -> bool`
  - `mail_roll_to_lab(roll_id: String, post_office_id: String, julian_day: float) -> bool`
  - `check_lab_delivery(julian_day: float) -> Array<Dictionary>`
- **Dependencies**: `thru::TrailCalendar`, `thru::TownHours`, `thru::DataSource` (`data/camera/rolls.json`).
- **Logic vs Rendering**: Pure camera mechanics and parcel state machine. (Viewport capture is delegated to UE engine hooks).
- **Unreal Mapping**: `thru::FilmCamera` + `UThruFilmCameraComponent`.

#### `godot/scripts/minigames/photo_frame.gd` (202 lines)
- **Purpose**: Photo composition scoring logic: evaluates if a photo angle sits $\ge 40^\circ$ from previous angles, checks subject distance ($1.5$–$12$ m), and grants morale bonuses if group members are in frame.
- **Key State**: Historical shot angles around subject, pose check rules.
- **Public Functions**:
  - `evaluate_shot(subject_pos: Vector3, camera_pos: Vector3, prior_angles: Array<float>) -> Dictionary`
  - `is_angle_distinct(new_angle: float, prior_angles: Array<float>, min_spread_deg: float) -> bool`
- **Dependencies**: None.
- **Logic vs Rendering**: Pure geometric angle and distance scoring math.
- **Unreal Mapping**: `thru::PhotoFrameLogic` + `UThruPhotoFrameComponent`.

---

## 4. Module Dependency Graph

```text
                                +-------------------+
                                |   thru::Rng       |
                                |  (splitmix/xoshiro|
                                +---------+---------+
                                          |
                                          v
+-----------------------+       +-------------------+       +-----------------------+
|  thru::DataSource     |       |   core_calendar   |<------+   Foundation          |
|  (JSON/Tables loader) |       |  (TrailCalendar)  |       |  (Zero dependencies)  |
+-----------+-----------+       +---+---+---+---+---+       +-----------------------+
            |                       |   |   |   |
            |            +----------+   |   |   +-----------------------+
            |            |              |   |                           |
            v            v              |   v                           v
  +--------------------+ |              | +---------------------+ +--------------------+
  |    celestial_sim   | |              | | trail_season_env    | |    town_hours      |
  | (Ephemeris, Math)  | |              | | (Season, Year, Ford)| | (Hours, Schedule)  |
  +--------------------+ |              | +----------+----------+ +---------+----------+
                         |              |            |                      |
                         |              v            v                      |
                         |        +---------------------+                   |
                         |        |     weather_sim     |                   |
                         |        | (Front, Wind, Cold) |                   |
                         |        +----------+----------+                   |
                         |                   |                              |
                         v                   v                              |
        +----------------------+      +----------------+                    |
        |   wildfire_smoke     |<-----+ trail_phenology|                    |
        | (FireRisk, Season)   |      |  & ecology     |                    |
        +----------------------+      +----------------+                    |
                         |                                                  |
                         v                                                  |
        +----------------------+      +----------------+                    |
        |   hiker_metabolism   |      |  hiker_cohort  |<-------------------+
        | (Hunger, WaterCarry) |      |    & bubble    |                    |
        +-----------+----------+      +-------+--------+                    |
                    |                         |                             |
                    v                         v                             |
        +----------------------+      +----------------+                    |
        | hiker_rhythm_fatigue |      | town_resupply  |<-------------------+
        | (Rhythm, Norovirus)  |      |   logistics    |                    |
        +----------------------+      +-------+--------+                    |
                                              |                             |
                                              v                             v
                                      +----------------+          +--------------------+
                                      | town_commerce  |          |  trail_registers   |
                                      |  & services    |          |     & journal      |
                                      +----------------+          +---------+----------+
                                              |                             |
                                              v                             v
                                      +----------------------------------------+
                                      |          encounters_promises           |
                                      |   (Promises, SocialGraph, Trouble)     |
                                      +-------------------+--------------------+
                                                          |
                                                          v
                                      +----------------------------------------+
                                      |      campaign_journey_progression      |
                                      |   (Checkpoints, Content, BlazeLedger)  |
                                      +-------------------+--------------------+
                                                          |
                                                          v
                                      +----------------------------------------+
                                      |           film_camera_logic            |
                                      |        (Rolls, Mail, PhotoFrame)       |
                                      +----------------------------------------+
```

---

## 5. Topological Port Order

The porting work is executed in 16 discrete, incrementally testable modules. Each module depends strictly on previously ported modules.

1. **`core_calendar`**
   - *GDScript*: `godot/scripts/trail_calendar.gd`
   - *Goal*: Establish deterministic civil calendar math, Daylight Saving Time conversions, and solar twilight formulas from continuous Julian Day numbers. Foundation of all temporal systems.
2. **`celestial_sim`**
   - *GDScript*: `godot/scripts/celestial_math.gd`, `godot/scripts/celestial_ephemeris.gd`
   - *Goal*: Astronomical topocentric transforms and NASA/JPL Sun/Moon position table sampling.
3. **`trail_season_environment`**
   - *GDScript*: `godot/scripts/trail_season.gd`, `godot/scripts/trail_year.gd`, `godot/scripts/intermittent_water.gd`, `godot/scripts/ford_crossings.gd`
   - *Goal*: Regional climate database, daily snow water equivalent (SWE) along route bins, intermittent stream flow, and snowmelt ford depth/speed.
4. **`weather_sim`**
   - *GDScript*: `godot/scripts/weather_front.gd`, `godot/scripts/thunder_delay.gd`, `godot/scripts/wind_diurnal.gd`, `godot/scripts/cold_air_pool.gd`
   - *Goal*: Moving weather front boundaries, acoustic thunder timing, diurnal wind scaling, and night cold air pool inversions.
5. **`wildfire_smoke`**
   - *GDScript*: `godot/scripts/fire_risk.gd`, `godot/scripts/fire_season.gd`, `godot/scripts/smoke_season.gd`
   - *Goal*: Fine fuel moisture danger ratings, MTBS active burn polygon tracking, and regional smoke particulate drift.
6. **`trail_phenology_ecology`**
   - *GDScript*: `godot/scripts/mosquito_season.gd`, `godot/scripts/wildflower_bloom.gd`, `godot/scripts/fall_colour.gd`, `godot/scripts/poodle_dog_bush.gd`
   - *Goal*: Ecological response models: snowmelt mosquito biting pressure, wildflower blooms, autumn foliage coloring, and poodle-dog bush dermatitis.
7. **`hiker_metabolism`**
   - *GDScript*: `godot/scripts/hiker_hunger.gd`, `godot/scripts/water_carry_data.gd`, `godot/scripts/water_carry.gd`, `godot/scripts/water_caches.gd`
   - *Goal*: Caloric expenditure, through-hiker late-season hunger curve, look-ahead water carry planning, and volunteer cache stocks.
8. **`hiker_rhythm_fatigue`**
   - *GDScript*: `godot/scripts/hiker_rhythm.gd`, `godot/scripts/hiker_midnight.gd`, `godot/scripts/norovirus_outbreak.gd`
   - *Goal*: Zero/nero rest rhythm, 9 PM camp lights-out etiquette, and norovirus epidemic container spreading and downtime.
9. **`hiker_cohort_bubble`**
   - *GDScript*: `godot/scripts/trail_bubble.gd`, `godot/scripts/trail_cohort.gd`, `godot/scripts/hiker_cohort.gd`, `godot/scripts/trail_permits.gd`, `godot/scripts/trail_resources.gd`
   - *Goal*: Hiker bubble wave progression, virtual named cohort agent roster, daily wear/tear/injury simulation, permits quota, and cache depletion.
10. **`town_hours_schedule`**
    - *GDScript*: `godot/scripts/town_hours.gd`, `godot/scripts/town_schedule.gd`, `godot/scripts/trailhead_traffic.gd`
    - *Goal*: Resupply stop facility hours, town life temporal state, and road crossing day-use traffic levels.
11. **`town_resupply_logistics`**
    - *GDScript*: `godot/scripts/hiker_box.gd`, `godot/scripts/resupply_plan.gd`, `godot/scripts/pct_box_chain.gd`, `godot/scripts/kennedy_applause.gd`
    - *Goal*: Hiker box loot generation, resupply schedule planning, postal mail drop hops, and Kennedy Meadows milestone arrival.
12. **`town_commerce_services`**
    - *GDScript*: `godot/scripts/snack_vending_site.gd`, `godot/scripts/hitch_wait.gd`, `godot/scripts/town_bed.gd`
    - *Goal*: Snack purchases, road hitchhiking wait times, and town lodging bed availability/soundscape cues.
13. **`trail_registers_journal`**
    - *GDScript*: `godot/scripts/trail_register.gd`, `godot/scripts/trail_journal.gd`, `godot/scripts/world_event_journal.gd`
    - *Goal*: Trailhead logbook sign/read interactions, closed daily journal entries, and append-only world event audit ledger.
14. **`encounters_promises`**
    - *GDScript*: `godot/scripts/encounter_library.gd`, `godot/scripts/geo_promises.gd`, `godot/scripts/social_graph.gd`, `godot/scripts/salt_thieves.gd`, `godot/scripts/trail_trouble.gd`
    - *Goal*: Encounter catalog loading, dinner promise contracts, directed social memory graph, salt-thief gear damage, and voting trouble dilemmas.
15. **`campaign_journey_progression`**
    - *GDScript*: `godot/scripts/campaign_content.gd`, `godot/scripts/journey_content.gd`, `godot/scripts/trail_content.gd`, `godot/scripts/pct_checkpoints.gd`, `godot/scripts/pct_blaze_ledger.gd`
    - *Goal*: Campaign narrative progression, journey milestones, host checkpoint verification, and blaze coverage traversal ledger.
16. **`film_camera_logic`**
    - *GDScript*: `godot/scripts/pct_film_camera.gd`, `godot/scripts/minigames/photo_frame.gd`
    - *Goal*: 35mm film roll state, shutter exposure counters, lab mailing, delivery times, photo album collections, and photo framing composition scoring.

---

MAP_DONE
