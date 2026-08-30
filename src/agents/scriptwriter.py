import json
import re
import logging
from typing import List, Optional
from google import genai
from google.genai import types

try:
    from ..config import Config
    from ..models import (
        KeyMoment, ComponentItem, TutorialScript, ScriptLine, ScriptCue
    )
except ImportError:
    from src.config import Config
    from src.models import (
        KeyMoment, ComponentItem, TutorialScript, ScriptLine, ScriptCue
    )

logger = logging.getLogger("scriptwriter_agent")


SCRIPTWRITER_SYSTEM_PROMPT = """
You are the Kid-Friendly Electronics Scriptwriter & Storyboard Director.
Your task is to write a thrilling, energetic, educational, and fun video script (~8-12yo audience) for a robotics/electronics tutorial.

You will be given:
- Project Name & Explanation
- Hardware Components
- Key Reaction Moments (with timestamps, real anime character names e.g. Mikasa Ackerman, Eren Jaeger, Anya, Luffy, reaction prompts, and SFX cues)
- Any optional revision notes

You MUST generate a JSON response strictly matching this structure:
{
  "title": "Thrilling Kid-Friendly Video Title (with emoji and curiosity hook)",
  "description": "Engaging YouTube/TikTok style description with bullet points, component checklist, fun facts, and hashtags #MakerKids #Arduino #Robotics #AnimeEd",
  "target_age_group": "8-12 years old",
  "explanation_summary": "Simplified clear explanation of the physics/circuit principles",
  "script_lines": [
    {
      "timestamp_str": "00:00",
      "speaker": "Host",
      "dialogue": "Welcome back, young inventors! Today, we are turning an Arduino into a REAL working sonar radar scanner!"
    },
    {
      "timestamp_str": "00:05",
      "speaker": "Host",
      "dialogue": "Let's flip the power switch! [SFX: power_on_chime] [REACTION: Goku_power_up] Look at those status LEDs wake up with full energy!"
    }
  ]
}

STRICT SCRIPTWRITING RULES:
1. Every Key Moment MUST be represented in the script at its corresponding timestamp.
2. At every key moment, insert inline cue tags:
   - `[SFX: sound_effect_name]` (e.g. `[SFX: radar_sweep_pulse]`)
   - `[REACTION: CharacterName_Emotion]` (e.g. `[REACTION: Mikasa_angry_glare]`, `[REACTION: Eren_shocked]`)
3. The tone must be enthusiastic, encouraging, and clear (like popular science shows for kids: Mark Rober, MythBusters Jr, SciShow Kids).
4. Emphasize safety (e.g. adult supervision when plugging in wires).
5. Output ONLY valid JSON enclosed in ```json ``` markdown codeblocks or raw JSON.
"""


class ScriptwriterAgent:
    def __init__(self):
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        self.model_name = Config.GEMINI_MODEL

    def generate_script(
        self,
        project_name: str,
        explanation_summary: str,
        components: List[ComponentItem],
        key_moments: List[KeyMoment],
        user_prompt: str,
        revision_note: Optional[str] = None
    ) -> TutorialScript:
        """Generates the full timestamped kid-friendly script with inline SFX and REACTION cues."""
        logger.info(f"Generating script for project: '{project_name}' (Revision note: {revision_note})")

        moments_formatted = "\n".join([
            f"- Moment {m.id} [{m.timestamp_str}]: Title: '{m.moment_title}', Action: '{m.description}', Reaction Cue: '{m.reaction_prompt}', SFX: '{m.sfx_query}'"
            for m in key_moments
        ])

        components_formatted = "\n".join([
            f"- {c.name}: {c.kid_description} (Purpose: {c.purpose})"
            for c in components
        ])

        prompt = f"""
{SCRIPTWRITER_SYSTEM_PROMPT}

PROJECT DETAILS:
- Project Name: {project_name}
- Concept Explanation: {explanation_summary}
- User Style/Goal: {user_prompt}

COMPONENTS:
{components_formatted}

KEY MOMENTS & CUES:
{moments_formatted}
"""
        if revision_note:
            prompt += f"""

REVISION / DIRECTOR'S FEEDBACK:
Please adjust the script according to this specific feedback:
"{revision_note}"
Make sure all changes reflect this director note!
"""

        prompt += "\nGenerate the complete script JSON now:"

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    response_mime_type="application/json"
                )
            )
            return self._parse_script_response(response.text, components, key_moments)

        except Exception as e:
            logger.error(f"Scriptwriter API error: {e}. Falling back to standard prompt.")
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                return self._parse_script_response(response.text, components, key_moments)
            except Exception as e2:
                logger.critical(f"Scriptwriter fallback failed: {e2}. Building programmatic script.")
                return self._build_fallback_script(project_name, explanation_summary, components, key_moments)

    def _parse_script_response(
        self,
        text: str,
        components: List[ComponentItem],
        key_moments: List[KeyMoment]
    ) -> TutorialScript:
        """Parses LLM JSON output into TutorialScript."""
        cleaned = text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        data = json.loads(cleaned)

        title = data.get("title", "Super Fun Arduino Robotics Project for Kids! 🤖✨")
        description = data.get("description", "Join us as we build an awesome smart electronics gadget step by step!")
        explanation = data.get("explanation_summary", "Learn how microcontrollers and sensors work together like magic!")

        script_lines: List[ScriptLine] = []
        raw_markdown_lines: List[str] = [
            f"# {title}",
            f"\n> **Target Audience**: 8-12 Years Old | **Project**: {title}\n",
            "## 📋 Description & Overview",
            description,
            "\n## 🛠️ Components Checklist",
        ]
        for c in components:
            raw_markdown_lines.append(f"- **{c.name}**: {c.kid_description}")

        raw_markdown_lines.append("\n## 🎬 Video Teleprompter Script with Cues\n")

        cue_regex = re.compile(r"\[(SFX|REACTION):\s*([^\]]+)\]", re.IGNORECASE)

        for item in data.get("script_lines", []):
            time_str = item.get("timestamp_str", "00:00")
            speaker = item.get("speaker", "Host")
            dialogue = item.get("dialogue", "")

            # Parse cues
            cues: List[ScriptCue] = []
            for match in cue_regex.finditer(dialogue):
                cue_type = match.group(1).upper()
                cue_text = match.group(2).strip()
                cues.append(ScriptCue(cue_type=cue_type, cue_text=cue_text))

            script_lines.append(
                ScriptLine(
                    timestamp_str=time_str,
                    speaker=speaker,
                    dialogue=dialogue,
                    cues=cues
                )
            )
            raw_markdown_lines.append(f"**[{time_str}] {speaker}**: {dialogue}")

        return TutorialScript(
            title=title,
            description=description,
            target_age_group=data.get("target_age_group", "8-12 years old"),
            explanation_summary=explanation,
            components=components,
            key_moments=key_moments,
            script_lines=script_lines,
            raw_markdown="\n".join(raw_markdown_lines)
        )

    def _build_fallback_script(
        self,
        project_name: str,
        explanation_summary: str,
        components: List[ComponentItem],
        key_moments: List[KeyMoment]
    ) -> TutorialScript:
        title = f"I Built a Real {project_name} for Kids! (Secret Radar Powers!) 🦇🤖"
        description = f"Ever wondered how bats navigate in pitch black or how submarines see underwater? In this video, we build {project_name} using Arduino! Learn how sound echo sensors work and build your own gadget."

        script_lines = [
            ScriptLine(
                timestamp_str="00:00",
                speaker="Host",
                dialogue=f"Hey makers! Today we are building something super cool: the {project_name}!"
            ),
            ScriptLine(
                timestamp_str="00:05",
                speaker="Host",
                dialogue="Let's flip on the main power switch! [SFX: power_on_boot_chime] [REACTION: Goku_power_up] It's alive and powering up to maximum level!"
            ),
            ScriptLine(
                timestamp_str="00:15",
                speaker="Host",
                dialogue=f"Watch the servo motor sweep side to side! [SFX: radar_sweep_sonar] [REACTION: Mikasa_angry_glare] It focuses like Mikasa scanning for targets across the room."
            ),
            ScriptLine(
                timestamp_str="00:28",
                speaker="Host",
                dialogue="Uh oh, someone put their hand right in front of our scanner! [SFX: alert_alarm_beep] [REACTION: Eren_shocked] Obstacle detected at 10 centimeters!"
            ),
            ScriptLine(
                timestamp_str="00:40",
                speaker="Host",
                dialogue="Everything is working perfectly! [SFX: victory_fanfare_jingle] [REACTION: Luffy_victory] High fives all around, you are now certified radar engineers!"
            )
        ]

        return TutorialScript(
            title=title,
            description=description,
            target_age_group="8-12 years old",
            explanation_summary=explanation_summary,
            components=components,
            key_moments=key_moments,
            script_lines=script_lines,
            raw_markdown=f"# {title}\n\n{description}"
        )
