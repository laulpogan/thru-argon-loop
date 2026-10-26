#!/bin/bash
set -euo pipefail
ROOT=/workspace/fullscene
UE=/opt/ue/home/ue4/UnrealEngine
mkdir -p "$ROOT/logs"
rm -f "$ROOT/ue_stage.txt" "$ROOT/ue_error.txt"
cd "$ROOT/proj"
export VK_ICD_FILENAMES=/etc/vulkan/icd.d/nvidia_icd.json
export SDL_VIDEODRIVER=offscreen
set +e
timeout "${UE_TIMEOUT:-7200}" su ue -c "$UE/Engine/Binaries/Linux/UnrealEditor $ROOT/proj/Creek.uproject -RenderOffscreen -vulkan -unattended -nosplash -NoLoadingScreen -NoVerifyGC -AllowStdOutLogVerbosity -stdout -FullStdOutLogOutput" > "$ROOT/logs/ue.log" 2>&1
status=$?
printf 'UE_EXIT %s\n' "$status" >> "$ROOT/ue_stage.txt"
exit "$status"
