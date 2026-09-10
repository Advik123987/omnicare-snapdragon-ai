/**
 * OmniCare AI - Ultra-Professional Clinical Cockpit Client Logic
 * Integrates:
 * - Real-time lesion canvas with Grad-CAM heatmap blending
 * - Web Audio API pulmonary breath acoustics synthesis
 * - Retinal fundus screening visualization
 * - 1-Click ABDM FHIR R4 JSON modal & download
 * - HP Wolf Security Encrypted Vault inspector
 * - HP AI Companion natural language query bridge
 */

const API_BASE = window.location.origin.includes(':8000') 
  ? window.location.origin 
  : 'http://localhost:8000';

let currentVisionResult = null;
let currentAudioResult = null;
let currentSoapResult = null;
let gradcamOpacity = 0.5;
let currentModality = 'lesion'; // 'lesion' or 'retina'

let currentPatient = {
  patient_id: "P-10024",
  name: "Aarav Mehra",
  age: 42,
  gender: "Male",
  abha_id: "aarav.mehra@abdm"
};

document.addEventListener('DOMContentLoaded', () => {
  initSpectrogram();
  initLesionCanvas();
  pollTelemetry();
  setInterval(pollTelemetry, 3000);
});

// Telemetry Polling
async function pollTelemetry() {
  try {
    const res = await fetch(`${API_BASE}/api/telemetry`);
    if (res.ok) {
      const data = await res.json();
      document.getElementById('nav-tops').innerText = `${data.peak_tops} TOPS`;
      document.getElementById('nav-latency').innerText = `${data.mean_latency_ms} ms`;
      document.getElementById('nav-fps').innerText = `${data.current_fps} FPS`;
    }
  } catch (err) {
    console.warn("Telemetry polling offline (fallback to simulation):", err);
  }
}

// ----------------- Canvas & Vision Rendering with Grad-CAM -----------------
function initLesionCanvas() {
  const canvas = document.getElementById('lesion-canvas');
  if (!canvas) return;
  canvas.width = 440;
  canvas.height = 290;
  drawSimulatedLesion("Melanoma", true, gradcamOpacity);
}

function updateGradcamOpacity(val) {
  gradcamOpacity = parseFloat(val);
  document.getElementById('gradcam-val').innerText = `${Math.round(gradcamOpacity * 100)}%`;
  const cond = currentVisionResult ? currentVisionResult.primary_condition : "Melanoma";
  if (currentModality === 'lesion') {
    drawSimulatedLesion(cond, true, gradcamOpacity);
  } else {
    drawSimulatedRetina(cond, gradcamOpacity);
  }
}

function drawSimulatedLesion(condition, withMask = true, heatmapAlpha = 0.5) {
  const canvas = document.getElementById('lesion-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  
  ctx.fillStyle = '#080C16';
  ctx.fillRect(0, 0, 440, 290);

  // Background skin tone
  const grad = ctx.createRadialGradient(220, 145, 30, 220, 145, 180);
  grad.addColorStop(0, '#D4A373');
  grad.addColorStop(1, '#9C6644');
  ctx.fillStyle = grad;
  ctx.beginPath();
  ctx.arc(220, 145, 135, 0, Math.PI * 2);
  ctx.fill();

  // Draw asymmetrical lesion pigment
  ctx.save();
  ctx.translate(220, 145);
  ctx.beginPath();
  
  const isMalignant = (condition === "Melanoma" || condition === "Basal Cell Carcinoma (BCC)");
  const points = 16;
  for (let i = 0; i <= points; i++) {
    const angle = (i / points) * Math.PI * 2;
    const rBase = isMalignant ? 54 : 38;
    const deform = isMalignant ? Math.sin(angle * 3) * 15 + Math.cos(angle * 5) * 8 : Math.sin(angle * 2) * 3;
    const r = rBase + deform;
    const px = Math.cos(angle) * r;
    const py = Math.sin(angle) * r;
    if (i === 0) ctx.moveTo(px, py);
    else ctx.lineTo(px, py);
  }
  ctx.closePath();

  // Irregular pigment
  const lesionGrad = ctx.createRadialGradient(5, -5, 5, 0, 0, 65);
  lesionGrad.addColorStop(0, isMalignant ? '#1A0E08' : '#4A2810');
  lesionGrad.addColorStop(0.5, isMalignant ? '#3D1308' : '#6F3D1B');
  lesionGrad.addColorStop(1, isMalignant ? '#681D0B' : '#8A5129');
  ctx.fillStyle = lesionGrad;
  ctx.fill();

  // Draw Grad-CAM Visual Attention Saliency Heatmap
  if (heatmapAlpha > 0.05) {
    ctx.save();
    ctx.globalAlpha = heatmapAlpha;
    const camGrad = ctx.createRadialGradient(10, -10, 5, 0, 0, 80);
    camGrad.addColorStop(0, 'rgba(255, 0, 0, 0.9)');    // High activation
    camGrad.addColorStop(0.4, 'rgba(255, 200, 0, 0.7)'); // Medium activation
    camGrad.addColorStop(0.8, 'rgba(0, 200, 255, 0.4)'); // Low activation
    camGrad.addColorStop(1, 'transparent');
    ctx.fillStyle = camGrad;
    ctx.beginPath();
    ctx.arc(5, -5, 80, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }

  // Overlay Segmentation Contour Mask
  if (withMask) {
    ctx.lineWidth = 2.5;
    ctx.strokeStyle = isMalignant ? '#EF4444' : '#10B981';
    ctx.shadowColor = isMalignant ? '#EF4444' : '#10B981';
    ctx.shadowBlur = 10;
    ctx.stroke();

    // Bounding Caliber Crosshair (ABCD Diameter)
    ctx.shadowBlur = 0;
    ctx.strokeStyle = 'rgba(0, 240, 255, 0.75)';
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.moveTo(-68, 0); ctx.lineTo(68, 0);
    ctx.moveTo(0, -58); ctx.lineTo(0, 58);
    ctx.stroke();
    ctx.setLineDash([]);

    // Caliber Text
    ctx.fillStyle = '#00F0FF';
    ctx.font = '11px monospace';
    ctx.fillText('NPU CALIBER: 7.2mm', -65, 75);
  }
  ctx.restore();
}

function drawSimulatedRetina(condition, heatmapAlpha = 0.5) {
  const canvas = document.getElementById('lesion-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  ctx.fillStyle = '#080C16';
  ctx.fillRect(0, 0, 440, 290);

  // Retinal orange-red circular fundus
  const grad = ctx.createRadialGradient(220, 145, 40, 220, 145, 130);
  grad.addColorStop(0, '#C84B18');
  grad.addColorStop(0.8, '#8D2700');
  grad.addColorStop(1, '#3B0F00');
  ctx.fillStyle = grad;
  ctx.beginPath();
  ctx.arc(220, 145, 130, 0, Math.PI * 2);
  ctx.fill();

  // Optic Disc
  ctx.fillStyle = '#FCE77D';
  ctx.beginPath();
  ctx.arc(170, 145, 24, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = '#FFF8DB';
  ctx.beginPath();
  ctx.arc(170, 145, 12, 0, Math.PI * 2);
  ctx.fill();

  // Blood vessels
  ctx.strokeStyle = '#5E1000';
  ctx.lineWidth = 2.5;
  ctx.beginPath();
  ctx.moveTo(170, 145);
  ctx.bezierCurveTo(200, 110, 250, 90, 310, 80);
  ctx.moveTo(170, 145);
  ctx.bezierCurveTo(210, 170, 270, 200, 320, 210);
  ctx.stroke();

  // Grad-CAM on macula
  if (heatmapAlpha > 0.05) {
    ctx.save();
    ctx.globalAlpha = heatmapAlpha;
    const camGrad = ctx.createRadialGradient(260, 145, 5, 260, 145, 45);
    camGrad.addColorStop(0, 'rgba(255, 0, 0, 0.85)');
    camGrad.addColorStop(0.6, 'rgba(255, 200, 0, 0.5)');
    camGrad.addColorStop(1, 'transparent');
    ctx.fillStyle = camGrad;
    ctx.beginPath();
    ctx.arc(260, 145, 45, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }

  // Crosshair
  ctx.strokeStyle = '#00F0FF';
  ctx.lineWidth = 1.5;
  ctx.strokeRect(235, 120, 50, 50);
  ctx.fillStyle = '#00F0FF';
  ctx.font = '10px monospace';
  ctx.fillText('MACULAR EXUDATE (NPU)', 230, 185);
}

// ----------------- Trigger Vision Screening -----------------
async function runVisionScreening(conditionPreset = "Melanoma") {
  currentModality = 'lesion';
  const btn = event?.target;
  if (btn) btn.innerText = "NPU Inferring...";

  try {
    const formData = new FormData();
    formData.append('lesion_type_hint', conditionPreset);

    const res = await fetch(`${API_BASE}/api/diagnostic/vision/lesion`, {
      method: 'POST',
      body: formData
    });

    if (res.ok) {
      currentVisionResult = await res.json();
      updateVisionUI(currentVisionResult);
      await runSoapScribe();
    }
  } catch (err) {
    console.error("Vision screening error:", err);
  } finally {
    if (btn) btn.innerText = "Trigger NPU Lesion Scan";
  }
}

async function runRetinaScreening() {
  currentModality = 'retina';
  try {
    const res = await fetch(`${API_BASE}/api/diagnostic/vision/retina`, { method: 'POST' });
    if (res.ok) {
      currentVisionResult = await res.json();
      drawSimulatedRetina(currentVisionResult.primary_condition, gradcamOpacity);
      document.getElementById('vision-latency').innerText = `${currentVisionResult.inference_latency_ms} ms | Hexagon NPU`;
      document.getElementById('diag-condition').innerText = `${currentVisionResult.primary_condition} (${currentVisionResult.confidence_pct}% Confidence)`;
      document.getElementById('diag-icd').innerText = `Ophthalmology Screening • Cup-to-Disc: ${currentVisionResult.optic_disc_cup_to_disc_ratio}`;
      await runSoapScribe();
    }
  } catch (err) {
    console.error("Retina screening error:", err);
  }
}

function updateVisionUI(data) {
  drawSimulatedLesion(data.primary_condition, true, gradcamOpacity);

  document.getElementById('vision-latency').innerText = `${data.inference_latency_ms} ms | Hexagon NPU`;

  const abcd = data.abcd_explainable_ai;
  document.getElementById('val-asym').innerText = `${abcd.asymmetry.score_pct}%`;
  document.getElementById('sub-asym').innerText = abcd.asymmetry.clinical_grade;

  document.getElementById('val-border').innerText = `${abcd.border.compactness_ratio}`;
  document.getElementById('sub-border').innerText = abcd.border.clinical_grade;

  document.getElementById('val-color').innerText = `${abcd.color.distinct_shades_count} Shades`;
  document.getElementById('sub-color').innerText = abcd.color.description;

  document.getElementById('val-diam').innerText = `${abcd.diameter.diameter_mm} mm`;
  document.getElementById('sub-diam').innerText = abcd.diameter.clinical_grade;

  const banner = document.getElementById('lesion-banner');
  banner.className = `diagnosis-banner ${data.primary_condition === 'Normal / Benign Nevus' ? 'normal' : (data.primary_condition.includes('Melanoma') ? '' : 'moderate')}`;
  document.getElementById('diag-condition').innerText = `${data.primary_condition} (${data.confidence_pct}% Confidence)`;
  document.getElementById('diag-icd').innerText = `ICD-10: ${data.icd10.code} • Total Dermatoscopy Score: ${abcd.total_dermatoscopy_score}`;
}

// ----------------- Audio Spectrogram & Web Audio Synthesizer -----------------
function initSpectrogram() {
  const container = document.getElementById('spectrogram-bars');
  if (!container) return;
  container.innerHTML = '';
  for (let i = 0; i < 36; i++) {
    const bar = document.createElement('div');
    bar.className = 'spectrogram-bar';
    bar.style.height = `${Math.floor(Math.random() * 25 + 10)}%`;
    container.appendChild(bar);
  }
}

function animateSpectrogram(isActive = true) {
  const bars = document.querySelectorAll('.spectrogram-bar');
  bars.forEach(bar => {
    const h = isActive ? Math.floor(Math.random() * 85 + 15) : Math.floor(Math.random() * 20 + 5);
    bar.style.height = `${h}%`;
  });
}

// Trigger Audio Screening with Genuine Web Audio Sound Generation
async function runAudioScreening(soundPreset = "Fine / Coarse Crackles (Pneumonia / Fibrosis)") {
  const interval = setInterval(() => animateSpectrogram(true), 100);

  // Play realistic pulmonary breath sound through Web Audio API
  if (window.pulmonarySynth) {
    if (soundPreset.includes('Crackles')) {
      window.pulmonarySynth.playRespiratorySound('crackles', 3.5);
    } else if (soundPreset.includes('Wheezing')) {
      window.pulmonarySynth.playRespiratorySound('wheezing', 3.5);
    } else {
      window.pulmonarySynth.playRespiratorySound('normal', 3.5);
    }
  }

  try {
    const formData = new FormData();
    formData.append('sound_type_hint', soundPreset);

    const res = await fetch(`${API_BASE}/api/diagnostic/audio/pulmonary`, {
      method: 'POST',
      body: formData
    });

    if (res.ok) {
      currentAudioResult = await res.json();
      updateAudioUI(currentAudioResult);
      await runSoapScribe();
    }
  } catch (err) {
    console.error("Audio screening error:", err);
  } finally {
    clearInterval(interval);
    setTimeout(() => animateSpectrogram(false), 500);
  }
}

function updateAudioUI(data) {
  document.getElementById('audio-latency').innerText = `${data.inference_latency_ms} ms | Hexagon NPU`;
  document.getElementById('audio-condition').innerText = `${data.primary_condition} (${data.confidence_pct}%)`;
  document.getElementById('audio-finding').innerText = data.clinical_interpretation;
  document.getElementById('audio-snr').innerText = `HP Poly Studio SNR: ${data.acoustic_biomarkers.poly_studio_snr_db} dB`;
}

// ----------------- Clinical Voice Dictation -----------------
async function runVoiceDictation(lang = "en") {
  try {
    const res = await fetch(`${API_BASE}/api/diagnostic/speech/transcribe?language=${lang}&preset_key=en_lesion`, {
      method: 'POST'
    });
    if (res.ok) {
      const data = await res.json();
      document.getElementById('dictation-text').value = data.transcription;
      await runSoapScribe();
    }
  } catch (err) {
    console.error("Voice dictation error:", err);
  }
}

// ----------------- Llama-3.2 Clinical SOAP Scribe -----------------
async function runSoapScribe() {
  const dictation = document.getElementById('dictation-text')?.value || "";

  try {
    const payload = {
      patient_info: currentPatient,
      vision_result: currentVisionResult,
      audio_result: currentAudioResult,
      dictation_text: dictation
    };

    const res = await fetch(`${API_BASE}/api/clinical/soap`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      currentSoapResult = await res.json();
      updateSoapUI(currentSoapResult);
    }
  } catch (err) {
    console.error("SOAP scribe error:", err);
  }
}

function updateSoapUI(data) {
  const soap = data.soap_note;
  const container = document.getElementById('soap-content');
  if (!container) return;

  container.innerHTML = `
    <div class="soap-section"><b>[S] SUBJECTIVE:</b><br>${soap.subjective}</div>
    <div class="soap-section"><b>[O] OBJECTIVE:</b><br>${soap.objective.replace(/•/g, '<br>•')}</div>
    <div class="soap-section"><b>[A] ASSESSMENT:</b><br>${soap.assessment.replace(/\n/g, '<br>')}</div>
    <div class="soap-section"><b>[P] PLAN:</b><br>${soap.plan.replace(/\n/g, '<br>')}</div>
  `;

  document.getElementById('scribe-speed').innerText = `${data.engine_meta.tokens_per_second} tok/s | ${data.engine_meta.generation_time_ms} ms`;
}

// ----------------- Patient Audio Counseling Readout -----------------
function playPatientCounselingAudio(lang = "en") {
  if (!currentSoapResult || !currentSoapResult.patient_counseling_audio_scripts) {
    alert("Please run a diagnostic screening first to generate clinical counseling instructions.");
    return;
  }

  const script = currentSoapResult.patient_counseling_audio_scripts[lang] || 
                 currentSoapResult.patient_counseling_audio_scripts["en"];

  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(script);
    utterance.rate = 0.92;
    if (lang === 'hi') utterance.lang = 'hi-IN';
    else if (lang === 'ta') utterance.lang = 'ta-IN';
    else utterance.lang = 'en-US';

    window.speechSynthesis.speak(utterance);
  } else {
    alert(`[HP Poly Studio Audio Counseling]:\n\n"${script}"`);
  }
}

// ----------------- 1-Click India ABDM FHIR R4 Modal & Export -----------------
async function viewAbdmFhirModal() {
  try {
    const payload = {
      patient_info: currentPatient,
      vision_result: currentVisionResult,
      audio_result: currentAudioResult,
      dictation_text: document.getElementById('dictation-text')?.value || ""
    };

    const res = await fetch(`${API_BASE}/api/export/abdm-fhir`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      const fhirData = await res.json();
      document.getElementById('fhir-modal-body').innerText = JSON.stringify(fhirData, null, 2);
      document.getElementById('fhir-modal').style.display = 'flex';
    }
  } catch (err) {
    console.error("FHIR fetch error:", err);
  }
}

function closeFhirModal() {
  document.getElementById('fhir-modal').style.display = 'none';
}

function copyFhirJson() {
  const text = document.getElementById('fhir-modal-body').innerText;
  navigator.clipboard.writeText(text);
  alert("ABDM FHIR R4 JSON copied to clipboard!");
}

function downloadFhirJsonFile() {
  const text = document.getElementById('fhir-modal-body').innerText;
  const blob = new Blob([text], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `ABDM_FHIR_DiagnosticReport_${currentPatient.patient_id}.json`;
  a.click();
  URL.revokeObjectURL(url);
}

// ----------------- HP Wolf Security Vault Storage & Inspector -----------------
async function saveToWolfVault() {
  if (!currentVisionResult && !currentAudioResult) {
    alert("No diagnostic results available to encrypt.");
    return;
  }

  try {
    const payload = {
      patient_info: currentPatient,
      diagnosis: currentVisionResult || currentAudioResult,
      soap_note: currentSoapResult || {}
    };

    const res = await fetch(`${API_BASE}/api/vault/store`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      const data = await res.json();
      alert(`[HP Wolf Security Vault Secured]\n\nRecord ID: ${data.record_id}\nAudit Hash: ${data.audit_hash}\nEncryption: ${data.encryption}\nCloud Leakage: ZERO BYTES`);
    }
  } catch (err) {
    console.error("Vault store error:", err);
  }
}

async function viewVaultAuditModal() {
  try {
    const res = await fetch(`${API_BASE}/api/vault/audit`);
    const recRes = await fetch(`${API_BASE}/api/vault/records`);
    if (res.ok && recRes.ok) {
      const audit = await res.json();
      const records = await recRes.json();
      const auditText = JSON.stringify({ audit_integrity: audit, encrypted_records: records }, null, 2);
      document.getElementById('vault-modal-body').innerText = auditText;
      document.getElementById('vault-modal').style.display = 'flex';
    }
  } catch (err) {
    console.error("Vault audit error:", err);
  }
}

function closeVaultModal() {
  document.getElementById('vault-modal').style.display = 'none';
}

// ----------------- HP AI Companion Assistant Query -----------------
async function askHpCompanion() {
  const input = document.getElementById('companion-input');
  const query = input?.value.trim();
  if (!query) return;

  const outputDiv = document.getElementById('companion-output');
  outputDiv.style.display = 'block';
  outputDiv.innerHTML = '<i>HP AI Companion is analyzing local encrypted patient records on Hexagon NPU...</i>';

  try {
    const res = await fetch(`${API_BASE}/api/hp-companion/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: query })
    });

    if (res.ok) {
      const data = await res.json();
      outputDiv.innerHTML = `<b>[${data.assistant}]</b><br>` + 
        data.response_markdown.replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<b>$1</b>');
    }
  } catch (err) {
    outputDiv.innerHTML = `<span style="color:#EF4444">Failed to query HP AI Companion. Ensure backend is running.</span>`;
  }
}
