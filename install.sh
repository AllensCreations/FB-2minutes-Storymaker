#!/usr/bin/env bash
# ==============================================================================
# FB 2minutes Storymaker - One-Line Installer & Auto-Updater
# Version: 1.0.21
#
# Usage:
#   Fresh Install / Auto-Update:
#     curl -fsSL https://raw.githubusercontent.com/AllensCreations/FBStoryMaker/main/install.sh | bash
#   Check Installed Version:
#     bash install.sh --version
#   Update Existing Installation:
#     bash install.sh --update
# ==============================================================================

set -e

APP_VERSION="1.0.21"
REPO_URL="https://github.com/AllensCreations/FBStoryMaker.git"

# Handle CLI flags
for arg in "$@"; do
    case "$arg" in
        -v|--version)
            echo "FB 2minutes Storymaker Installer v${APP_VERSION}"
            exit 0
            ;;
        -h|--help)
            echo "FB 2minutes Storymaker Installer v${APP_VERSION}"
            echo ""
            echo "Usage: bash install.sh [options]"
            echo ""
            echo "Options:"
            echo "  -v, --version       Display installer version and exit"
            echo "  -u, --update        Force update existing installation"
            echo "  -h, --help          Show this help message"
            exit 0
            ;;
    esac
done

# If already inside the repo folder, install/update in-place; otherwise use ./FBStoryMaker
if [ -f "main.py" ] && ([ "$(basename "$(pwd)")" = "FBStoryMaker" ] || [ -d "src/align_engine" ]); then
    TARGET_DIR="."
else
    TARGET_DIR="./FBStoryMaker"
fi

# Detect currently installed version if exists
CURRENT_VERSION="none"
if [ "$TARGET_DIR" = "." ] && [ -f "VERSION" ]; then
    CURRENT_VERSION=$(head -n1 "VERSION" | tr -d '[:space:]')
elif [ -d "$TARGET_DIR" ] && [ -f "$TARGET_DIR/VERSION" ]; then
    CURRENT_VERSION=$(head -n1 "$TARGET_DIR/VERSION" | tr -d '[:space:]')
fi

echo "========================================================"
echo "🎬 FB 2minutes Storymaker - Installer / Auto-Updater"
echo "📌 Release Target: v${APP_VERSION}"
if [ "$CURRENT_VERSION" != "none" ]; then
    echo "📦 Detected Installed Version: v${CURRENT_VERSION}"
fi
echo "========================================================"

# 1. Detect Environment & Install System Packages
IS_TERMUX=0
if [ -n "$TERMUX_VERSION" ] || (command -v pkg >/dev/null 2>&1 && [ -n "$PREFIX" ]); then
    IS_TERMUX=1
    echo "📱 Environment: Termux on Android detected!"
    echo "📦 Ensuring Termux packages (git, python, python-pillow, ffmpeg, curl)..."
    pkg install -y git python python-pillow ffmpeg curl || true
elif [ -f /etc/debian_version ]; then
    echo "🐧 Environment: Debian / Ubuntu detected!"
    SUDO_CMD=""
    if [ "$(id -u)" -ne 0 ] && command -v sudo >/dev/null 2>&1; then
        SUDO_CMD="sudo"
    fi
    echo "📦 Ensuring system packages (git, python3, python3-pil, python3-venv, ffmpeg, curl)..."
    $SUDO_CMD apt-get update -qq || true
    $SUDO_CMD apt-get install -y -qq git python3 python3-pil python3-venv ffmpeg curl || true
elif [ "$(uname -s)" = "Darwin" ]; then
    echo "🍏 Environment: macOS detected!"
    if command -v brew >/dev/null 2>&1; then
        echo "📦 Ensuring dependencies via Homebrew (ffmpeg, python)..."
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

# 3. Clean Stale Processes & Port Locks
echo "🔄 Clearing any existing processes on ports 8000/8001..."
pkill -f "web/server.py" 2>/dev/null || true
pkill -f "main.py" 2>/dev/null || true
pkill -f "app.py" 2>/dev/null || true
fuser -k 8000/tcp 2>/dev/null || true
fuser -k 8001/tcp 2>/dev/null || true

# 4. Clone or Auto-Update Repository
export GIT_TERMINAL_PROMPT=0

if [ "$TARGET_DIR" = "." ]; then
    echo "📂 Operating in-place within current repository directory."
    if [ -d ".git" ] && command -v git >/dev/null 2>&1; then
        echo "🔄 Checking for release updates via git..."
        if timeout 10 git fetch origin main >/dev/null 2>&1; then
            if git diff-index --quiet HEAD -- 2>/dev/null; then
                git pull --rebase origin main || true
            else
                echo "Notice: Local modifications detected. Keeping local changes."
            fi
        else
            echo "Notice: Remote fetch skipped (offline or prompt disabled)."
        fi
    fi
    # If a nested clone exists inside this repo, update it as well
    if [ -d "FBStoryMaker" ] && [ -f "FBStoryMaker/main.py" ]; then
        echo "Notice: Found nested clone 'FBStoryMaker'. Updating it as well..."
        (cd FBStoryMaker && timeout 10 git fetch origin main 2>/dev/null && git pull --rebase origin main 2>/dev/null || true)
    fi
elif [ -d "$TARGET_DIR" ]; then
    echo "📂 Directory '$TARGET_DIR' already exists. Auto-updating to v${APP_VERSION}..."
    cd "$TARGET_DIR"
    if [ -d ".git" ] && command -v git >/dev/null 2>&1; then
        echo "🔄 Pulling latest updates via git..."
        timeout 10 git fetch origin main >/dev/null 2>&1 || true
        git pull --rebase origin main 2>/dev/null || true
    fi
else
    echo "📥 Creating and cloning repository into '$TARGET_DIR'..."
    if command -v git >/dev/null 2>&1; then
        git clone "$REPO_URL" "$TARGET_DIR"
        cd "$TARGET_DIR"
    else
        echo "Notice: git not found, downloading repository archive..."
        mkdir -p "$TARGET_DIR"
        curl -fsSL "https://github.com/AllensCreations/FBStoryMaker/archive/refs/heads/main.tar.gz" | tar -xz -C "$TARGET_DIR" --strip-components=1
        cd "$TARGET_DIR"
    fi
fi

PROJECT_ABS_PATH="$(pwd)"

# 5. Write Current Version Metadata
echo "$APP_VERSION" > "$PROJECT_ABS_PATH/VERSION"
echo "$APP_VERSION" > "$PROJECT_ABS_PATH/.version"

# 6. Verify Pillow & Python Dependencies
echo "🔍 Checking Python dependencies..."
if ! $PYTHON_BIN -c "import PIL" >/dev/null 2>&1; then
    echo "Installing Pillow for Python..."
    if [ "$IS_TERMUX" -eq 1 ]; then
        pkg install -y python-pillow || true
    else
        $PYTHON_BIN -m pip install "Pillow>=10.0.0" || $PYTHON_BIN -m pip install "Pillow>=10.0.0" --break-system-packages || true
    fi
fi

# 7. Synchronize HTML Assets (ensuring parity across web/ and mobile)
echo "📑 Synchronizing web and mobile HTML interfaces..."
cp -f "$PROJECT_ABS_PATH/index.html" "$PROJECT_ABS_PATH/web/index.html" 2>/dev/null || true
cp -f "$PROJECT_ABS_PATH/index.html" "$PROJECT_ABS_PATH/AR.html" 2>/dev/null || true

# Sync to TrebEdit if installed on Android Termux
for trebedit_dir in "/storage/emulated/0/TrebEdit" "/sdcard/TrebEdit" "$HOME/storage/shared/TrebEdit"; do
    if [ -d "$trebedit_dir" ]; then
        echo "📱 Syncing HTML assets to TrebEdit workspace ($trebedit_dir)..."
        cp -f "$PROJECT_ABS_PATH/AR.html" "$trebedit_dir/" 2>/dev/null || true
        cp -f "$PROJECT_ABS_PATH/index.html" "$trebedit_dir/" 2>/dev/null || true
    fi
done

# 8. Create / Update Global CLI Launchers
echo "⚡ Setting up global 'fbsm' and 'fb-storymaker' launchers..."
LAUNCHER_SCRIPT="#!/usr/bin/env bash
# FB 2minutes Storymaker Launcher v${APP_VERSION}
exec $PYTHON_BIN \"$PROJECT_ABS_PATH/main.py\" \"\$@\"
"
TUI_LAUNCHER_SCRIPT="#!/usr/bin/env bash
# FB 2minutes Storymaker Terminal Launcher v${APP_VERSION}
if [ \"\$#\" -eq 0 ]; then
    set -- --tui
fi
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
    echo "✓ Global launcher ready: $LAUNCHER_PATH"

    TUI_LAUNCHER_PATH="$BIN_DIR/fbsm"
    echo "$TUI_LAUNCHER_SCRIPT" > "$TUI_LAUNCHER_PATH"
    chmod +x "$TUI_LAUNCHER_PATH"
    echo "✓ Terminal launcher ready: $TUI_LAUNCHER_PATH"
fi

echo ""
echo "========================================================"
echo "🎉 FB 2minutes Storymaker v${APP_VERSION} Ready!"
echo "========================================================"
echo "Location: $PROJECT_ABS_PATH"
echo "Version:  v${APP_VERSION}"
echo ""
echo "🚀 Quickstart Commands:"
echo "  1. Open selector menu:             fbsm"
echo "     (Use Up/Down and Enter; video rendering is in the Web Studio)"
echo ""
echo "  2. Launch Creative Studio Web UI:  fb-storymaker --web"
echo "     (Then open: http://localhost:8000)"
echo ""
echo "  3. Interactive Terminal UI:       fb-storymaker --tui"
echo "     (Open the selector menu directly)"
echo ""
echo "  4. Check Version & Options:        fb-storymaker --version"
echo ""
echo "Or run directly inside the project folder:"
if [ "$TARGET_DIR" != "." ]; then
    echo "  cd $TARGET_DIR"
fi
echo "  make web    # Web UI Studio"
echo "  make tui    # Termux Interactive Console"
echo "  make run    # App menu in a terminal; Web Studio otherwise"
echo "========================================================"
