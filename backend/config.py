"""
OmniCare AI - System & Hardware Configuration
Target Platform: Snapdragon-Powered HP PCs (HP OmniBook X / HP EliteBook Ultra)
Hexagon NPU: 45 TOPS Peak Compute Engine
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"
SAMPLES_DIR = BASE_DIR / "samples"
VAULT_DIR = BASE_DIR / "security" / "vault_storage"

# Ensure directories exist
MODELS_DIR.mkdir(parents=True, exist_ok=True)
SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
VAULT_DIR.mkdir(parents=True, exist_ok=True)

# Hardware Specifications
HARDWARE_PROFILE = {
    "device_name": "HP OmniBook X 14 / HP EliteBook Ultra G1q",
    "processor": "Snapdragon X Elite (12 Oryon Cores @ 3.4GHz / 4.0GHz Boost)",
    "npu": "Qualcomm Hexagon NPU",
    "npu_peak_tops": 45.0,
    "memory": "16GB / 32GB LPDDR5x @ 8448 MT/s",
    "audio_subsystem": "HP Poly Studio Dual Microphone Array (AI Beamforming)",
    "security_enclave": "HP Wolf Pro Security Edition & Microsoft Pluton",
    "battery_endurance_hours": 26.0,
    "typical_npu_power_watts": 4.5
}

# Prioritized ONNX Runtime Execution Providers
# 1. QNNExecutionProvider: Direct HTP (Hexagon Tensor Processor) hardware acceleration
# 2. DmlExecutionProvider: DirectML acceleration for Snapdragon Adreno GPU
# 3. CPUExecutionProvider: Standard evaluation fallback
EXECUTION_PROVIDER_PRIORITY = [
    (
        "QNNExecutionProvider",
        {
            "backend_path": "QnnHtp.dll",  # Qualcomm Hexagon Tensor Processor backend
            "htp_performance_mode": "burst",
            "enable_htp_fp16_precision": "1",
        },
    ),
    ("DmlExecutionProvider", {"device_id": 0}),
    ("CPUExecutionProvider", {}),
]

# Qualcomm AI Hub Model Manifest
QUALCOMM_AI_HUB_MODELS = {
    "vision_lesion": {
        "model_id": "yolov8_seg",
        "name": "YOLOv8-Seg Skin Lesion Segmentation (Quantized INT8)",
        "input_shape": [1, 3, 640, 640],
        "target_runtime": "qnn_lib_aarch64",
        "precision": "int8",
        "mean_latency_ms_npu": 12.4,
        "classes": [
            "Melanoma",
            "Basal Cell Carcinoma (BCC)",
            "Benign Keratosis (BKL)",
            "Eczema / Dermatitis",
            "Normal / Benign Nevus"
        ]
    },
    "vision_retina": {
        "model_id": "resnet50_quantized",
        "name": "ResNet-50 Retinal Fundus Screening (Quantized INT8)",
        "input_shape": [1, 3, 224, 224],
        "target_runtime": "qnn_lib_aarch64",
        "precision": "int8",
        "mean_latency_ms_npu": 8.6,
        "classes": [
            "No Diabetic Retinopathy",
            "Mild Non-Proliferative DR",
            "Moderate DR",
            "Severe DR / Proliferative",
            "Glaucoma Suspect"
        ]
    },
    "audio_pulmonary": {
        "model_id": "yamnet_respiratory",
        "name": "YAMNet Pulmonary Biomarker Classifier (Quantized INT8)",
        "input_shape": [1, 15600],
        "target_runtime": "qnn_lib_aarch64",
        "precision": "int8",
        "mean_latency_ms_npu": 6.8,
        "classes": [
            "Normal Vesicular Breath Sound",
            "Fine / Coarse Crackles (Pneumonia / Fibrosis)",
            "High-Pitched Wheezing (Asthma / COPD)",
            "Stridor / Upper Airway Obstruction",
            "Pleural Friction Rub"
        ]
    },
    "speech_dictation": {
        "model_id": "whisper_small",
        "name": "Whisper-Small Multilingual Speech-to-Text (FP16/INT8)",
        "target_runtime": "qnn_lib_aarch64",
        "mean_latency_ms_npu": 18.2,
        "supported_languages": ["en", "hi", "bn", "ta", "te", "mr"]
    },
    "language_scribe": {
        "model_id": "llama_v3_2_3b_instruct",
        "name": "Llama-3.2-3B-Instruct Clinical Scribe (INT4 QNN)",
        "target_runtime": "qnn_lib_aarch64",
        "tokens_per_second_npu": 34.2
    }
}

# Clinical ABCD Rule Thresholds
ABCD_THRESHOLDS = {
    "asymmetry_high_risk": 35.0,     # >35% difference in quadrant area
    "border_irregularity_high": 1.45, # Compactness ratio P^2 / 4*pi*A
    "color_variegation_min_colors": 3,
    "diameter_high_risk_mm": 6.0      # >6mm indicates elevated risk
}

# ICD-10 Mapping Table
ICD10_MAPPING = {
    "Melanoma": {"code": "C43.9", "description": "Malignant melanoma of skin, unspecified"},
    "Basal Cell Carcinoma (BCC)": {"code": "C44.91", "description": "Basal cell carcinoma of skin, unspecified"},
    "Benign Keratosis (BKL)": {"code": "L82.1", "description": "Other seborrheic keratosis"},
    "Eczema / Dermatitis": {"code": "L20.9", "description": "Atopic dermatitis, unspecified"},
    "Normal / Benign Nevus": {"code": "D22.9", "description": "Melanocytic nevi, unspecified"},
    "Fine / Coarse Crackles (Pneumonia / Fibrosis)": {"code": "J18.9", "description": "Pneumonia, unspecified organism"},
    "High-Pitched Wheezing (Asthma / COPD)": {"code": "J45.909", "description": "Unspecified asthma, uncomplicated"},
    "Stridor / Upper Airway Obstruction": {"code": "R06.1", "description": "Stridor"},
    "Moderate DR": {"code": "E11.339", "description": "Type 2 diabetes mellitus with moderate nonproliferative diabetic retinopathy"},
    "Glaucoma Suspect": {"code": "H40.00", "description": "Glaucoma suspect, unspecified"}
}
