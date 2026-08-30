import os
import re
import wave
import math
import struct
import logging
from pathlib import Path
from typing import List, Optional
import httpx

try:
    from ..config import Config
    from ..models import KeyMoment, AudioAsset
except ImportError:
    from src.config import Config
    from src.models import KeyMoment, AudioAsset

logger = logging.getLogger("sound_designer_agent")


class SoundDesignerAgent:
    def __init__(self):
        self.freesound_api_key = Config.FREESOUND_API_KEY
        self.has_freesound = bool(self.freesound_api_key and not self.freesound_api_key.startswith("your_"))
        if self.has_freesound:
            logger.info("Freesound API key active. CC-licensed audio search enabled.")
        else:
            logger.info("Freesound API key not configured. Using high-fidelity procedural audio synthesizer engine.")

    def generate_sound_effects_for_moments(
        self,
        moments: List[KeyMoment],
        output_dir: Path
    ) -> List[AudioAsset]:
        """Creates or downloads audio sound effects for each key moment."""
        audio_dir = output_dir / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)

        assets: List[AudioAsset] = []

        for moment in moments:
            slug = self._slugify(moment.moment_title)
            filename = f"moment_{moment.id}_{slug}.wav"
            target_path = audio_dir / filename
            rel_url = f"audio/{filename}"

            logger.info(f"Designing sound effect for Moment {moment.id}: '{moment.sfx_query}'...")

            success = False
            source_type = "procedural_synth"

            # 1. Try Freesound API if key is present
            if self.has_freesound:
                success = self._fetch_freesound_audio(moment.sfx_query, target_path)
                if success:
                    source_type = "freesound"

            # 2. Procedural Audio Synthesizer fallback/primary
            if not success:
                self._synthesize_moment_audio(moment, target_path)
                source_type = "procedural_synth"

            assets.append(
                AudioAsset(
                    moment_id=moment.id,
                    filename=filename,
                    local_path=str(target_path),
                    url_path=rel_url,
                    sfx_name=moment.sfx_query,
                    duration_seconds=1.5,
                    source=source_type,
                    license="CC-BY / Freesound" if source_type == "freesound" else "CC0 Procedural Synthesis"
                )
            )

        return assets

    def _fetch_freesound_audio(self, query: str, output_path: Path) -> bool:
        """Queries Freesound API for CC-licensed sound and downloads preview."""
        try:
            url = "https://freesound.org/apiv2/search/text/"
            params = {
                "query": query,
                "token": self.freesound_api_key,
                "fields": "id,name,previews,license",
                "page_size": 3,
                "filter": "duration:[0.5 TO 4.0]"
            }
            with httpx.Client(timeout=10.0) as client:
                res = client.get(url, params=params)
                if res.status_code == 200:
                    results = res.json().get("results", [])
                    if results:
                        sound = results[0]
                        previews = sound.get("previews", {})
                        preview_url = previews.get("preview-hq-mp3") or previews.get("preview-lq-mp3")
                        if preview_url:
                            audio_res = client.get(preview_url)
                            if audio_res.status_code == 200:
                                with open(output_path, "wb") as f:
                                    f.write(audio_res.content)
                                logger.info(f"Downloaded Freesound audio '{sound.get('name')}' -> {output_path.name}")
                                return True
            logger.warning(f"Freesound query '{query}' returned no suitable results. Falling back to synthesizer.")
        except Exception as e:
            logger.warning(f"Freesound API error for '{query}': {e}")
        return False

    def _synthesize_moment_audio(self, moment: KeyMoment, output_path: Path) -> None:
        """
        Synthesizes crystal-clear 44.1kHz 16-bit mono WAV sound effects
        tailored to the moment's emotional cue.
        """
        sample_rate = 44100
        moment_id = moment.id
        title_lower = (moment.moment_title + " " + moment.sfx_query).lower()

        if "power" in title_lower or "boot" in title_lower or moment_id == 1:
            # Ascending Power-Up Arpeggio: C5 (523Hz) -> E5 (659Hz) -> G5 (784Hz) -> C6 (1046Hz)
            samples = self._synth_arpeggio([523.25, 659.25, 784.00, 1046.50], note_dur=0.18, sample_rate=sample_rate)
        elif "radar" in title_lower or "sweep" in title_lower or "sonar" in title_lower or moment_id == 2:
            # Submarine Sonar Ping & Swept Sine: 900Hz -> 1600Hz -> 750Hz with resonance decay
            samples = self._synth_sonar_ping(sample_rate=sample_rate)
        elif "alert" in title_lower or "shock" in title_lower or "obstacle" in title_lower or moment_id == 3:
            # Dual-tone pulsating 8-bit alarm: 880Hz / 587Hz rapid warble
            samples = self._synth_alert_alarm(sample_rate=sample_rate)
        elif "victory" in title_lower or "fanfare" in title_lower or "celebrat" in title_lower or moment_id == 4:
            # Celebratory Fanfare with Sparkles: C5 -> E5 -> G5 -> C6 (sustained) + harmonic vibrato
            samples = self._synth_victory_fanfare(sample_rate=sample_rate)
        else:
            # High-tech Magic Blip
            samples = self._synth_arpeggio([440.0, 880.0, 1760.0], note_dur=0.15, sample_rate=sample_rate)

        # Write WAV file
        with wave.open(str(output_path), "w") as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            raw_frames = struct.pack(f"<{len(samples)}h", *samples)
            wav_file.writeframes(raw_frames)

        logger.info(f"Synthesized procedural WAV audio -> {output_path.name} ({len(samples)/sample_rate:.2f}s)")

    def _synth_arpeggio(self, freqs: List[float], note_dur: float, sample_rate: int) -> List[int]:
        """Synthesizes a bright, multi-note arpeggio with smooth envelope."""
        samples: List[int] = []
        for freq in freqs:
            num_samples = int(note_dur * sample_rate)
            for i in range(num_samples):
                t = i / sample_rate
                # Envelope: quick attack, smooth exponential decay
                env = math.exp(-3.0 * t / note_dur)
                # Primary sine + overtone for rich chime timber
                val = 0.7 * math.sin(2 * math.pi * freq * t) + 0.3 * math.sin(4 * math.pi * freq * t)
                int_val = int(val * env * 24000)
                samples.append(max(-32767, min(32767, int_val)))
        return samples

    def _synth_sonar_ping(self, sample_rate: int) -> List[int]:
        """Synthesizes a submarine radar sonar pulse with frequency modulation and echo."""
        duration = 1.4
        num_samples = int(duration * sample_rate)
        samples = []
        base_freq = 1100.0

        for i in range(num_samples):
            t = i / sample_rate
            # Sweeping frequency modulated ping
            cur_freq = base_freq + 400.0 * math.sin(2 * math.pi * 3.0 * t) * math.exp(-1.5 * t)
            # Reverb echo envelope
            decay = math.exp(-2.5 * t) + 0.25 * math.exp(-1.2 * max(0, t - 0.25))
            val = math.sin(2 * math.pi * cur_freq * t) * decay
            int_val = int(val * 26000)
            samples.append(max(-32767, min(32767, int_val)))
        return samples

    def _synth_alert_alarm(self, sample_rate: int) -> List[int]:
        """Synthesizes an urgent 8-bit dual-tone alarm beep sequence."""
        samples = []
        pulses = 3
        pulse_dur = 0.25

        for _ in range(pulses):
            num_samples = int(pulse_dur * sample_rate)
            for i in range(num_samples):
                t = i / sample_rate
                freq = 880.0 if (i % (sample_rate // 20)) < (sample_rate // 40) else 659.25
                # Square-ish wave for 8-bit retro arcade feel
                sine = math.sin(2 * math.pi * freq * t)
                val = 0.8 if sine > 0 else -0.8
                env = 1.0 - (t / pulse_dur) * 0.4
                int_val = int(val * env * 20000)
                samples.append(max(-32767, min(32767, int_val)))
            # Short silence between beeps
            silence_samples = int(0.08 * sample_rate)
            samples.extend([0] * silence_samples)

        return samples

    def _synth_victory_fanfare(self, sample_rate: int) -> List[int]:
        """Synthesizes a celebratory level-up fanfare chord."""
        samples = []
        # Intro quick notes
        quick_notes = [523.25, 659.25, 783.99]
        for f in quick_notes:
            num = int(0.12 * sample_rate)
            for i in range(num):
                t = i / sample_rate
                val = math.sin(2 * math.pi * f * t) * math.exp(-2.0 * t / 0.12)
                samples.append(int(val * 22000))

        # Big sustained triumph chord (C6 + E6 + G6)
        chord_dur = 1.2
        chord_samples = int(chord_dur * sample_rate)
        for i in range(chord_samples):
            t = i / sample_rate
            env = math.exp(-1.5 * t)
            # Vibrato
            vib = 1.0 + 0.02 * math.sin(2 * math.pi * 6.0 * t)
            c6 = math.sin(2 * math.pi * 1046.50 * vib * t)
            e6 = math.sin(2 * math.pi * 1318.51 * vib * t)
            g6 = math.sin(2 * math.pi * 1567.98 * vib * t)
            val = (c6 * 0.45 + e6 * 0.35 + g6 * 0.20) * env
            samples.append(int(val * 25000))

        return samples

    def _slugify(self, text: str) -> str:
        slug = re.sub(r"[^\w\s-]", "", text).strip().lower()
        return re.sub(r"[-\s]+", "_", slug)[:20]
