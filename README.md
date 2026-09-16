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
└── main.py                 # Application entry point
```

## Getting Started

1. Clone this repository
2. Prepare your assets:
   - Place voice-over narration in `assets/voice-over/` (.mp3)
   - Place scene script in `assets/scripts/` (.txt)
   - Place ordered visual illustrations in `assets/visuals/` (.zip with numbered files)
3. Run the application: `python main.py`
4. Find your exported story video in `assets/output/`

## Development

This project is structured as a Python package with modular components. Each module in `src/` corresponds to a major component of the architectural pipeline.

To contribute:
1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Submit a pull request