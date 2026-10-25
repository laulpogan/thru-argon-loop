#!/bin/bash
# bulk subtask: summarize the newest UE log's errors with gemini-3.8-flash
L=$(ls -t /workspace/unreal/logs/*.log | head -1)
grep -E "Error|error:|THRU:|Warning: .*Python|Traceback|Fatal|MovieRender" "$L" | tail -300 > /tmp/ue_err.txt
ARGON_LANE=unreal-flash argon -m gemini-3.8-flash -f /tmp/ue_err.txt "This is an Unreal Engine 5.6 headless editor log excerpt from a Python build+Movie Render Queue script. List the real errors (ignore benign noise) and the most likely fix for each, in under 15 lines."
