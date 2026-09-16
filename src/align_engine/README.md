# Speech-Cue Align Engine

This module implements the **Speech-Cue Align Engine** component of the FB 2minutes Storymaker pipeline, responsible for analyzing voice-over audio and aligning it with scene scripts to determine optimal cut points for visual transitions.

## Functionality

The Speech-Cue Align Engine performs two main tasks:

### 1. Audio Analysis
- Detects speech segments and silent pauses in voice-over audio
- Uses volume envelope analysis to identify sentence boundaries and breaths
- Configurable minimum silence duration for what constitutes a "break"

### 2. Speech-Script Alignment
- Parses scene scripts into individual segments (sentences/phrases)
- Aligns detected speech segments with script segments
- Creates a mapping between scene indices and timed speech segments
- Exports alignment data for use by downstream modules

## Key Features

- **Silence & Breathing Snapper**: Places cut markers in the center of detected silences >250ms
- **Script Verification**: Uses text script to confirm sentence boundaries, preventing awkward cuts
- **Confidence Scoring**: Provides confidence levels for each alignment
- **Flexible Input**: Works with various audio formats (placeholder for actual implementation)
- **Simple Export**: Outputs alignment data in human-readable text format

## Implementation Details

### Core Classes

#### `SpeechCueAlignEngine`
Main engine class that coordinates audio analysis and script alignment.

##### Methods:
- `analyze_audio(audio_path)`: Detects speech segments in audio file
- `parse_script(script_path)`: Parses script file into segments
- `align_speech_with_script(audio_path, script_path)`: Performs the full alignment
- `export_alignment(result, output_path)`: Exports results for downstream use

#### Data Classes
- `SpeechSegment`: Represents a timed segment of speech with text and confidence
- `AlignmentResult`: Contains all aligned segments, scene mapping, and total duration

## Usage

### As a Module
```python
from src.align-engine.align_engine import SpeechCueAlignEngine

engine = SpeechCueAlignEngine(min_silence_duration=0.25)
result = engine.align_speech_with_script(
    audio_path=Path("assets/voice-over/narration.mp3"),
    script_path=Path("assets/scripts/story.txt")
)

# Access results
for i, segment in enumerate(result.segments):
    print(f"Scene {i}: {segment.text} ({segment.start_time:.2f}s-{segment.end_time:.2f}s)")

# Export for next stage
engine.export_alignment(result, "assets/processed/alignment.txt")
```

### Command Line Interface
```bash
python -m src.align-engine.align_engine \
    --audio assets/voice-over/narration.mp3 \
    --script assets/scripts/story.txt \
    --output assets/processed/alignment.txt
```

## Integration with Pipeline

This module is the **first stage** in the FB 2minutes Storymaker pipeline:

```
[Raw Voice-Over (.mp3)] + [Scene Script (.txt)]
                           │
                           ▼
               Speech-Cue Align Engine  ◄────┐
                           │                 │
                           ▼                 │
               [Aligned Speech Segments]     │
                           │                 │
                           ▼                 │
               Scene Duration Director ──────┘
                           │
                           ▼
                    [Scene-to-Image Mapping]
                           │
                           ▼
                  Visual Choreography Core
                           │
                           ▼
               [Processed Visual Sequence]
                           │
                           ▼
                Final Master Video Exporter
                           │
                           ▼
                  [Output Video File]
```

## Dependencies

Currently implemented as a standalone module with no external dependencies.
For production implementation, would require:
- Audio processing: `librosa`, `numpy`, `scipy`
- Optional: `pydub` for audio format handling
- Optional: `whisper` or `Vosk` for speech-to-text alignment verification

## Future Enhancements

1. **Actual Audio Processing**: Replace placeholder with real audio analysis using librosa
2. **Advanced Alignment**: Implement forced alignment or dynamic time warping for better accuracy
3. **Multiple Export Formats**: Support JSON, YAML, or binary formats for alignment data
4. **Visualization Tools**: Add ability to plot audio waveform with detected segments
5. **Error Handling**: Improve validation and error reporting for malformed inputs
6. **Performance Optimization**: Cache audio analysis results for faster reprocessing