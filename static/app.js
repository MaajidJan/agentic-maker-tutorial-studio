// Botrix Agentic Tutorial Assistant - Frontend Controller

let currentJobId = null;
let pollTimer = null;

// DOM Elements
const jobForm = document.getElementById("jobForm");
const promptInput = document.getElementById("promptInput");
const mediaInput = document.getElementById("mediaInput");
const dropZone = document.getElementById("dropZone");
const filePreviewList = document.getElementById("filePreviewList");
const startBtn = document.getElementById("startBtn");

const pipelineSection = document.getElementById("pipelineSection");
const progressBar = document.getElementById("progressBar");
const activeJobIdBadge = document.getElementById("activeJobIdBadge");

const resultsSection = document.getElementById("resultsSection");
const previewStatusText = document.getElementById("previewStatusText");
const approveBtn = document.getElementById("approveBtn");
const reviseBtn = document.getElementById("reviseBtn");
const downloadZipBtn = document.getElementById("downloadZipBtn");

const extractedProjectName = document.getElementById("extractedProjectName");
const projectTitle = document.getElementById("projectTitle");
const projectDescription = document.getElementById("projectDescription");
const kidExplanation = document.getElementById("kidExplanation");
const componentsList = document.getElementById("componentsList");
const momentsGrid = document.getElementById("momentsGrid");
const scriptContent = document.getElementById("scriptContent");

// Revision Modal Elements
const revisionModal = document.getElementById("revisionModal");
const closeModalBtn = document.getElementById("closeModalBtn");
const cancelRevisionBtn = document.getElementById("cancelRevisionBtn");
const submitRevisionBtn = document.getElementById("submitRevisionBtn");
const revisionNoteInput = document.getElementById("revisionNoteInput");

// Initialize Presets
document.querySelectorAll(".preset-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    promptInput.value = btn.dataset.preset;
  });
});

// File Upload Drag & Drop
dropZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropZone.classList.add("dragover");
});

dropZone.addEventListener("dragleave", () => {
  dropZone.classList.remove("dragover");
});

dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropZone.classList.remove("dragover");
  if (e.dataTransfer.files.length) {
    mediaInput.files = e.dataTransfer.files;
    updateFilePreview();
  }
});

mediaInput.addEventListener("change", updateFilePreview);

function updateFilePreview() {
  const files = mediaInput.files;
  if (!files || files.length === 0) {
    filePreviewList.innerHTML = "";
    return;
  }
  const fileNames = Array.from(files).map(f => `📄 ${f.name} (${(f.size/1024).toFixed(0)} KB)`).join("<br>");
  filePreviewList.innerHTML = `<strong>Selected Files:</strong><br>${fileNames}`;
}

// Form Submission
jobForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const prompt = promptInput.value.trim() || "Make this electronics build exciting for kids with anime reactions!";

  startBtn.disabled = true;
  startBtn.innerHTML = "<span class='btn-icon'>⏳</span> Launching Agent Pipeline...";

  const formData = new FormData();
  formData.append("prompt", prompt);
  if (mediaInput.files.length > 0) {
    for (let i = 0; i < mediaInput.files.length; i++) {
      formData.append("files", mediaInput.files[i]);
    }
  }

  try {
    const res = await fetch("/api/jobs", {
      method: "POST",
      body: formData
    });
    const data = await res.json();
    currentJobId = data.job_id;

    pipelineSection.classList.remove("hidden");
    resultsSection.classList.add("hidden");
    activeJobIdBadge.innerText = `Job ID: ${currentJobId}`;
    
    // Start Polling
    startPolling(currentJobId);
  } catch (err) {
    alert("Failed to submit job: " + err.message);
    startBtn.disabled = false;
    startBtn.innerHTML = "<span class='btn-icon'>⚡</span> Launch Autonomous Agent Pipeline";
  }
});

function startPolling(jobId) {
  if (pollTimer) clearInterval(pollTimer);
  pollTimer = setInterval(() => pollJobStatus(jobId), 1200);
}

async function pollJobStatus(jobId) {
  try {
    const res = await fetch(`/api/jobs/${jobId}`);
    if (!res.ok) return;
    const job = await res.json();

    updateStepperUI(job);

    if (job.status === "AWAITING_APPROVAL" || job.status === "APPROVED") {
      clearInterval(pollTimer);
      renderJobPreview(job);
      startBtn.disabled = false;
      startBtn.innerHTML = "<span class='btn-icon'>⚡</span> Launch Autonomous Agent Pipeline";
    } else if (job.status === "FAILED") {
      clearInterval(pollTimer);
      alert("Pipeline Error: " + (job.error_message || "Unknown error"));
      startBtn.disabled = false;
      startBtn.innerHTML = "<span class='btn-icon'>⚡</span> Launch Autonomous Agent Pipeline";
    }
  } catch (err) {
    console.error("Polling error:", err);
  }
}

function updateStepperUI(job) {
  const percent = job.progress_percentage || 10;
  progressBar.style.width = `${percent}%`;

  const s1 = document.getElementById("stepAnalyzer");
  const s2 = document.getElementById("stepScriptwriter");
  const s3 = document.getElementById("stepArtist");
  const s4 = document.getElementById("stepSound");

  const st1 = document.getElementById("statusAnalyzer");
  const st2 = document.getElementById("statusScriptwriter");
  const st3 = document.getElementById("statusArtist");
  const st4 = document.getElementById("statusSound");

  // Reset
  [s1, s2, s3, s4].forEach(s => s.className = "step-card");

  if (job.status === "ANALYZING") {
    s1.className = "step-card active";
    st1.innerText = "Analyzing Media...";
  } else if (job.status === "SCRIPTING") {
    s1.className = "step-card completed";
    st1.innerText = "Done";
    s2.className = "step-card active";
    st2.innerText = "Writing Script...";
  } else if (job.status === "GENERATING_ASSETS") {
    s1.className = "step-card completed"; st1.innerText = "Done";
    s2.className = "step-card completed"; st2.innerText = "Done";
    s3.className = "step-card active"; st3.innerText = "Generating Stickers...";
    s4.className = "step-card active"; st4.innerText = "Synthesizing Audio...";
  } else if (job.status === "AWAITING_APPROVAL" || job.status === "APPROVED") {
    s1.className = "step-card completed"; st1.innerText = "Done";
    s2.className = "step-card completed"; st2.innerText = "Done";
    s3.className = "step-card completed"; st3.innerText = "Done";
    s4.className = "step-card completed"; st4.innerText = "Done";
  }
}

function renderJobPreview(job) {
  resultsSection.classList.remove("hidden");

  // Project details
  extractedProjectName.innerText = job.project_name || "Smart Robotics Project";
  if (job.script) {
    projectTitle.innerText = job.script.title;
    projectDescription.innerText = job.script.description;
    kidExplanation.innerText = job.script.explanation_summary;

    // Components
    componentsList.innerHTML = "";
    (job.script.components || []).forEach(c => {
      const card = document.createElement("div");
      card.className = "component-card";
      card.innerHTML = `<strong>${c.name}</strong><span>${c.kid_description}</span>`;
      componentsList.appendChild(card);
    });

    // Script Lines with highlighted cues
    scriptContent.innerHTML = "";
    (job.script.script_lines || []).forEach(line => {
      let dialogue = line.dialogue;
      dialogue = dialogue.replace(/\[SFX:\s*([^\]]+)\]/gi, "<span class='highlight-sfx'>[SFX: $1]</span>");
      dialogue = dialogue.replace(/\[REACTION:\s*([^\]]+)\]/gi, "<span class='highlight-reaction'>[REACTION: $1]</span>");

      const row = document.createElement("div");
      row.className = "script-line-item";
      row.innerHTML = `<span class="script-time">[${line.timestamp_str}]</span> <span class="script-speaker">${line.speaker}:</span> <span>${dialogue}</span>`;
      scriptContent.appendChild(row);
    });
  }

  // Key Moments Grid
  momentsGrid.innerHTML = "";
  (job.key_moments || []).forEach(km => {
    const sticker = (job.stickers || []).find(s => s.moment_id === km.id);
    const audio = (job.audio_effects || []).find(a => a.moment_id === km.id);

    const stickerSrc = sticker ? `/outputs/temp_${job.job_id}/${sticker.url_path}` : "";
    const audioSrc = audio ? `/outputs/temp_${job.job_id}/${audio.url_path}` : "";

    const charName = sticker ? (sticker.character_name || km.character_name || "Character") : (km.character_name || "Character");
    const themeName = sticker ? (sticker.theme_or_series || km.theme_or_series || "") : (km.theme_or_series || "");
    const sourceType = sticker ? (sticker.source_type || "dynamic_agent_search") : "dynamic_agent_search";

    const tile = document.createElement("div");
    tile.className = "moment-tile";
    tile.innerHTML = `
      <div class="moment-sticker-preview">
        <img src="${stickerSrc}" alt="${charName} Reaction ${km.id}" onerror="this.src='/static/placeholder.png'" />
        <span class="character-badge">🎭 ${charName} ${themeName ? `• ${themeName}` : ''}</span>
      </div>
      <div class="moment-info">
        <span class="moment-time-tag">Moment ${km.id} &bull; ${km.timestamp_str}</span>
        <h4>${km.moment_title}</h4>
        <p class="moment-action">${km.description}</p>
        <div class="reaction-tag-box">
          <span class="reaction-label">Reaction Beat:</span>
          <em>"${km.reaction_prompt}"</em>
        </div>
        <audio controls src="${audioSrc}"></audio>
      </div>
    `;
    momentsGrid.appendChild(tile);
  });

  if (job.approved) {
    previewStatusText.innerText = "Approved & Exported! 🎉";
    previewStatusText.style.color = "#10b981";
    approveBtn.classList.add("hidden");
    reviseBtn.classList.add("hidden");
    downloadZipBtn.classList.remove("hidden");
  } else {
    previewStatusText.innerText = "Awaiting Director Review";
    previewStatusText.style.color = "#f59e0b";
    approveBtn.classList.remove("hidden");
    reviseBtn.classList.remove("hidden");
    downloadZipBtn.classList.add("hidden");
  }
}

// Approval Action
approveBtn.addEventListener("click", async () => {
  if (!currentJobId) return;
  approveBtn.disabled = true;
  approveBtn.innerText = "Exporting...";

  try {
    const res = await fetch(`/api/jobs/${currentJobId}/approve`, { method: "POST" });
    const data = await res.json();
    alert("🎉 " + data.message);
    pollJobStatus(currentJobId);
  } catch (err) {
    alert("Approval error: " + err.message);
    approveBtn.disabled = false;
    approveBtn.innerText = "✅ Approve & Export Final Package";
  }
});

// Download ZIP
downloadZipBtn.addEventListener("click", () => {
  if (currentJobId) {
    window.location.href = `/api/jobs/${currentJobId}/export`;
  }
});

// Revision Modal Actions
reviseBtn.addEventListener("click", () => {
  revisionModal.classList.remove("hidden");
});

closeModalBtn.addEventListener("click", () => {
  revisionModal.classList.add("hidden");
});

cancelRevisionBtn.addEventListener("click", () => {
  revisionModal.classList.add("hidden");
});

submitRevisionBtn.addEventListener("click", async () => {
  const note = revisionNoteInput.value.trim();
  if (!note) {
    alert("Please enter revision instructions.");
    return;
  }

  submitRevisionBtn.disabled = true;
  submitRevisionBtn.innerText = "Submitting feedback...";

  try {
    await fetch(`/api/jobs/${currentJobId}/revise`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ revision_note: note })
    });
    revisionModal.classList.add("hidden");
    submitRevisionBtn.disabled = false;
    submitRevisionBtn.innerText = "⚡ Re-run Pipeline with Feedback";
    startPolling(currentJobId);
  } catch (err) {
    alert("Revision error: " + err.message);
    submitRevisionBtn.disabled = false;
  }
});
