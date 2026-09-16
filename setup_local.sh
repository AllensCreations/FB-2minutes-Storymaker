#!/usr/bin/env bash
# ==============================================================================
# FB 2minutes Storymaker - Local Setup Script
# Sets up Python virtual environment, dependencies, FFmpeg check, and sample assets.
# ==============================================================================

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_DIR"

echo "========================================================"
echo "🎬 Setting up FB 2minutes Storymaker Environment"
echo "========================================================"

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
    if [ -f /etc/debian_version ] && [ "$(id -u)" -eq 0 ]; then
        echo "Installing FFmpeg via apt..."
        apt-get update -qq && apt-get install -y -qq ffmpeg
        echo "✓ FFmpeg installed successfully."
    else
        echo "Please install FFmpeg:"
        echo "  - Ubuntu/Debian: sudo apt update && sudo apt install -y ffmpeg"
        echo "  - macOS:         brew install ffmpeg"
        echo "  - Windows:       winget install Gyan.FFmpeg or choco install ffmpeg"
    fi
fi

# 3. Setup Virtual Environment
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

# 4. Install Dependencies
echo "Installing Python dependencies from requirements.txt..."
$PIP_CMD install -r requirements.txt || {
    echo "Falling back to installing Pillow..."
    $PIP_CMD install "Pillow>=10.0.0" || true
}

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
