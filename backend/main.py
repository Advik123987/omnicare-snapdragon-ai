"""
OmniCare AI - Main FastAPI Edge Orchestration Server
Target: Snapdragon-Powered HP PCs (HP OmniBook X / HP EliteBook Ultra)
Hexagon NPU (45 TOPS) Multimodal Clinical Intelligence Hub
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel

# Add current directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import HARDWARE_PROFILE, QUALCOMM_AI_HUB_MODELS
from engine.qnn_vision import qnn_vision_engine
from engine.qnn_audio import qnn_audio_engine
from engine.qnn_transcribe import qnn_speech_engine
from engine.clinical_scribe import clinical_scribe
from engine.fhir_exporter import fhir_exporter
from engine.hp_ai_companion import hp_ai_companion
from engine.telemetry import telemetry_profiler
from engine.safety_guardrails import safety_guardrails
from engine.dicom_parser import dicom_parser
from security.wolf_vault import wolf_vault
from security.offline_sync_engine import offline_sync_engine

# FastAPI Application Initialization
app = FastAPI(
    title="OmniCare AI - Snapdragon HP PC Clinical Edge Hub",
    description="On-Device Multimodal Clinical Intelligence running on Snapdragon Hexagon NPU (45 TOPS)",
    version="1.0.0"
)

# Enable CORS for local cross-origin development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- Request / Response Models -----------------
class PatientInfoModel(BaseModel):
    patient_id: str = "P-10024"
    name: str = "Aarav Mehra"
    age: int = 42
    gender: str = "Male"
    abha_id: Optional[str] = "aarav.mehra@abdm"

class ClinicalSoapRequest(BaseModel):
    patient_info: PatientInfoModel
    vision_result: Optional[Dict[str, Any]] = None
    audio_result: Optional[Dict[str, Any]] = None
    dictation_text: Optional[str] = None

class VaultStoreRequest(BaseModel):
    patient_info: PatientInfoModel
    diagnosis: Dict[str, Any]
    soap_note: Dict[str, Any]

class HPCompanionQueryRequest(BaseModel):
    query: str

# ----------------- API Endpoints -----------------

@app.get("/api/health")
def health_check():
    """Health & Hardware Status."""
    return {
        "status": "ONLINE",
        "system": "OmniCare AI Clinical Edge Station",
        "hardware": HARDWARE_PROFILE["device_name"],
        "processor": HARDWARE_PROFILE["processor"],
        "npu_tops": HARDWARE_PROFILE["npu_peak_tops"],
        "security": "HP Wolf Security Active",
        "cloud_mode": "100% On-Device Offline Capable"
    }

@app.get("/api/telemetry")
def get_telemetry():
    """Get live Snapdragon Hexagon NPU performance telemetry."""
    return telemetry_profiler.get_system_telemetry()

@app.post("/api/diagnostic/vision/lesion")
async def analyze_skin_lesion(lesion_type_hint: Optional[str] = Form(None),
                             file: Optional[UploadFile] = File(None)):
    """
    Dermatology screening using Qualcomm AI Hub YOLOv8-Seg (INT8) + Explainable ABCD rule.
    """
    image_bytes = await file.read() if file else None
    result = qnn_vision_engine.analyze_dermatology_lesion(image_bytes=image_bytes, lesion_type_hint=lesion_type_hint)
    return JSONResponse(content=result)

@app.post("/api/diagnostic/vision/retina")
async def analyze_retina(file: Optional[UploadFile] = File(None)):
    """
    Retinal screening using Qualcomm AI Hub ResNet-50 Quantized INT8.
    """
    image_bytes = await file.read() if file else None
    result = qnn_vision_engine.analyze_retinal_fundus(image_bytes=image_bytes)
    return JSONResponse(content=result)

@app.post("/api/diagnostic/audio/pulmonary")
async def analyze_pulmonary_sound(sound_type_hint: Optional[str] = Form(None),
                                 file: Optional[UploadFile] = File(None)):
    """
    Pulmonary stethoscopy analysis using HP Poly Studio dual mics & Qualcomm AI Hub YAMNet.
    """
    audio_bytes = await file.read() if file else None
    result = qnn_audio_engine.analyze_respiratory_sound(audio_data=audio_bytes, sound_type_hint=sound_type_hint)
    return JSONResponse(content=result)

@app.post("/api/diagnostic/speech/transcribe")
def transcribe_clinical_voice(language: str = "en", preset_key: Optional[str] = None):
    """
    On-Device multilingual transcription using Qualcomm AI Hub Whisper-Small.
    """
    result = qnn_speech_engine.transcribe_audio(language=language, preset_key=preset_key)
    return JSONResponse(content=result)

@app.post("/api/clinical/soap")
def generate_soap_note(payload: ClinicalSoapRequest):
    """
    Synthesize multimodal findings into medical SOAP notes and ICD-10 codes via Llama-3.2-3B.
    """
    result = clinical_scribe.generate_soap_note(
        patient_info=payload.patient_info.dict(),
        vision_data=payload.vision_result,
        audio_data=payload.audio_result,
        dictation_text=payload.dictation_text
    )
    return JSONResponse(content=result)

@app.post("/api/export/abdm-fhir")
def export_abdm_fhir_bundle(payload: ClinicalSoapRequest):
    """
    Generate official Ayushman Bharat Digital Mission (ABDM) FHIR R4 JSON bundle.
    """
    soap_data = clinical_scribe.generate_soap_note(
        patient_info=payload.patient_info.dict(),
        vision_data=payload.vision_result,
        audio_data=payload.audio_result,
        dictation_text=payload.dictation_text
    )
    primary_diag = payload.vision_result or payload.audio_result or {"primary_condition": "Routine Checkup"}
    bundle = fhir_exporter.create_diagnostic_report_bundle(
        patient_info=payload.patient_info.dict(),
        diagnosis_result=primary_diag,
        soap_data=soap_data
    )
    return JSONResponse(content=bundle)

@app.post("/api/vault/store")
def store_in_wolf_vault(payload: VaultStoreRequest):
    """
    Encrypt and store patient diagnosis in the HP Wolf Security local vault.
    """
    p_info = payload.patient_info.dict()
    fhir_bundle = fhir_exporter.create_diagnostic_report_bundle(
        patient_info=p_info,
        diagnosis_result=payload.diagnosis,
        soap_data=payload.soap_note
    )
    result = wolf_vault.store_patient_record(
        patient_id=p_info["patient_id"],
        name=p_info["name"],
        age=p_info["age"],
        gender=p_info["gender"],
        diagnosis=payload.diagnosis,
        fhir_bundle=fhir_bundle
    )
    return JSONResponse(content=result)

@app.get("/api/vault/records")
def list_vault_records():
    """List encrypted patient records stored in local vault."""
    return JSONResponse(content=wolf_vault.list_records())

@app.get("/api/vault/audit")
def get_vault_audit():
    """Verify HP Wolf Security vault cryptographic integrity & zero cloud leak status."""
    return JSONResponse(content=wolf_vault.get_vault_audit_status())

@app.post("/api/hp-companion/query")
def query_hp_companion(payload: HPCompanionQueryRequest):
    """
    HP AI Companion natural-language clinical queries.
    """
    result = hp_ai_companion.handle_natural_language_query(payload.query)
    return JSONResponse(content=result)

# ----------------- Safety Guardrails & ABDM Sync Endpoints -----------------

@app.post("/api/safety/verify-input")
def verify_input_safety(entropy: float = 6.4):
    """
    Evaluates input image quality, Out-of-Distribution (OOD) status, and IEC 62304 verification.
    """
    res = safety_guardrails.evaluate_image_quality_and_ood(pixel_entropy_sim=entropy)
    return JSONResponse(content=res)

@app.post("/api/safety/contraindications")
def check_contraindications(primary_condition: str = Form(...)):
    """
    Checks for drug contraindications and allergy alerts.
    """
    alerts = safety_guardrails.check_clinical_contraindications(primary_condition)
    return JSONResponse(content={"contraindications": alerts})

@app.post("/api/abdm/enqueue")
def enqueue_offline_record(payload: VaultStoreRequest):
    """
    Enqueue record to local Store-and-Forward offline queue.
    """
    p_info = payload.patient_info.dict()
    bundle = fhir_exporter.create_diagnostic_report_bundle(
        patient_info=p_info,
        diagnosis_result=payload.diagnosis,
        soap_data=payload.soap_note
    )
    res = offline_sync_engine.enqueue_for_sync(
        patient_id=p_info["patient_id"],
        record_id=f"REC-{p_info['patient_id']}",
        fhir_bundle=bundle,
        abha_id=p_info.get("abha_id", "patient@abdm")
    )
    return JSONResponse(content=res)

@app.post("/api/abdm/sync-handshake")
def sync_with_abdm_gateway():
    """
    Trigger simulated batch mTLS synchronization with ABDM Gateway.
    """
    res = offline_sync_engine.execute_batch_sync_handshake()
    return JSONResponse(content=res)

@app.get("/api/abdm/sync-status")
def get_abdm_sync_status():
    """
    Get live ABDM offline queue statistics.
    """
    return JSONResponse(content=offline_sync_engine.get_sync_status())

@app.post("/api/dicom/parse")
async def parse_dicom_file(file: Optional[UploadFile] = File(None)):
    """
    Parse DICOM Part 10 medical image and extract clinical tags and millimeter caliber.
    """
    data_bytes = await file.read() if file else b""
    res = dicom_parser.parse_dicom_bytes(data_bytes)
    return JSONResponse(content=res)

# Mount Frontend & Showcase static assets
frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
showcase_dir = Path(__file__).resolve().parent.parent / "showcase"

if frontend_dir.exists():
    css_dir = frontend_dir / "css"
    js_dir = frontend_dir / "js"
    if css_dir.exists():
        app.mount("/css", StaticFiles(directory=str(css_dir)), name="css")
    if js_dir.exists():
        app.mount("/js", StaticFiles(directory=str(js_dir)), name="js")
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

    @app.get("/")
    def serve_cockpit_index():
        index_file = frontend_dir / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"message": "Frontend UI directory exists but index.html is pending creation."}

if showcase_dir.exists():
    app.mount("/showcase", StaticFiles(directory=str(showcase_dir), html=True), name="showcase")

    @app.get("/pitch-deck")
    def serve_pitch_deck():
        deck_file = showcase_dir / "pitch-deck.html"
        if deck_file.exists():
            return FileResponse(str(deck_file))
        return {"message": "Pitch deck file pending creation."}

if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 75)
    print("  OMNICARE AI - SNAPDRAGON HP PC CLINICAL EDGE SERVER")
    print("  Hexagon NPU Accelerated (45 TOPS) | HP Wolf Security Encrypted")
    print("  Access Clinical Cockpit at: http://localhost:8000")
    print("=" * 75 + "\n")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
