#!/bin/bash
cd /workspace/unreal/src
export GEMINI_API_KEY=$(tr "\0" "\n" </proc/1/environ | sed -n "s/^GEMINI_API_KEY=//p")
export ARGON_LANE=unreal-orch TZ=America/Los_Angeles
timeout 4200 pi --provider google --model gemini-4-argon -p "$(cat ORCH.md)" > /workspace/unreal/out/pi.log 2>&1
echo PI_EXIT $? >> /workspace/unreal/out/pi.log
