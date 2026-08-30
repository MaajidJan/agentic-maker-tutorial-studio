import os
import sys
import shutil
import zipfile
import logging
from pathlib import Path
from typing import List, Optional

# Add submission root to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from src.config import Config
from src.models import (
    JobState, JobStatus, CreateJobRequest, RevisionRequest, ApprovalRequest
)
from src.firestore_store import job_store
from src.agents.orchestrator import orchestrator

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("maker_studio_api")

app = FastAPI(
    title="Autonomous Agentic Maker Studio",
    description="Autonomous Multimodal AI Agent Studio creating kid-friendly tutorial packages.",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static & Output file mounts
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
Config.OUTPUT_BASE_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/outputs", StaticFiles(directory=str(Config.OUTPUT_BASE_DIR)), name="outputs")


@app.get("/health")
def health_check():
    """Health check for monitoring."""
    return {
        "status": "healthy",
        "service": "agentic-maker-tutorial-studio",
        "firestore_connected": job_store.db is not None,
        "config": Config.validate_keys()
    }


@app.get("/api/config")
def get_config():
    """Returns configuration and active model statuses."""
    return {
        "models": {
            "text": Config.GEMINI_MODEL,
            "image": Config.GEMINI_IMAGE_MODEL
        },
        "gcp_project": Config.GOOGLE_CLOUD_PROJECT,
        "firestore_collection": Config.FIRESTORE_COLLECTION,
        "freesound_active": bool(Config.FREESOUND_API_KEY)
    }


@app.get("/api/jobs")
def list_jobs(limit: int = 15):
    """Lists recent jobs from Firestore / persistent store."""
    return job_store.list_jobs(limit=limit)


@app.post("/api/jobs")
async def create_job(
    background_tasks: BackgroundTasks,
    prompt: str = Form(default="Make this Arduino build super fun, interactive, and educational for kids (8-12yo) with anime-style reactions!"),
    files: List[UploadFile] = File(default=[])
):
    """
    Submits a new tutorial creation job with photos/video media and goal prompt.
    Runs asynchronously in the background while returning immediate job ID for status polling.
    """
    import uuid
    job_id = f"job_{uuid.uuid4().hex[:10]}"
    upload_dir = Config.OUTPUT_BASE_DIR / f"uploads_{job_id}"
    upload_dir.mkdir(parents=True, exist_ok=True)

    saved_media_paths = []
    for f in files:
        if f.filename:
            target_file = upload_dir / f.filename
            with open(target_file, "wb") as out_f:
                content = await f.read()
                out_f.write(content)
            saved_media_paths.append(str(target_file))

    # If no media uploaded, use default sample fixture
    if not saved_media_paths:
        sample_img = Config.SAMPLE_DATA_DIR / "arduino_radar.jpg"
        if sample_img.exists():
            saved_media_paths.append(str(sample_img))

    # Initialize initial state
    initial_job = JobState(
        job_id=job_id,
        status=JobStatus.PENDING,
        prompt=prompt,
        media_filenames=[Path(p).name for p in saved_media_paths],
        progress_percentage=5,
        current_step_description="Queued in job runner..."
    )
    job_store.save_job(initial_job)

    # Launch autonomous agent pipeline in background task
    background_tasks.add_task(
        orchestrator.run_pipeline,
        media_paths=saved_media_paths,
        user_prompt=prompt,
        job_id=job_id
    )

    return {
        "job_id": job_id,
        "status": JobStatus.PENDING,
        "message": "Job initiated successfully. Poll /api/jobs/{job_id} for live progress.",
        "poll_url": f"/api/jobs/{job_id}"
    }


@app.get("/api/jobs/{job_id}")
def get_job_status(job_id: str):
    """Returns the full state and generated assets for a specific job."""
    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found.")
    return job


@app.post("/api/jobs/{job_id}/revise")
def revise_job(
    job_id: str,
    req: RevisionRequest,
    background_tasks: BackgroundTasks
):
    """Sends director revision feedback and triggers regeneration."""
    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found.")

    background_tasks.add_task(
        orchestrator.revise_job,
        job_id=job_id,
        revision_note=req.revision_note
    )
    return {"message": "Revision started", "job_id": job_id, "status": JobStatus.REVISING}


@app.post("/api/jobs/{job_id}/approve")
def approve_job(job_id: str):
    """Approves the package and exports the final timestamped bundle."""
    job = orchestrator.approve_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found.")
    return {
        "message": "Job approved and exported successfully!",
        "job_id": job_id,
        "status": job.status,
        "output_dir": job.output_dir
    }


@app.get("/api/jobs/{job_id}/export")
def download_export_zip(job_id: str):
    """Zips and downloads the final exported tutorial package."""
    job = job_store.get_job(job_id)
    if not job or not job.output_dir:
        raise HTTPException(status_code=400, detail="Job must be approved and exported before downloading.")

    export_path = Path(job.output_dir)
    if not export_path.exists():
        raise HTTPException(status_code=404, detail="Export directory not found on disk.")

    zip_filename = f"{job_id}_tutorial_package.zip"
    zip_path = Config.OUTPUT_BASE_DIR / zip_filename

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_f:
        for root, _, files in os.walk(export_path):
            for file in files:
                file_full = Path(root) / file
                rel_path = file_full.relative_to(export_path)
                zip_f.write(file_full, arcname=str(rel_path))

    return FileResponse(
        path=str(zip_path),
        filename=zip_filename,
        media_type="application/zip"
    )


@app.get("/")
def serve_index():
    """Serves the interactive web dashboard."""
    index_path = STATIC_DIR / "index.html"
    if not index_path.exists():
        return HTMLResponse("<h1>Autonomous Maker Studio Ready</h1><p>Static index.html not yet built.</p>")
    with open(index_path, "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    config = uvicorn.Config(app=app, host="0.0.0.0", port=port, log_level="info", access_log=True)
    server = uvicorn.Server(config)
    server.run()
