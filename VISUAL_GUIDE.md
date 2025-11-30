# ComfyUI Visual Workflow Guide

## Node Overview

### Available Nodes (in "Face Extraction" category)

```
┌─────────────────────────────────────────────────┐
│  1. Load Reference Face                         │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│  Input:  IMAGE                                  │
│  Output: FACE_REFERENCE                         │
│                                                 │
│  Purpose: Set the face to match                 │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  2. Extract Matching Faces                      │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│  Inputs:  FACE_REFERENCE, IMAGE                 │
│  Outputs: IMAGE[], MASK[], STRING               │
│                                                 │
│  Parameters:                                    │
│  • similarity_threshold: 0.4 (slider 0-1)       │
│  • min_face_size: 64px                          │
│  • padding: 0.3 (30% extra)                     │
│  • device: cpu/cuda                             │
│                                                 │
│  Purpose: Extract from single/batch images      │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  3. Batch Extract from Video                    │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│  Input:  FACE_REFERENCE                         │
│  Outputs: IMAGE[], MASK[], STRING               │
│                                                 │
│  Parameters:                                    │
│  • video_path: "/path/to/video.mp4"             │
│  • similarity_threshold: 0.4                    │
│  • sample_every_n_frames: 1 (1-30)              │
│  • max_frames: 0 (0=all)                        │
│  • device: cpu/cuda                             │
│                                                 │
│  Purpose: Process entire videos                 │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  4. Save Extracted Faces                        │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│  Inputs:  IMAGE[], MASK[]                       │
│  Output:  STRING                                │
│                                                 │
│  Parameters:                                    │
│  • output_dir: "output/extracted"               │
│  • prefix: "face"                               │
│                                                 │
│  Purpose: Save faces and masks to disk          │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  5. Face Extraction Stats                       │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│  Inputs:  IMAGE[], STRING                       │
│  Output:  STRING                                │
│                                                 │
│  Purpose: Display extraction statistics         │
└─────────────────────────────────────────────────┘
```

## Workflow 1: Basic Image Extraction

### Visual Layout

```
┌──────────────┐
│  LoadImage   │  (reference.png)
│  Reference   │
└──────┬───────┘
       │
       v
┌──────────────────┐
│ Load Reference   │
│      Face        │
└──────┬───────────┘
       │
       │ FACE_REFERENCE
       v
┌──────────────┐     ┌──────────────────┐
│  LoadImage   │────>│  Extract         │
│   Input      │     │  Matching Faces  │
└──────────────┘     └────┬─────┬───────┘
                          │     │
                   IMAGE[]│     │MASK[]
                          v     v
                    ┌─────────────────┐
                    │  Save Extracted │
                    │     Faces       │
                    └─────────────────┘
                          │
                          v
                    output/faces/
                    output/masks/
```

### Step-by-Step

1. **Add LoadImage node**
   - Load your reference face image
   - This is the person you want to extract

2. **Add Load Reference Face node**
   - Connect LoadImage → Load Reference Face
   - This extracts the face embedding

3. **Add another LoadImage node**
   - Load the image(s) you want to extract faces from

4. **Add Extract Matching Faces node**
   - Connect Load Reference Face → reference input
   - Connect second LoadImage → input_image
   - Adjust threshold slider (0.4 is good start)
   - Choose device (cuda for speed)

5. **Add Save Extracted Faces node**
   - Connect faces output → faces input
   - Connect masks output → masks input
   - Set output_dir and prefix
   - This saves everything to disk

6. **Queue Prompt**
   - Click "Queue Prompt" button
   - Watch faces being extracted
   - Check output directory

## Workflow 2: Video Batch Extraction

### Visual Layout

```
┌──────────────┐
│  LoadImage   │  (reference.png)
│  Reference   │
└──────┬───────┘
       │
       v
┌──────────────────┐
│ Load Reference   │
│      Face        │
└──────┬───────────┘
       │
       │ FACE_REFERENCE
       v
┌──────────────────────┐
│  Batch Extract       │
│   from Video         │
│                      │
│  video_path:         │
│  "/path/video.mp4"   │
│  threshold: 0.4      │
│  sample_frames: 3    │
│  device: cuda        │
└────┬─────────┬───────┘
     │         │
     │IMAGE[]  │MASK[]
     v         v
┌─────────────────┐
│  Save Extracted │
│     Faces       │
└─────────────────┘
     │
     v
output/
├── faces/
└── masks/
```

### Step-by-Step

1. **Add LoadImage node**
   - Load reference face

2. **Add Load Reference Face node**
   - Connect LoadImage

3. **Add Batch Extract from Video node**
   - Connect Load Reference Face
   - Enter full video path
   - Set parameters:
     * threshold: 0.4 (adjust as needed)
     * sample_every_n_frames: 3 (faster)
     * max_frames: 0 (all frames)
     * device: cuda (if available)

4. **Add Save Extracted Faces node**
   - Connect faces and masks
   - Set output directory
   - Set prefix (e.g., "scene1")

5. **Optional: Add SaveImage node**
   - Connect faces output
   - Preview extracted faces in ComfyUI

6. **Queue Prompt**
   - Processing starts automatically
   - Check terminal for progress
   - Faces saved to output directory

## Parameter Tuning Visually

### Threshold Slider (Most Important!)

```
0.3         0.4         0.5         0.6         0.7
├───────────┼───────────┼───────────┼───────────┤
│           │           │           │           │
Lenient    DEFAULT    Balanced    Strict    Very Strict
(more      (start     (fewer      (high     (minimal
faces)     here)      wrong)      precision) matches)
```

**How to adjust**:
1. Start at 0.4
2. Run extraction
3. Check results:
   - Too many wrong faces? → Slide right (increase)
   - Missing correct faces? → Slide left (decrease)
4. Re-run with new threshold

### Frame Sampling Visual

```
Frame Sampling: 1 (Process ALL frames)
├─┬─┬─┬─┬─┬─┬─┬─┬─┬─┐
1 2 3 4 5 6 7 8 9 10
✓ ✓ ✓ ✓ ✓ ✓ ✓ ✓ ✓ ✓   Slowest, most thorough

Frame Sampling: 3 (Every 3rd frame)
├─┬─┬─┬─┬─┬─┬─┬─┬─┬─┐
1 2 3 4 5 6 7 8 9 10
✓ . . ✓ . . ✓ . . ✓   3x faster, good balance

Frame Sampling: 10 (Every 10th frame)
├─┬─┬─┬─┬─┬─┬─┬─┬─┬─┐
1 2 3 4 5 6 7 8 9 10
✓ . . . . . . . . .   10x faster, quick preview
```

## Common Node Connections

### Pattern 1: Single Reference, Multiple Inputs

```
        [Reference]
             |
    [Load Reference Face]
             |
     ┌───────┴───────┬───────┬───────┐
     v               v       v       v
[Extract #1]  [Extract #2] ... [Extract #N]
     |               |       |       |
     v               v       v       v
 [Save #1]      [Save #2] ... [Save #N]
```

Use for: Processing multiple images with same reference

### Pattern 2: Preview Before Save

```
[Reference] → [Load Ref] → [Extract] ──┬→ [SaveImage] (preview)
                                        │
                             [Input]────┘
                                        └→ [Save Faces] (disk)
```

Use for: Visual preview before committing to save

### Pattern 3: Statistics Tracking

```
[Reference] → [Load Ref] → [Extract] → [Stats] → [Print]
                               |
                          [Input]
```

Use for: Monitoring extraction performance

## Tips for Visual Workflow Building

### Tip 1: Use Reroute Nodes
```
[Reference] → [○] ──┬→ [Extract #1]
              Reroute├→ [Extract #2]
                     └→ [Extract #3]
```
Keep complex workflows clean

### Tip 2: Group Related Nodes
```
┌─────────────────────────────────┐
│  REFERENCE SETUP                │
│  ┌──────┐  ┌──────────┐        │
│  │ Load │→ │ Load Ref │        │
│  └──────┘  └──────────┘        │
└─────────────────────────────────┘
```
Use comments or spacing to organize

### Tip 3: Color Code Connections
- FACE_REFERENCE: One color
- IMAGE outputs: Another color
- MASK outputs: Another color

### Tip 4: Add Preview Nodes
Always add at least one SaveImage:
- Visual feedback
- Quick quality check
- See what's being extracted

## Workflow Templates

### Template 1: Single Image Quick Test
```
Nodes needed: 3
Time: 1 minute
Purpose: Test if reference works
```

### Template 2: Video Preview
```
Nodes needed: 4
Time: 2-3 minutes
Purpose: Quick preview of video footage
Settings: sample_every_n_frames=10, max_frames=500
```

### Template 3: Full Video Extraction
```
Nodes needed: 4
Time: 10-30 minutes per video
Purpose: Complete dataset extraction
Settings: sample_every_n_frames=3, device=cuda
```

### Template 4: Multi-Video Batch
```
Nodes needed: 5+
Time: Variable
Purpose: Process multiple videos
Pattern: One reference → Multiple video extractors
```

## Keyboard Shortcuts in ComfyUI

While building workflows:

- **Space**: Open node menu
- **Ctrl+Enter**: Queue prompt
- **Ctrl+Shift+Enter**: Queue prompt (front of queue)
- **Ctrl+C**: Copy selected nodes
- **Ctrl+V**: Paste nodes
- **Delete**: Delete selected nodes
- **Ctrl+Z**: Undo
- **Ctrl+Y**: Redo

## Saving Your Workflow

1. Build your workflow
2. Click "Save" button
3. Give it a name (e.g., "my_face_extraction.json")
4. Save to ComfyUI directory
5. Load anytime with "Load" button

## Sharing Workflows

To share with others:
1. Save workflow as JSON
2. Share the JSON file
3. Others load with "Load" button
4. All nodes reconnect automatically

---

**Quick Start**: Load `example_workflow.json` and start experimenting! 🎨
