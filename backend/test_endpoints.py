"""
OmniCare AI - Automated End-to-End Test Script
Tests all FastAPI endpoints, models, vault encryption, and FHIR export
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from fastapi.testclient import TestClient
from main import app

def test_all_omnicare_endpoints():
    client = TestClient(app)
    print("=" * 75)
    print("  OMNICARE AI - AUTOMATED ENDPOINT VERIFICATION")
    print("=" * 75)

    # 1. Health check
    res = client.get("/api/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print(f"[✓] GET /api/health -> {res.json()['status']} ({res.json()['hardware']})")

    # 2. Telemetry
    res = client.get("/api/telemetry")
    assert res.status_code == 200, f"Telemetry failed: {res.text}"
    print(f"[✓] GET /api/telemetry -> Peak TOPS: {res.json()['peak_tops']}, Mean Latency: {res.json()['mean_latency_ms']} ms")

    # 3. Vision Lesion Analysis
    res = client.post("/api/diagnostic/vision/lesion", data={"lesion_type_hint": "Melanoma"})
    assert res.status_code == 200, f"Vision lesion failed: {res.text}"
    v_data = res.json()
    print(f"[✓] POST /api/diagnostic/vision/lesion -> {v_data['primary_condition']} ({v_data['confidence_pct']}%) in {v_data['inference_latency_ms']} ms")
    assert "abcd_explainable_ai" in v_data
    print(f"    • Explainable ABCD Total Score: {v_data['abcd_explainable_ai']['total_dermatoscopy_score']}")

    # 4. Retinal Screening (ResNet-50 INT8)
    res = client.post("/api/diagnostic/vision/retina")
    assert res.status_code == 200, f"Retina screening failed: {res.text}"
    r_data = res.json()
    print(f"[✓] POST /api/diagnostic/vision/retina -> {r_data['primary_condition']} ({r_data['confidence_pct']}%) in {r_data['inference_latency_ms']} ms")

    # 5. Pulmonary Audio Analysis
    res = client.post("/api/diagnostic/audio/pulmonary", data={"sound_type_hint": "Fine / Coarse Crackles (Pneumonia / Fibrosis)"})
    assert res.status_code == 200, f"Audio failed: {res.text}"
    a_data = res.json()
    print(f"[✓] POST /api/diagnostic/audio/pulmonary -> {a_data['primary_condition']} ({a_data['confidence_pct']}%) in {a_data['inference_latency_ms']} ms")

    # 6. Speech Transcription
    res = client.post("/api/diagnostic/speech/transcribe?language=en&preset_key=en_lesion")
    assert res.status_code == 200, f"Transcribe failed: {res.text}"
    s_data = res.json()
    print(f"[✓] POST /api/diagnostic/speech/transcribe -> '{s_data['transcription'][:45]}...'")

    # 7. Contactless Camera rPPG Vitals
    res = client.post("/api/diagnostic/vitals/rppg", data={"preset": "normal", "lux": 450.0})
    assert res.status_code == 200, f"rPPG failed: {res.text}"
    rppg_data = res.json()
    print(f"[✓] POST /api/diagnostic/vitals/rppg -> HR: {rppg_data['vital_signs']['heart_rate_bpm']} BPM, SpO2: {rppg_data['vital_signs']['blood_oxygen_spo2_pct']}%, RR: {rppg_data['vital_signs']['respiratory_rate_rpm']} in {rppg_data['inference_latency_ms']} ms")
    assert len(rppg_data["pulse_waveform"]) > 0

    # 8. 12-Lead Paper ECG Digitization & Arrhythmia Classification
    res = client.post("/api/diagnostic/cardiac/ecg-digitize", data={"condition_hint": "Acute ST-Elevation Myocardial Infarction (STEMI)"})
    assert res.status_code == 200, f"ECG failed: {res.text}"
    ecg_data = res.json()
    print(f"[✓] POST /api/diagnostic/cardiac/ecg-digitize -> {ecg_data['primary_diagnosis']} (ST-Elev: {ecg_data['clinical_intervals']['st_elevation_mm']} mm, QTc: {ecg_data['clinical_intervals']['qtc_interval_ms']} ms) in {ecg_data['inference_latency_ms']} ms")
    assert len(ecg_data["digitized_waveform_mv"]) > 0

    # 7. Clinical SOAP Note Generation
    soap_payload = {
        "patient_info": {
            "patient_id": "P-10024",
            "name": "Aarav Mehra",
            "age": 42,
            "gender": "Male",
            "abha_id": "aarav.mehra@abdm"
        },
        "vision_result": v_data,
        "audio_result": a_data,
        "dictation_text": s_data["transcription"]
    }
    res = client.post("/api/clinical/soap", json=soap_payload)
    assert res.status_code == 200, f"SOAP failed: {res.text}"
    soap_data = res.json()
    print(f"[✓] POST /api/clinical/soap -> Triage Priority: {soap_data['triage_priority']}, ICD-10: {soap_data['icd10_code']}")

    # 8. 1-Click ABDM / ABHA FHIR R4 Bundle Export
    res = client.post("/api/export/abdm-fhir", json=soap_payload)
    assert res.status_code == 200, f"FHIR export failed: {res.text}"
    fhir_data = res.json()
    assert fhir_data["resourceType"] == "Bundle"
    print(f"[✓] POST /api/export/abdm-fhir -> Valid FHIR R4 DocumentBundle ({len(fhir_data['entry'])} entries)")

    # 9. HP Wolf Security Vault Storage & Encryption
    vault_payload = {
        "patient_info": soap_payload["patient_info"],
        "diagnosis": v_data,
        "soap_note": soap_data
    }
    res = client.post("/api/vault/store", json=vault_payload)
    assert res.status_code == 200, f"Vault store failed: {res.text}"
    vault_resp = res.json()
    print(f"[✓] POST /api/vault/store -> Status: {vault_resp['status']} (Hash: {vault_resp['audit_hash'][:20]}...)")

    # 10. HP Wolf Security Vault Listing & Cryptographic Audit
    res = client.get("/api/vault/records")
    assert res.status_code == 200, f"Vault records failed: {res.text}"
    rec_data = res.json()
    res = client.get("/api/vault/audit")
    assert res.status_code == 200, f"Vault audit failed: {res.text}"
    audit_data = res.json()
    print(f"[✓] GET  /api/vault/records & /audit -> {len(rec_data)} Encrypted Records, Integrity: {audit_data['integrity']}")

    # 11. HP AI Companion Query
    res = client.post("/api/hp-companion/query", json={"query": "HP AI: Summarize all critical melanoma and pneumonia alerts"})
    assert res.status_code == 200, f"HP Companion query failed: {res.text}"
    hp_resp = res.json()
    print(f"[✓] POST /api/hp-companion/query -> Intent: {hp_resp['intent']}")

    # 12. Clinical Safety Guardrails & OOD Verification
    res = client.post("/api/safety/verify-input?entropy=6.4")
    assert res.status_code == 200, f"Safety verify failed: {res.text}"
    safe_data = res.json()
    print(f"[✓] POST /api/safety/verify-input -> OOD: {safe_data['ood_detected']} (Status: {safe_data['quality_status']}, IEC 62304: {safe_data['iec_62304_verification']})")

    # 13. Clinical Contraindication Checker
    res = client.post("/api/safety/contraindications", data={"primary_condition": "Pneumonia"})
    assert res.status_code == 200, f"Contraindication check failed: {res.text}"
    contra_data = res.json()
    print(f"[✓] POST /api/safety/contraindications -> Found {len(contra_data['contraindications'])} allergy/drug warnings")

    # 14. ABDM Store-and-Forward Offline Sync Queue Enqueue & Status
    res = client.post("/api/abdm/enqueue", json=vault_payload)
    assert res.status_code == 200, f"ABDM enqueue failed: {res.text}"
    sync_enq = res.json()
    res = client.get("/api/abdm/sync-status")
    assert res.status_code == 200, f"ABDM sync status failed: {res.text}"
    print(f"[✓] POST /api/abdm/enqueue & GET /sync-status -> Enqueued: {sync_enq['queue_item_id']} (Pending: {sync_enq['pending_sync_count']})")

    # 15. ABDM Batch mTLS Sync Handshake
    res = client.post("/api/abdm/sync-handshake")
    assert res.status_code == 200, f"ABDM handshake failed: {res.text}"
    handshake = res.json()
    print(f"[✓] POST /api/abdm/sync-handshake -> Status: {handshake['handshake_status']} ({handshake['synced_records_count']} records synced)")

    # 16. DICOM Part 10 Medical Image Parser
    res = client.post("/api/dicom/parse")
    assert res.status_code == 200, f"DICOM parse failed: {res.text}"
    dcm = res.json()
    print(f"[✓] POST /api/dicom/parse -> Modality: {dcm['dicom_header']['Modality']}, Caliber Ratio: {dcm['pixel_to_mm_ratio']} mm/px")

    # 17. Frontend Static UI Routing & Pitch Deck Route Verification
    r_index = client.get("/")
    assert r_index.status_code == 200, "Frontend root index failed"
    r_css = client.get("/css/cockpit.css")
    assert r_css.status_code == 200, "Frontend CSS static route failed"
    r_js = client.get("/js/cockpit.js")
    assert r_js.status_code == 200, "Frontend JS static route failed"
    r_deck = client.get("/pitch-deck")
    assert r_deck.status_code == 200, "Showcase Pitch Deck route failed"
    r_show = client.get("/showcase/")
    assert r_show.status_code == 200, "Showcase Portal route failed"
    print(f"[✓] GET  / , /css, /js, /pitch-deck, /showcase/ -> All Static & Presentation Routes Verified (200 OK)")

    # 18. NEWS2 Deterioration & Shock Index Predictor
    res = client.post("/api/clinical/news2-risk", json={
        "respiration_rate": 28.0,
        "spo2_percent": 91.0,
        "systolic_bp": 88.0,
        "heart_rate": 118.0,
        "temperature_celsius": 38.6,
        "consciousness_avpu": "Alert",
        "supplemental_o2": True,
        "suspected_infection": True
    })
    assert res.status_code == 200, f"NEWS2 failed: {res.text}"
    news2_data = res.json()
    assert news2_data["total_news2_score"] >= 7, "Critical vitals should score >= 7 on NEWS2"
    assert news2_data["clinical_risk_tier"] == "HIGH_CRITICAL"
    print(f"[✓] POST /api/clinical/news2-risk -> NEWS2 Score: {news2_data['total_news2_score']}/20 ({news2_data['clinical_risk_tier']}), Shock Idx: {news2_data['hemodynamic_shock_index']['shock_index']}")

    # 19. Drug Guardian & PMBJP Generic Substitution Engine
    res = client.post("/api/clinical/drug-guardian", json={
        "prescribed_drugs": ["Augmentin 625mg", "Pan-D", "Telma-AM"],
        "patient_qtc_ms": 420.0
    })
    assert res.status_code == 200, f"Drug Guardian failed: {res.text}"
    drug_data = res.json()
    assert len(drug_data["jan_aushadhi_substitutions"]) == 3
    assert drug_data["financial_equity_summary"]["net_savings_percentage"] > 70.0
    print(f"[✓] POST /api/clinical/drug-guardian -> Savings: ₹{drug_data['financial_equity_summary']['net_family_savings_inr']} ({drug_data['financial_equity_summary']['net_savings_percentage']}%), DDI Risk: {drug_data['ddi_risk_level']}")

    # 20. Council of AI Specialists Multi-Agent Consensus Panel
    res = client.post("/api/clinical/council-deliberate", json={
        "patient_info": {"patient_id": "P-10024", "name": "Aarav Mehra", "age": 42, "gender": "Male"},
        "vision_findings": {"condition": "Cutaneous Melanoma", "confidence": 94.6},
        "ecg_findings": {"primary_rhythm": "Normal Sinus Rhythm", "st_elevation_mm": 0.0, "qtc_bazett_ms": 412.0},
        "audio_findings": {"condition": "Normal Breath"},
        "prescriptions": ["Augmentin 625mg"]
    })
    assert res.status_code == 200, f"Council deliberation failed: {res.text}"
    council_data = res.json()
    assert len(council_data["specialist_panel"]) == 4
    assert council_data["chief_medical_officer_synthesis"]["inter_agent_agreement_pct"] > 90.0
    print(f"[✓] POST /api/clinical/council-deliberate -> Inter-Agent Agreement: {council_data['chief_medical_officer_synthesis']['inter_agent_agreement_pct']}%, Panel: 4 Specialists")

    # 21. POCUS Handheld Ultrasound Scanner (Echo & Lung)
    res_echo = client.post("/api/diagnostic/pocus/cardiac", data={"preset": "normal"})
    assert res_echo.status_code == 200, f"POCUS Echo failed: {res_echo.text}"
    echo_data = res_echo.json()
    assert echo_data["hemodynamic_metrics"]["ejection_fraction_pct"] > 55.0

    res_lung = client.post("/api/diagnostic/pocus/lung", data={"preset": "pneumothorax"})
    assert res_lung.status_code == 200, f"POCUS Lung failed: {res_lung.text}"
    lung_data = res_lung.json()
    assert lung_data["m_mode_pattern"] == "STRATOSPHERE_BARCODE_SIGN"
    print(f"[✓] POST /api/diagnostic/pocus/cardiac & /lung -> EF: {echo_data['hemodynamic_metrics']['ejection_fraction_pct']}%, Lung Sign: {lung_data['m_mode_pattern']}")

    # 22. Multilingual Patient Counseling in Regional Languages
    res = client.post("/api/counseling/regional-vernacular", json={
        "language_code": "ta",
        "patient_name": "Aarav Mehra",
        "condition_name": "Cutaneous Melanoma",
        "triage_urgency": "HIGH_RISK"
    })
    assert res.status_code == 200, f"Regional counseling failed: {res.text}"
    counsel_data = res.json()
    assert counsel_data["language_name"] == "Tamil"
    print(f"[✓] POST /api/counseling/regional-vernacular -> Lang: {counsel_data['language_name']} ({counsel_data['native_script_name']}), Audio Duration: {counsel_data['audio_synthesis_specs']['duration_seconds']}s")

    # 23. DICOM 3.0 Web-PACS Micro-Server & SOP Export
    res_pacs = client.get("/api/pacs/studies")
    assert res_pacs.status_code == 200, f"PACS query failed: {res_pacs.text}"
    pacs_studies = res_pacs.json()
    assert len(pacs_studies) >= 2

    res_export = client.post("/api/pacs/export-instance", json={
        "patient_id": "P-10024",
        "patient_name": "Aarav Mehra",
        "modality": "CR",
        "findings": {"status": "Field Screening Clear"}
    })
    assert res_export.status_code == 200, f"PACS export failed: {res_export.text}"
    export_data = res_export.json()
    print(f"[✓] GET  /api/pacs/studies & POST /export-instance -> Local Studies: {len(pacs_studies)}, SOP Instance Created: {export_data['dicom_web_metadata']['SOPInstanceUID']}")

    # 24. Differential Privacy & Federated Edge Learning Gradient Step
    res = client.post("/api/federated/dp-gradient-step", json={
        "model_name": "YOLOv8-Lesion-INT8",
        "local_sample_count": 14,
        "epsilon_budget": 1.2,
        "delta_target": 1e-5
    })
    assert res.status_code == 200, f"Federated DP-SGD failed: {res.text}"
    fed_data = res.json()
    assert fed_data["dpdp_act_section_8_compliance"] == "PASS_ZERO_RAW_DATA_LEAK"
    print(f"[✓] POST /api/federated/dp-gradient-step -> DP Budget: ε={fed_data['differential_privacy_guarantee']['epsilon_privacy_loss']}, Hash: {fed_data['sanitized_delta_sha256'][:16]}...")

    # 25. HP Smart Sense Dynamic Hardware & Thermal Governor
    res_gov = client.get("/api/hardware/governor")
    assert res_gov.status_code == 200, f"Hardware Governor get failed: {res_gov.text}"

    res_set = client.post("/api/hardware/governor/set-mode", json={"mode_key": "eco"})
    assert res_set.status_code == 200, f"Hardware Governor set failed: {res_set.text}"
    gov_set = res_set.json()
    assert gov_set["profile_details"]["target_npu_tops"] == 28.0
    print(f"[✓] GET  /api/hardware/governor & POST /set-mode -> Switched to: '{gov_set['profile_details']['mode_name']}' (Battery: {gov_set['profile_details']['battery_runtime_hours']}h)")

    print("\n" + "=" * 75)
    print("  ALL 25 ADVANCED CLINICAL, HARDWARE & REGULATORY TESTS PASSED!")
    print("=" * 75)

if __name__ == "__main__":
    test_all_omnicare_endpoints()

