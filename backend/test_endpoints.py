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

    print("\n" + "=" * 75)
    print("  ALL 17 CLINICAL, REGULATORY & ARCHITECTURAL ENDPOINT TESTS PASSED!")
    print("=" * 75)

if __name__ == "__main__":
    test_all_omnicare_endpoints()
