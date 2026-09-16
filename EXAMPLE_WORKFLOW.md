# Example Workflow for FB 2minutes Storymaker

This guide explains how to prepare assets, run the storytelling engine, and preview your creations.

---

## Step 1: Prepare Your Assets

The pipeline expects 3 primary inputs in the `assets/` directory:

### 1. Voice-Over (`assets/voice-over/narration.mp3` or `.wav`)
Place your voice-over narration in `assets/voice-over/`:
```
assets/voice-over/
└── narration.mp3
```

### 2. Scene Script (`assets/scripts/story.txt`)
Create a text file with your scenes in `assets/scripts/`:
```
assets/scripts/
└── story.txt
```

Example `story.txt` format:
```text
[Scene 1: Introduction]
In a quiet village nestled between rolling hills, a young baker named Elsa begins her day before sunrise.

[Scene 2: The Problem]
But today, the magical yeast that makes her bread rise has gone missing from her pantry.

[Scene 3: The Journey]
Elsa must venture into the Enchanted Forest to find the legendary Golden Yeast.

[Scene 4: The Discovery]
Deep in the forest, she discovers the yeast guarded by a friendly forest spirit.

[Scene 5: The Return]
With the Golden Yeast restored, Elsa bakes the most magnificent bread the village has ever seen.

[Scene 6: Celebration]
The village celebrates with a feast, and Elsa's fame as the finest baker spreads throughout the land.
```

### 3. Visual Assets (`assets/visuals/story_visuals.zip`)
Prepare a ZIP file with sequentially numbered illustrations (PNG, JPG, or WebP):
```
assets/visuals/
└── story_visuals.zip
```

Inside the ZIP archive, name the files matching scene numbers:
```
story_visuals.zip
├── scene_1.png    # Village bakery sunrise
├── scene_2.png    # Empty yeast jar
├── scene_3.png    # Enchanted forest trail
├── scene_4.png    # Forest spirit discovery
├── scene_5.png    # Golden loaf
└── scene_6.png    # Village celebration feast
```

*(Tip: You can regenerate sample assets anytime using `make sample-assets` or `python3 main.py --generate-assets`)*

---

## Step 2: Run the Storymaker

### Option A: Via Command Line
```bash
# Run full rendering pipeline
make run
# or
python3 main.py
```

### Option B: Via Creative Studio Web UI
```bash
# Launch local Web Studio
make web
# or
python3 main.py --web
```
Open **http://localhost:8000** in your browser to inspect assets, preview storyboard cards, trigger rendering, and watch the video playback.

---

## Step 3: View & Export Your Master Video

The completed 9:16 vertical video will be exported to:
```
assets/output/
└── final_story.mp4
```

### Video Specifications:
- **Format**: H.264 / AAC MP4 (FastStart enabled)
- **Aspect Ratio**: 9:16 vertical (1080 &times; 1920)
- **Frame Rate**: 24 fps (customizable with `--fps`)
- **Aesthetics**: Picture-Book Motion (Spring-pop entrances, slow push micro-drift, dynamic narrative caption card)
