# FB-2minutes Storymaker

An automated storytelling engine that creates storybook-style videos by synchronizing voice-over, scripts, and visual assets with "Picture-Book Motion" aesthetics.

## 🎬 Overview

This project implements the architectural blueprint for an automated storytelling engine that replicates the editorial behavior, pacing, and visual style of storybook-style videos without copying specific artistic assets.

### Core Philosophy: "Picture-Book Motion"
- **The Canvas is a Page**: Static background creates visual continuity while isolated character illustrations enter and exit
- **The Voice is the Conductor**: Visual cuts follow narrative pauses (breaths, sentence conclusions) rather than rigid BPM
- **Movement Serves Focus**: Subtle motion (micro-zooms, pans) draws attention to key elements

## ✅ Current Implementation Status

### Working Components:
- **Speech-Cue Align Engine** (`src/align_engine/`) - **IMPLEMENTED & TESTED**
  - Audio analysis and script alignment
  - Sentence break detection and pause snapping
  - Speech-script alignment with confidence scoring
  - Export functionality for downstream modules

### Ready for Implementation:
- **Scene Duration Director** (`src/duration_director/`) - Structure ready
- **Visual Choreography Core** (`src/choreography_core/`) - Structure ready  
- **Final Master Video Exporter** (`src/exporter/`) - Structure ready

## 📁 Project Structure
```
FB-2minutes-Storymaker/
├── src/
│   ├── align_engine/           # ✅ Speech-Cue Align Engine (IMPLEMENTED)
│   │   ├── align_engine.py     # Main implementation
│   │   └── README.md           # Component documentation
│   ├── duration_director/      # 🔲 Scene Duration Director
│   ├── choreography_core/      # 🔲 Visual Choreography Core
│   └── exporter/               # 🔲 Final Master Video Exporter
├── assets/
│   ├── voice-over/             # 📁 Input audio files (.mp3)
│   │   └── narration.mp3       # ✅ Sample voice-over
│   ├── scripts/                # 📁 Input scene scripts (.txt)
│   │   └── story.txt           # ✅ Sample script
│   ├── visuals/                # 📁 Input visual assets (.zip, ordered)
│   │   └── story_visuals.zip   # ✅ Sample visuals ZIP
│   └── output/                 # 📁 Exported videos (empty)
├── docs/                       # 📖 Documentation
├── main.py                     # ▶️ Application entry point
├── README.md                   # 📄 This file
├── requirements.txt            # 📦 Python dependencies
├── setup.py                    # 📦 Package installation
├── Makefile                    # ⚙️ Development commands
└── EXAMPLE_WORKFLOW.md         # 📖 Detailed asset preparation guide
```

## 🚀 Getting Started

### Option 1: Run Directly (Recommended)
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

## 🔧 How It Works

### 1. Check Asset Status
Run `python main.py` to see if your assets are ready:
```
Asset Status:
  Voice-over (.mp3): ✓ Found
  Scene Script (.txt): ✓ Found
  Visual Assets (.zip): ✓ Found

🚀 All assets detected! Ready to process.
   (Implementation pending - this is the scaffold)
```

### 2. Test the Speech-Cue Align Engine
The first implemented module can be tested directly:
```bash
python -m src.align_engine.align_engine \
    --audio assets/voice-over/narration.mp3 \
    --script assets/scripts/story.txt \
    --output assets/processed/alignment.txt
```

This will:
- Analyze the audio for speech segments and pauses
- Parse the script into segments
- Align speech with script segments
- Export the alignment results

### 3. View Results
Check the generated alignment file:
```bash
cat assets/processed/alignment.txt
```

Sample output:
```
# FB 2minutes Storymaker - Speech Alignment Export
# Total Duration: 21.00 seconds
# Number of Segments: 5

Scene 0:
  Time: 0.00s - 3.20s
  Text: [Scene 1: Introduction]
  Confidence: 0.80

Scene 1:
  Time: 3.70s - 7.10s
  Text: In a quiet village nestled between rolling hills, a young baker named Elsa begins her day before sunrise
  Confidence: 0.80
```

## 📦 Development Setup

### Installation
```bash
# Install in development mode
make install          # Production dependencies only
make dev              # With development dependencies
```

### Development Commands
```bash
make test             # Run tests (when implemented)
make test-cov         # Run tests with coverage
make lint             # Run flake8 linting
make format           # Format code with black and isort
make type-check       # Run mypy and pyright for static type analysis
make run              # Run the application
make help             # Show all available commands
```

### Asset Preparation
See `EXAMPLE_WORKFLOW.md` for detailed guidance on preparing:
1. Voice-over narration (.mp3)
2. Scene script (.txt) 
3. Visual illustrations (.zip with numbered files)

Your exported story video will be saved to `assets/output/`.

## 🔄 Implementation Roadmap

As you work on implementing the architectural blueprint:

1. **src/align_engine/** - Speech-Cue Align Engine ✅ **COMPLETED**
   - Audio processing, sentence detection, timing alignment

2. **src/duration_director/** - Scene Duration Director 🔲
   - Scene-to-image mapping, duration calculation

3. **src/choreography_core/** - Visual Choreography Core 🔲
   - Transition effects (Gentle Spring Pop, Cross-Dissolve Paper Cut)
   - Subtle life micro-drift (slow push-in, breathing drift)
   - Aspect composition (upper third for visuals, lower third for captions)

4. **src/exporter/** - Final Master Video Exporter 🔲
   - Video assembly, encoding, output generation (9:16 vertical story)

## 📚 Dependencies

### Runtime Dependencies
Add to `requirements.txt` as modules are implemented:
- Audio processing: `librosa>=0.10.0`, `numpy>=1.24.0`
- Video processing: `opencv-python>=4.8.0`, `moviepy>=1.0.0`, `Pillow>=10.0.0`
- Document processing: `python-docx>=1.1.0`

### Development Dependencies (included in `make dev`)
- Type checking: `mypy>=1.0.0`, `pyright>=1.1.0`
- Testing: `pytest>=7.0.0`, `pytest-cov>=4.0.0`
- Code quality: `black>=23.0.0`, `flake8>=6.0.0`, `isort>=5.12.0`

## 📖 Example Workflow

See `EXAMPLE_WORKFLOW.md` for a complete walkthrough of:
1. Preparing your assets (voice-over, script, visuals)
2. Running the alignment engine
3. Implementing subsequent modules
4. Generating your final story video

## 🛠️ Troubleshooting

### Common Issues
- **"Visual Assets (.zip): ✗ Missing"**: Ensure you have a .zip file in `assets/visuals/`
- **Import errors**: Make sure you're running from the project root directory
- **Permission issues**: Use `chmod +x` on scripts if needed

### Getting Help
- Check the console output for specific error messages
- Refer to `EXAMPLE_WORKFLOW.md` for detailed asset preparation
- Each module has its own README in `src/*/README.md`

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

Inspired by the Picture-Book Motion storytelling technique for creating engaging, storybook-style short-form videos.

---
*Built with ❤️ for creators who want to automate their storytelling workflow.*