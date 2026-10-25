set -x
export DEBIAN_FRONTEND=noninteractive
apt-get update && apt-get install -y libvulkan1 vulkan-tools mesa-utils xvfb libxkbcommon0 libnss3 libxcomposite1 libxrandr2 libxi6 libxcursor1 libasound2 libpulse0 ffmpeg git-lfs tmux rsync
curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && apt-get install -y nodejs
npm i -g @earendil-works/pi-coding-agent@0.86.0 || npm i -g @mariozechner/pi-coding-agent
vulkaninfo --summary 2>&1 | head -40
which pi; pi --version
echo BOOTSTRAP_DONE
