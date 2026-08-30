import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

try:
    from ..config import Config
    from ..models import JobState, JobStatus, TutorialScript
    from ..firestore_store import job_store
    from ..exporter import PackageExporter
    from .analyzer import AnalyzerAgent
    from .scriptwriter import ScriptwriterAgent
    from .sticker_artist import StickerArtistAgent
    from .sound_designer import SoundDesignerAgent
except ImportError:
    from src.config import Config
    from src.models import JobState, JobStatus, TutorialScript
    from src.firestore_store import job_store
    from src.exporter import PackageExporter
    from src.agents.analyzer import AnalyzerAgent
    from src.agents.scriptwriter import ScriptwriterAgent
    from src.agents.sticker_artist import StickerArtistAgent
    from src.agents.sound_designer import SoundDesignerAgent

logger = logging.getLogger("botrix_orchestrator")


class BotrixOrchestrator:
    def __init__(self):
        self.analyzer = AnalyzerAgent()
        self.scriptwriter = ScriptwriterAgent()
        self.sticker_artist = StickerArtistAgent()
        self.sound_designer = SoundDesignerAgent()
        self.store = job_store

    def run_pipeline(
        self,
        media_paths: List[str],
        user_prompt: str,
        job_id: Optional[str] = None
    ) -> JobState:
        """
        Executes the autonomous end-to-end Botrix pipeline:
        1. Multimodal project analysis (Gemini 3.5 Flash)
        2. Storyboard scriptwriting with cues (Gemini 3.5 Flash)
        3. Reaction sticker asset generation (Gemini Image / Vector Synthesizer)
        4. SFX sound design (Freesound / Procedural 44.1kHz Synth)
        5. State persistence in Firestore
        """
        if not job_id:
            job_id = f"job_{uuid.uuid4().hex[:10]}"

        # Initialize output folder for this run's working assets
        working_dir = Config.OUTPUT_BASE_DIR / f"temp_{job_id}"
        working_dir.mkdir(parents=True, exist_ok=True)

        job = JobState(
            job_id=job_id,
            status=JobStatus.ANALYZING,
            prompt=user_prompt,
            media_filenames=[Path(p).name for p in media_paths],
            progress_percentage=10,
            current_step_description="Multimodal project analysis (Gemini 3.5 Flash)..."
        )
        self.store.save_job(job)
        logger.info(f"[{job_id}] Initialized job state. Step 1: Multimodal analysis.")

        try:
            # Step 1: Multimodal Analysis
            project_name, explanation, components, moments = self.analyzer.analyze(
                media_paths=media_paths,
                user_prompt=user_prompt
            )
            job.project_name = project_name
            job.key_moments = moments

            # Step 2: Scriptwriting
            job.status = JobStatus.SCRIPTING
            job.progress_percentage = 35
            job.current_step_description = "Writing kid-friendly script & cue tags..."
            self.store.save_job(job)
            logger.info(f"[{job_id}] Step 2: Generating script for '{project_name}'...")

            script = self.scriptwriter.generate_script(
                project_name=project_name,
                explanation_summary=explanation,
                components=components,
                key_moments=moments,
                user_prompt=user_prompt
            )
            job.script = script

            # Step 3: Sticker & Audio Generation
            job.status = JobStatus.GENERATING_ASSETS
            job.progress_percentage = 60
            job.current_step_description = "Generating original anime mascot stickers & sound effects..."
            self.store.save_job(job)
            logger.info(f"[{job_id}] Step 3: Generating reaction stickers & sound cues...")

            stickers = self.sticker_artist.generate_stickers_for_moments(
                moments=moments,
                output_dir=working_dir
            )
            job.stickers = stickers

            audio_effects = self.sound_designer.generate_sound_effects_for_moments(
                moments=moments,
                output_dir=working_dir
            )
            job.audio_effects = audio_effects

            # Step 4: Awaiting Approval
            job.status = JobStatus.AWAITING_APPROVAL
            job.progress_percentage = 85
            job.current_step_description = "Assets ready! Awaiting director approval or revision notes."
            job.updated_at = datetime.utcnow().isoformat()
            self.store.save_job(job)
            logger.info(f"[{job_id}] Pipeline completed up to preview. Ready for review.")

            return job

        except Exception as e:
            logger.exception(f"[{job_id}] Pipeline execution failed: {e}")
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            job.current_step_description = f"Error: {e}"
            self.store.save_job(job)
            return job

    def revise_job(self, job_id: str, revision_note: str) -> Optional[JobState]:
        """Handles director's revision feedback and regenerates modified script/assets."""
        job = self.store.get_job(job_id)
        if not job:
            logger.error(f"Job {job_id} not found for revision.")
            return None

        logger.info(f"[{job_id}] Processing revision note: '{revision_note}'")
        job.status = JobStatus.REVISING
        job.progress_percentage = 40
        job.revision_history.append(f"[{datetime.utcnow().strftime('%H:%M:%S')}] {revision_note}")
        job.current_step_description = f"Revising script with feedback: {revision_note[:40]}..."
        self.store.save_job(job)

        try:
            working_dir = Config.OUTPUT_BASE_DIR / f"temp_{job_id}"
            working_dir.mkdir(parents=True, exist_ok=True)

            # Regenerate script with revision note
            script = self.scriptwriter.generate_script(
                project_name=job.project_name or "Robotics Project",
                explanation_summary=job.script.explanation_summary if job.script else "",
                components=job.script.components if job.script else [],
                key_moments=job.key_moments,
                user_prompt=job.prompt,
                revision_note=revision_note
            )
            job.script = script

            # Refresh assets if needed
            stickers = self.sticker_artist.generate_stickers_for_moments(
                moments=job.key_moments,
                output_dir=working_dir
            )
            job.stickers = stickers

            audio_effects = self.sound_designer.generate_sound_effects_for_moments(
                moments=job.key_moments,
                output_dir=working_dir
            )
            job.audio_effects = audio_effects

            job.status = JobStatus.AWAITING_APPROVAL
            job.progress_percentage = 85
            job.current_step_description = "Revision complete! Ready for review."
            job.updated_at = datetime.utcnow().isoformat()
            self.store.save_job(job)
            return job

        except Exception as e:
            logger.error(f"[{job_id}] Revision failed: {e}")
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            self.store.save_job(job)
            return job

    def approve_job(self, job_id: str) -> Optional[JobState]:
        """Approves the package and exports the final timestamped bundle."""
        job = self.store.get_job(job_id)
        if not job:
            logger.error(f"Job {job_id} not found for approval.")
            return None

        logger.info(f"[{job_id}] Approved! Exporting final output package...")
        job.status = JobStatus.APPROVED
        job.approved = True
        job.progress_percentage = 100
        job.current_step_description = "Package approved and exported successfully!"

        export_dir = PackageExporter.export_package(job)
        job.output_dir = str(export_dir)
        job.updated_at = datetime.utcnow().isoformat()
        self.store.save_job(job)
        return job


# Singleton orchestrator
orchestrator = BotrixOrchestrator()
