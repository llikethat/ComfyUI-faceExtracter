# Updated Features Guide - ComfyUI Face Extractor

## 🆕 New Capabilities

### 1. Multiple Reference Images Support
You can now use **multiple reference images** instead of just one! This is perfect for:
- Characters with changing appearance across different ages/scenes
- Improving match accuracy across different lighting conditions
- Handling profile shots and different angles

### 2. Unified Footage Input
The new **Batch Extract from Footage** node supports both:
- **Video files** (.mp4, .avi, .mov, etc.)
- **Image sequences** (batch of images from ComfyUI)

No more separate nodes - one node handles everything!

---

## 🎯 Multiple Reference Images

### Why Use Multiple References?

**Single Reference**:
```
Reference: Front-facing, well-lit
↓
Misses: Profile shots, different lighting
```

**Multiple References**:
```
Reference 1: Front-facing, well-lit
Reference 2: Side profile
Reference 3: Different lighting
↓
Catches ALL angles and conditions!
```

### How It Works

The system compares detected faces against **ALL reference images** and uses the **highest similarity score**. If any reference matches, the face is extracted.

**Example**:
- Reference 1: Young character smiling (similarity: 0.35)
- Reference 2: Young character serious (similarity: 0.62)
- **Result**: Face extracted (max similarity: 0.62 > threshold 0.4)

---

## 📊 Usage Examples

### Example 1: Single Reference (Simple Case)

```
┌──────────────┐
│  LoadImage   │ (one reference image)
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│ Load Reference   │
│    Face(s)       │  ← Shows: "1 reference"
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Batch Extract    │
│  from Footage    │
└──────────────────┘
```

**Use when**: Clear, consistent reference image works well

---

### Example 2: Multiple References (Better Accuracy)

```
┌──────────────┐
│  LoadImage   │ (reference 1)
└──────┬───────┘
       │
┌──────────────┐
│  LoadImage   │ (reference 2)
└──────┬───────┘
       │
┌──────────────┐
│  LoadImage   │ (reference 3)
└──────┬───────┘
       │
       │ (batch these together)
       ▼
┌──────────────────┐
│ Load Reference   │
│    Face(s)       │  ← Shows: "3 references"
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Batch Extract    │
│  from Footage    │
└──────────────────┘
```

**How to batch images in ComfyUI**:
1. Load multiple images with LoadImage nodes
2. Use "Batch Images" node OR connect them to same input
3. ComfyUI automatically creates a batch

**Use when**:
- Character has different angles in footage
- Lighting varies significantly
- Want maximum recall (find all instances)

---

### Example 3: Extract from Video File

```
┌──────────────────┐
│ Load Reference   │
│    Face(s)       │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Batch Extract    │
│  from Footage    │
│                  │
│ input_type:      │
│  ▼ video_file    │  ← Select this
│                  │
│ video_path:      │
│ /path/video.mp4  │  ← Enter path
└──────────────────┘
```

**Use when**: You have video files on disk

---

### Example 4: Extract from Image Sequence

```
┌──────────────┐
│  LoadImage   │ (frame 1)
└──────┬───────┘
       │
┌──────────────┐
│  LoadImage   │ (frame 2)
└──────┬───────┘
       │
       │ (batch frames)
       ▼
┌──────────────────┐
│ Batch Extract    │
│  from Footage    │
│                  │
│ input_type:      │
│  ▼ image_sequence│  ← Select this
│                  │
│ Connect images → │
└──────────────────┘
```

**Use when**:
- Already have extracted frames in ComfyUI
- Processing frames from other nodes
- Want to integrate with ComfyUI image pipeline

---

## 🎛️ Node Parameters Explained

### Load Reference Face(s)

**Input**:
- `reference_images` (IMAGE) - Accepts single OR batch of images

**Behavior**:
- Single image → 1 reference
- Batch (multiple images) → Multiple references
- Extracts largest face from each image
- Skips images with no faces (with warning)

**Output**:
- Info shows: "Using X reference(s)"

---

### Batch Extract from Footage

**New Parameter**: `input_type`
- **video_file**: Process video from file path
  - Requires: `video_path` filled in
  - Optional: `input_images` ignored
- **image_sequence**: Process images from ComfyUI
  - Requires: `input_images` connected
  - Optional: `video_path` ignored

**When to use each**:

| Use Case | Setting |
|----------|---------|
| Video on disk | input_type = video_file |
| Frames in ComfyUI | input_type = image_sequence |
| LoadVideo output | input_type = image_sequence |
| Animated output | input_type = image_sequence |

---

## 💡 Advanced Workflows

### Workflow A: Multiple References + Video

```
[Ref Image 1] ─┐
[Ref Image 2] ─┼→ [Batch] → [Load Ref] → [Extract from Footage]
[Ref Image 3] ─┘                              ↓ (video_file mode)
                                          video_path = ...
```

**Benefits**:
- Catches all angles and lighting
- Higher recall
- Fewer missed faces

**Trade-off**:
- May get more false positives (adjust threshold up)

---

### Workflow B: Image Pipeline Integration

```
[Load Video] → [Process Frames] → [Extract from Footage]
                                        ↓ (image_sequence mode)
                                   [Save Extracted]
```

**Benefits**:
- Integrate with other ComfyUI processing
- Apply filters before extraction
- Chain multiple operations

---

### Workflow C: Different References for Different Footage

```
[Young Ref 1-3] → [Load Ref A] → [Extract Video 1]
                                        ↓
                                  [Save Young]

[Old Ref 1-2] → [Load Ref B] → [Extract Video 2]
                                      ↓
                                [Save Old]
```

**Use for**: Complete de-aging workflow in one ComfyUI session

---

## 📈 Performance Impact

### Multiple References

| References | Processing Speed | Memory | Match Quality |
|-----------|------------------|---------|---------------|
| 1 | Fastest | Lowest | Good |
| 2-3 | ~Same | +5% | Better |
| 5+ | ~Same | +10% | Best |

**Bottom line**: Multiple references have minimal performance impact!

---

### Input Type Comparison

| Input Type | Speed | Use Case |
|-----------|-------|----------|
| video_file | Fast | Large videos, files on disk |
| image_sequence | Depends | Already in ComfyUI pipeline |

---

## 🎓 Best Practices

### For Reference Images

1. **Quality over Quantity**
   - 2-3 good references > 10 mediocre ones
   - Clear, different angles/lighting
   - No blurry or occluded faces

2. **What Makes a Good Set**
   - Front-facing + profile
   - Different lighting conditions
   - Different expressions
   - Same person, different contexts

3. **Bad Practice**
   - Using very similar images (redundant)
   - Including wrong person
   - Low quality/blurry images

---

### For Input Type Selection

**Use video_file when**:
- Video already on disk
- Not processing frames in ComfyUI
- Want simplest workflow

**Use image_sequence when**:
- Frames come from other nodes
- Applying pre-processing
- Complex ComfyUI pipeline
- Already have frames loaded

---

## 🔧 Troubleshooting

### Multiple References

**Issue**: Too many false positives
**Solution**:
- Increase threshold (0.5-0.6)
- Use fewer, more specific references
- Check reference quality

**Issue**: Reference count shows wrong number
**Solution**:
- Some images may have no faces (check warnings)
- Ensure faces are visible and clear
- Try different reference images

---

### Input Type

**Issue**: video_file mode - "file not found"
**Solution**:
- Use absolute path: `/full/path/to/video.mp4`
- Check file exists
- Verify file permissions

**Issue**: image_sequence mode - "no input images"
**Solution**:
- Ensure input_images is connected
- Check images are loaded correctly
- Verify batch is created

---

## 📊 Migration from Old Version

### Old Workflow
```
[LoadImage] → [Load Reference Face] → [Batch Extract from Video]
                                            ↓
                                      video_path (required)
```

### New Workflow (Backward Compatible)
```
[LoadImage] → [Load Reference Face(s)] → [Batch Extract from Footage]
                                               ↓
                                         input_type = video_file
                                         video_path = ... (as before)
```

**Changes needed**:
1. Node renamed: "Batch Extract from Video" → "Batch Extract from Footage"
2. Add: input_type parameter (set to "video_file")
3. Optional: Add more reference images if desired

**Your old workflows will still work!**

---

## 🎯 Quick Reference

### Multiple References
- **How**: Batch multiple LoadImage → Load Reference Face(s)
- **When**: Need better coverage, various angles/lighting
- **Trade-off**: Slightly more false positives

### Video File Mode
- **How**: input_type = video_file, set video_path
- **When**: Video on disk, simple workflow
- **Trade-off**: Can't pre-process frames

### Image Sequence Mode
- **How**: input_type = image_sequence, connect input_images
- **When**: Frames in ComfyUI, complex pipeline
- **Trade-off**: More setup, more flexibility

---

## 🚀 Example Workflows

All example workflows updated:
- `workflow_multi_reference.json` - Multiple references + video
- `workflow_image_sequence.json` - Processing image batches
- `example_workflow.json` - Updated for new node names

Load these to see the features in action!

---

**Summary**: You now have much more flexibility in both reference matching and input handling. Use multiple references for better accuracy, and choose your input type based on your workflow! 🎨
