import os
import sys
import wave
import json
import pytest
from pathlib import Path
from PIL import Image

# Ensure submission root is in sys.path
SUBMISSION_DIR = Path(__file__).resolve().parent.parent
if str(SUBMISSION_DIR) not in sys.path:
    sys.path.insert(0, str(SUBMISSION_DIR))

from src.config import Config
from src.models import (
    JobState, JobStatus, KeyMoment, ComponentItem, TutorialScript, ScriptLine, ScriptCue
)
from src.agents.analyzer import AnalyzerAgent
from src.agents.scriptwriter import ScriptwriterAgent
from src.agents.sticker_artist import StickerArtistAgent
from src.agents.sound_designer import SoundDesignerAgent
from src.agents.orchestrator import orchestrator
from src.exporter import PackageExporter
from src.firestore_store import job_store
from main import app
from fastapi.testclient import TestClient


@pytest.fixture
def sample_moments():
    return [
        KeyMoment(
            id=1,
            timestamp_seconds=5,
            timestamp_str="00:05",
            moment_title="Power Up",
            description="Arduino powers on and LED blinks green",
            character_name="Goku",
            theme_or_series="Dragon Ball",
            reaction_prompt="Goku power up glowing aura",
            image_search_query="Goku power up sticker png",
            sfx_query="power on boot chime"
        ),
        KeyMoment(
            id=2,
            timestamp_seconds=15,
            timestamp_str="00:15",
            moment_title="Radar Sweep",
            description="Servo rotates 180 degrees scanning the room",
            character_name="Mikasa Ackerman",
            theme_or_series="Attack on Titan",
            reaction_prompt="Mikasa intense focus glare",
            image_search_query="Mikasa Ackerman angry focus sticker",
            sfx_query="sonar radar pulse ping"
        ),
        KeyMoment(
            id=3,
            timestamp_seconds=28,
            timestamp_str="00:28",
            moment_title="Object Alert",
            description="Obstacle detected 10cm away",
            character_name="Anya Forger",
            theme_or_series="Spy x Family",
            reaction_prompt="Anya shock face wide eyes",
            image_search_query="Anya Forger shock face sticker",
            sfx_query="retro obstacle alarm alert"
        ),
        KeyMoment(
            id=4,
            timestamp_seconds=40,
            timestamp_str="00:40",
            moment_title="Victory Celebration",
            description="Successful room mapping completed",
            character_name="Luffy",
            theme_or_series="One Piece",
            reaction_prompt="Luffy victory laugh celebration",
            image_search_query="Luffy victory laugh sticker",
            sfx_query="cheerful victory fanfare jingle"
        )
    ]


@pytest.fixture
def sample_components():
    return [
        ComponentItem(name="Arduino Uno", purpose="Microcontroller", kid_description="The master brain!"),
        ComponentItem(name="HC-SR04 Ultrasonic Sensor", purpose="Distance measurement", kid_description="The bat-sonar ears!"),
        ComponentItem(name="SG90 Servo Motor", purpose="Rotation", kid_description="The mechanical neck!")
    ]


def test_analyzer_heuristic_fallback(sample_moments, sample_components):
    analyzer = AnalyzerAgent()
    proj, expl, comps, moments = analyzer._create_heuristic_fallback("test prompt")
    assert "Radar" in proj or len(proj) > 3
    assert len(comps) >= 3
    assert len(moments) >= 3
    assert moments[0].timestamp_str == "00:05"


def test_scriptwriter_parsing(sample_moments, sample_components):
    writer = ScriptwriterAgent()
    mock_json = """
    {
      "title": "I Built a Real Sonar Radar for Kids! 🦇🤖",
      "description": "Learn how to build a secret sonar radar with Arduino!",
      "target_age_group": "8-12 years old",
      "explanation_summary": "Uses sound echoes to detect objects in the room.",
      "script_lines": [
        {
          "timestamp_str": "00:00",
          "speaker": "Host",
          "dialogue": "Welcome makers! Today we are building a sonar radar!"
        },
        {
          "timestamp_str": "00:05",
          "speaker": "Host",
          "dialogue": "Let's turn it on! [SFX: power_chime] [REACTION: botrix_thumbs_up] Look at it boot up!"
        }
      ]
    }
    """
    script = writer._parse_script_response(mock_json, sample_components, sample_moments)
    assert script.title == "I Built a Real Sonar Radar for Kids! 🦇🤖"
    assert len(script.script_lines) == 2
    assert len(script.script_lines[1].cues) == 2
    assert script.script_lines[1].cues[0].cue_type == "SFX"
    assert script.script_lines[1].cues[1].cue_type == "REACTION"


def test_sticker_artist_generation(tmp_path, sample_moments, monkeypatch):
    artist = StickerArtistAgent()
    monkeypatch.setattr(artist, "_search_and_create_real_anime_sticker", lambda m, p: ("https://example.com/anime.png", False, "test query"))
    stickers = artist.generate_stickers_for_moments(sample_moments, tmp_path)
    assert len(stickers) == 4
    for s in stickers:
        path = Path(s.local_path)
        assert path.exists()
        assert path.suffix.lower() == ".png"
        img = Image.open(path)
        assert img.size == (512, 512)
        assert img.mode == "RGBA"


def test_sound_designer_synthesizer(tmp_path, sample_moments, monkeypatch):
    designer = SoundDesignerAgent()
    monkeypatch.setattr(designer, "_fetch_freesound_audio", lambda q, p: False)
    audio_assets = designer.generate_sound_effects_for_moments(sample_moments, tmp_path)
    assert len(audio_assets) == 4
    for a in audio_assets:
        path = Path(a.local_path)
        assert path.exists()
        assert path.suffix.lower() == ".wav"
        with wave.open(str(path), "rb") as wf:
            assert wf.getnchannels() == 1
            assert wf.getsampwidth() == 2
            assert wf.getframerate() == 44100
            assert wf.getnframes() > 0


def test_job_store_persistence(sample_moments, sample_components):
    job_id = "test_job_12345"
    test_job = JobState(
        job_id=job_id,
        status=JobStatus.AWAITING_APPROVAL,
        prompt="Test prompt",
        project_name="Test Arduino Project",
        key_moments=sample_moments
    )
    job_store.save_job(test_job)
    retrieved = job_store.get_job(job_id)
    assert retrieved is not None
    assert retrieved.job_id == job_id
    assert retrieved.project_name == "Test Arduino Project"
    assert len(retrieved.key_moments) == 4


def test_exporter_bundle(tmp_path, sample_moments, sample_components, monkeypatch):
    # Setup working temp directory
    working_dir = tmp_path / "temp_test_job"
    working_dir.mkdir(parents=True, exist_ok=True)

    artist = StickerArtistAgent()
    monkeypatch.setattr(artist, "_search_and_create_real_anime_sticker", lambda m, p: ("https://example.com/anime.png", False, "test query"))
    stickers = artist.generate_stickers_for_moments(sample_moments, working_dir)

    designer = SoundDesignerAgent()
    monkeypatch.setattr(designer, "_fetch_freesound_audio", lambda q, p: False)
    audio = designer.generate_sound_effects_for_moments(sample_moments, working_dir)

    writer = ScriptwriterAgent()
    script = writer._build_fallback_script("Test Radar", "Explanation", sample_components, sample_moments)

    job = JobState(
        job_id="test_export_999",
        status=JobStatus.AWAITING_APPROVAL,
        prompt="Test export prompt",
        project_name="Test Radar Scanner",
        script=script,
        key_moments=sample_moments,
        stickers=stickers,
        audio_effects=audio
    )

    export_dir = PackageExporter.export_package(job)
    assert export_dir.exists()
    assert (export_dir / "script.json").exists()
    assert (export_dir / "teleprompter_script.md").exists()
    assert (export_dir / "manifest.json").exists()
    assert (export_dir / "index.html").exists()
    assert (export_dir / "stickers").exists()
    assert (export_dir / "audio").exists()
    assert len(list((export_dir / "stickers").glob("*.png"))) == 4
    assert len(list((export_dir / "audio").glob("*.wav"))) == 4


def test_fastapi_endpoints(monkeypatch):
    monkeypatch.setattr(orchestrator, "run_pipeline", lambda **kwargs: None)
    client = TestClient(app)
    
    # 1. Health check
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "config" in data

    # 2. Config endpoint
    res_cfg = client.get("/api/config")
    assert res_cfg.status_code == 200
    assert "models" in res_cfg.json()

    # 3. Create job
    res_job = client.post("/api/jobs", data={"prompt": "Test kid robot tutorial"})
    assert res_job.status_code == 200
    job_info = res_job.json()
    assert "job_id" in job_info
    assert job_info["status"] == "PENDING"
