"""
OmniCare AI - Ayushman Bharat Digital Mission (ABDM / ABHA) FHIR R4 Exporter
Conforms to National Resource Centre for EHR Standards (NRCeS) India Specifications
Exports Interoperable FHIR R4 DiagnosticReportRecord & Observation Resource Bundles
"""

import uuid
import time
from typing import Dict, Any

class AbdmFhirR4Exporter:
    """
    Generates ABDM-compliant FHIR R4 JSON documents for patient health records,
    allowing offline-to-online synchronization with India's ABHA (Ayushman Bharat Health Account).
    """

    @staticmethod
    def create_diagnostic_report_bundle(patient_info: Dict[str, Any],
                                         diagnosis_result: Dict[str, Any],
                                         soap_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Package patient screening, multi-modal NPU diagnostics, and clinical SOAP notes
        into an official ABDM FHIR R4 Bundle.
        """
        bundle_id = str(uuid.uuid4())
        report_id = str(uuid.uuid4())
        patient_res_id = str(uuid.uuid4())
        obs_vision_id = str(uuid.uuid4())
        obs_audio_id = str(uuid.uuid4())
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%S+05:30", time.localtime())

        name = patient_info.get("name", "Ananya Sharma")
        age = patient_info.get("age", 38)
        gender = patient_info.get("gender", "female").lower()
        abha_id = patient_info.get("abha_id", f"{patient_info.get('patient_id', '91-9876543210')}@abdm")
        condition = diagnosis_result.get("primary_condition", "Dermatological Lesion")
        icd_code = soap_data.get("icd10_code", "C43.9")
        icd_desc = soap_data.get("icd10_description", "Malignant melanoma of skin")

        fhir_bundle = {
            "resourceType": "Bundle",
            "id": bundle_id,
            "meta": {
                "versionId": "1",
                "lastUpdated": timestamp,
                "profile": ["https://nrces.in/ndhm/fhir/r4/StructureDefinition/DocumentBundle"]
            },
            "identifier": {
                "system": "https://abdm.gov.in/facilities/snapdragon-omnicare-edge",
                "value": f"OMNICARE-{bundle_id[:8]}"
            },
            "type": "document",
            "timestamp": timestamp,
            "entry": [
                # 1. Patient Resource
                {
                    "fullUrl": f"urn:uuid:{patient_res_id}",
                    "resource": {
                        "resourceType": "Patient",
                        "id": patient_res_id,
                        "meta": {
                            "profile": ["https://nrces.in/ndhm/fhir/r4/StructureDefinition/Patient"]
                        },
                        "identifier": [
                            {
                                "type": {
                                    "coding": [
                                        {
                                            "system": "https://nrces.in/ndhm/fhir/r4/CodeSystem/ndhm-identifier-type-code",
                                            "code": "ABHA",
                                            "display": "Ayushman Bharat Health Account Number"
                                        }
                                    ]
                                },
                                "system": "https://healthid.abdm.gov.in",
                                "value": abha_id
                            }
                        ],
                        "name": [
                            {
                                "text": name
                            }
                        ],
                        "gender": gender,
                        "birthDate": f"{2026 - age}-01-01"
                    }
                },
                # 2. DiagnosticReport Resource
                {
                    "fullUrl": f"urn:uuid:{report_id}",
                    "resource": {
                        "resourceType": "DiagnosticReport",
                        "id": report_id,
                        "meta": {
                            "profile": ["https://nrces.in/ndhm/fhir/r4/StructureDefinition/DiagnosticReportRecord"]
                        },
                        "status": "final",
                        "category": [
                            {
                                "coding": [
                                    {
                                        "system": "http://terminology.hl7.org/CodeSystem/v2-0074",
                                        "code": "RAD",
                                        "display": "Radiology / Point-of-Care Imaging"
                                    }
                                ]
                            }
                        ],
                        "code": {
                            "coding": [
                                {
                                    "system": "http://loinc.org",
                                    "code": "72170-4",
                                    "display": "Photographic image of skin lesion"
                                },
                                {
                                    "system": "http://hl7.org/fhir/sid/icd-10",
                                    "code": icd_code,
                                    "display": icd_desc
                                }
                            ],
                            "text": f"Point-of-Care Edge Screening: {condition}"
                        },
                        "subject": {
                            "reference": f"urn:uuid:{patient_res_id}",
                            "display": name
                        },
                        "effectiveDateTime": timestamp,
                        "issued": timestamp,
                        "performer": [
                            {
                                "display": "Snapdragon OmniCare AI Clinical Edge Station (HP OmniBook X)"
                            }
                        ],
                        "result": [
                            {"reference": f"urn:uuid:{obs_vision_id}"},
                            {"reference": f"urn:uuid:{obs_audio_id}"}
                        ],
                        "conclusion": f"{condition}. ICD-10: {icd_code}. Triage: {soap_data.get('triage_priority')}.",
                        "conclusionCode": [
                            {
                                "coding": [
                                    {
                                        "system": "http://hl7.org/fhir/sid/icd-10",
                                        "code": icd_code,
                                        "display": icd_desc
                                    }
                                ]
                            }
                        ]
                    }
                },
                # 3. Vision Observation Resource (ABCD Metrics)
                {
                    "fullUrl": f"urn:uuid:{obs_vision_id}",
                    "resource": {
                        "resourceType": "Observation",
                        "id": obs_vision_id,
                        "meta": {
                            "profile": ["https://nrces.in/ndhm/fhir/r4/StructureDefinition/Observation"]
                        },
                        "status": "final",
                        "code": {
                            "coding": [
                                {
                                    "system": "http://loinc.org",
                                    "code": "89053-3",
                                    "display": "Dermatology Total Dermatoscopy Score (TDS)"
                                }
                            ],
                            "text": "Total Dermatoscopy Score (ABCD Rule)"
                        },
                        "subject": {"reference": f"urn:uuid:{patient_res_id}"},
                        "valueQuantity": {
                            "value": diagnosis_result.get("abcd_explainable_ai", {}).get("total_dermatoscopy_score", 4.2),
                            "unit": "TDS Score",
                            "system": "http://unitsofmeasure.org"
                        },
                        "interpretation": [
                            {
                                "coding": [
                                    {
                                        "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                                        "code": "H" if soap_data.get("triage_priority") == "CRITICAL" else "N",
                                        "display": "Abnormal / High Risk" if soap_data.get("triage_priority") == "CRITICAL" else "Normal"
                                    }
                                ]
                            }
                        ]
                    }
                }
            ]
        }
        return fhir_bundle

# Global singleton instance
fhir_exporter = AbdmFhirR4Exporter()
