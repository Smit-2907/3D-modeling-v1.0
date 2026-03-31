"""
Food-to-3D Pipeline Stage Orchestrator
Coordinates the flow: Image → TripoSR (AI) → Blender (GLB Export)
Includes 'Smart Checkpoints' to resume failed or partially complete jobs.
"""

import logging
import os
import shutil
import time
import uuid
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Dict

from config import (
    BASE_DIR,
    INPUT_DIR,
    OUTPUT_DIR,
    BLENDER_EXECUTABLE,
    MAX_POLY_COUNT,
)

logger = logging.getLogger("pipeline")

@dataclass
class PipelineResult:
    job_id: str
    success: bool = False
    obj_path: Optional[str] = None
    glb_path: Optional[str] = None
    error: Optional[str] = None
    elapsed_seconds: float = 0.0

def validate_image(image_path: str):
    """Basic validation to ensure image exists and is readable."""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Input image not found: {image_path}")
    
    from PIL import Image
    try:
        with Image.open(image_path) as img:
            img.verify()
    except Exception as e:
        raise ValueError(f"Invalid image file: {e}")

def run_triposr(image_path: str, output_dir: str, job_id: str) -> str:
    """Run the AI reconstruction stage."""
    from triposr_engine import get_engine
    
    obj_path = os.path.join(output_dir, "mesh.obj")
    
    logger.info(f"[{job_id}] 🤖 Calling TripoSR Engine...")
    engine = get_engine()
    engine.generate_mesh(
        image_path=image_path,
        output_path=obj_path,
        output_format="obj",
        remove_bg=True
    )
    
    if not os.path.exists(obj_path):
        raise RuntimeError("TripoSR failed to produce an OBJ file")
        
    return obj_path

def run_blender_conversion(obj_path: str, glb_path: str, job_id: str, max_polys: int = MAX_POLY_COUNT) -> str:
    """Run the Blender optimization and export stage."""
    blender_exe = BLENDER_EXECUTABLE
    convert_script = str(BASE_DIR / "convert_to_glb.py")

    if not os.path.exists(blender_exe):
        logger.warning(f"Blender not found at '{blender_exe}'. Trying PATH...")
        blender_exe = "blender"

    cmd = [
        blender_exe,
        "--background",
        "--python", convert_script,
        "--",
        "--input", obj_path,
        "--output", glb_path,
        "--max-polys", str(max_polys),
    ]

    logger.info(f"[{job_id}] 🧊 Running Blender Process...")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=300
        )

        if result.returncode != 0:
            logger.error(f"[{job_id}] Blender Error:\n{result.stderr}")
            raise RuntimeError(f"Blender failed with exit code {result.returncode}")

    except Exception as e:
        raise RuntimeError(f"Blender pipeline error: {e}")

    if not os.path.exists(glb_path):
        raise RuntimeError("Blender conversion failed to produce a GLB")

    return glb_path

def run_pipeline(
    image_path: str,
    job_id: Optional[str] = None,
    max_polys: int = MAX_POLY_COUNT,
) -> PipelineResult:
    """
    Execute the full Food-to-3D pipeline with 'Smart Resumption'.
    """
    if job_id is None:
        job_id = str(uuid.uuid4())[:8]

    start_time = time.time()
    logger.info(f"{'='*60}")
    logger.info(f"[{job_id}] SMART PIPELINE START")
    logger.info(f"{'='*60}")

    result = PipelineResult(job_id=job_id)

    try:
        validate_image(image_path)

        job_dir = os.path.join(OUTPUT_DIR, job_id)
        os.makedirs(job_dir, exist_ok=True)

        # ─── Step 1: AI (Check for existing mesh) ───
        obj_path = os.path.join(job_dir, "mesh.obj")
        if os.path.exists(obj_path) and os.path.getsize(obj_path) > 1000:
            logger.info(f"[{job_id}] ⏩ SMART RESUME: Found mesh.obj. Skipping Stage 1 (AI).")
        else:
            logger.info(f"[{job_id}] ⏳ Stage 1: AI Reconstruction...")
            obj_path = run_triposr(image_path, job_dir, job_id)
            
        result.obj_path = obj_path

        # ─── Step 2: Blender (Check for existing model) ───
        glb_path = os.path.join(job_dir, "model.glb")
        if os.path.exists(glb_path) and os.path.getsize(glb_path) > 1000:
            logger.info(f"[{job_id}] ⏩ SMART RESUME: Found model.glb. Skipping Stage 2 (Blender).")
        else:
            logger.info(f"[{job_id}] ⏳ Stage 2: Blender Optimization & Export...")
            glb_path = run_blender_conversion(obj_path, glb_path, job_id, max_polys=max_polys)

        result.glb_path = glb_path
        result.success = True

    except Exception as e:
        logger.error(f"[{job_id}] ❌ Pipeline failed: {e}")
        result.error = str(e)
        result.success = False

    result.elapsed_seconds = time.time() - start_time
    logger.info(f"[{job_id}] ✨ Final Status: {'SUCCESS' if result.success else 'FAILED'} ({result.elapsed_seconds:.1f}s)")
    return result
