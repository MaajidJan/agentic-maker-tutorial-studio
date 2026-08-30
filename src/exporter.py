import os
import json
import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

try:
    from .models import JobState, TutorialScript, KeyMoment, StickerAsset, AudioAsset
    from .config import Config
except ImportError:
    from src.models import JobState, TutorialScript, KeyMoment, StickerAsset, AudioAsset
    from src.config import Config

logger = logging.getLogger("botrix_exporter")


class PackageExporter:
    @staticmethod
    def export_package(job: JobState) -> Path:
        """
        Creates a final timestamped local output folder with all generated assets,
        JSON representations, markdown teleprompter script, and interactive HTML manifest viewer.
        """
        timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        slug_name = (job.project_name or "botrix_tutorial").lower().replace(" ", "_")[:20]
        export_dir = Config.OUTPUT_BASE_DIR / f"run_{timestamp_str}_{slug_name}"
        export_dir.mkdir(parents=True, exist_ok=True)

        stickers_export_dir = export_dir / "stickers"
        audio_export_dir = export_dir / "audio"
        stickers_export_dir.mkdir(exist_ok=True)
        audio_export_dir.mkdir(exist_ok=True)

        # 1. Copy Sticker Assets
        updated_stickers = []
        for s in job.stickers:
            src_path = Path(s.local_path)
            dest_path = stickers_export_dir / s.filename
            if src_path.exists() and src_path.resolve() != dest_path.resolve():
                shutil.copy2(src_path, dest_path)
            s_copy = s.model_copy()
            s_copy.local_path = str(dest_path)
            s_copy.url_path = f"stickers/{s.filename}"
            updated_stickers.append(s_copy)

        # 2. Copy Audio Assets
        updated_audio = []
        for a in job.audio_effects:
            src_path = Path(a.local_path)
            dest_path = audio_export_dir / a.filename
            if src_path.exists() and src_path.resolve() != dest_path.resolve():
                shutil.copy2(src_path, dest_path)
            a_copy = a.model_copy()
            a_copy.local_path = str(dest_path)
            a_copy.url_path = f"audio/{a.filename}"
            updated_audio.append(a_copy)

        # 3. Export script.json
        script_dict = job.script.model_dump() if job.script else {}
        with open(export_dir / "script.json", "w", encoding="utf-8") as f:
            json.dump(script_dict, f, indent=2, default=str)

        # 4. Export teleprompter_script.md
        markdown_content = job.script.raw_markdown if (job.script and job.script.raw_markdown) else ""
        with open(export_dir / "teleprompter_script.md", "w", encoding="utf-8") as f:
            f.write(markdown_content)

        # 5. Export manifest.json (Index mapping)
        manifest = {
            "job_id": job.job_id,
            "exported_at": datetime.utcnow().isoformat(),
            "project_name": job.project_name,
            "title": job.script.title if job.script else "",
            "description": job.script.description if job.script else "",
            "target_age_group": job.script.target_age_group if job.script else "8-12 years old",
            "explanation_summary": job.script.explanation_summary if job.script else "",
            "components": [c.model_dump() for c in (job.script.components if job.script else [])],
            "key_moments_map": []
        }

        for km in job.key_moments:
            sticker = next((s for s in updated_stickers if s.moment_id == km.id), None)
            audio = next((a for a in updated_audio if a.moment_id == km.id), None)
            manifest["key_moments_map"].append({
                "moment_id": km.id,
                "timestamp_str": km.timestamp_str,
                "timestamp_seconds": km.timestamp_seconds,
                "title": km.moment_title,
                "description": km.description,
                "sticker": sticker.model_dump() if sticker else None,
                "audio": audio.model_dump() if audio else None,
                "reaction_prompt": km.reaction_prompt,
                "sfx_query": km.sfx_query
            })

        with open(export_dir / "manifest.json", "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, default=str)

        # 6. Generate interactive HTML manifest viewer
        PackageExporter._generate_interactive_html_viewer(export_dir, manifest, job)

        logger.info(f"Successfully exported final tutorial package to: {export_dir}")
        return export_dir

    @staticmethod
    def _generate_interactive_html_viewer(export_dir: Path, manifest: Dict[str, Any], job: JobState) -> None:
        """Generates a standalone, beautiful HTML previewer for the exported package."""
        moments_html = ""
        for m in manifest.get("key_moments_map", []):
            st = m.get("sticker") or {}
            au = m.get("audio") or {}
            sticker_src = st.get("url_path", "")
            audio_src = au.get("url_path", "")

            char_label = st.get('character_name', 'Character')
            theme_label = st.get('theme_or_series') or st.get('anime_series', '')
            if theme_label:
                char_label += f" • {theme_label}"

            moments_html += f"""
            <div class="moment-card">
              <div class="moment-header">
                <span class="badge">Moment {m.get('moment_id')} &bull; {m.get('timestamp_str')}</span>
                <h3>{m.get('title')}</h3>
              </div>
              <p class="moment-desc">{m.get('description')}</p>
              
              <div class="assets-row">
                <div class="sticker-box">
                  <div class="asset-label">🎨 Dynamic Reaction ({st.get('source_type', 'AI Agent Search')})</div>
                  <img src="{sticker_src}" alt="Sticker {m.get('moment_id')}" class="sticker-img" />
                  <div class="sticker-caption"><strong>{char_label}</strong><br/><em>{st.get('emotion', 'Reaction')}</em></div>
                </div>

                <div class="audio-box">
                  <div class="asset-label">🔊 SFX Cue ({au.get('source', 'Synthesized')})</div>
                  <div class="audio-title">{au.get('sfx_name', 'Sound Effect')}</div>
                  <audio controls src="{audio_src}"></audio>
                </div>
              </div>
            </div>
            """

        components_html = "".join([
            f"<li><strong>{c.get('name')}</strong>: {c.get('kid_description')}</li>"
            for c in manifest.get("components", [])
        ])

        script_lines_html = ""
        if job.script and job.script.script_lines:
            for line in job.script.script_lines:
                dialogue_formatted = line.dialogue
                # Highlight SFX and REACTION tags
                dialogue_formatted = dialogue_formatted.replace("[SFX:", "<span class='cue-sfx'>[SFX:")
                dialogue_formatted = dialogue_formatted.replace("[REACTION:", "<span class='cue-reaction'>[REACTION:")
                dialogue_formatted = dialogue_formatted.replace("]", "]</span>")

                script_lines_html += f"""
                <div class="script-row">
                  <span class="time-tag">[{line.timestamp_str}]</span>
                  <span class="speaker-tag">{line.speaker}:</span>
                  <span class="dialogue-text">{dialogue_formatted}</span>
                </div>
                """

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{manifest.get('title', 'Botrix Tutorial Assistant Package')}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #090d16;
      --card-bg: rgba(22, 30, 49, 0.85);
      --card-border: rgba(56, 189, 248, 0.18);
      --primary: #38bdf8;
      --primary-glow: rgba(56, 189, 248, 0.35);
      --accent: #f43f5e;
      --accent-green: #10b981;
      --text: #f1f5f9;
      --text-muted: #94a3b8;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Plus Jakarta Sans', sans-serif;
      background: radial-gradient(circle at top right, #1e1b4b 0%, var(--bg) 60%);
      color: var(--text);
      min-height: 100vh;
      padding: 2.5rem 1.5rem;
    }}
    .container {{ max-width: 1100px; margin: 0 auto; }}
    header {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 20px;
      padding: 2rem;
      backdrop-filter: blur(12px);
      box-shadow: 0 10px 30px rgba(0,0,0,0.5);
      margin-bottom: 2rem;
    }}
    .logo-badge {{
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      background: rgba(56, 189, 248, 0.12);
      border: 1px solid var(--primary);
      padding: 0.35rem 0.9rem;
      border-radius: 999px;
      font-size: 0.82rem;
      font-weight: 700;
      color: var(--primary);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 1rem;
    }}
    h1 {{
      font-family: 'Outfit', sans-serif;
      font-size: 2.2rem;
      font-weight: 800;
      color: #ffffff;
      line-height: 1.25;
      margin-bottom: 0.8rem;
    }}
    .description {{
      color: var(--text-muted);
      font-size: 1.05rem;
      line-height: 1.6;
      margin-bottom: 1.2rem;
    }}
    .meta-pills {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.75rem;
      margin-top: 1rem;
    }}
    .pill {{
      background: rgba(255,255,255,0.06);
      padding: 0.4rem 0.85rem;
      border-radius: 8px;
      font-size: 0.85rem;
      border: 1px solid rgba(255,255,255,0.1);
    }}
    .section-title {{
      font-family: 'Outfit', sans-serif;
      font-size: 1.5rem;
      font-weight: 700;
      margin: 2.5rem 0 1.2rem 0;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}
    .moments-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 1.5rem;
    }}
    .moment-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 16px;
      padding: 1.5rem;
      backdrop-filter: blur(10px);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: transform 0.2s ease, border-color 0.2s ease;
    }}
    .moment-card:hover {{
      transform: translateY(-4px);
      border-color: var(--primary);
    }}
    .moment-header {{ margin-bottom: 0.8rem; }}
    .badge {{
      display: inline-block;
      font-size: 0.75rem;
      font-weight: 700;
      color: #38bdf8;
      background: rgba(56, 189, 248, 0.15);
      padding: 0.25rem 0.6rem;
      border-radius: 6px;
      margin-bottom: 0.4rem;
    }}
    .moment-card h3 {{
      font-family: 'Outfit', sans-serif;
      font-size: 1.2rem;
      color: #ffffff;
    }}
    .moment-desc {{
      color: var(--text-muted);
      font-size: 0.92rem;
      line-height: 1.5;
      margin-bottom: 1.2rem;
    }}
    .assets-row {{
      display: flex;
      flex-direction: column;
      gap: 1rem;
      background: rgba(0,0,0,0.25);
      padding: 1rem;
      border-radius: 12px;
    }}
    .sticker-box {{ text-align: center; }}
    .asset-label {{
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #94a3b8;
      margin-bottom: 0.5rem;
      font-weight: 600;
    }}
    .sticker-img {{
      max-width: 160px;
      max-height: 160px;
      object-fit: contain;
      filter: drop-shadow(0 6px 12px rgba(0,0,0,0.6));
      transition: transform 0.25s ease;
    }}
    .sticker-img:hover {{ transform: scale(1.08) rotate(3deg); }}
    .sticker-caption {{
      font-size: 0.8rem;
      color: #cbd5e1;
      margin-top: 0.4rem;
    }}
    .audio-box {{
      display: flex;
      flex-direction: column;
      gap: 0.4rem;
    }}
    .audio-title {{
      font-size: 0.85rem;
      font-weight: 600;
      color: #38bdf8;
    }}
    audio {{ width: 100%; height: 36px; border-radius: 8px; }}
    .script-container {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 16px;
      padding: 1.5rem;
      margin-top: 1rem;
    }}
    .script-row {{
      padding: 0.75rem 0;
      border-bottom: 1px solid rgba(255,255,255,0.06);
      font-size: 0.95rem;
      line-height: 1.6;
    }}
    .script-row:last-child {{ border-bottom: none; }}
    .time-tag {{ color: #38bdf8; font-weight: 700; margin-right: 0.5rem; font-family: monospace; }}
    .speaker-tag {{ color: #f43f5e; font-weight: 700; margin-right: 0.5rem; }}
    .cue-sfx {{
      background: rgba(245, 158, 11, 0.2);
      border: 1px solid #f59e0b;
      color: #fbbf24;
      padding: 0.15rem 0.45rem;
      border-radius: 4px;
      font-weight: 600;
      font-size: 0.85rem;
    }}
    .cue-reaction {{
      background: rgba(236, 72, 153, 0.2);
      border: 1px solid #ec4899;
      color: #f472b6;
      padding: 0.15rem 0.45rem;
      border-radius: 4px;
      font-weight: 600;
      font-size: 0.85rem;
    }}
    .components-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 16px;
      padding: 1.5rem;
      margin-top: 1rem;
    }}
    .components-card ul {{ padding-left: 1.2rem; line-height: 1.8; color: #cbd5e1; }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="logo-badge">🤖 Botrix Agentic Tutorial Package</div>
      <h1>{manifest.get('title', 'Tutorial Video Package')}</h1>
      <p class="description">{manifest.get('description', '')}</p>
      <div class="meta-pills">
        <div class="pill">🎯 Target: <strong>{manifest.get('target_age_group')}</strong></div>
        <div class="pill">⚡ Exported: <strong>{manifest.get('exported_at')[:19].replace('T', ' ')} UTC</strong></div>
        <div class="pill">📦 Job ID: <strong>{manifest.get('job_id')}</strong></div>
      </div>
    </header>

    <h2 class="section-title">✨ Key Moments, Anime Stickers & Sound Effects</h2>
    <div class="moments-grid">
      {moments_html}
    </div>

    <h2 class="section-title">🛠️ Hardware Components Checklist</h2>
    <div class="components-card">
      <ul>
        {components_html}
      </ul>
    </div>

    <h2 class="section-title">🎬 Teleprompter Script with Live Cues</h2>
    <div class="script-container">
      {script_lines_html}
    </div>
  </div>
</body>
</html>
"""
        with open(export_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(html_content)
