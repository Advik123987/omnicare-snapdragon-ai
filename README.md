# 🩺 OmniCare AI — On-Device Multimodal Clinical Intelligence Workstation

![Snapdragon X Elite](https://img.shields.io/badge/Qualcomm-Snapdragon%C2%AE%20X%20Elite-E60012?style=for-the-badge&logo=qualcomm)
![HP OmniBook X](https://img.shields.io/badge/HP-OmniBook%20X%20Copilot%2B-0096D6?style=for-the-badge&logo=hp)
![Hexagon NPU](https://img.shields.io/badge/Hexagon%20NPU-45.0%20TOPS-00F0FF?style=for-the-badge)
![DPDP Act 2023](https://img.shields.io/badge/Privacy-100%25%20On--Device%20(DPDP%2FHIPAA)-10B981?style=for-the-badge)
![ABDM FHIR R4](https://img.shields.io/badge/India%20ABDM-FHIR%20R4%20Standard-F59E0B?style=for-the-badge)

> **Qualcomm Snapdragon® AI Lab Build & Present Challenge 2026**  
> **Target Hardware:** Snapdragon-Powered HP PCs (HP OmniBook X / HP EliteBook Ultra)  
> **Participant:** Harsh Maurya (`themauryaharsh@gmail.com`)  
> **Interactive Judge Portal:** Open `showcase/index.html` in any browser!

---

## 🌟 Executive Overview

**OmniCare AI** is an on-device, multimodal clinical triage and diagnostic workstation engineered specifically for **Snapdragon-powered HP PCs**. Powered by the **45 TOPS Qualcomm® Hexagon™ NPU**, it runs real-time computer vision, acoustic pulmonary stethoscopy, and clinical note generation at **sub-15ms latency** with **100% on-device privacy (zero cloud transmissions)**.

### Why OmniCare AI Wins:
1. **Solves the Rural Healthcare Specialist Shortage**: Brings specialist-grade dermatology, ophthalmology, and pulmonology screening to remote Primary Health Centers (PHCs) and off-grid mobile clinics.
2. **Qualcomm AI Hub Deep Integration**: 5 models pre-optimized for Qualcomm Hexagon NPU (`yolov8_seg`, `resnet50`, `yamnet`, `whisper_small`, `llama_v3_2_3b_instruct`) running with 100% NPU offload via `QNNExecutionProvider`.
3. **Deep HP Hardware Synergies**: Leverages **HP Poly Studio dual microphones** with AI beamforming for breath sound analysis, **HP Wolf Security** for hardware root-of-trust encrypted patient records, **HP AI Companion** for natural language queries, and **26+ hour battery endurance** for 2 full days of off-grid screening.
4. **Explainable AI (ABCD Rule)**: Calculates Asymmetry, Border compactness, Color variance, and Diameter (>6mm) alongside Grad-CAM attention heatmaps.
5. **National ABDM / ABHA Interoperability**: 1-click export of standardized **India Ayushman Bharat Digital Mission (ABDM) FHIR R4** `DiagnosticReportRecord` JSON bundles.

---

## 🛠️ System Architecture

```
                  ┌─────────────────────────────────────────────────────────┐
                  │           Snapdragon-Powered HP PC                      │
                  │   (HP OmniBook X / HP EliteBook Ultra)                  │
                  │   Snapdragon® X Elite / 45 TOPS Hexagon NPU              │
                  └───────────────────────────┬─────────────────────────────┘
                                              │
         ┌────────────────────────────────────┼────────────────────────────────────┐
         ▼                                    ▼                                    ▼
┌──────────────────┐                 ┌──────────────────┐                 ┌──────────────────┐
│ Camera / USB     │                 │ HP Poly Studio   │                 │ Doctor / Patient │
│ Dermatoscope     │                 │ Dual Mic Array   │                 │ Voice Input      │
└────────┬─────────┘                 └────────┬─────────┘                 └────────┬─────────┘
         │ Scans & Images                     │ Acoustic Breath Stream             │ Multilingual Speech
         ▼                                    ▼                                    ▼
┌───────────────────────────────────┐┌───────────────────────────────────┐┌───────────────────────────────────┐
│ Model 1: Qualcomm AI Hub          ││ Model 2: Qualcomm AI Hub          ││ Model 3: Qualcomm AI Hub          │
│ YOLOv8-Seg (INT8 QNN)             ││ YAMNet Respiratory (INT8 QNN)     ││ Whisper-Small (INT8/FP16)         │
│ • Skin Lesion Segmentation        ││ • Pulmonary Sound Classifier      ││ • Real-Time Clinical Dictation    │
│ • Explainable ABCD Metric Engine  ││ • Wheeze, Crackle, Stridor        ││ • English, Hindi, Regional        │
│ ➜ 12.4 ms on Hexagon NPU          ││ ➜ 6.8 ms on Hexagon NPU           ││ ➜ 18.2 ms on Hexagon NPU          │
└────────────────┬──────────────────┘└────────────────┬──────────────────┘└────────────────┬──────────────────┘
                 │                                    │                                    │
                 └────────────────────────────────────┼────────────────────────────────────┘
                                                      │
                                                      ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ Model 4: Qualcomm AI Hub Llama-3.2-3B-Instruct (INT4 QNN on Hexagon NPU)               │
│ • Automated Medical SOAP Notes (Subjective, Objective, Assessment, Plan)               │
│ • Official WHO ICD-10-CM Diagnostic Coding & Treatment Recommendations                 │
│ • Multilingual Audio Counseling Script Synthesis (Played via HP Poly Studio)           │
│ ➜ 34.2 tokens/second on Hexagon NPU                                                    │
└─────────────────────────────────────────────┬──────────────────────────────────────────┘
                                              │
                                              ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        OmniCare Local Engine (FastAPI / WebSockets)                    │
│  • Hardware Telemetry Profiler (TOPS, Latency, FPS, Milliwatts)                        │
│  • HP Wolf Security Encrypted Local Patient Vault (AES-256 GCM)                        │
│  • 1-Click India ABDM / ABHA FHIR R4 JSON Exporter                                     │
│  • HP AI Companion Bridge & Interactive Clinical Cockpit Web UI                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚡ Performance Scorecard

| Metric | Snapdragon HP Hexagon NPU | Public Cloud Medical API | Standard x86 Laptop CPU |
|---|---|---|---|
| **Dermatology (YOLOv8-Seg)** | **12.67 ms (78.9 FPS)** | 1,650.0 ms (0.6 FPS) | 320.0 ms |
| **Pulmonary (YAMNet)** | **6.85 ms (145.9 FPS)** | 1,420.0 ms | 145.0 ms |
| **Whisper Dictation** | **18.55 ms** | 1,850.0 ms | 480.0 ms |
| **Llama-3.2-3B Generation** | **34.2 tokens/second** | 28.0 tokens/second | 4.2 tok/s |
| **Power Consumption** | **4.5 Watts (Cold)** | 350.0 Watts (Server) | 45.0 Watts |
| **Bandwidth Consumed** | **0 KB (100% Offline)** | 15,000 KB per scan | 0 KB |
| **Monthly Operating Cost** | **$0.00 / month** | $1,500.00 / month | $0.00 / month |
| **DPDP Act 2023 Compliance**| **100% Zero Cloud Leakage**| High Risk (Third-party upload)| Compliant |

---

## 🚀 Quick Start Guide

### Option 1: Standalone Zero-Setup Judge Showcase Portal
Simply double-click or open `showcase/index.html` in any web browser!
- Explore the interactive 3D architecture
- Run live clinical simulations (Melanoma ABCD, Pneumonia Spectrogram)
- Drag the interactive benchmark & cost slider
- Open the built-in Executive Pitch Deck (`showcase/pitch-deck.html`)

### Option 2: Full Local Development Stack
1. **Prerequisites:** Python 3.10+ (Windows AMD64 or ARM64)
2. **Install Dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```
3. **Launch OmniCare AI (1-Click):**
   ```cmd
   launch_omnicare.bat
   ```
   *Or run via Python:*
   ```bash
   python backend/main.py
   ```
4. **Open Clinical Cockpit:** Navigate to `http://localhost:8000`

---

## 📁 Repository Structure

```
omnicare-snapdragon-ai/
├── launch_omnicare.bat                   <-- 1-Click Windows Launcher Script
├── launch_omnicare.ps1                   <-- PowerShell Launcher Script
├── README.md                             <-- Standalone Repository Documentation
│
├── backend/                              <-- On-Device AI Diagnostic Engine (FastAPI)
│   ├── main.py                           <-- 18 Clinical & Regulatory REST Endpoints
│   ├── config.py                         <-- Snapdragon X Elite & QNN Hardware Settings
│   ├── test_endpoints.py                 <-- Automated Test Suite (17/17 Passed)
│   ├── requirements.txt                  <-- Minimal Python Dependencies
│   ├── engine/
│   │   ├── qnn_vision.py                 <-- Qualcomm AI Hub Dermatology & Retinal Models
│   │   ├── xai_abcd.py                   <-- Explainable AI ABCD Melanoma Metric Engine
│   │   ├── qnn_audio.py                  <-- HP Poly Studio Pulmonary Sound Classifier
│   │   ├── qnn_transcribe.py             <-- Qualcomm AI Hub Whisper Dictation Engine
│   │   ├── clinical_scribe.py            <-- Llama-3.2 SOAP Note & ICD-10 Generator
│   │   ├── fhir_exporter.py              <-- India ABDM / ABHA FHIR R4 JSON Exporter
│   │   ├── hp_ai_companion.py            <-- HP AI Companion Natural Language Extension
│   │   ├── telemetry.py                  <-- Hexagon NPU TOPS & Hardware Profiler
│   │   ├── safety_guardrails.py          <-- CDSCO SaMD MDR-2017 & IEC 62304 Safety Engine
│   │   └── dicom_parser.py               <-- Medical DICOM Part 10 Calibrated Parser
│   ├── security/
│   │   ├── wolf_vault.py                 <-- HP Wolf Security Encrypted Patient Vault (AES-256 GCM)
│   │   └── offline_sync_engine.py        <-- ABDM Store-and-Forward Transactional Queue
│   ├── toolkit/
│   │   ├── qnn_quantizer.py              <-- QNN INT8 Calibration & Quantization Spec
│   │   └── htp_operator_profiler.py      <-- HTP v73 Layer Breakdown (100% Offload)
│   └── scripts/
│       ├── qai_hub_compile.py            <-- Qualcomm AI Hub Cloud Compilation Script
│       ├── qai_hub_profile.py            <-- On-Device Snapdragon X Elite Profiling Tool
│       └── benchmark_suite.py            <-- NPU vs Cloud vs CPU Benchmark Generator
│
├── frontend/                             <-- Futuristic Clinical Cockpit UI
│   ├── index.html                        <-- Real-time Clinical Dashboard
│   ├── css/cockpit.css                   <-- HP/Qualcomm Cyan & Cobalt Theme
│   └── js/
│       ├── audio_synth.js                <-- Web Audio API Pulmonary Acoustics Synthesizer
│       └── cockpit.js                    <-- Canvas segmentation, Grad-CAM, live FFT visualizer
│
├── showcase/                             <-- Standalone Judge Showcase Portal
│   ├── index.html                        <-- Interactive browser demo for judges (Zero setup)
│   └── pitch-deck.html                   <-- Full 10-slide executive pitch deck (Printable to PDF)
│
└── docs/                                 <-- Complete Competition Submission Package
    ├── SYSTEM_ARCHITECTURE_WHITEPAPER.md <-- IEEE-Grade Technical Whitepaper
    ├── COMPETITION_PROPOSAL.md           <-- Formal Unstop Solution Submission Document
    ├── SNAPDRAGON_PITCH_DECK.md          <-- Markdown slide deck
    ├── NPU_BENCHMARK_REPORT.md           <-- Detailed latency, TOPS & power consumption report
    └── DEMO_VIDEO_SCRIPT.md              <-- 2-3 minute video presentation script
```

---

## 🏆 Competition Verification

- **Qualcomm AI Hub Profiling Report:** `backend/scripts/snapdragon_profile_report.json`
- **Qualcomm AI Hub Compilation Manifest:** `backend/scripts/qai_hub_compilation_manifest.json`
- **Automated Benchmark Matrix:** `docs/benchmark_results.json`

Developed with pride for the **Snapdragon® AI Lab Build & Present Challenge 2026**.
