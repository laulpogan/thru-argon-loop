#!/bin/bash
# usage: run_ue.sh  (reads /workspace/unreal/run.json). Runs as user ue.
UE=/opt/ue/home/ue4/UnrealEngine
rm -f /workspace/unreal/ue_stage.txt /workspace/unreal/ue_error.txt
cd /workspace/unreal/proj
timeout ${UE_TIMEOUT:-3000} su ue -c "$UE/Engine/Binaries/Linux/UnrealEditor /workspace/unreal/proj/Creek.uproject -RenderOffscreen -vulkan -unattended -nosplash -nosound -NoLoadingScreen -NoVerifyGC -AllowStdOutLogVerbosity -stdout -FullStdOutLogOutput" > /workspace/unreal/logs/ue_$(date +%H%M%S).log 2>&1
echo "UE_EXIT $?" >> /workspace/unreal/ue_stage.txt
