import os
import json
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path

# Support both package-relative and sys.path imports
try:
    from .config import Config
    from .models import JobState, JobStatus
except ImportError:
    from src.config import Config
    from src.models import JobState, JobStatus

logger = logging.getLogger("botrix_firestore")

# Fallback local directory
LOCAL_STATE_DIR = Config.OUTPUT_BASE_DIR / ".state"
LOCAL_STATE_DIR.mkdir(parents=True, exist_ok=True)


class JobStore:
    def __init__(self):
        self.use_firestore = Config.USE_FIRESTORE
        self.db = None
        self.collection_name = Config.FIRESTORE_COLLECTION
        
        if self.use_firestore:
            try:
                from google.cloud import firestore
                project_id = Config.GOOGLE_CLOUD_PROJECT
                self.db = firestore.Client(project=project_id)
                logger.info(f"Initialized Google Cloud Firestore client for project '{project_id}' (Collection: '{self.collection_name}')")
            except Exception as e:
                logger.warning(f"Could not connect to Firestore ({e}). Falling back to local persistent store.")
                self.db = None
        else:
            logger.info("Firestore disabled by config. Using local JSON store.")

    def save_job(self, job: JobState) -> None:
        """Persist or update job state in Firestore and local snapshot."""
        job_data = job.model_dump()
        
        # 1. Local mirror persistence (always succeeds)
        local_path = LOCAL_STATE_DIR / f"{job.job_id}.json"
        try:
            with open(local_path, "w", encoding="utf-8") as f:
                json.dump(job_data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to write local state mirror: {e}")

        # 2. Firestore cloud persistence
        if self.db is not None:
            try:
                doc_ref = self.db.collection(self.collection_name).document(job.job_id)
                doc_ref.set(job_data)
                logger.debug(f"Saved job {job.job_id} to Firestore collection {self.collection_name}")
            except Exception as e:
                logger.warning(f"Firestore write error for {job.job_id}: {e}")

    def get_job(self, job_id: str) -> Optional[JobState]:
        """Fetch job state from Firestore, with local fallback."""
        # 1. Try Firestore
        if self.db is not None:
            try:
                doc_ref = self.db.collection(self.collection_name).document(job_id)
                doc = doc_ref.get()
                if doc.exists:
                    data = doc.to_dict()
                    return JobState(**data)
            except Exception as e:
                logger.warning(f"Firestore read error for {job_id}: {e}")

        # 2. Try Local fallback
        local_path = LOCAL_STATE_DIR / f"{job_id}.json"
        if local_path.exists():
            try:
                with open(local_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return JobState(**data)
            except Exception as e:
                logger.error(f"Error loading local job state {job_id}: {e}")

        return None

    def list_jobs(self, limit: int = 20) -> List[JobState]:
        """List recent jobs from Firestore or local directory."""
        jobs = []
        if self.db is not None:
            try:
                docs = self.db.collection(self.collection_name).order_by("created_at", direction="DESCENDING").limit(limit).stream()
                for doc in docs:
                    jobs.append(JobState(**doc.to_dict()))
                if jobs:
                    return jobs
            except Exception as e:
                logger.warning(f"Firestore list error: {e}")

        # Fallback to local files
        try:
            for p in sorted(LOCAL_STATE_DIR.glob("*.json"), key=os.path.getmtime, reverse=True)[:limit]:
                with open(p, "r", encoding="utf-8") as f:
                    jobs.append(JobState(**json.load(f)))
        except Exception as e:
            logger.error(f"Local list error: {e}")

        return jobs


job_store = JobStore()
