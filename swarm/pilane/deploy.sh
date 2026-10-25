#!/bin/bash
# Deploy + bootstrap pilane orchestrator pods (cpu3c, 16 vCPU) via overflow tooling; log to pilane/deploy.log.
cd ~/cs-audit/gemini-hackathon/overflow
for i in "$@"; do
  N=thru-cpu-overflow-pilane-$i
  ( python3 provision_pilane.py deploy --name $N --vcpus ${VCPUS:-16} && sleep 45 && { for t in 1 2 3 4 5 6; do python3 setup-cpu.py --name $N && break; sleep 30; done; } && echo "READY $N $(date +%T)" ) >> ../pilane/deploy-$i.log 2>&1 &
  sleep 3
done
wait
