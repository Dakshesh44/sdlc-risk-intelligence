"""
MODEL LOADER - Strict ML Integrity Layer
"""

import json
from pathlib import Path

import joblib


# =========================
# PATH CONFIGURATION
# =========================

BASE_DIR = Path(__file__).resolve().parents[1]

MODEL_PATH = BASE_DIR / "model" / "model.pkl"
ENCODER_PATH = BASE_DIR / "model" / "label_encoder.pkl"
METADATA_PATH = BASE_DIR / "model" / "model_metadata.json"


# =========================
# CACHED INSTANCES
# =========================

_model = None
_label_encoder = None
_metadata = None


# =========================
# LOAD METADATA
# =========================

def load_metadata():
    global _metadata

    if _metadata is None:
        if not METADATA_PATH.exists():
            raise FileNotFoundError(
                f"Metadata file not found at {METADATA_PATH}"
            )

        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            _metadata = json.load(f)

    return _metadata


# =========================
# LOAD MODEL
# =========================

def load_model():
    global _model

    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model file not found at {MODEL_PATH}"
            )

        try:
            _model = joblib.load(MODEL_PATH)
        except ModuleNotFoundError as e:
            if "xgboost" in str(e):
                raise RuntimeError(
                    "Model requires xgboost. Install dependencies from requirements.txt."
                ) from e

            raise

        metadata = load_metadata()

        # STRICT CLASS COUNT CHECK
        if len(metadata["class_labels"]) != _model.n_classes_:
            raise ValueError(
                "Class label count mismatch with trained model"
            )

    return _model


# =========================
# LOAD ENCODER
# =========================

def load_encoder():
    global _label_encoder

    if _label_encoder is None:
        if not ENCODER_PATH.exists():
            raise FileNotFoundError(
                f"Encoder file not found at {ENCODER_PATH}"
            )

        _label_encoder = joblib.load(ENCODER_PATH)

    return _label_encoder


# =========================
# VALIDATE INTEGRITY
# =========================

def validate_model_integrity():
    metadata = load_metadata()
    encoder = load_encoder()

    if metadata["feature_count"] != len(metadata["feature_order"]):
        raise ValueError("Feature count mismatch in metadata")

    if list(encoder.classes_) != metadata["class_labels"]:
        raise ValueError(
            "Class label mismatch between encoder and metadata"
        )

    return True


# =========================
# FEATURE ORDER
# =========================

def get_feature_order():
    metadata = load_metadata()
    feature_order = metadata.get("feature_order", [])

    if len(feature_order) != metadata.get("feature_count"):
        raise ValueError("Invalid metadata: feature_count and feature_order mismatch")

    return feature_order


# =========================
# PREDICT
# =========================

def predict_proba(feature_vector: list):
    if len(feature_vector) != len(get_feature_order()):
        raise ValueError("Feature vector length mismatch")

    validate_model_integrity()

    model = load_model()
    probabilities = model.predict_proba([feature_vector])[0]

    return probabilities


# =========================
# GET CLASS LABELS
# =========================

def get_class_labels():
    metadata = load_metadata()
    return metadata["class_labels"]
