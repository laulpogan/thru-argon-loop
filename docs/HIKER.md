# HIKER asset fixes (pod lane), 2026-10-25

> Post-deadline work. None of this is in the submitted video, which is the no-hiker cut `final_v5_nohiker.mp4` (see [`VIDEO.md`](VIDEO.md)).

Scene: no-hiker bridge/creek walk frames 1500-2400 + hiker. Pods u1 (1838), u2 (12181), u3 (1260), u6 (1673).
Scripts: `pipeline/pod-assetfix/` (gen.py, ue_main.py, params.json, passhk.sh, hkfull.sh, pass2.sh, run json).

## 1. Pack/hat do not track the body
- Bug: pack and hat drift off the torso (Paul 4:31: "don't even track with the body").
- Root cause: gear was a separate spawnable keyed to the hiker ROOT transform only; it never saw bone motion (bob, sway, lean).
- Fix A (old hiker): MovieScene3DAttachTrack to the hiker binding, socket spine_03 (pack) and Head (hat); relative transform = desired actor-space gear transform x inverse(ref-pose bone transform, RTS_ACTOR), constant key. Bone names printed: root, pelvis, spine_01..03, neck_01, Head, clavicle_*... (hiker_male).
- Fix B (preferred): clothed PCT hiker meshes (hero-pct-hiker-clothed-women-s / men-s) have the pack, hat and poles SKINNED into the mesh, so they move with the bones by construction.
- Verified-by (Fix B, women Var1, run hkw on u3, frames 1500-2400): hkw_poses.jpg = turn 1554 / stride 1700 / stride 1729 / pause 1950; hkw_stride_crops.jpg = 1700/1715/1729/1744 back view, legs and arms alternate, pack + hat + pole stay locked to the torso/head. Men's variant: hkm_poses.jpg (same frames), also tracks.
- Fix A result (old hiker, run hka on u2): attach works (pack and hat now move with spine_03/Head: hka_poses.jpg), but the relative offset is wrong: pack hangs on the left shoulder, rotated. Needs the bone-local axes worked out; superseded by Fix B, left as RUN fallback (no_attach false).

## 2. Pack orientation backwards
- Bug: straps/back panel faced away from the back (pass 2).
- Root cause: hiker_pack_1990s.glb forward axis is opposite to our yaw convention; pack_yaw default 0.
- Fix: pack_yaw default 180 (ue_main add_gear); in Fix B the pack is modelled on the back.

## 3. Skin-coloured shirt / grey mannequin
- Root cause: hiker_male is a bare body; clothing was a height-band procedural material (OUTFIT).
- Fix: clothed hiker swap (RUN hiker_glb / hiker_var / hiker_basecolor); every slot gets M_HikerAlt built from the asset's own basecolor atlas (no glTF MI left on the mesh, avoids the UE-23902 invalid BaseColorTexture crash). Walk clip Quaternius_WalkCycle (1.25 s) at walk_rate 1.29 (= 1.375 x 1.25/1.3333). Rig has no idle clip: pause holds the pose (rate 0.002).

## 4. Pack re-import segfault
- Bug: SIGSEGV in FUniformExpressionSet::FillUniformBuffer during MRQ on 2nd+ build of a pod (pass3, fix runs 16:24-16:35).
- Root cause: re-importing backpack.glb (replace_existing) over its live glTF material instance + textures leaves the MI pointing at a replaced/invalid texture.
- Fix: idempotent import, in ue_main: delete /Game/Mesh/backpack and /Game/Mesh/hat (and /Game/T/T_Pack_D/N, /Game/Pack/hiker_alt) before import; passhk.sh also removes them from Content before launch. Verified: fix/fixtest/nohiker runs after 16:36 all UE_EXIT 0.

## 5. u6 numpy
- Bug: gen.py ModuleNotFoundError numpy on u6 (pip had installed for python3.11, gen.py runs /usr/bin/python3 = 3.10).
- Fix: python3 -m pip install numpy trimesh pillow scipy on u6. Verified: python3 imports OK (numpy 2.2.6).
- Second u6 bug: /workspace/unreal was root:root 755, so ue_main (runs as user ue) could not write ue_stage.txt -> PermissionError, editor idled. Fix: chown ue:ue /workspace/unreal. Verified by the hkfull 2262-3013 slice on u6.

## 6. Hiker basecolor PermissionError (17:05)
- Root cause: ue_main copied the hiker atlas into assets/ (root-owned). Fix: copy to /tmp/thru_tex/ and import from there.

## Clips
- hkw_1500_2400.mp4 (women Var1), hkm_1500_2400.mp4 (men): 900 frames, 15 s, 1080p60, ambience from 25 s.
- Full 3013-frame walk with women Var1: run hkfull split u3/u1/u2/u6 (0-754/754-1508/1508-2262/2262-3013), started 17:15.
- Known limits: rig has no idle clip, so the idle segments hold a near-still pose; walk_rate 1.29 assumes the same stride as hiker_male (not FK-measured).

## Full walk (17:24)
- walk_clothed_women_full.mp4: 3013 frames, 50.2 s, 1080p60 H.264 + AAC 48k ambience; women Var1, pack/hat/pole skinned. full_chunks.jpg = frames 200/900/1950/2500.

Verification stills and clips named above (hkw_poses.jpg, hkm_poses.jpg, hkw_1500_2400.mp4, walk_clothed_women_full.mp4, etc.) are kept off-repo.
