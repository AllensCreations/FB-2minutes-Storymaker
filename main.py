"""
FB 2minutes Storymaker - Automated Storytelling Engine
Based on the architectural blueprint for "Picture-Book Motion" storytelling videos.
"""

import os
import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

def main():
    print("FB 2minutes Storymaker - Automated Storytelling Engine")
    print("=" * 55)
    print("Architecture: Picture-Book Motion")
    print("Components:")
    print("  1. Speech-Cue Align Engine")
    print("  2. Scene Duration Director")
    print("  3. Visual Choreography Core")
    print("  4. Final Master Video Exporter")
    print("\nWorkflow:")
    print("  [Voice-Over] + [Script] + [Visuals] → Align → Duration → Choreography → Export")
    print("\nTo get started:")
    print("  1. Place voice-over (.mp3) in assets/voice-over/")
    print("  2. Place scene script (.txt) in assets/scripts/")
    print("  3. Place ordered visuals (.zip) in assets/visuals/")
    print("  4. Run: python main.py")

if __name__ == "__main__":
    main()
