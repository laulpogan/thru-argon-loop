import os, json, re
from concurrent.futures import ThreadPoolExecutor
from common import run, BASE
SPEC = os.path.expanduser("~/cs-audit/gemini-hackathon/reset/unreal-models/specs-from-managed-agent"); os.makedirs(SPEC, exist_ok=True)
JOBS = [
 "Southern California desert, Campo to Mount Laguna (Mile 0-42): Southern Terminus monument, chaparral, manzanita, desert scrub",
 "Anza-Borrego / San Felipe Hills and Scissors Crossing (Mile 77-91): cholla, ocotillo, the Highway 78 underpass and road crossing",
 "Mojave and Tehachapi wind farm section (Mile 520-566): Joshua trees, wind turbines, LA Aqueduct pipe walk, dirt roads",
 "San Jacinto / Fuller Ridge and Mount San Jacinto (Mile 150-200): Jeffrey pine, granite, snow patches, Black Mountain Road",
 "Kennedy Meadows South, gateway to the Sierra (Mile 702): the General Store porch, South Fork Kern River, sagebrush meadow",
 "High Sierra passes: Forester Pass and Muir Pass (Mile 779-838): Muir Hut stone shelter, talus, alpine lakes, switchbacks",
 "High Sierra subalpine forest and meadows: Evolution Valley, Lyell Canyon: lodgepole pine, whitebark pine, meadow grasses, creek fords",
 "Sierra trail infrastructure: PCT trail signs, wilderness boundary signs, bear boxes (food lockers), wooden footbridges, rock cairns",
 "Tuolumne Meadows and Sonora Pass road crossings: Tioga Road (CA-120) crossing, trailhead parking, ranger vehicles, Tuolumne store",
 "Northern California: Lassen Volcanic NP and Hat Creek Rim (Mile 1350-1420): volcanic boulders, manzanita, fire-scarred pines, Subway Cave",
 "Northern California: Castle Crags and Burney Falls (Mile 1420-1510): granite spires, Burney Falls, Douglas fir, I-5 crossing at Castella",
 "Oregon: Crater Lake rim and Mount Thielsen (Mile 1820-1870): pumice flats, mountain hemlock, Rim Village, volcanic peaks",
 "Oregon: Central Cascades lava fields, McKenzie Pass and Obsidian Falls (Mile 1960-2000): basalt lava rock, Dee Wright Observatory, obsidian",
 "Oregon / Washington: Timberline Lodge on Mount Hood and the Bridge of the Gods over the Columbia River (Mile 2100-2150)",
 "Washington: Goat Rocks Knife's Edge and Glacier Peak wilderness (Mile 2280-2550): ridge talus, subalpine fir, glacier ice, wildflowers",
 "Washington North Cascades to the Northern Terminus (Mile 2600-2650): Stehekin bakery and bus, Northern Terminus monument at the Canadian border, Hart's Pass",
 "PCT trail towns and resupply: Idyllwild, Big Bear, Sierra City, Cascade Locks storefronts, post office, hiker box, trail angel cache",
 "PCT vehicles and road crossings: USFS pickup, trail-angel shuttle van, 1990s Subaru Outback at a trailhead, cattle guard, highway trail crossing sign",
]
def job(i, theme):
    p = (f"PCT section/theme for this job: {theme}.\nUse the asset-spec skill. Emit 3 to 5 asset specs, one FILE block each named specs/<name>.json. "
         "Keep each spec under 2 KB. End with a one-paragraph summary.")
    r, files, it = run("thru-asset-librarian", p, p, label=f"librarian/fanout-{i:02d}")
    saved = []
    for k, v in files.items():
        try: d = json.loads(v)
        except Exception: continue
        for spec in (d if isinstance(d, list) else [d]):
            name = re.sub(r"[^a-z0-9_]+", "_", str(spec.get("name", f"asset_{i}")).lower())[:60]
            spec["_provenance"] = {"agent": "thru-asset-librarian", "interaction_id": r["interaction_id"], "environment_id": r["environment_id"], "job": theme}
            fn = f"{SPEC}/{i:02d}_{name}.json"; json.dump(spec, open(fn, "w"), indent=1); saved.append(os.path.basename(fn))
    print(i, r["status"], r["seconds"], r["interaction_id"], len(saved), saved, flush=True)
    return r
with ThreadPoolExecutor(8) as ex:
    list(ex.map(lambda a: job(*a), enumerate(JOBS)))
