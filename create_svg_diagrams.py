import os
from pathlib import Path

docs_dir = Path("docs")
docs_dir.mkdir(parents=True, exist_ok=True)

# 1. Architecture Diagram SVG
arch_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 680" width="100%" height="100%">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#070a13" />
      <stop offset="50%" stop-color="#0f172a" />
      <stop offset="100%" stop-color="#070a13" />
    </linearGradient>
    <filter id="shadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="8" stdDeviation="12" flood-color="#000" flood-opacity="0.6"/>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="1200" height="680" fill="url(#bgGrad)" rx="16" />
  <rect width="1198" height="678" x="1" y="1" fill="none" stroke="#1e293b" stroke-width="2" rx="15" />

  <!-- Header Banner -->
  <g transform="translate(40, 35)">
    <rect x="0" y="0" width="310" height="28" rx="14" fill="rgba(56, 189, 248, 0.12)" stroke="rgba(56, 189, 248, 0.3)" stroke-width="1" />
    <text x="15" y="18" fill="#38bdf8" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" letter-spacing="1">⚡ ALL THINGS AGENTIC HACKATHON</text>
    
    <text x="0" y="62" fill="#ffffff" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="28" font-weight="800">Autonomous Agentic Maker Studio</text>
    <text x="0" y="88" fill="#94a3b8" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="14">Multi-Agent AI Architecture • Powered by Google Gemini 3.5 Flash &amp; Google ADK</text>
  </g>

  <!-- Flow Arrows (Connecting Lines) -->
  <g stroke="#334155" stroke-width="2" stroke-dasharray="6,6" fill="none">
    <path d="M 230 330 L 280 330" />
    <path d="M 480 330 L 530 330" />
    <path d="M 730 310 L 780 250" />
    <path d="M 730 350 L 780 410" />
    <path d="M 970 250 L 1000 310 L 1020 310" />
    <path d="M 970 410 L 1000 350 L 1020 350" />
  </g>

  <!-- COL 1: Ingestion Layer -->
  <g transform="translate(40, 160)" filter="url(#shadow)">
    <rect width="190" height="340" rx="14" fill="#0f172a" stroke="#1e293b" stroke-width="1.5" />
    <rect width="190" height="38" rx="14" fill="rgba(255,255,255,0.03)" />
    <text x="16" y="24" fill="#94a3b8" font-family="sans-serif" font-size="11" font-weight="700" letter-spacing="0.5">1. INGESTION LAYER</text>

    <rect x="14" y="55" width="162" height="110" rx="10" fill="#1e293b" stroke="#334155" stroke-width="1" />
    <text x="26" y="80" fill="#f8fafc" font-family="sans-serif" font-size="13" font-weight="700">📷 Project Media</text>
    <text x="26" y="102" fill="#94a3b8" font-family="sans-serif" font-size="11">• Circuit Photos</text>
    <text x="26" y="122" fill="#94a3b8" font-family="sans-serif" font-size="11">• MP4 Video Clips</text>
    <text x="26" y="142" fill="#38bdf8" font-family="sans-serif" font-size="10">Raw Electronics Input</text>

    <rect x="14" y="180" width="162" height="110" rx="10" fill="#1e293b" stroke="#334155" stroke-width="1" />
    <text x="26" y="205" fill="#f8fafc" font-family="sans-serif" font-size="13" font-weight="700">💬 Creative Goal</text>
    <text x="26" y="227" fill="#94a3b8" font-family="sans-serif" font-size="11">• 8-12yo Target Tone</text>
    <text x="26" y="247" fill="#94a3b8" font-family="sans-serif" font-size="11">• Style / Franchise</text>
    <text x="26" y="267" fill="#c084fc" font-family="sans-serif" font-size="10">Zero Hardcoding Prompt</text>
  </g>

  <!-- COL 2: Analyzer Agent -->
  <g transform="translate(280, 160)" filter="url(#shadow)">
    <rect width="200" height="340" rx="14" fill="#0f172a" stroke="rgba(56, 189, 248, 0.4)" stroke-width="1.5" />
    <rect width="200" height="38" rx="14" fill="rgba(56, 189, 248, 0.1)" />
    <text x="16" y="24" fill="#38bdf8" font-family="sans-serif" font-size="11" font-weight="700" letter-spacing="0.5">2. MULTIMODAL ANALYZER</text>

    <g transform="translate(14, 52)">
      <rect width="172" height="42" rx="8" fill="#1e293b" />
      <text x="12" y="22" fill="#38bdf8" font-family="sans-serif" font-size="11" font-weight="700">🧠 Gemini 3.5 Flash</text>
      <text x="12" y="36" fill="#64748b" font-family="sans-serif" font-size="9">Google GenAI SDK</text>
    </g>

    <g transform="translate(14, 106)">
      <text x="0" y="16" fill="#f8fafc" font-family="sans-serif" font-size="12" font-weight="700">Autonomous Reasoning:</text>
      
      <rect x="0" y="26" width="172" height="44" rx="6" fill="rgba(255,255,255,0.03)" stroke="#1e293b" />
      <text x="10" y="44" fill="#cbd5e1" font-family="sans-serif" font-size="10" font-weight="600">Hardware Detection</text>
      <text x="10" y="58" fill="#94a3b8" font-family="sans-serif" font-size="9">Arduino, HC-SR04, Servo</text>

      <rect x="0" y="78" width="172" height="44" rx="6" fill="rgba(255,255,255,0.03)" stroke="#1e293b" />
      <text x="10" y="96" fill="#cbd5e1" font-family="sans-serif" font-size="10" font-weight="600">Kid Analogies</text>
      <text x="10" y="110" fill="#94a3b8" font-family="sans-serif" font-size="9">Bat echo radar sensor</text>

      <rect x="0" y="130" width="172" height="44" rx="6" fill="rgba(255,255,255,0.03)" stroke="#1e293b" />
      <text x="10" y="148" fill="#cbd5e1" font-family="sans-serif" font-size="10" font-weight="600">Key Reaction Moments</text>
      <text x="10" y="162" fill="#38bdf8" font-family="sans-serif" font-size="9">Dynamic Search Queries</text>
    </g>
  </g>

  <!-- COL 3: Scriptwriter Agent -->
  <g transform="translate(530, 160)" filter="url(#shadow)">
    <rect width="200" height="340" rx="14" fill="#0f172a" stroke="rgba(192, 132, 252, 0.4)" stroke-width="1.5" />
    <rect width="200" height="38" rx="14" fill="rgba(192, 132, 252, 0.1)" />
    <text x="16" y="24" fill="#c084fc" font-family="sans-serif" font-size="11" font-weight="700" letter-spacing="0.5">3. SCRIPTWRITER AGENT</text>

    <g transform="translate(14, 52)">
      <rect width="172" height="42" rx="8" fill="#1e293b" />
      <text x="12" y="22" fill="#c084fc" font-family="sans-serif" font-size="11" font-weight="700">✍️ Storyboard Director</text>
      <text x="12" y="36" fill="#64748b" font-family="sans-serif" font-size="9">Google Agent Dev Kit (ADK)</text>
    </g>

    <g transform="translate(14, 106)">
      <text x="0" y="16" fill="#f8fafc" font-family="sans-serif" font-size="12" font-weight="700">Structured Deliverables:</text>
      
      <rect x="0" y="26" width="172" height="44" rx="6" fill="rgba(255,255,255,0.03)" stroke="#1e293b" />
      <text x="10" y="44" fill="#cbd5e1" font-family="sans-serif" font-size="10" font-weight="600">Video Title &amp; Hook</text>
      <text x="10" y="58" fill="#94a3b8" font-family="sans-serif" font-size="9">YouTube &amp; TikTok optimized</text>

      <rect x="0" y="78" width="172" height="52" rx="6" fill="rgba(255,255,255,0.03)" stroke="#1e293b" />
      <text x="10" y="96" fill="#cbd5e1" font-family="sans-serif" font-size="10" font-weight="600">Synchronized Cue Tags</text>
      <text x="10" y="112" fill="#f43f5e" font-family="monospace" font-size="9">[SFX: ping] [REACTION: shock]</text>

      <rect x="0" y="138" width="172" height="36" rx="6" fill="rgba(255,255,255,0.03)" stroke="#1e293b" />
      <text x="10" y="156" fill="#cbd5e1" font-family="sans-serif" font-size="10" font-weight="600">Teleprompter Lines</text>
      <text x="10" y="166" fill="#94a3b8" font-family="sans-serif" font-size="9">Timestamped dialogue</text>
    </g>
  </g>

  <!-- COL 4: Parallel Synthesis -->
  <g transform="translate(780, 160)" filter="url(#shadow)">
    <g transform="translate(0, 0)">
      <rect width="190" height="160" rx="14" fill="#0f172a" stroke="rgba(244, 63, 94, 0.4)" stroke-width="1.5" />
      <rect width="190" height="34" rx="14" fill="rgba(244, 63, 94, 0.1)" />
      <text x="14" y="22" fill="#f43f5e" font-family="sans-serif" font-size="11" font-weight="700">🎨 REACTION STICKER ENGINE</text>
      <text x="14" y="60" fill="#f8fafc" font-family="sans-serif" font-size="11" font-weight="600">• Web Frame Retrieval</text>
      <text x="14" y="80" fill="#94a3b8" font-family="sans-serif" font-size="10">• Real Character Matches</text>
      <text x="14" y="100" fill="#94a3b8" font-family="sans-serif" font-size="10">• PIL 28px White Die-Cut</text>
      <text x="14" y="120" fill="#94a3b8" font-family="sans-serif" font-size="10">• Drop Shadows &amp; Tags</text>
      <rect x="14" y="132" width="162" height="18" rx="4" fill="rgba(244, 63, 94, 0.15)" />
      <text x="20" y="145" fill="#fda4af" font-family="sans-serif" font-size="9" font-weight="700">Output: High-Res PNGs</text>
    </g>

    <g transform="translate(0, 180)">
      <rect width="190" height="160" rx="14" fill="#0f172a" stroke="rgba(52, 211, 153, 0.4)" stroke-width="1.5" />
      <rect width="190" height="34" rx="14" fill="rgba(52, 211, 153, 0.1)" />
      <text x="14" y="22" fill="#34d399" font-family="sans-serif" font-size="11" font-weight="700">🔊 SOUND DESIGNER AGENT</text>
      <text x="14" y="60" fill="#f8fafc" font-family="sans-serif" font-size="11" font-weight="600">• Freesound API Engine</text>
      <text x="14" y="80" fill="#94a3b8" font-family="sans-serif" font-size="10">• 44.1kHz 16-bit WAV Synth</text>
      <text x="14" y="100" fill="#94a3b8" font-family="sans-serif" font-size="10">• Sonar Radar Pings</text>
      <text x="14" y="120" fill="#94a3b8" font-family="sans-serif" font-size="10">• Power Boots &amp; Alarms</text>
      <rect x="14" y="132" width="162" height="18" rx="4" fill="rgba(52, 211, 153, 0.15)" />
      <text x="20" y="145" fill="#a7f3d0" font-family="sans-serif" font-size="9" font-weight="700">Output: Broadcast WAVs</text>
    </g>
  </g>

  <!-- COL 5: Director Desk & Exporter -->
  <g transform="translate(1020, 160)" filter="url(#shadow)">
    <rect width="140" height="340" rx="14" fill="#0f172a" stroke="rgba(56, 189, 248, 0.5)" stroke-width="1.5" />
    <rect width="140" height="38" rx="14" fill="rgba(56, 189, 248, 0.12)" />
    <text x="12" y="24" fill="#38bdf8" font-family="sans-serif" font-size="10" font-weight="700" letter-spacing="0.5">5. REVIEW &amp; EXPORT</text>

    <rect x="10" y="52" width="120" height="95" rx="8" fill="#1e293b" stroke="#334155" />
    <text x="18" y="72" fill="#f8fafc" font-family="sans-serif" font-size="10" font-weight="700">🎛️ Director Desk</text>
    <text x="18" y="90" fill="#94a3b8" font-family="sans-serif" font-size="9">• Live Web UI</text>
    <text x="18" y="106" fill="#94a3b8" font-family="sans-serif" font-size="9">• HITL Feedback</text>
    <text x="18" y="122" fill="#94a3b8" font-family="sans-serif" font-size="9">• Audio Player</text>
    <text x="18" y="138" fill="#38bdf8" font-family="sans-serif" font-size="9" font-weight="600">1-Click Approve</text>

    <rect x="10" y="160" width="120" height="165" rx="8" fill="rgba(56, 189, 248, 0.08)" stroke="rgba(56, 189, 248, 0.3)" />
    <text x="18" y="180" fill="#38bdf8" font-family="sans-serif" font-size="11" font-weight="700">📦 Package</text>
    <text x="18" y="200" fill="#cbd5e1" font-family="sans-serif" font-size="9">📁 stickers/*.png</text>
    <text x="18" y="218" fill="#cbd5e1" font-family="sans-serif" font-size="9">📁 audio/*.wav</text>
    <text x="18" y="236" fill="#cbd5e1" font-family="sans-serif" font-size="9">📄 script.json</text>
    <text x="18" y="254" fill="#cbd5e1" font-family="sans-serif" font-size="9">📄 script.md</text>
    <text x="18" y="272" fill="#cbd5e1" font-family="sans-serif" font-size="9">📄 manifest.json</text>
    <text x="18" y="290" fill="#38bdf8" font-family="sans-serif" font-size="9" font-weight="700">🌐 index.html</text>
    <text x="18" y="310" fill="#10b981" font-family="sans-serif" font-size="8">Standalone Player</text>
  </g>

  <!-- Bottom Tech Stack Pills -->
  <g transform="translate(40, 530)">
    <rect width="1120" height="110" rx="14" fill="#0f172a" stroke="#1e293b" />
    <text x="24" y="32" fill="#94a3b8" font-family="sans-serif" font-size="11" font-weight="700" letter-spacing="1">INFRASTRUCTURE &amp; TECH STACK</text>
    
    <g transform="translate(24, 48)">
      <rect x="0" y="0" width="180" height="42" rx="8" fill="#1e293b" stroke="#334155" />
      <text x="14" y="24" fill="#38bdf8" font-family="sans-serif" font-size="12" font-weight="700">🧠 Gemini 3.5 Flash</text>
      <text x="14" y="36" fill="#64748b" font-family="sans-serif" font-size="9">google-genai SDK</text>

      <rect x="195" y="0" width="180" height="42" rx="8" fill="#1e293b" stroke="#334155" />
      <text x="14" y="24" fill="#c084fc" font-family="sans-serif" font-size="12" font-weight="700">🤖 Google ADK</text>
      <text x="14" y="36" fill="#64748b" font-family="sans-serif" font-size="9">Agent Dev Kit State Flow</text>

      <rect x="390" y="0" width="165" height="42" rx="8" fill="#1e293b" stroke="#334155" />
      <text x="14" y="24" fill="#34d399" font-family="sans-serif" font-size="12" font-weight="700">⚡ Python &amp; FastAPI</text>
      <text x="14" y="36" fill="#64748b" font-family="sans-serif" font-size="9">Async REST &amp; WebSockets</text>

      <rect x="570" y="0" width="170" height="42" rx="8" fill="#1e293b" stroke="#334155" />
      <text x="14" y="24" fill="#38bdf8" font-family="sans-serif" font-size="12" font-weight="700">☁️ Google Cloud Run</text>
      <text x="14" y="36" fill="#64748b" font-family="sans-serif" font-size="9">Serverless Microservice</text>

      <rect x="755" y="0" width="160" height="42" rx="8" fill="#1e293b" stroke="#334155" />
      <text x="14" y="24" fill="#fb923c" font-family="sans-serif" font-size="12" font-weight="700">🔥 Cloud Firestore</text>
      <text x="14" y="36" fill="#64748b" font-family="sans-serif" font-size="9">Async Job State Memory</text>

      <rect x="930" y="0" width="160" height="42" rx="8" fill="#1e293b" stroke="#334155" />
      <text x="14" y="24" fill="#f43f5e" font-family="sans-serif" font-size="12" font-weight="700">🎨 PIL &amp; Synth</text>
      <text x="14" y="36" fill="#64748b" font-family="sans-serif" font-size="9">Die-Cut &amp; 44.1kHz WAV</text>
    </g>
  </g>
</svg>
"""

# 2. Workflow Diagram SVG
workflow_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 480" width="100%" height="100%">
  <defs>
    <linearGradient id="bgGrad2" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0b1120" />
      <stop offset="100%" stop-color="#070a13" />
    </linearGradient>
    <filter id="shadow2" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="6" stdDeviation="10" flood-color="#000" flood-opacity="0.5"/>
    </filter>
  </defs>

  <rect width="1100" height="480" fill="url(#bgGrad2)" rx="16" stroke="#1e293b" stroke-width="2" />

  <g transform="translate(40, 30)">
    <text x="0" y="24" fill="#38bdf8" font-family="sans-serif" font-size="12" font-weight="700" letter-spacing="1">END-TO-END AUTONOMOUS PIPELINE</text>
    <text x="0" y="52" fill="#ffffff" font-family="sans-serif" font-size="24" font-weight="800">State Machine &amp; Human-in-the-Loop Review Cycle</text>
  </g>

  <!-- 5 Sequential Workflow Steps -->
  <g transform="translate(40, 110)">
    <!-- Step 1: Input -->
    <g transform="translate(0, 0)" filter="url(#shadow2)">
      <rect width="180" height="210" rx="12" fill="#0f172a" stroke="#334155" stroke-width="1.5" />
      <circle cx="28" cy="28" r="14" fill="rgba(56, 189, 248, 0.2)" />
      <text x="24" y="33" fill="#38bdf8" font-family="sans-serif" font-size="13" font-weight="800">1</text>
      <text x="50" y="32" fill="#ffffff" font-family="sans-serif" font-size="13" font-weight="700">Ingestion</text>
      
      <text x="16" y="70" fill="#cbd5e1" font-family="sans-serif" font-size="11" font-weight="600">User uploads:</text>
      <text x="16" y="92" fill="#94a3b8" font-family="sans-serif" font-size="10">• Hardware photos/clips</text>
      <text x="16" y="112" fill="#94a3b8" font-family="sans-serif" font-size="10">• Custom creative prompt</text>
      <rect x="14" y="150" width="152" height="40" rx="6" fill="#1e293b" />
      <text x="22" y="174" fill="#38bdf8" font-family="monospace" font-size="10">State: PENDING</text>
    </g>

    <!-- Arrow 1 -->
    <path d="M 190 105 L 220 105" stroke="#38bdf8" stroke-width="3" fill="none" marker-end="url(#arrow)" />

    <!-- Step 2: Analyzer -->
    <g transform="translate(230, 0)" filter="url(#shadow2)">
      <rect width="180" height="210" rx="12" fill="#0f172a" stroke="rgba(56, 189, 248, 0.4)" stroke-width="1.5" />
      <circle cx="28" cy="28" r="14" fill="rgba(56, 189, 248, 0.2)" />
      <text x="24" y="33" fill="#38bdf8" font-family="sans-serif" font-size="13" font-weight="800">2</text>
      <text x="50" y="32" fill="#ffffff" font-family="sans-serif" font-size="13" font-weight="700">Multimodal</text>
      
      <text x="16" y="70" fill="#cbd5e1" font-family="sans-serif" font-size="11" font-weight="600">Gemini 3.5 Flash:</text>
      <text x="16" y="92" fill="#94a3b8" font-family="sans-serif" font-size="10">• Detects components</text>
      <text x="16" y="112" fill="#94a3b8" font-family="sans-serif" font-size="10">• Crafts analogies</text>
      <text x="16" y="132" fill="#94a3b8" font-family="sans-serif" font-size="10">• Formulates search queries</text>
      <rect x="14" y="150" width="152" height="40" rx="6" fill="#1e293b" />
      <text x="22" y="174" fill="#38bdf8" font-family="monospace" font-size="10">State: ANALYZING</text>
    </g>

    <!-- Arrow 2 -->
    <path d="M 420 105 L 450 105" stroke="#c084fc" stroke-width="3" fill="none" />

    <!-- Step 3: Script & Cues -->
    <g transform="translate(460, 0)" filter="url(#shadow2)">
      <rect width="180" height="210" rx="12" fill="#0f172a" stroke="rgba(192, 132, 252, 0.4)" stroke-width="1.5" />
      <circle cx="28" cy="28" r="14" fill="rgba(192, 132, 252, 0.2)" />
      <text x="24" y="33" fill="#c084fc" font-family="sans-serif" font-size="13" font-weight="800">3</text>
      <text x="50" y="32" fill="#ffffff" font-family="sans-serif" font-size="13" font-weight="700">Script &amp; Cues</text>
      
      <text x="16" y="70" fill="#cbd5e1" font-family="sans-serif" font-size="11" font-weight="600">Google ADK Pipeline:</text>
      <text x="16" y="92" fill="#94a3b8" font-family="sans-serif" font-size="10">• YouTube Title &amp; Hook</text>
      <text x="16" y="112" fill="#94a3b8" font-family="sans-serif" font-size="10">• [SFX] sync markers</text>
      <text x="16" y="132" fill="#94a3b8" font-family="sans-serif" font-size="10">• [REACTION] sync beats</text>
      <rect x="14" y="150" width="152" height="40" rx="6" fill="#1e293b" />
      <text x="22" y="174" fill="#c084fc" font-family="monospace" font-size="10">State: SCRIPTING</text>
    </g>

    <!-- Arrow 3 -->
    <path d="M 650 105 L 680 105" stroke="#f43f5e" stroke-width="3" fill="none" />

    <!-- Step 4: Asset Synthesis -->
    <g transform="translate(690, 0)" filter="url(#shadow2)">
      <rect width="180" height="210" rx="12" fill="#0f172a" stroke="rgba(244, 63, 94, 0.4)" stroke-width="1.5" />
      <circle cx="28" cy="28" r="14" fill="rgba(244, 63, 94, 0.2)" />
      <text x="24" y="33" fill="#f43f5e" font-family="sans-serif" font-size="13" font-weight="800">4</text>
      <text x="50" y="32" fill="#ffffff" font-family="sans-serif" font-size="13" font-weight="700">Synthesis</text>
      
      <text x="16" y="70" fill="#cbd5e1" font-family="sans-serif" font-size="11" font-weight="600">Parallel Generation:</text>
      <text x="16" y="92" fill="#94a3b8" font-family="sans-serif" font-size="10">• PIL 28px Die-Cut PNGs</text>
      <text x="16" y="112" fill="#94a3b8" font-family="sans-serif" font-size="10">• 44.1kHz WAV Audio</text>
      <text x="16" y="132" fill="#94a3b8" font-family="sans-serif" font-size="10">• Firestore Job Sync</text>
      <rect x="14" y="150" width="152" height="40" rx="6" fill="#1e293b" />
      <text x="22" y="174" fill="#f43f5e" font-family="monospace" font-size="9">GENERATING_ASSETS</text>
    </g>

    <!-- Arrow 4 -->
    <path d="M 880 105 L 910 105" stroke="#10b981" stroke-width="3" fill="none" />

    <!-- Step 5: Review & Export -->
    <g transform="translate(920, 0)" filter="url(#shadow2)">
      <rect width="100" height="210" rx="12" fill="#0f172a" stroke="rgba(16, 185, 129, 0.5)" stroke-width="1.5" />
      <circle cx="28" cy="28" r="14" fill="rgba(16, 185, 129, 0.2)" />
      <text x="24" y="33" fill="#10b981" font-family="sans-serif" font-size="13" font-weight="800">5</text>
      <text x="48" y="32" fill="#ffffff" font-family="sans-serif" font-size="12" font-weight="700">Export</text>
      
      <text x="10" y="70" fill="#cbd5e1" font-family="sans-serif" font-size="10" font-weight="600">Director:</text>
      <text x="10" y="90" fill="#94a3b8" font-family="sans-serif" font-size="9">• Review Desk</text>
      <text x="10" y="108" fill="#94a3b8" font-family="sans-serif" font-size="9">• HITL notes</text>
      <text x="10" y="126" fill="#10b981" font-family="sans-serif" font-size="9" font-weight="700">• 1-Click ZIP</text>
      <rect x="8" y="150" width="84" height="40" rx="6" fill="#1e293b" />
      <text x="14" y="174" fill="#10b981" font-family="monospace" font-size="9">APPROVED</text>
    </g>
  </g>

  <!-- Human-in-the-Loop Feedback Arc Line -->
  <g transform="translate(0, 340)">
    <path d="M 970 0 Q 700 80 550 0" stroke="#fbbf24" stroke-width="2" stroke-dasharray="6,4" fill="none" />
    <rect x="680" y="24" width="160" height="24" rx="6" fill="#1e293b" stroke="#fbbf24" stroke-width="1" />
    <text x="690" y="40" fill="#fbbf24" font-family="sans-serif" font-size="10" font-weight="700">🔄 Director Revision Loop</text>
  </g>
</svg>
"""

with open(docs_dir / "architecture_diagram.svg", "w", encoding="utf-8") as f:
    f.write(arch_svg.strip())

with open(docs_dir / "workflow_diagram.svg", "w", encoding="utf-8") as f:
    f.write(workflow_svg.strip())

print("Successfully created docs/architecture_diagram.svg and docs/workflow_diagram.svg")
