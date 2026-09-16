#!/usr/bin/env bash
# ==============================================================================
# FB 2minutes Storymaker - Local Setup Script
# Sets up Python environment, dependencies, FFmpeg check, and sample assets.
# Includes first-class support for Termux (Android), Debian/Ubuntu, macOS, Windows.
# ==============================================================================

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_DIR"

echo "========================================================"
echo "🎬 Setting up FB 2minutes Storymaker Environment"
echo "========================================================"

# 0. Check for Termux (Android)
IS_TERMUX=0
if [ -n "$TERMUX_VERSION" ] || (command -v pkg >/dev/null 2>&1 && [ -n "$PREFIX" ]); then
    IS_TERMUX=1
    echo "📱 Termux (Android) environment detected!"
    echo "Installing Termux pre-compiled packages (python-pillow, ffmpeg)..."
    pkg install -y python-pillow ffmpeg || true
fi

# 1. Check Python
echo -n "Checking Python 3... "
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    echo "❌ Python 3 was not found. Please install Python 3.8+."
    exit 1
fi
PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✓ Found Python $PYTHON_VERSION ($PYTHON_CMD)"

# 2. Check FFmpeg
echo -n "Checking FFmpeg... "
if command -v ffmpeg >/dev/null 2>&1; then
    FFMPEG_VER=$(ffmpeg -version 2>&1 | head -n1)
    echo "✓ Found ($FFMPEG_VER)"
else
    echo "⚠️  FFmpeg is not installed!"
    echo "FFmpeg is required to export video and encode audio."
    if [ "$IS_TERMUX" -eq 1 ]; then
        echo "Installing FFmpeg via pkg..."
        pkg install -y ffmpeg || true
    elif [ -f /etc/debian_version ] && [ "$(id -u)" -eq 0 ]; then
        echo "Installing FFmpeg via apt..."
        apt-get update -qq && apt-get install -y -qq ffmpeg
        echo "✓ FFmpeg installed successfully."
    else
        echo "Please install FFmpeg:"
        echo "  - Termux (Android): pkg install -y ffmpeg"
        echo "  - Ubuntu/Debian:    sudo apt update && sudo apt install -y ffmpeg"
        echo "  - macOS:            brew install ffmpeg"
        echo "  - Windows:          winget install Gyan.FFmpeg or choco install ffmpeg"
    fi
fi

# 3. Setup Virtual Environment (optional on Termux)
if [ "$IS_TERMUX" -eq 1 ]; then
    echo "Using Termux Python environment directly to utilize system-installed python-pillow..."
    RUN_PYTHON="$PYTHON_CMD"
    PIP_CMD="$PYTHON_CMD -m pip"
else
    if [ -z "$VIRTUAL_ENV" ]; then
        if [ ! -d ".venv" ]; then
            echo "Creating Python virtual environment (.venv)..."
            $PYTHON_CMD -m venv .venv || true
        fi

        if [ -f ".venv/bin/activate" ]; then
            echo "Activating virtual environment (.venv)..."
            # shellcheck disable=SC1091
            source .venv/bin/activate
            PIP_CMD="pip"
            RUN_PYTHON=".venv/bin/python"
        else
            echo "Using system Python environment..."
            PIP_CMD="$PYTHON_CMD -m pip"
            RUN_PYTHON="$PYTHON_CMD"
        fi
    else
        echo "Using existing active virtual environment: $VIRTUAL_ENV"
        PIP_CMD="pip"
        RUN_PYTHON="python"
    fi
fi

# 4. Check & Install Pillow
echo -n "Checking Pillow (PIL)... "
if $RUN_PYTHON -c "import PIL" >/dev/null 2>&1; then
    echo "✓ Pillow is installed."
else
    echo "⚠️ Pillow not detected."
    if [ "$IS_TERMUX" -eq 1 ]; then
        echo "Installing python-pillow via pkg..."
        pkg install -y python-pillow || true
    else
        echo "Installing Pillow via pip..."
        $PIP_CMD install "Pillow>=10.0.0" || $PIP_CMD install "Pillow>=10.0.0" --break-system-packages || true
    fi
fi

# 5. Generate Sample Assets
echo "Ensuring sample story assets exist..."
$RUN_PYTHON scripts/generate_sample_assets.py

echo ""
echo "========================================================"
echo "🎉 Setup complete! You are ready to create stories."
echo "========================================================"
echo ""
echo "Quick Commands:"
echo "  1. Run Storymaker via CLI:  make run   (or $RUN_PYTHON main.py)"
echo "  2. Launch Web UI Studio:    make web   (or $RUN_PYTHON main.py --web)"
echo "  3. Run Test Suite:          make test"
echo ""
