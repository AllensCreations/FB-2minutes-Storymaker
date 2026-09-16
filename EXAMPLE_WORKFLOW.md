# End-to-End Workflow: FB 2minutes Storymaker

This practical, end-to-end sample workflow illustrates exactly how assets move through the system from raw files to the final exported storytelling video.

---

## Phase 1: Asset Preparation & Ingestion

### 1. Script Preparation (`script.txt`)
Write the narration broken down into single sentence beats. Each line represents one distinct visual scene:
```text
Line 1: A young girl named Scout grows up in a quiet southern town.
Line 2: She spends her days exploring with her older brother Jem.
Line 3: But the town hides a dark secret behind closed doors.
Line 4: An innocent man is accused of a crime he did not commit.
```

### 2. Voice-Over Recording (`narration.mp3` or `.wav`)
- Record the audio reading the script naturally, leaving a distinct **0.3s to 0.5s pause** between sentences.
- Total length example: **24.0 seconds**.

### 3. Visual Asset Packaging (`scenes.zip` or individual images)
Export illustrations on clean/white backgrounds and name them in matching order:
- `01_scout_intro.png`
- `02_scout_and_jem.png`
- `03_shadowy_house.png`
- `04_courtroom_accusal.png`

---

## Phase 2: Automated Analysis & Timing Alignment

Once you drop the three files into the app (or click **"✨ Load Scout & Jem Sample Story"**), the engine runs the following steps automatically:

### Step A: Silence Detection
The engine reads the waveform and spots natural breathing gaps where volume drops below **-35dB**:
- **Gap 1 found at**: `5.4s`
- **Gap 2 found at**: `11.8s`
- **Gap 3 found at**: `17.2s`
- **Audio ends at**: `24.0s`

### Step B: Scene Mapping Matrix
The engine pairs line count, image count, and detected timestamps:

| Scene | Image Asset | Narration Line | Start Time | End Time | Duration |
|:---:|:---|:---|:---:|:---:|:---:|
| **01** | `01_scout_intro.png` | *"A young girl named Scout grows up..."* | 0.0s | 5.4s | 5.4s |
| **02** | `02_scout_and_jem.png` | *"She spends her days exploring with..."* | 5.4s | 11.8s | 6.4s |
| **03** | `03_shadowy_house.png` | *"But the town hides a dark secret..."* | 11.8s | 17.2s | 5.4s |
| **04** | `04_courtroom_accusal.png` | *"An innocent man is accused of a crime..."* | 17.2s | 24.0s | 6.8s |

---

## Phase 3: Visual Choreography & Styling Engine

For every scene block, the system automatically assigns motion and typographic rules:

- **Scene 01 Choreography:**
  - **Entrance:** Gentle pop-in scale ($0.94 \to 1.0$) over the first 300ms.
  - **Continuous Motion:** Subtle camera push-in (+4% zoom) toward the character's face.
  - **Captions:** Clean charcoal text rendered in the lower third, broken into two readable phrases:
    - *Beat A:* *"A young girl named Scout"*
    - *Beat B:* *"grows up in a quiet southern town."*

- **Scene 02 Choreography:**
  - **Entrance:** Soft 150ms opacity dissolve.
  - **Continuous Motion:** Gentle horizontal pan across both characters (+30px slide).
  - **Captions:** Text updates automatically at the midpoint of the scene.

- **Scene 03 Choreography:**
  - **Entrance:** Slight zoom pop-in to signal a tonal shift.
  - **Continuous Motion:** Handheld subtle float (slight breathing sway).

---

## Phase 4: Review & One-Click Master Export

1. **Timeline Scrub:** Hit **Play** in the browser to preview the synchronization. If Scene 3 needs to cut half a second earlier, drag its cut marker on the interactive waveform.
2. **Export Trigger:** Click **Export Master Video**.
3. **Internal Processing:** The browser captures the 30 FPS canvas rendering and mixes it directly with the narration audio buffer.
4. **Final Delivery:** The video encodes and downloads to your device as a vertical 1080&times;1920 video ready for upload.
