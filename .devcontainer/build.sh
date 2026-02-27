#!/usr/bin/env bash

# Stop on errors
set -e

cd "$(dirname "$0")/.."

HA_CONFIG_DIR="${PWD}/config"
HA_DEFAULT_CONFIG_DIR="${PWD}/.devcontainer/.ha_config"

# Setup venv if not devcontainer of venv is not activated
if [ ! -n "$DEVCONTAINER" ] && [ ! -n "$VIRTUAL_ENV" ];then
  virtualenv .venv
  source .venv/bin/activate
fi

# Install packages
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y
# sudo apt-get install -y python3-pip python3-dev python3-venv autoconf libssl-dev \
#     libxml2-dev libxslt1-dev libjpeg-dev libffi-dev libudev-dev zlib1g-dev pkg-config \
#     libavformat-dev libavcodec-dev libavdevice-dev libavutil-dev libswscale-dev \
#     libswresample-dev libavfilter-dev ffmpeg libgammu-dev build-essential
sudo apt-get install -y libturbojpeg0 ffmpeg libpcap-dev
sudo apt-get install -y just
sudo apt-get clean

# Install go2rtc
HA_GO2RTC_VERSION=$(curl --silent -qI https://github.com/AlexxIT/go2rtc/releases/latest | awk -F '/' '/^location/ {print  substr($NF, 1, length($NF)-1)}')
echo "https://github.com/AlexxIT/go2rtc/releases/download/${HA_GO2RTC_VERSION}/go2rtc_linux_amd64"
sudo curl -o  /bin/go2rtc -fL "https://github.com/AlexxIT/go2rtc/releases/download/${HA_GO2RTC_VERSION}/go2rtc_linux_amd64"
sudo chmod +x /bin/go2rtc

# Install Python dependencies
echo "📦 Installing Python dependencies..."
uv pip install --upgrade pip

echo "🏠 Installing Home Assistant..."
uv pip install homeassistant

echo "📦 Installing zlib_ng and isal packages..."
pip3 install zlib_ng isal

# Create HA config dir if missing
mkdir -p "${HA_CONFIG_DIR}"

# Copy default configuration only if configuration.yaml does not exist
if [ ! -f "${HA_CONFIG_DIR}/configuration.yaml" ]; then
  if [ -f "${HA_DEFAULT_CONFIG_DIR}/configuration-default.yaml" ]; then
    cp "${HA_DEFAULT_CONFIG_DIR}/configuration-default.yaml" "${HA_CONFIG_DIR}/configuration.yaml"
    echo "[setup-ha] Seeded configuration.yaml from configuration-default.yaml"
  else
    echo "[setup-ha] WARNING: configuration-default.yaml not found; leaving configuration.yaml absent"
  fi
else
  echo "[setup-ha] configuration.yaml already present; not overwriting"
fi


# Ensure HA config structure (safe; ignore errors)
hass --script ensure_config -c "${HA_CONFIG_DIR}"
echo "[setup-ha] Ensured HA config structure in ${HA_CONFIG_DIR}"

# Create onboarding file to skip onboarding (valid JSON)
mkdir -p "${HA_CONFIG_DIR}/.storage"

cat > "${HA_CONFIG_DIR}/.storage/onboarding" << 'EOF'
{
    "version": 3,
    "key": "onboarding",
    "data": {
        "done": [
            "core_config",
            "analytics",
            "integration"
        ]
    }
}
EOF
echo "[setup-ha] Created onboarding file to skip onboarding"

# Install pre-commit hooks
uv tool install prek
uv run prek install

# Install Dependencies
echo "🛠️ Installing development dependencies..."
uv sync --all-extras --group dev
