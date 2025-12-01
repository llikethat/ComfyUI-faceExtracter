# DFL Face Extractor for ComfyUI

**Version 3.0 - Memory-Aware Processing**

Automated face extraction for DeepFaceLab de-aging and face swap workflows.

## ⚠️ Important: Don't Use VHS_LoadVideo for Large Videos!

**Problem**: VHS_LoadVideo loads ALL frames into memory before processing.
- 20,000 frames at 1080p = ~120 GB RAM → **CRASH**

**Solution**: Use this node's built-in video loading with `video_path` input.
- Streaming mode: ~500 MB RAM regardless of video length ✓

## Features

- **Built-in Video Loading**: No VHS dependency needed for large videos
- **Streaming Mode**: Process videos of ANY length with constant memory
- **Chunked Mode**: Faster processing with memory-aware batching
- **GPU Accelerated**: Face detection on CUDA
- **Auto-incrementing Output**: Each run creates a new numbered folder
- **Memory Monitoring**: Real-time RAM usage tracking

## Installation

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/llikethat/ComfyUI-faceExtractor.git
cd ComfyUI-faceExtractor
pip install -r requirements.txt
```

## GPU vs CPU Processing

| Component | Device | Notes |
|-----------|--------|-------|
| Face Detection | **GPU** | InsightFace + CUDA |
| Face Embedding | **GPU** | ArcFace model |
| Video Decoding | CPU | OpenCV |
| Image Saving | CPU | PNG write |

## Nodes

### DFL Reference Embedding

Compute face embeddings from reference images.

| Input | Description |
|-------|-------------|
| reference_images | Single image or batch (use ImageBatch for multiple) |
| detection_backend | "insightface" (GPU) or "opencv_cascade" (CPU) |
| min_confidence | Minimum detection confidence (default: 0.5) |

### DFL Face Extractor

**Main extraction node with built-in video loading.**

| Input | Description |
|-------|-------------|
| **video_path** | **Direct path to video file (RECOMMENDED)** |
| images | Alternative: IMAGE input from other nodes |
| reference_embedding | From DFL Reference Embedding |
| similarity_threshold | Match threshold 0.3-0.95 (default: 0.6) |
| margin_factor | Padding around face (default: 0.4) |
| output_size | Output resolution (default: 512) |
| max_faces_per_frame | Max faces to extract per frame (default: 1) |
| frame_skip | Process every Nth frame (default: 1) |
| start_frame | Start at this frame (default: 0) |
| end_frame | End at this frame, -1=all (default: -1) |
| **processing_mode** | **"streaming" (low RAM) or "chunked" (faster)** |
| **memory_threshold_percent** | **Max RAM to use (default: 75%)** |
| output_prefix | Folder name prefix (default: "dfl_extract") |

### DFL Face Matcher

Compare two faces for threshold tuning.

## Processing Modes

### Streaming Mode (Default) ⭐ RECOMMENDED
```
Processing: One frame at a time
Memory: ~500 MB constant
Speed: Moderate
Best for: Large videos, limited RAM
```

### Chunked Mode
```
Processing: Batches based on available RAM
Memory: Up to memory_threshold_percent of system RAM
Speed: Faster (batch GPU processing)
Best for: When you have RAM to spare
```

## Memory Comparison

| Video | VHS_LoadVideo | Streaming Mode | Chunked Mode |
|-------|---------------|----------------|--------------|
| 1 min (1,440 frames) | ~8 GB | ~500 MB | ~2 GB |
| 10 min (14,400 frames) | ~86 GB | ~500 MB | ~2 GB |
| 2 hours (172,800 frames) | **~1 TB** ❌ | ~500 MB ✓ | ~2 GB ✓ |

## Workflows

### 01 - Basic Extraction
Single reference + direct video path. No VHS needed.

### 02 - Multi-Reference
3+ reference images for robust matching. Lower threshold, better accuracy.

### 03 - Threshold Tuning
Compare same vs different person to find optimal threshold.

### 04 - De-aging Pipeline
Complete workflow for source (young) and destination (old) extraction.

## Quick Start

1. **Load reference image** of target character
2. **Enter video path** directly in DFL Face Extractor (not VHS!)
3. **Set processing_mode** to "streaming" for large videos
4. **Run** - faces saved to `ComfyUI/output/dfl_extract_001/`

## Console Output

The node prints progress and memory usage:
```
[DFL Extractor] Using GPU: NVIDIA RTX A6000 (48.0 GB)
[DFL Extractor] System Memory: 64.0 GB available / 128.0 GB total
[DFL Extractor] Video: 172800 frames, 1920x1080, 24.00 fps, 7200.0s
[DFL Extractor] STREAMING MODE - Processing 172800 frames
[DFL Extractor] Memory usage: ~constant (1 frame at a time)
...
[DFL Extractor] ✓ Extracted 15234 faces to /output/dfl_extract_001
[DFL Extractor] ✓ Time: 3842.5s (3.9 faces/sec)
```

## Directory Structure

```
ComfyUI/output/
├── dfl_extract_001/
│   ├── aligned/
│   │   ├── 00000000_0.png
│   │   ├── 00000024_0.png
│   │   └── ...
│   ├── masks/
│   │   ├── 00000000_0_mask.png
│   │   └── ...
│   └── extraction_log.json
├── dfl_extract_002/
│   └── ...
```

## For DeepFaceLab

After extraction, copy to DFL workspace:
```bash
# Source faces
cp ComfyUI/output/data_src_001/aligned/* workspace/data_src/aligned/

# Destination faces  
cp ComfyUI/output/data_dst_001/aligned/* workspace/data_dst/aligned/
```

## License

MIT License
