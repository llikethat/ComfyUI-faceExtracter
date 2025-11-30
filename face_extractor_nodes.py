"""
ComfyUI Face Extractor Nodes v2
Custom nodes for automated face extraction with multiple references and flexible input
"""

import torch
import numpy as np
import cv2
from PIL import Image
import folder_paths
import os
from pathlib import Path
import json
from typing import Tuple, List, Dict, Optional
import tempfile

try:
    from insightface.app import FaceAnalysis
    INSIGHTFACE_AVAILABLE = True
except ImportError:
    INSIGHTFACE_AVAILABLE = False
    print("WARNING: InsightFace not installed. Face extraction nodes will not work.")
    print("Install with: pip install insightface onnxruntime")


class FaceExtractorCore:
    """Core face extraction logic with multi-reference support"""
    
    def __init__(self, device='cpu'):
        if not INSIGHTFACE_AVAILABLE:
            raise ImportError("InsightFace is required. Install with: pip install insightface onnxruntime")
        
        self.app = FaceAnalysis(
            name='buffalo_l',
            providers=['CUDAExecutionProvider'] if device == 'cuda' else ['CPUExecutionProvider']
        )
        self.app.prepare(ctx_id=0 if device == 'cuda' else -1, det_size=(640, 640))
        self.reference_embeddings = []  # Support multiple references
        
    def set_references(self, image_arrays: List[np.ndarray]):
        """Set reference faces from multiple images (batch)"""
        self.reference_embeddings = []
        faces_found = 0
        
        for img_array in image_arrays:
            bgr_image = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            faces = self.app.get(bgr_image)
            
            if len(faces) == 0:
                print(f"Warning: No face detected in one reference image, skipping")
                continue
            
            # Use largest face if multiple detected
            if len(faces) > 1:
                faces = sorted(faces, key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]), reverse=True)
                print(f"Info: Found {len(faces)} faces in reference image, using largest")
            
            self.reference_embeddings.append(faces[0].embedding)
            faces_found += 1
        
        if len(self.reference_embeddings) == 0:
            raise ValueError("No faces detected in any reference images")
        
        return faces_found
    
    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Compute cosine similarity between embeddings"""
        return np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))
    
    def compute_max_similarity(self, target_embedding: np.ndarray) -> float:
        """Compute maximum similarity against all reference embeddings"""
        if len(self.reference_embeddings) == 0:
            raise ValueError("No reference embeddings set")
        
        max_sim = 0.0
        for ref_emb in self.reference_embeddings:
            sim = self.compute_similarity(ref_emb, target_embedding)
            max_sim = max(max_sim, sim)
        
        return max_sim
    
    def extract_matching_faces(
        self,
        image_array: np.ndarray,
        similarity_threshold: float = 0.4,
        min_face_size: int = 64,
        padding: float = 0.3
    ) -> List[Dict]:
        """Extract faces matching reference from image"""
        if len(self.reference_embeddings) == 0:
            raise ValueError("Reference images not set")
        
        # Convert RGB to BGR
        bgr_image = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        faces = self.app.get(bgr_image)
        
        matched_faces = []
        
        for face in faces:
            # Check similarity against all references (use max)
            similarity = self.compute_max_similarity(face.embedding)
            
            if similarity >= similarity_threshold:
                # Check size
                face_width = face.bbox[2] - face.bbox[0]
                face_height = face.bbox[3] - face.bbox[1]
                
                if face_width < min_face_size or face_height < min_face_size:
                    continue
                
                # Extract face with padding
                h, w = image_array.shape[:2]
                x1, y1, x2, y2 = face.bbox.astype(int)
                
                pad_w = int(face_width * padding)
                pad_h = int(face_height * padding)
                
                x1_pad = max(0, x1 - pad_w)
                y1_pad = max(0, y1 - pad_h)
                x2_pad = min(w, x2 + pad_w)
                y2_pad = min(h, y2 + pad_h)
                
                # Extract face (RGB)
                face_img = image_array[y1_pad:y2_pad, x1_pad:x2_pad].copy()
                
                # Create mask
                mask = np.zeros((y2_pad - y1_pad, x2_pad - x1_pad), dtype=np.uint8)
                face_y1 = y1 - y1_pad
                face_y2 = y2 - y1_pad
                face_x1 = x1 - x1_pad
                face_x2 = x2 - x1_pad
                mask[face_y1:face_y2, face_x1:face_x2] = 255
                
                matched_faces.append({
                    'face': face_img,
                    'mask': mask,
                    'bbox': face.bbox.tolist(),
                    'similarity': float(similarity),
                    'padded_bbox': [x1_pad, y1_pad, x2_pad, y2_pad]
                })
        
        return matched_faces


class LoadReferenceImages:
    """Load one or more reference images for face matching"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "reference_images": ("IMAGE",),
            }
        }
    
    RETURN_TYPES = ("FACE_REFERENCE",)
    RETURN_NAMES = ("reference",)
    FUNCTION = "load_references"
    CATEGORY = "Face Extraction"
    
    def load_references(self, reference_images):
        """Load reference image(s) and extract face embedding(s)
        
        Supports:
        - Single image: (1, H, W, C)
        - Multiple images: (N, H, W, C)
        """
        # Convert from ComfyUI format (B, H, W, C) to list of numpy arrays
        image_arrays = []
        
        batch_size = reference_images.shape[0]
        for i in range(batch_size):
            img_array = (reference_images[i].cpu().numpy() * 255).astype(np.uint8)
            image_arrays.append(img_array)
        
        # Store reference data
        reference_data = {
            'images': image_arrays,
            'count': len(image_arrays),
            'loaded': True
        }
        
        print(f"Loaded {len(image_arrays)} reference image(s)")
        
        return (reference_data,)


class ExtractFromFootage:
    """Universal extraction node supporting images, image sequences, and video files"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "reference": ("FACE_REFERENCE",),
                "input_mode": (["images", "video_file"],),
                "similarity_threshold": ("FLOAT", {
                    "default": 0.4,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.05,
                    "display": "slider"
                }),
                "min_face_size": ("INT", {
                    "default": 64,
                    "min": 32,
                    "max": 512,
                    "step": 16
                }),
                "padding": ("FLOAT", {
                    "default": 0.3,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.1
                }),
                "sample_every_n_frames": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 30,
                    "step": 1
                }),
                "max_frames": ("INT", {
                    "default": 0,  # 0 = all frames
                    "min": 0,
                    "max": 10000,
                    "step": 100
                }),
                "device": (["cpu", "cuda"],),
            },
            "optional": {
                "input_images": ("IMAGE",),
                "video_path": ("STRING", {"default": ""}),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "MASK", "STRING")
    RETURN_NAMES = ("faces", "masks", "info")
    FUNCTION = "extract_faces"
    CATEGORY = "Face Extraction"
    OUTPUT_IS_LIST = (True, True, False)
    
    def extract_faces(self, reference, input_mode, similarity_threshold, 
                     min_face_size, padding, sample_every_n_frames, max_frames, device,
                     input_images=None, video_path=None):
        """Extract matching faces from images or video
        
        Modes:
        - images: Process from input_images parameter (single or batch)
        - video_file: Process from video file path
        """
        
        # Initialize extractor
        extractor = FaceExtractorCore(device=device)
        
        # Set references
        extractor.set_references(reference['images'])
        
        all_faces = []
        all_masks = []
        stats = {
            'frames_processed': 0,
            'faces_found': 0,
            'reference_count': reference['count']
        }
        
        if input_mode == "images":
            if input_images is None:
                return ([], [], "Error: No input images provided for 'images' mode")
            
            # Process image sequence (single or batch)
            batch_size = input_images.shape[0]
            
            for i in range(batch_size):
                # Check sampling
                if i % sample_every_n_frames != 0:
                    continue
                
                stats['frames_processed'] += 1
                
                img_array = (input_images[i].cpu().numpy() * 255).astype(np.uint8)
                
                # Extract faces
                matched_faces = extractor.extract_matching_faces(
                    img_array,
                    similarity_threshold=similarity_threshold,
                    min_face_size=min_face_size,
                    padding=padding
                )
                
                stats['faces_found'] += len(matched_faces)
                
                for match in matched_faces:
                    face_tensor = torch.from_numpy(match['face']).float() / 255.0
                    all_faces.append(face_tensor)
                    
                    mask_tensor = torch.from_numpy(match['mask']).float() / 255.0
                    all_masks.append(mask_tensor)
                
                # Check max frames
                if max_frames > 0 and stats['frames_processed'] >= max_frames:
                    break
            
            info = f"Images: Processed {stats['frames_processed']}/{batch_size} images, found {stats['faces_found']} faces (using {stats['reference_count']} reference(s))"
            
        elif input_mode == "video_file":
            if not video_path or not os.path.exists(video_path):
                return ([], [], f"Error: Video file not found: {video_path}")
            
            # Open video
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return ([], [], f"Error: Could not open video: {video_path}")
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            frame_idx = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Sample frames
                if frame_idx % sample_every_n_frames != 0:
                    frame_idx += 1
                    continue
                
                stats['frames_processed'] += 1
                
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Extract faces
                matched_faces = extractor.extract_matching_faces(
                    frame_rgb,
                    similarity_threshold=similarity_threshold,
                    min_face_size=min_face_size,
                    padding=padding
                )
                
                stats['faces_found'] += len(matched_faces)
                
                for match in matched_faces:
                    face_tensor = torch.from_numpy(match['face']).float() / 255.0
                    all_faces.append(face_tensor)
                    
                    mask_tensor = torch.from_numpy(match['mask']).float() / 255.0
                    all_masks.append(mask_tensor)
                
                frame_idx += 1
                
                # Check max frames
                if max_frames > 0 and stats['frames_processed'] >= max_frames:
                    break
            
            cap.release()
            info = f"Video: Processed {stats['frames_processed']}/{total_frames} frames ({fps:.1f}fps), found {stats['faces_found']} faces (using {stats['reference_count']} reference(s))"
        
        else:
            return ([], [], f"Error: Unknown input mode: {input_mode}")
        
        # Handle empty results
        if len(all_faces) == 0:
            empty_face = torch.zeros((64, 64, 3))
            empty_mask = torch.zeros((64, 64))
            all_faces = [empty_face]
            all_masks = [empty_mask]
            info = f"No faces found. {info}"
        
        return (all_faces, all_masks, info)


class SaveExtractedFaces:
    """Save extracted faces to disk in ComfyUI output folder"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "faces": ("IMAGE",),
                "masks": ("MASK",),
                "subfolder": ("STRING", {"default": "extracted_faces"}),
                "prefix": ("STRING", {"default": "face"}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("save_path",)
    FUNCTION = "save_faces"
    CATEGORY = "Face Extraction"
    OUTPUT_NODE = True
    
    def save_faces(self, faces, masks, subfolder, prefix):
        """Save faces and masks to ComfyUI output folder"""
        
        # Use ComfyUI's output directory
        from folder_paths import get_output_directory
        output_base = get_output_directory()
        
        # Create subdirectories in ComfyUI output folder
        output_path = Path(output_base) / subfolder
        faces_dir = output_path / "faces"
        masks_dir = output_path / "masks"
        
        faces_dir.mkdir(parents=True, exist_ok=True)
        masks_dir.mkdir(parents=True, exist_ok=True)
        
        # Handle list input
        if isinstance(faces, list):
            face_list = faces
            mask_list = masks if isinstance(masks, list) else [masks] * len(faces)
        else:
            face_list = [faces]
            mask_list = [masks]
        
        saved_count = 0
        
        for idx, (face_tensor, mask_tensor) in enumerate(zip(face_list, mask_list)):
            # Convert to numpy
            face_np = (face_tensor.cpu().numpy() * 255).astype(np.uint8)
            mask_np = (mask_tensor.cpu().numpy() * 255).astype(np.uint8)
            
            # Save face
            face_path = faces_dir / f"{prefix}_{idx:06d}.png"
            face_img = Image.fromarray(face_np)
            face_img.save(face_path)
            
            # Save mask
            mask_path = masks_dir / f"{prefix}_mask_{idx:06d}.png"
            mask_img = Image.fromarray(mask_np)
            mask_img.save(mask_path)
            
            saved_count += 1
        
        result = f"Saved {saved_count} faces to ComfyUI/output/{subfolder}"
        print(result)
        return (result,)


class FaceExtractionStats:
    """Display statistics about extraction"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "faces": ("IMAGE",),
                "info_string": ("STRING", {"default": ""}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("statistics",)
    FUNCTION = "get_stats"
    CATEGORY = "Face Extraction"
    OUTPUT_NODE = True
    
    def get_stats(self, faces, info_string):
        """Generate statistics string"""
        
        if isinstance(faces, list):
            count = len(faces)
            if count > 0 and faces[0].shape[0] > 0:
                avg_size = sum(f.shape[0] * f.shape[1] for f in faces) / count
                stats = f"{info_string}\nTotal faces: {count}\nAverage size: {int(avg_size)} pixels²"
            else:
                stats = "No faces extracted"
        else:
            batch_size = faces.shape[0]
            stats = f"{info_string}\nBatch size: {batch_size}"
        
        print(stats)
        return (stats,)


# Node class mappings for ComfyUI
NODE_CLASS_MAPPINGS = {
    "LoadReferenceImages": LoadReferenceImages,
    "ExtractFromFootage": ExtractFromFootage,
    "SaveExtractedFaces": SaveExtractedFaces,
    "FaceExtractionStats": FaceExtractionStats,
}

# Display name mappings
NODE_DISPLAY_NAME_MAPPINGS = {
    "LoadReferenceImages": "Load Reference Face(s)",
    "ExtractFromFootage": "Extract from Footage",
    "SaveExtractedFaces": "Save Extracted Faces",
    "FaceExtractionStats": "Face Extraction Stats",
}
