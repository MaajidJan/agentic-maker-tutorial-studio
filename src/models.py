from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class JobStatus(str, Enum):
    PENDING = "PENDING"
    ANALYZING = "ANALYZING"
    SCRIPTING = "SCRIPTING"
    GENERATING_ASSETS = "GENERATING_ASSETS"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    REVISING = "REVISING"
    APPROVED = "APPROVED"
    FAILED = "FAILED"


class ComponentItem(BaseModel):
    name: str = Field(..., description="Component name, e.g. HC-SR04 Ultrasonic Sensor")
    purpose: str = Field(..., description="Technical purpose in the circuit")
    kid_description: str = Field(..., description="Fun, kid-friendly explanation (e.g. 'The robot bat-ears that listen for echo bounces!')")


class KeyMoment(BaseModel):
    id: int = Field(..., description="Sequential moment identifier (1 to 5)")
    timestamp_seconds: int = Field(default=0, description="Approximate video timestamp in seconds")
    timestamp_str: str = Field(..., description="Formatted timestamp (e.g. 00:15)")
    moment_title: str = Field(..., description="Short catchy title for the beat")
    description: str = Field(..., description="What happens on screen")
    character_name: str = Field(default="Character", description="Dynamic character or entity chosen by the AI agent to match the prompt and theme")
    theme_or_series: str = Field(default="Dynamic Theme", description="Theme, franchise, anime, style or concept chosen by the AI agent")
    reaction_prompt: str = Field(..., description="Specific emotional expression or pose dynamically chosen by the agent")
    image_search_query: str = Field(default="", description="Targeted web search query dynamically formulated by the agent to find the image")
    sfx_query: str = Field(..., description="Sound effect search term or synthesizer sound signature")


class ScriptCue(BaseModel):
    cue_type: str = Field(..., description="'SFX' or 'REACTION'")
    cue_text: str = Field(..., description="The cue tag contents")


class ScriptLine(BaseModel):
    timestamp_str: str = Field(..., description="Timecode e.g. 00:05")
    speaker: str = Field(default="Host", description="Speaker name (e.g. Host, Botrix)")
    dialogue: str = Field(..., description="Dialogue text with inline cues")
    cues: List[ScriptCue] = Field(default_factory=list)


class TutorialScript(BaseModel):
    title: str = Field(..., description="Exciting kid-friendly video title")
    description: str = Field(..., description="Fun video description with hashtags and takeaways")
    target_age_group: str = Field(default="8-12 years old")
    explanation_summary: str = Field(..., description="Clear explanation of how the device works for kids")
    components: List[ComponentItem] = Field(default_factory=list)
    key_moments: List[KeyMoment] = Field(default_factory=list)
    script_lines: List[ScriptLine] = Field(default_factory=list)
    raw_markdown: Optional[str] = None


class StickerAsset(BaseModel):
    moment_id: int
    filename: str
    local_path: str
    url_path: str
    character_name: str = "Character"
    theme_or_series: str = "Theme"
    emotion: str
    prompt_used: str
    search_query_used: Optional[str] = None
    source_url: Optional[str] = None
    source_type: str = "dynamic_agent_search"  # 'dynamic_agent_search', 'procedural'
    format: str = "PNG"


class AudioAsset(BaseModel):
    moment_id: int
    filename: str
    local_path: str
    url_path: str
    sfx_name: str
    duration_seconds: float = 1.0
    source: str = "procedural_synth"  # 'freesound' or 'procedural_synth'
    license: str = "CC0 / Generated"


class JobState(BaseModel):
    job_id: str
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    status: JobStatus = JobStatus.PENDING
    prompt: str = ""
    media_filenames: List[str] = Field(default_factory=list)
    project_name: Optional[str] = None
    script: Optional[TutorialScript] = None
    key_moments: List[KeyMoment] = Field(default_factory=list)
    stickers: List[StickerAsset] = Field(default_factory=list)
    audio_effects: List[AudioAsset] = Field(default_factory=list)
    revision_history: List[str] = Field(default_factory=list)
    approved: bool = False
    output_dir: Optional[str] = None
    error_message: Optional[str] = None
    progress_percentage: int = 0
    current_step_description: str = "Job initialized"


# API Request / Response models
class CreateJobRequest(BaseModel):
    prompt: str = Field(default="Make this electronics project super fun and interactive for kids with anime-style reaction beats!")
    media_urls: Optional[List[str]] = Field(default_factory=list)


class RevisionRequest(BaseModel):
    revision_note: str = Field(..., description="Feedback note for re-generating or tweaking the script/assets")


class ApprovalRequest(BaseModel):
    approved: bool = True
    export_format: str = "bundle"
