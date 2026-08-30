import os
import json
import re
import logging
from pathlib import Path
from typing import List, Optional, Tuple
from google import genai
from google.genai import types

try:
    from ..config import Config
    from ..models import KeyMoment, ComponentItem, JobState, JobStatus
except ImportError:
    from src.config import Config
    from src.models import KeyMoment, ComponentItem, JobState, JobStatus

logger = logging.getLogger("analyzer_agent")


ANALYZER_SYSTEM_PROMPT = """
You are the Botrix Multimodal Project Analyzer & Dynamic Reaction Director.
Your mission is to inspect the provided video/photos and user prompt of an electronics/robotics build, and extract structured insights for a kid-friendly (~8-12 years old) tutorial video.

DYNAMIC AGENTIC CREATIVITY RULES:
1. You have complete agentic freedom to choose characters, themes, aesthetics, and emotional reactions that BEST match whatever the user asks for in their prompt (e.g. any anime like Jujutsu Kaisen, Demon Slayer, Attack on Titan, One Piece, Studio Ghibli, Naruto; or gaming like Pokémon, Minecraft, Mario, Zelda; or sci-fi / superhero / cartoon / cyberpunk / retro styles).
2. If the user prompt mentions a specific style or franchise, STRICTLY respect and embrace that theme with relevant characters.
3. For each key moment, formulate a crisp, targeted `image_search_query` that our image retrieval agent can use to find the exact high-res character reaction frame on the web.

You MUST produce a valid JSON object strictly matching this schema:
{
  "project_name": "Catchy Name of the Project (e.g. Ultrasonic Radar Scanner 3000)",
  "explanation_summary": "A super clear, exciting explanation of how this project works tailored for an 8-12 year old kid. Use fun analogies (e.g. bats echolocating, electric nerves, robot superhero vision).",
  "components": [
    {
      "name": "Component Name (e.g. HC-SR04 Ultrasonic Sensor)",
      "purpose": "Technical role in the circuit",
      "kid_description": "Fun kid-friendly description of what it does (e.g. 'The robot ears that shout invisible sound waves and time the echo!')"
    }
  ],
  "key_moments": [
    {
      "id": 1,
      "timestamp_seconds": 5,
      "timestamp_str": "00:05",
      "moment_title": "Power On & Boot Sequence",
      "description": "The Arduino LED lights up and the servo initializes.",
      "character_name": "Name of chosen character (e.g. Gojo Satoru, Pikachu, Luffy, Goku, Miles Morales)",
      "theme_or_series": "Franchise or theme (e.g. Jujutsu Kaisen, Pokemon, One Piece, Cyberpunk)",
      "reaction_prompt": "Specific emotional expression (e.g. 'Gojo Satoru confident smile lowering blindfold')",
      "image_search_query": "Targeted image search string (e.g. 'Gojo Satoru confident smile anime sticker png')",
      "sfx_query": "high tech futuristic power on boot chime"
    }
  ]
}

CRITICAL RULES:
1. Provide between 3 to 5 distinct key moments with realistic timestamps.
2. Select dynamic, expressive character moments that fit the emotional beat (booting up, scanning, obstacle shock/alert, celebration victory).
3. Keep the language fun, safe, motivating, and easy to understand for young makers.
4. Output ONLY valid JSON, enclosed in ```json ``` markdown codeblocks or raw JSON.
"""


class AnalyzerAgent:
    def __init__(self):
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        self.model_name = Config.GEMINI_MODEL

    def analyze(self, media_paths: List[str], user_prompt: str) -> Tuple[str, str, List[ComponentItem], List[KeyMoment]]:
        """
        Multimodal analysis of input media and prompt using Gemini.
        Returns: (project_name, explanation_summary, components, key_moments)
        """
        logger.info(f"Starting multimodal analysis on {len(media_paths)} media files with prompt: '{user_prompt}'")
        contents = []

        # Prepare multimodal media parts
        for media_path in media_paths:
            path_obj = Path(media_path)
            if not path_obj.exists():
                logger.warning(f"Media file not found: {media_path}")
                continue

            suffix = path_obj.suffix.lower()
            try:
                if suffix in [".jpg", ".jpeg", ".png", ".webp", ".gif"]:
                    with open(path_obj, "rb") as f:
                        image_bytes = f.read()
                    mime_type = "image/jpeg" if suffix in [".jpg", ".jpeg"] else f"image/{suffix.replace('.', '')}"
                    contents.append(
                        types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
                    )
                    logger.info(f"Loaded image part from {path_obj.name} ({len(image_bytes)} bytes)")
                elif suffix in [".mp4", ".mov", ".avi", ".webm", ".mkv"]:
                    logger.info(f"Uploading video file to Gemini: {path_obj.name}")
                    file_ref = self.client.files.upload(file=str(path_obj))
                    contents.append(file_ref)
            except Exception as e:
                logger.error(f"Error loading media file {media_path}: {e}")

        # Add instructions and user prompt
        prompt_text = f"""
{ANALYZER_SYSTEM_PROMPT}

USER GOAL & INSTRUCTIONS:
{user_prompt}

Analyze the provided media and create the structured JSON output now:
"""
        contents.append(prompt_text)

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=0.4,
                    response_mime_type="application/json"
                )
            )
            raw_text = response.text
            logger.info("Received Gemini analyzer response")
            return self._parse_response(raw_text)

        except Exception as e:
            logger.error(f"Analyzer API call error: {e}. Attempting fallback parser.")
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=contents,
                )
                return self._parse_response(response.text)
            except Exception as e2:
                logger.critical(f"Multimodal analysis completely failed: {e2}")
                return self._create_heuristic_fallback(user_prompt)

    def _parse_response(self, text: str) -> Tuple[str, str, List[ComponentItem], List[KeyMoment]]:
        """Parses the JSON response into typed models."""
        cleaned = text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        data = json.loads(cleaned)
        project_name = data.get("project_name", "Awesome Electronics Robot Build")
        explanation = data.get("explanation_summary", "An exciting hands-on electronics project built with microcontrollers, sensors, and actuators!")

        components = [
            ComponentItem(
                name=c.get("name", "Electronic Component"),
                purpose=c.get("purpose", "Circuit element"),
                kid_description=c.get("kid_description", "A cool part that makes the project work!")
            )
            for c in data.get("components", [])
        ]

        key_moments = []
        for i, km in enumerate(data.get("key_moments", []), start=1):
            char_name = km.get("character_name") or km.get("anime_character") or "Hero Character"
            theme_name = km.get("theme_or_series") or km.get("anime_series") or "Anime / Sci-Fi"
            reaction = km.get("reaction_prompt") or f"{char_name} dynamic emotion"
            search_query = km.get("image_search_query") or f"{char_name} {reaction} sticker png"

            key_moments.append(
                KeyMoment(
                    id=km.get("id", i),
                    timestamp_seconds=km.get("timestamp_seconds", (i - 1) * 15),
                    timestamp_str=km.get("timestamp_str", f"00:{(i - 1) * 15:02d}"),
                    moment_title=km.get("moment_title", f"Key Moment {i}"),
                    description=km.get("description", "Exciting action beat in the build"),
                    character_name=char_name,
                    theme_or_series=theme_name,
                    reaction_prompt=reaction,
                    image_search_query=search_query,
                    sfx_query=km.get("sfx_query", "retro arcade power up chime")
                )
            )

        if not key_moments:
            key_moments = self._default_moments()

        return project_name, explanation, components, key_moments

    def _default_moments(self) -> List[KeyMoment]:
        return [
            KeyMoment(
                id=1,
                timestamp_seconds=5,
                timestamp_str="00:05",
                moment_title="Powering Up The Circuit",
                description="The microcontroller powers on and status lights turn green.",
                character_name="Gojo Satoru",
                theme_or_series="Jujutsu Kaisen",
                reaction_prompt="Gojo Satoru confident smile lowering blindfold glowing aura",
                image_search_query="Gojo Satoru confident smile anime sticker png",
                sfx_query="high tech futuristic power on boot chime"
            ),
            KeyMoment(
                id=2,
                timestamp_seconds=18,
                timestamp_str="00:18",
                moment_title="Active Radar Sweep",
                description="The sensor sweeps side to side scanning the environment.",
                character_name="Mikasa Ackerman",
                theme_or_series="Attack on Titan",
                reaction_prompt="Mikasa Ackerman intense focused scanning eye glare",
                image_search_query="Mikasa Ackerman focused glare anime sticker",
                sfx_query="radar sweep sonar ping pulse"
            ),
            KeyMoment(
                id=3,
                timestamp_seconds=32,
                timestamp_str="00:32",
                moment_title="Obstacle Alert Detected",
                description="Sensor detects an obstacle close up!",
                character_name="Anya Forger",
                theme_or_series="Spy x Family",
                reaction_prompt="Anya Forger iconic surprised shock face wide eyes meme",
                image_search_query="Anya Forger shock face meme sticker png",
                sfx_query="retro game obstacle alert beep alarm"
            ),
            KeyMoment(
                id=4,
                timestamp_seconds=45,
                timestamp_str="00:45",
                moment_title="Mission Accomplished Victory",
                description="Successful test sequence completed!",
                character_name="Luffy",
                theme_or_series="One Piece",
                reaction_prompt="Luffy joyful victory open laugh celebration hands up",
                image_search_query="Luffy Gear 5 laughing victory anime sticker png",
                sfx_query="cheerful video game victory level up fanfare jingle"
            )
        ]

    def _create_heuristic_fallback(self, prompt: str) -> Tuple[str, str, List[ComponentItem], List[KeyMoment]]:
        project_name = "Arduino Smart Radar & Scanner"
        explanation = "This smart radar sends out silent ultrasonic sound waves (just like a bat!) to measure distance, while a servo motor rotates it 180 degrees to map the entire room."
        components = [
            ComponentItem(name="Arduino Microcontroller", purpose="Main brain", kid_description="The master brain that runs our code instructions!"),
            ComponentItem(name="HC-SR04 Ultrasonic Sensor", purpose="Distance measurement", kid_description="The bat-ears that shout sound pulses and time the echo return!"),
            ComponentItem(name="SG90 Micro Servo Motor", purpose="Physical rotation", kid_description="The robotic neck muscle that turns the sensor back and forth!"),
            ComponentItem(name="Breadboard & Jumper Wires", purpose="Circuit interconnects", kid_description="The super-highway wires that carry electricity and signals!")
        ]
        return project_name, explanation, components, self._default_moments()
