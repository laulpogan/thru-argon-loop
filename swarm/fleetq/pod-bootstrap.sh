#!/usr/bin/env bash
# fleetq shared pod bootstrap: idempotent; official Blender 3.0.1, PIL/numpy, argon CLI, GPU-enable module. No secrets touched/written.
set -euo pipefail
F=/opt/fleetq; mkdir -p $F /opt/thru /work/proof
[ -f $F/ready ] && grep -q v4 $F/ready && { cat $F/ready; exit 0; }
export DEBIAN_FRONTEND=noninteractive
need=""; for b in rsync curl xz python3; do command -v $b >/dev/null || need=1; done
python3 -c 'import PIL,numpy' 2>/dev/null || need=1
if [ -n "$need" ] || ! ldconfig -p | grep -q libXi.so.6; then
  apt-get update -qq >/dev/null
  apt-get install -y -qq --no-install-recommends rsync curl xz-utils python3 python3-pil python3-numpy libxi6 libxrender1 libxkbcommon0 libsm6 libgl1 libxxf86vm1 libxfixes3 libx11-6 libxext6 >/dev/null
fi
p=/opt/thru/blender-3.0.1-linux-x64
if [ ! -x "$p/blender" ]; then
  curl -fsSL --retry 2 --max-time 300 https://download.blender.org/release/Blender3.0/blender-3.0.1-linux-x64.tar.xz -o /opt/thru/blender.tar.xz
  echo '4f17aa3d10ed6e13e6a75479f1a506f58998b8c007812a0886d9254c953e2ae5  /opt/thru/blender.tar.xz' | sha256sum -c - >/dev/null
  tar -xJf /opt/thru/blender.tar.xz -C /opt/thru && rm /opt/thru/blender.tar.xz
fi
ln -sf "$p/blender" /usr/local/bin/blender
# assetfactory install-blender.sh expects /opt/blender-3.0.1-linux-x64; concurrent slots race on its download. Pre-provide it.
if ! [ -x /opt/blender-3.0.1-linux-x64/blender ] || [ -f /opt/blender-3.0.1-linux-x64.tar.xz ]; then
  pgrep -f install-blender >/dev/null || { rm -rf /opt/blender-3.0.1-linux-x64 /opt/blender-3.0.1-linux-x64.tar.xz; ln -s "$p" /opt/blender-3.0.1-linux-x64; }
fi
install -m 755 $F/argon /usr/local/bin/argon 2>/dev/null || true
cp $F/fleetq_gpu.py "$p/3.0/scripts/modules/fleetq_gpu.py"
dev=$(blender -b --python-expr 'import fleetq_gpu;print("FQDEV",fleetq_gpu.enable())' 2>&1 | grep -E "FQDEV|FLEETQ_GPU" | tr '\n' ' ')
gpu=$(command -v nvidia-smi >/dev/null && nvidia-smi --query-gpu=name --format=csv,noheader | head -1 || echo none)
gem=$(tr '\0' '\n' </proc/1/environ | grep -c '^GEMINI_API_KEY=' || true)
echo "v4 blender=$(readlink -f /usr/local/bin/blender) gpu=$gpu dev=[$dev] gemini_env=$gem nproc=$(nproc) godot=$(command -v godot || echo none)" | tee $F/ready
