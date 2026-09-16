# FB-2minutes Storymaker

An automated storytelling engine that creates storybook-style videos by synchronizing voice-over, scripts, and visual assets with "Picture-Book Motion" aesthetics.

## Architectural Overview

Based on the blueprint for an automated storytelling engine that replicates editorial behavior, pacing, and visual style without copying specific artistic assets.

### Core Philosophy: "Picture-Book Motion"
- **The Canvas is a Page**: Static background creates visual continuity while isolated character illustrations enter and exit
- **The Voice is the Conductor**: Visual cuts follow narrative pauses (breaths, sentence conclusions) rather than rigid BPM
- **Movement Serves Focus**: Subtle motion (micro-zooms, pans) draws attention to key elements

## System Pipeline

```
[Raw Voice-Over (.mp3)] [Scene Script (.txt)] [Ordered Visuals (.zip)]
           │                       │                       │
           └──────────────┬────────┘                       │
                          ▼                                │
           ┌─────────────────────────────┐                 │
           │   Speech-Cue Align Engine   │                 │
           │  • Sentence break detection │                 │
           │  • Pause & breath snapping  │                 │
           └──────────────┬──────────────┘                 │
                          ▼                                │
           ┌─────────────────────────────┐                 │
           │   Scene Duration Director   │◄────────────────┘
           │  • Maps Scene[N] -> Img[N]  │
           │  • Allocates start/end time │
           └──────────────┬──────────────┘
                          ▼
           ┌─────────────────────────────┐
           │   Visual Choreography Core  │
           │  • Pop-In / Page-Turn FX    │
           │  • Character micro-drift    │
           │  • Dynamic typography sync  │
           └──────────────┬──────────────┘
                          ▼
           ┌─────────────────────────────┐
           │   Final Master Video Exporter
           │   (9:16 Vertical Story)     │
           └─────────────────────────────┘
```

## Key Modules

### 1. Speech-Cue Align Engine
- Dynamically sets cut points based on speech analysis
- Silence & Breathing Snapper: Places cut markers in sentence pauses
- Script Verification: Ensures alignments match script boundaries

### 2. Visual Choreography Core
- **Scene Entrances**: 
  - Gentle Spring Pop (scale 90%→102%→100% over 250ms)
  - Cross-Dissolve Paper Cut (150ms opacity dissolve)
- **Subtle Life Micro-Drift**:
  - Slow Intentional Push (3-5% zoom over scene duration)
  - Breathing Drift (1-2 pixel oscillation)
- **Aspect Composition**: Centers artwork in upper third, reserves lower third for captions

### 3. Storybook Caption Engine
- Chunks sentences into 4-7 word semantic bites
- Clean, rounded serif or friendly sans-serif font
- High-contrast charcoal text on pure white canvas
- Centered alignment in lower third

## Project Structure
```
FB-2minutes-Storymaker/
├── src/
│   ├── align-engine/       # Speech-Cue Align Engine
│   ├── duration-director/  # Scene Duration Director
│   ├── choreography-core/  # Visual Choreography Core
│   └── exporter/           # Final Master Video Exporter
├── assets/
│   ├── voice-over/         # Input audio files (.mp3)
│   ├── scripts/            # Input scene scripts (.txt)
│   ├── visuals/            # Input visual assets (.zip, ordered)
│   └── output/             # Exported videos
├── docs/                   # Documentation
├── main.py                 # Application entry point
├── README.md
├── requirements.txt
├── setup.py
├── Makefile
└── EXAMPLE_WORKFLOW.md
```

## Getting Started

### Option 1: Run Directly (Recommended for Development)
```bash
# Clone the repository
git clone https://github.com/AllensCreations/FB-2minutes-Storymaker.git
cd FB-2minutes-Storymaker

# Run the application
python main.py
```

### Option 2: Using Makefile
```bash
# Install development dependencies
make dev

# Run the application
make run
```

### Option 3: Install as Command-Line Tool
```bash
# Install in development mode (allows code changes to take effect immediately)
pip install -e .

# Then run from anywhere
fb-storymaker
```

### Asset Preparation
See `EXAMPLE_WORKFLOW.md` for detailed guidance on preparing:
1. Voice-over narration (.mp3)
2. Scene script (.txt) 
3. Visual illustrations (.zip with numbered files)

Your exported story video will be saved to `assets/output/`.

## Development Commands

This project includes a Makefile with convenient development commands:

```bash
# Installation
make install     # Install package in production mode
make dev         # Install with development dependencies

# Testing
make test        # Run tests
make test-cov    # Run tests with coverage report

# Code Quality
make lint        # Run flake8 linting
make format      # Format code with black and isort

# Type Checking
make type-check  # Run mypy and pyright for static type analysis

# Running
make run         # Run the application
make help        # Show all available commands
```

## Development Setup

1. **Fork and clone** the repository
2. **Create a feature branch** for your work
3. **Install development dependencies**: `make dev`
4. **Implement your changes** in the appropriate `src/` module
5. **Run tests and type checking**: `make test` and `make type-check`
6. **Format your code**: `make format`
7. **Submit a pull request**

## Modules to Implement

As you work on implementing the architectural blueprint:

1. **src/align-engine/** - Speech-Cue Align Engine
   - Audio processing, sentence detection, timing alignment

2. **src/duration-director/** - Scene Duration Director
   - Scene-to-image mapping, duration calculation

3. **src/choreography-core/** - Visual Choreography Core
   - Transition effects, micro-movements, frame composition

4. **src/exporter/** - Final Master Video Exporter
   - Video assembly, encoding, output generation

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

Inspired by the Picture-Book Motion storytelling technique for creating engaging, storybook-style short-form videos.