# ComfyUI File Paths Guide

## 📁 Where Files Are Saved

### Output Location
All extracted faces are automatically saved to **ComfyUI's output folder**:

```
ComfyUI/
└── output/
    └── extracted_faces/        ← Your subfolder (customizable)
        ├── faces/              ← Extracted face images
        │   ├── face_000000.png
        │   ├── face_000001.png
        │   └── ...
        └── masks/              ← Face masks
            ├── face_mask_000000.png
            ├── face_mask_000001.png
            └── ...
```

**Actual path on your system**:
- Windows: `C:\Users\YourName\ComfyUI\output\extracted_faces\`
- Mac: `/Users/YourName/ComfyUI/output/extracted_faces/`
- Linux: `/home/username/ComfyUI/output/extracted_faces/`

---

## 🎛️ Save Node Parameters

### subfolder
- **Default**: "extracted_faces"
- **What it does**: Creates subfolder in ComfyUI/output/
- **Example**: "my_project" → ComfyUI/output/my_project/

### prefix
- **Default**: "face"
- **What it does**: Prefix for all saved files
- **Example**: "scene1" → scene1_000000.png, scene1_000001.png, etc.

---

## 📂 Example Folder Structure

### Single Extraction
```
ComfyUI/output/
└── extracted_faces/
    ├── faces/
    │   ├── face_000000.png
    │   ├── face_000001.png
    │   └── face_000002.png
    └── masks/
        ├── face_mask_000000.png
        ├── face_mask_000001.png
        └── face_mask_000002.png
```

### Multiple Extractions (Different Projects)
```
ComfyUI/output/
├── young_character/
│   ├── faces/
│   │   ├── young_000000.png
│   │   └── ...
│   └── masks/
│       └── ...
├── old_character/
│   ├── faces/
│   │   ├── old_000000.png
│   │   └── ...
│   └── masks/
│       └── ...
└── scene_1/
    ├── faces/
    │   ├── scene1_000000.png
    │   └── ...
    └── masks/
        └── ...
```

---

## 🔍 Finding Your Files

### Method 1: Through ComfyUI
1. After extraction, look at the SaveExtractedFaces node output
2. It will show: "Saved X faces to ComfyUI/output/subfolder_name"
3. Navigate to that folder in your file browser

### Method 2: Direct Access
1. Find your ComfyUI installation folder
2. Open the `output` subfolder
3. Look for your subfolder (default: `extracted_faces`)

### Method 3: Quick Access (Windows)
1. Press `Windows + R`
2. Type: `%USERPROFILE%\ComfyUI\output`
3. Press Enter

### Method 4: Quick Access (Mac/Linux)
```bash
# Open in Finder/File Manager
cd ~/ComfyUI/output
open .  # Mac
xdg-open .  # Linux
```

---

## 📋 Node Configuration Examples

### Example 1: Default Settings
```
Save Extracted Faces Node:
- subfolder: "extracted_faces"
- prefix: "face"

Result:
ComfyUI/output/extracted_faces/faces/face_000000.png
```

### Example 2: Custom Project
```
Save Extracted Faces Node:
- subfolder: "movie_deaging_project"
- prefix: "actor_young"

Result:
ComfyUI/output/movie_deaging_project/faces/actor_young_000000.png
```

### Example 3: Multiple Scenes
```
Scene 1 Node:
- subfolder: "scene_1"
- prefix: "s1"

Scene 2 Node:
- subfolder: "scene_2"
- prefix: "s2"

Result:
ComfyUI/output/scene_1/faces/s1_000000.png
ComfyUI/output/scene_2/faces/s2_000000.png
```

---

## 🎯 Best Practices

### Organization Tips
1. **Use descriptive subfolder names**
   - ✅ "actor_young_footage"
   - ✅ "destination_character"
   - ❌ "output1", "test"

2. **Use meaningful prefixes**
   - ✅ "scene1", "angle_front", "young"
   - ❌ "f", "x", "temp"

3. **Separate source and destination**
   ```
   ComfyUI/output/
   ├── src_young_character/    ← For training
   └── dst_old_character/       ← For training
   ```

4. **Archive completed projects**
   - Copy folders out of ComfyUI/output
   - Keep organized backup
   - Free up space for new projects

---

## 🔄 Integration with DeepFaceLab

### After Extraction

**Your faces are in**:
```
ComfyUI/output/extracted_faces/faces/
```

**Copy to DFL**:

**Windows**:
```cmd
xcopy "C:\Users\YourName\ComfyUI\output\extracted_faces\faces\*" "C:\DeepFaceLab\workspace\data_src\aligned\" /E /I
```

**Mac/Linux**:
```bash
cp ~/ComfyUI/output/extracted_faces/faces/* ~/DeepFaceLab/workspace/data_src/aligned/
```

### Complete Workflow
```
1. Extract young character:
   ComfyUI/output/young_character/faces/* 
   → DeepFaceLab/workspace/data_src/aligned/

2. Extract old character:
   ComfyUI/output/old_character/faces/*
   → DeepFaceLab/workspace/data_dst/aligned/

3. Start DFL training
```

---

## 🛠️ Troubleshooting

### "Can't find my files!"
**Check**:
1. Look at SaveExtractedFaces node output message
2. Navigate to ComfyUI/output folder
3. Check subfolder name matches what you entered
4. Files are in the `faces` subdirectory

### "Permission denied"
**Solution**:
- Run ComfyUI with proper permissions
- Check folder isn't open in another program
- Ensure disk has space

### "Output folder doesn't exist"
**Solution**:
- ComfyUI creates it automatically
- If missing, create: ComfyUI/output/ manually
- Restart ComfyUI

---

## 💡 Quick Reference

| What | Default Location |
|------|-----------------|
| **Extracted faces** | `ComfyUI/output/extracted_faces/faces/` |
| **Face masks** | `ComfyUI/output/extracted_faces/masks/` |
| **Custom subfolder** | `ComfyUI/output/YOUR_SUBFOLDER/` |
| **File naming** | `PREFIX_000000.png` (incremental) |

---

## 📝 Summary

✅ All files save to **ComfyUI/output/** automatically  
✅ Use **subfolder** parameter to organize projects  
✅ Use **prefix** parameter to name files  
✅ Files are always in **faces/** and **masks/** subdirectories  
✅ Ready for DeepFaceLab with simple copy command  

**No system paths needed - everything stays in ComfyUI!** 🎉
