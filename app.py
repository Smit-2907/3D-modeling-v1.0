"""
FastAPI Application — Food Image → 3D Model API

Endpoints:
    POST /generate-3d/     Upload image, trigger pipeline, return GLB URL
    GET  /model/{job_id}    Download generated .glb file
    GET  /status/{job_id}   Check processing status
    GET  /gallery          View the 3D collection gallery
    GET  /                  Serve the frontend UI
"""

import asyncio
import logging
import os
import shutil
import uuid
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from config import (
    INPUT_DIR,
    OUTPUT_DIR,
    STATIC_DIR,
    ALLOWED_IMAGE_EXTENSIONS,
    MAX_FILE_SIZE_MB,
    MAX_POLY_COUNT,
    LOG_FORMAT,
    LOG_LEVEL,
    SERVER_HOST,
    SERVER_PORT,
)

# ─── Logging ───
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger("api")

# ─── App ───
app = FastAPI(
    title="Food3D — Image to 3D Model API",
    description="Convert food images into AR-ready 3D models (.glb) using TripoSR + Blender",
    version="1.0.0",
)

# CORS — allow the frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Job Memory (Persistent Across Restarts) ───
jobs: dict[str, dict] = {}
JOBS_FILE = OUTPUT_DIR / "jobs_registry.json"

def save_jobs():
    """Save the jobs registry to disk."""
    try:
        with open(JOBS_FILE, "w") as f:
            json.dump(jobs, f, indent=4)
        logger.debug(f"Saved {len(jobs)} jobs to persistent registry.")
    except Exception as e:
        logger.warning(f"Failed to save jobs registry: {e}")

def load_jobs():
    """Load the jobs registry from disk."""
    global jobs
    if JOBS_FILE.exists():
        try:
            with open(JOBS_FILE, "r") as f:
                jobs = json.load(f)
            logger.info(f"📁 Loaded {len(jobs)} jobs from persistent registry.")
        except Exception as e:
            logger.warning(f"Failed to load jobs registry: {e}")

# Initial load
load_jobs()


# ═══════════════════════════════════════════════
#  Background task: runs the full pipeline
# ═══════════════════════════════════════════════

def process_image_task(job_id: str, image_path: str):
    """Run the full pipeline in the background."""
    from pipeline import run_pipeline

    jobs[job_id]["status"] = "processing"
    jobs[job_id]["started_at"] = datetime.now().isoformat()
    save_jobs()

    logger.info(f"[API] Background task started for job {job_id}")

    result = run_pipeline(
        image_path=image_path,
        job_id=job_id,
        max_polys=MAX_POLY_COUNT,
    )

    if result.success:
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["glb_path"] = result.glb_path
        jobs[job_id]["obj_path"] = result.obj_path
        jobs[job_id]["glb_url"] = f"/model/{job_id}"
        jobs[job_id]["elapsed_seconds"] = result.elapsed_seconds
        
        # Save to permanent cache
        if "file_hash" in jobs[job_id]:
            try:
                h = jobs[job_id]["file_hash"]
                cfile = OUTPUT_DIR / "image_cache.json"
                cache = {}
                if cfile.exists():
                    with open(cfile, "r") as f: cache = json.load(f)
                cache[h] = job_id
                with open(cfile, "w") as f: json.dump(cache, f, indent=4)
                logger.info(f"✨ Job {job_id} cached for future use")
            except: pass
    else:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = result.error
        jobs[job_id]["elapsed_seconds"] = result.elapsed_seconds

    jobs[job_id]["completed_at"] = datetime.now().isoformat()
    save_jobs() # Save again on completion
    logger.info(f"[API] Job {job_id} → {jobs[job_id]['status']}")


# ═══════════════════════════════════════════════
#  API Endpoints
# ═══════════════════════════════════════════════

@app.post("/generate-3d/", response_class=JSONResponse)
async def generate_3d(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    logger.info(f"📥 [API] Received upload request: {file.filename}")
    
    # ─── Validate file type ───
    ext = Path(file.filename or "unknown").suffix.lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format '{ext}'. Allowed: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}",
        )

    # ─── Read file ───
    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400, 
            detail=f"File too large ({size_mb:.1f} MB). Max: {MAX_FILE_SIZE_MB} MB"
        )

    # ─── Fingerprint check ───
    import hashlib
    file_hash = hashlib.sha256(contents).hexdigest()
    cache_file = OUTPUT_DIR / "image_cache.json"
    if cache_file.exists():
        try:
            with open(cache_file, "r") as f:
                cache = json.load(f)
                if file_hash in cache:
                    cached_id = cache[file_hash]
                    if (OUTPUT_DIR / cached_id / "model.glb").exists():
                        logger.info(f"🎯 Cache Hit: {cached_id}")
                        # Update in-memory job if not present
                        if cached_id not in jobs:
                            jobs[cached_id] = {
                                "job_id": cached_id,
                                "status": "completed",
                                "glb_url": f"/model/{cached_id}"
                            }
                        return {"job_id": cached_id, "status": "completed", "glb_url": f"/model/{cached_id}", "is_cached": True}
        except: pass

    # ─── Create job ───
    job_id = str(uuid.uuid4())[:8]
    input_dir = INPUT_DIR / job_id
    input_dir.mkdir(parents=True, exist_ok=True)
    
    image_path = str(input_dir / f"input{ext}")
    with open(image_path, "wb") as f:
        f.write(contents)

    # ─── Register job ───
    jobs[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "file_hash": file_hash,
        "original_filename": file.filename,
        "image_path": image_path,
        "created_at": datetime.now().isoformat(),
        "started_at": None,
        "completed_at": None,
        "glb_url": None,
        "error": None,
    }
    save_jobs()

    # ─── Enqueue ───
    background_tasks.add_task(process_image_task, job_id, image_path)

    return {
        "job_id": job_id,
        "status": "queued",
        "status_url": f"/status/{job_id}",
    }


@app.get("/status/{job_id}", response_class=JSONResponse)
async def get_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]


@app.get("/model/{job_id}")
async def get_model(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Model not ready")

    glb_path = job.get("glb_path")
    # If path missing but dir exists, infer it
    if not glb_path:
        inf_path = OUTPUT_DIR / job_id / "model.glb"
        if inf_path.exists(): glb_path = str(inf_path)

    if not glb_path or not os.path.exists(glb_path):
        raise HTTPException(status_code=404, detail="GLB file not found")

    return FileResponse(path=glb_path, media_type="model/gltf-binary", filename=f"model_{job_id}.glb")


@app.get("/jobs", response_class=JSONResponse)
async def list_jobs():
    # Return jobs sorted by date (newest first)
    sorted_jobs = sorted(jobs.values(), key=lambda x: x.get("created_at", ""), reverse=True)
    return {"total": len(jobs), "jobs": sorted_jobs}


@app.get("/gallery", response_class=FileResponse)
async def serve_gallery():
    return FileResponse(STATIC_DIR / "gallery.html")


@app.get("/", response_class=FileResponse)
async def serve_frontend():
    return FileResponse(STATIC_DIR / "index.html")

# Mount output for thumbnails
app.mount("/output", StaticFiles(directory=str(OUTPUT_DIR)), name="output")
# Mount static for assets
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.on_event("startup")
async def on_startup():
    logger.info("🚀 Food3D Server is running with Persistent Memory & Gallery support.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host=SERVER_HOST, port=SERVER_PORT)
