set -o pipefail
date
crane export ghcr.io/epicgames/unreal-engine:dev-slim-5.6.1 - | tar x -C /opt/ue --wildcards "home/ue4/UnrealEngine/*"
echo EXIT $?
rm -f /root/.docker/config.json
date
echo PULL_DONE
