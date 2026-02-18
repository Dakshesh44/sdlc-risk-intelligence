"""
MODEL LOADER — ML Inference Layer

Responsible for:
- Loading trained model
- Providing prediction interface
- Preventing reload on every request
"""

import os
import joblib

MODEL_PATH = "backend/ml/model.pkl"

_model = None  # Cached model instance


def load_model():
    global _model

    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Model file not found at {MODEL_PATH}"
            )

        _model = joblib.load(MODEL_PATH)

    return _model


def predict_proba(feature_vector: list):
    """
    Input: Ordered feature vector (length 28)
    Output: Probability array of 6 SDLC classes
    """
    model = load_model()
    probabilities = model.predict_proba([feature_vector])[0]
    return probabilities
