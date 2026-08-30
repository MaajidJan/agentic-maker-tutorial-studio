import os
from pathlib import Path
from dotenv import load_dotenv

# Search for root .env or local .env
CURRENT_DIR = Path(__file__).resolve().parent
SUBMISSION_DIR = CURRENT_DIR.parent
ROOT_DIR = SUBMISSION_DIR.parent

# Load environment variables from root .env first, then local fallback
root_env = ROOT_DIR / ".env"
local_env = SUBMISSION_DIR / ".env"

if root_env.exists():
    load_dotenv(dotenv_path=root_env, override=False)
elif local_env.exists():
    load_dotenv(dotenv_path=local_env, override=False)
else:
    load_dotenv(override=False)


class Config:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
    GEMINI_IMAGE_MODEL: str = os.getenv("GEMINI_IMAGE_MODEL", "gemini-3.1-flash-image")
    
    # Sound Effect API
    FREESOUND_API_KEY: str = os.getenv("FREESOUND_API_KEY", "")
    if FREESOUND_API_KEY.startswith("your_") or not FREESOUND_API_KEY.strip():
        FREESOUND_API_KEY = ""

    # Google Cloud & Firestore Settings
    GOOGLE_CLOUD_PROJECT: str = os.getenv("GOOGLE_CLOUD_PROJECT", os.getenv("GCP_PROJECT", "botrix-agentic-project"))
    FIRESTORE_COLLECTION: str = os.getenv("FIRESTORE_COLLECTION", "botrix_tutorial_jobs")
    USE_FIRESTORE: bool = os.getenv("USE_FIRESTORE", "true").lower() in ("true", "1", "yes")

    # Storage Paths
    OUTPUT_BASE_DIR: Path = SUBMISSION_DIR / "outputs"
    SAMPLE_DATA_DIR: Path = SUBMISSION_DIR / "sample_data"
    STATIC_DIR: Path = SUBMISSION_DIR / "static"

    @classmethod
    def validate_keys(cls) -> dict:
        """Returns the status of all required and optional API keys."""
        return {
            "gemini_api_key_present": bool(cls.GEMINI_API_KEY and not cls.GEMINI_API_KEY.startswith("your_")),
            "freesound_api_key_present": bool(cls.FREESOUND_API_KEY),
            "google_cloud_project": cls.GOOGLE_CLOUD_PROJECT,
            "gemini_model": cls.GEMINI_MODEL,
            "gemini_image_model": cls.GEMINI_IMAGE_MODEL
        }
