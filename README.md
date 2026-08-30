# 🤖 Botrix Agentic Tutorial Assistant
> **"All Things Agentic" Hackathon • Taskmaster Track**  
> Autonomous Multimodal AI Agent transforming robotics & electronics media into thrilling, kid-friendly (~8-12yo) tutorial video packages with timestamped scripts, anime reaction stickers, and sound effects.

---

## 🌟 Key Features

1. **Multimodal Circuit & Project Analysis**: Analyzes photos or video clips of electronics builds (e.g. Arduino sonar radar, obstacle robot, LED matrices) using **Gemini 3.5 Flash** to extract project name, a kid-friendly explanation with intuitive analogies, full hardware components list, and 3-5 dramatic key moments.
2. **Kid-Friendly Scriptwriting with Inline Cue Tags**: Automatically composes catchy YouTube/TikTok-style video titles, descriptions, and a full teleprompter script with inline `[SFX: ...]` and `[REACTION: ...]` cue markers synchronized to key moments.
3. **Real Anime Character Reaction Sticker Engine**: Searches and retrieves high-resolution real anime character reaction frames (e.g. *Mikasa Ackerman angry/focused glare*, *Eren Jaeger in shock*, *Anya Forger shock face*, *Luffy laughing victory*, *Goku power-up*) and automatically formats them into stylized, die-cut vinyl reaction stickers with drop shadows and emotion badges. Seamlessly aligns with Attack on Titan, One Piece, Spy x Family, Naruto, and custom anime themes.
4. **Freesound & Procedural Audio Engine**: Searches CC-licensed audio via Freesound API (`FREESOUND_API_KEY`) or synthesizes crystal-clear 44.1kHz 16-bit WAV sound effects (radar sonar pings, power-up arpeggios, alert alarms, level-up victory fanfares) out of the box.
5. **Interactive Director Review & Revision Loop**: Interactive approval flow in CLI and Web UI. Allows the director to review the full teleprompter script, inspect stickers, play audio cues, and provide natural-language revision notes to regenerate or tweak any step.
6. **Package Exporter**: Automatically packages everything into a timestamped local folder with `script.json`, `teleprompter_script.md`, `stickers/`, `audio/`, `manifest.json`, and a standalone interactive `index.html` player.
7. **Google Cloud Infrastructure (Cloud Run + Firestore)**:
   - **Firestore**: Persistent asynchronous job memory and state snapshot store across pipeline steps.
   - **Cloud Run**: Ready-to-deploy HTTP microservice with live streaming web dashboard, REST API, and ZIP package export.

---

## 🚀 Quick Start & Local Execution

### 1. Prerequisites & Environment Setup
Make sure you have Python 3.10+ installed and the environment variables configured in your root `.env`:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.5-flash
GOOGLE_CLOUD_PROJECT=your_gcp_project_id
# Optional: Freesound API Key (for CC-licensed sound downloads from freesound.org)
FREESOUND_API_KEY=your_freesound_api_key_here
```

Install dependencies:
```bash
cd botrix-agentic-submission
pip install -r requirements.txt
```

### 2. Run via Local CLI (Fast Iteration)
Run the agent pipeline directly from the command line:

```bash
# Using the workspace virtual environment:
.venv\Scripts\python.exe botrix-agentic-submission/cli.py

# Custom media and prompt:
.venv\Scripts\python.exe botrix-agentic-submission/cli.py --media botrix-agentic-submission/sample_data/arduino_radar.jpg --prompt "Make this ultrasonic radar build exciting for 10-year-olds with anime reactions and cool sound effects!"

# Non-interactive automated mode:
.venv\Scripts\python.exe botrix-agentic-submission/cli.py --auto-approve
```

**CLI Features:**
- Colored terminal status indicators
- Step-by-step progress tracking
- Interactive Director approval prompt:
  - `[A]` Approve and export final bundle
  - `[R]` Request revision / give feedback notes (e.g. *"Add more bat jokes"*)
  - `[Q]` Quit

---

### 3. Run Web Dashboard Locally
Launch the FastAPI development server:

```bash
.venv\Scripts\python.exe botrix-agentic-submission/main.py
```
Open your browser at **`http://localhost:8080`** to access the Web Studio Dashboard.

---

## ☁️ Google Cloud Deployment (Cloud Run & Firestore)

Follow these exact `gcloud` commands to deploy Botrix as a managed Cloud Run service with Firestore persistence:

### Step 1: Set Active GCP Project
```bash
export GCP_PROJECT="your-gcp-project-id"
gcloud config set project $GCP_PROJECT
```

### Step 2: Enable Required Cloud APIs
```bash
gcloud services enable \
    run.googleapis.com \
    firestore.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com
```

### Step 3: Initialize Firestore (Native Mode)
```bash
gcloud firestore databases create --location=us-central1 --type=firestore-native
```

### Step 4: Deploy to Cloud Run
```bash
gcloud run deploy botrix-agentic-tutorial-assistant \
    --source . \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars "GEMINI_API_KEY=$GEMINI_API_KEY,GEMINI_MODEL=gemini-3.5-flash,GOOGLE_CLOUD_PROJECT=$GCP_PROJECT,USE_FIRESTORE=true,FIRESTORE_COLLECTION=botrix_tutorial_jobs" \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300
```

Once deployed, Google Cloud will provide your live public Cloud Run URL:
```text
Service URL: https://botrix-agentic-tutorial-assistant-xxxxx-uc.a.run.app
```

---

## 📁 Output Deliverables Structure

When a run is approved (via CLI or Web UI), a timestamped directory is created in `outputs/run_YYYYMMDD_HHMMSS_<slug>/`:

```text
outputs/run_20260830_120000_ultrasonic_radar/
├── script.json              # Complete structured JSON metadata, components, and cue lines
├── teleprompter_script.md   # Formatted markdown script with inline [SFX] and [REACTION] tags
├── manifest.json            # Index mapping key moments to generated stickers and audio files
├── index.html               # Standalone interactive HTML player & multimedia viewer
├── stickers/                # Original anime mascot reaction sticker PNGs
│   ├── moment_1_power_up.png
│   ├── moment_2_radar_sweep.png
│   ├── moment_3_alert_triggered.png
│   └── moment_4_victory_cheer.png
└── audio/                   # 44.1kHz sound effect WAV files
    ├── moment_1_power_boot.wav
    ├── moment_2_sonar_ping.wav
    ├── moment_3_obstacle_alarm.wav
    └── moment_4_victory_fanfare.wav
```

---

## 🧪 Running Automated Tests

Run the test suite to verify pipeline functionality:
```bash
pytest tests/ -v
```

---

## 🔑 API Keys & Services Status

| Service / Key | Status | Description |
| :--- | :--- | :--- |
| `GEMINI_API_KEY` | ✅ **Active** | Powers Multimodal Analysis, Scriptwriting & Image Generation (Gemini 3.5 Flash) |
| `GOOGLE_CLOUD_PROJECT` | ✅ **Configured** | Configured for Firestore persistence and Cloud Run deployment |
| `FREESOUND_API_KEY` | ⚡ **Optional / Auto-fallback** | CC-licensed sound effects. If omitted or rate-limited, built-in procedural 44.1kHz audio synthesis engine generates all sound cues automatically. |
| `Firestore` | ✅ **Supported** | Cloud Run job memory with automatic local state mirroring for CLI testing. |
