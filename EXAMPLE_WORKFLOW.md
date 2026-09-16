# Example Workflow for FB 2minutes Storymaker

## Step 1: Prepare Your Assets

### Voice-Over
Place your narration audio file in `assets/voice-over/`:
```
assets/voice-over/
└── narration.mp3
```

### Scene Script
Create a text file with your scene descriptions in `assets/scripts/`:
```
assets/scripts/
└── story.txt
```

Example story.txt format:
```
[Scene 1: Introduction]
In a quiet village nestled between rolling hills, a young baker named Elsa begins her day before sunrise.

[Scene 2: Conflict]
But today, the magical yeast that makes her bread rise has gone missing from her pantry.

[Scene 3: Journey]
Elsa must venture into the Enchanted Forest to find the legendary Golden Yeast.

[Scene 4: Resolution]
With the Golden Yeast restored, Elsa bakes the most magnificent bread the village has ever seen.
```

### Visual Assets
Prepare a ZIP file with numbered illustrations in `assets/visuals/`:
```
assets/visuals/
└── story_visuals.zip
```

Inside the ZIP, name your files sequentially:
```
story_visuals.zip
├── 01.png    # Village sunrise
├── 02.png    # Empty pantry
├── 03.png    # Enchanted forest path
├── 04.png    # Golden yeast discovery
└── 05.png    # Village feast
```

## Step 2: Run the Storymaker

```bash
# Using the installed command
fb-storymaker

# Or directly with Python
python main.py
```

## Step 3: Find Your Output

Your completed story video will be in:
```
assets/output/
└── story_video.mp4
```

## Development Notes

As you implement each module:

1. **Speech-Cue Align Engine** (`src/align_engine/`):
   - Will analyze narration.mp3 for sentence breaks and breaths
   - Will read story.txt for semantic boundaries
   - Will output timing mappings for each scene

2. **Scene Duration Director** (`src/duration-director/`):
   - Will map each scene to its corresponding visual (01.png, 02.png, etc.)
   - Will allocate display time based on speech analysis

3. **Visual Choreography Core** (`src/choreography-core/`):
   - Will apply Gentle Spring Pop transitions between scenes
   - Will add subtle micro-movements to keep visuals engaging
   - Will compose frames with visuals in upper third, text in lower third

4. **Final Master Video Exporter** (`src/exporter/`):
   - Will assemble the processed visual sequence with audio
   - Will export as MP4 in 9:16 vertical format suitable for stories/reels
