#!/usr/bin/env bash
# ==============================================================================
# FB 2minutes Storymaker - One-Line Installer
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/AllensCreations/FB-2minutes-Storymaker/main/install.sh | bash
# ==============================================================================

set -e

REPO_URL="https://github.com/AllensCreations/FB-2minutes-Storymaker.git"

# If already inside the repo folder, install/update in-place; otherwise use ./FB-2minutes-Storymaker
if [ -f "main.py" ] && ([ "$(basename "$(pwd)")" = "FB-2minutes-Storymaker" ] || [ -d "src/align_engine" ]); then
    TARGET_DIR="."
else
    TARGET_DIR="./FB-2minutes-Storymaker"
fi

echo "========================================================"
echo "🎬 FB 2minutes Storymaker - One-Line Installer"
echo "========================================================"

# 1. Detect Environment & Install System Packages
IS_TERMUX=0
if [ -n "$TERMUX_VERSION" ] || (command -v pkg >/dev/null 2>&1 && [ -n "$PREFIX" ]); then
    IS_TERMUX=1
    echo "📱 Environment: Termux on Android detected!"
    echo "📦 Installing Termux packages (git, python, python-pillow, ffmpeg)..."
    pkg install -y git python python-pillow ffmpeg curl || true
elif [ -f /etc/debian_version ]; then
    echo "🐧 Environment: Debian / Ubuntu detected!"
    SUDO_CMD=""
    if [ "$(id -u)" -ne 0 ] && command -v sudo >/dev/null 2>&1; then
        SUDO_CMD="sudo"
    fi
    echo "📦 Installing system packages (git, python3, python3-pil, ffmpeg)..."
    $SUDO_CMD apt-get update -qq || true
    $SUDO_CMD apt-get install -y -qq git python3 python3-pil python3-venv ffmpeg curl || true
elif [ "$(uname -s)" = "Darwin" ]; then
    echo "🍏 Environment: macOS detected!"
    if command -v brew >/dev/null 2>&1; then
        echo "📦 Installing dependencies via Homebrew (ffmpeg, python)..."
        brew install ffmpeg python || true
        pip3 install "Pillow>=10.0.0" || true
    else
        echo "Notice: Homebrew not found. Please ensure FFmpeg and Python are installed."
    fi
else
    echo "💻 Environment: Linux / Unix"
fi

# 2. Check Python interpreter
if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
else
    echo "❌ Error: Python 3 was not found. Please install Python 3.8+."
    exit 1
fi

PYTHON_VER=$($PYTHON_BIN -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✓ Python interpreter: $PYTHON_BIN (v$PYTHON_VER)"

# 3. Create or Update Repository
# Terminate any stale storymaker servers to prevent port lockups
pkill -f "web/server.py" 2>/dev/null || true
pkill -f "main.py" 2>/dev/null || true
pkill -f "python.*server" 2>/dev/null || true
fuser -k 8000/tcp 2>/dev/null || true
fuser -k 8001/tcp 2>/dev/null || true

if [ "$TARGET_DIR" = "." ]; then
    echo "📂 Operating in-place within current repository directory."
    if [ -d ".git" ] && command -v git >/dev/null 2>&1; then
        echo "Pulling latest updates via git..."
        git fetch origin main || true
        git reset --hard origin/main || git pull origin main || true
    fi
    # If a nested clone exists inside this repo, update it as well
    if [ -d "FB-2minutes-Storymaker" ] && [ -f "FB-2minutes-Storymaker/main.py" ]; then
        echo "Notice: Found nested clone 'FB-2minutes-Storymaker'. Updating it as well..."
        (cd FB-2minutes-Storymaker && git fetch origin main 2>/dev/null && git reset --hard origin/main 2>/dev/null || git pull origin main 2>/dev/null || true)
    fi
elif [ -d "$TARGET_DIR" ]; then
    echo "📂 Directory '$TARGET_DIR' already exists. Updating..."
    cd "$TARGET_DIR"
    if [ -d ".git" ] && command -v git >/dev/null 2>&1; then
        echo "Pulling latest updates via git..."
        git fetch origin main || true
        git reset --hard origin/main || git pull origin main || true
    fi
else
    echo "📥 Creating and cloning repository into '$TARGET_DIR'..."
    if command -v git >/dev/null 2>&1; then
        git clone "$REPO_URL" "$TARGET_DIR"
        cd "$TARGET_DIR"
    else
        echo "git not found, downloading repository archive..."
        mkdir -p "$TARGET_DIR"
        curl -fsSL "https://github.com/AllensCreations/FB-2minutes-Storymaker/archive/refs/heads/main.tar.gz" | tar -xz -C "$TARGET_DIR" --strip-components=1
        cd "$TARGET_DIR"
    fi
fi

PROJECT_ABS_PATH="$(pwd)"

# 4. Verify Pillow & Dependencies
echo "🔍 Checking Python dependencies..."
if ! $PYTHON_BIN -c "import PIL" >/dev/null 2>&1; then
    echo "Installing Pillow for Python..."
    if [ "$IS_TERMUX" -eq 1 ]; then
        pkg install -y python-pillow || true
    else
        $PYTHON_BIN -m pip install "Pillow>=10.0.0" || $PYTHON_BIN -m pip install "Pillow>=10.0.0" --break-system-packages || true
    fi
fi

# 5. Generate / Verify Preloaded Story Assets
echo "🎨 Ensuring preloaded story assets exist..."
$PYTHON_BIN scripts/generate_sample_assets.py --theme elsa

# 5b. Sync to TrebEdit if installed on Android
for trebedit_dir in "/storage/emulated/0/TrebEdit" "/sdcard/TrebEdit" "$HOME/storage/shared/TrebEdit"; do
    if [ -d "$trebedit_dir" ]; then
        echo "📱 Syncing HTML assets to TrebEdit workspace ($trebedit_dir)..."
        cp -f "$PROJECT_ABS_PATH/AR.html" "$trebedit_dir/" 2>/dev/null || true
        cp -f "$PROJECT_ABS_PATH/index.html" "$trebedit_dir/" 2>/dev/null || true
    fi
done

# 6. Create Global CLI Launcher Command (fb-storymaker)
echo "⚡ Setting up global 'fb-storymaker' command..."
LAUNCHER_SCRIPT="#!/usr/bin/env bash
exec $PYTHON_BIN \"$PROJECT_ABS_PATH/main.py\" \"\$@\"
"

BIN_DIR=""
if [ "$IS_TERMUX" -eq 1 ] && [ -n "$PREFIX" ] && [ -d "$PREFIX/bin" ]; then
    BIN_DIR="$PREFIX/bin"
elif [ "$(id -u)" -eq 0 ] && [ -d "/usr/local/bin" ]; then
    BIN_DIR="/usr/local/bin"
elif [ -d "$HOME/.local/bin" ]; then
    BIN_DIR="$HOME/.local/bin"
else
    mkdir -p "$HOME/.local/bin"
    BIN_DIR="$HOME/.local/bin"
fi

if [ -n "$BIN_DIR" ]; then
    LAUNCHER_PATH="$BIN_DIR/fb-storymaker"
    echo "$LAUNCHER_SCRIPT" > "$LAUNCHER_PATH"
    chmod +x "$LAUNCHER_PATH"
    echo "✓ Global launcher created: $LAUNCHER_PATH"
fi

echo ""
echo "========================================================"
echo "🎉 FB 2minutes Storymaker Installed Successfully!"
echo "========================================================"
echo ""
echo "Location: $PROJECT_ABS_PATH"
echo ""
echo "🚀 Quickstart Commands:"
echo "  1. Interactive Termux Console UI:  fb-storymaker --tui"
echo "     (Mobile dashboard with menu, rendering & matrix viewer)"
echo ""
echo "  2. Launch Creative Studio Web UI:  fb-storymaker --web"
echo "     (Then open: http://localhost:8000)"
echo ""
echo "  3. Direct Video Render via CLI:    fb-storymaker --run"
echo ""
echo "  4. Explore All Options:            fb-storymaker --help"
echo ""
echo "Or run directly inside the project folder:"
if [ "$TARGET_DIR" != "." ]; then
    echo "  cd $TARGET_DIR"
fi
echo "  make tui    # Termux Interactive Console"
echo "  make web    # Web UI Studio"
echo "  make run    # Direct CLI Render"
echo "========================================================"
