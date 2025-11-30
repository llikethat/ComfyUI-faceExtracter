# Installation Guide - ComfyUI Face Extractor

## Prerequisites

- ComfyUI installed and working
- Python 3.9 or higher
- (Optional but recommended) NVIDIA GPU with CUDA for 10-30x speedup

## Installation Methods

### Method 1: Direct Installation (Recommended)

```bash
# Navigate to ComfyUI custom nodes directory
cd /path/to/ComfyUI/custom_nodes/

# Clone or copy this repository
git clone <repository-url> ComfyUI_FaceExtractor
# OR manually create the directory and copy files

cd ComfyUI_FaceExtractor

# Install dependencies
pip install -r requirements.txt

# For GPU support (optional, much faster)
pip install onnxruntime-gpu
```

### Method 2: Manual Installation

1. **Create Directory**
   ```bash
   mkdir -p /path/to/ComfyUI/custom_nodes/ComfyUI_FaceExtractor
   ```

2. **Copy Files**
   Copy these files to the directory:
   - `__init__.py`
   - `face_extractor_nodes.py`
   - `requirements.txt`
   - `README.md`
   - `example_workflow.json`
   - `workflow_video_extraction.json`

3. **Install Dependencies**
   ```bash
   cd /path/to/ComfyUI/custom_nodes/ComfyUI_FaceExtractor
   pip install insightface onnxruntime opencv-python numpy
   ```

## Verification

### 1. Restart ComfyUI

After installation, restart ComfyUI completely:
```bash
# Stop ComfyUI
# Then start again
python main.py
```

### 2. Check Node Menu

In ComfyUI:
1. Right-click on canvas
2. Look for **"Face Extraction"** category
3. Should see 5 nodes:
   - Load Reference Face
   - Extract Matching Faces
   - Batch Extract from Video
   - Save Extracted Faces
   - Face Extraction Stats

### 3. Load Example Workflow

1. In ComfyUI, click "Load" button
2. Navigate to `ComfyUI/custom_nodes/ComfyUI_FaceExtractor/`
3. Load `example_workflow.json`
4. You should see the complete workflow

## Troubleshooting Installation

### "No module named 'insightface'"

**Solution**:
```bash
pip install insightface onnxruntime
```

### "Cannot import name 'FaceAnalysis'"

**Solution**: InsightFace installation incomplete
```bash
pip uninstall insightface
pip install insightface --no-cache-dir
```

### Nodes Don't Appear in Menu

**Solution 1**: Check __init__.py exists
```bash
ls /path/to/ComfyUI/custom_nodes/ComfyUI_FaceExtractor/__init__.py
```

**Solution 2**: Check for Python errors
```bash
# Check ComfyUI terminal for error messages
# Look for import errors or syntax errors
```

**Solution 3**: Restart ComfyUI completely
```bash
# Kill all ComfyUI processes
# Start fresh
```

### "CUDA not available" (want GPU)

**Solution**:
```bash
# Install GPU version of ONNX Runtime
pip uninstall onnxruntime
pip install onnxruntime-gpu

# Verify CUDA installation
python -c "import torch; print(torch.cuda.is_available())"
```

### Import Errors

If you see:
```
ImportError: DLL load failed while importing cv2
```

**Solution**:
```bash
pip uninstall opencv-python
pip install opencv-python-headless
```

## Updating

To update the nodes:

```bash
cd /path/to/ComfyUI/custom_nodes/ComfyUI_FaceExtractor
git pull  # if using git
# OR manually replace files
pip install -r requirements.txt --upgrade
```

Then restart ComfyUI.

## Uninstallation

To remove the nodes:

```bash
cd /path/to/ComfyUI/custom_nodes/
rm -rf ComfyUI_FaceExtractor
```

Then restart ComfyUI.

## Post-Installation

### Quick Test

1. Load `example_workflow.json`
2. Replace the reference image path
3. Replace the input image path  
4. Click "Queue Prompt"
5. Check if faces are extracted

### GPU Test

To verify GPU is working:
1. In "Extract Matching Faces" node
2. Set `device` to "cuda"
3. Run workflow
4. Check ComfyUI terminal - should see CUDA being used
5. Processing should be much faster

### First Real Use

1. **Prepare Reference**
   - Get clear photo of person to extract
   - Place in ComfyUI input folder
   - Load with LoadImage node

2. **Load Video Workflow**
   - Load `workflow_video_extraction.json`
   - Set video path to your video file
   - Adjust threshold (start with 0.4)
   - Queue prompt

3. **Check Results**
   - Output saved to specified directory
   - Review `faces/` folder
   - Adjust parameters if needed

## Directory Structure After Installation

```
ComfyUI/
└── custom_nodes/
    └── ComfyUI_FaceExtractor/
        ├── __init__.py
        ├── face_extractor_nodes.py
        ├── requirements.txt
        ├── README.md
        ├── INSTALLATION.md (this file)
        ├── example_workflow.json
        └── workflow_video_extraction.json
```

## System Requirements

**Minimum**:
- Python 3.9+
- 8GB RAM
- 10GB free disk space
- CPU with AVX2 support

**Recommended**:
- Python 3.10+
- 16GB RAM
- NVIDIA GPU with 6GB+ VRAM
- CUDA 11.8+
- 50GB+ free disk space (for output faces)

## Getting Help

If installation fails:

1. Check ComfyUI console for specific errors
2. Verify Python version: `python --version`
3. Check installed packages: `pip list | grep insightface`
4. Review README.md for usage instructions
5. Try manual installation method

## Next Steps

After successful installation:

1. Read README.md for complete documentation
2. Load and explore example workflows
3. Prepare your reference image
4. Start extracting faces!

---

**Installation complete!** You should now see Face Extraction nodes in ComfyUI. 🎉
