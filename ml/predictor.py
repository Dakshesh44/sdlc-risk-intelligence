import os
import json
import joblib
import numpy as np
import shap
from .feature_config import FEATURE_ORDER

# -----------------------------
# 1️⃣ Load Model Artifacts (once)
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "model")

MODEL_PATH = os.path.join(MODEL_DIR, "sdlc_model.pkl")
ENCODER_PATH = os.path.join(MODEL_DIR, "label_encoder.pkl")

model = joblib.load(MODEL_PATH)
label_encoder = joblib.load(ENCODER_PATH)

explainer = shap.TreeExplainer(model)


# -----------------------------
# 2️⃣ Prediction Function
# -----------------------------
def predict(project_features: dict) -> dict:
    """
    Input:
        project_features: dict of 28 normalized feature values (0–1)

    Output:
        {
            predicted_sdlc: str,
            confidence_score: float,
            probabilities: dict,
            top_features: list
        }
    """

    # -----------------------------
    # Validate Input
    # -----------------------------
    missing_features = [
        f for f in FEATURE_ORDER if f not in project_features
    ]
    if missing_features:
        raise ValueError(f"Missing required features: {missing_features}")

    # -----------------------------
    # Convert to Ordered Vector
    # -----------------------------
    input_vector = np.array(
        [[project_features[f] for f in FEATURE_ORDER]]
    )

    # -----------------------------
    # Model Prediction
    # -----------------------------
    probabilities = model.predict_proba(input_vector)[0]
    predicted_index = int(np.argmax(probabilities))

    predicted_sdlc = label_encoder.inverse_transform(
        [predicted_index]
    )[0]

    confidence_score = float(probabilities[predicted_index])

    # -----------------------------
    # SHAP Explanation
    # -----------------------------
    shap_values = explainer.shap_values(input_vector)

    # Multi-class → select SHAP for predicted class
    class_shap_values = shap_values[predicted_index][0]

    feature_impacts = [
        {
            "feature": FEATURE_ORDER[i],
            "impact": float(class_shap_values[i])
        }
        for i in range(len(FEATURE_ORDER))
    ]

    # Sort by absolute impact
    feature_impacts.sort(
        key=lambda x: abs(x["impact"]),
        reverse=True
    )

    top_features = feature_impacts[:3]

    # -----------------------------
    # Structured Output
    # -----------------------------
    return {
        "predicted_sdlc": predicted_sdlc,
        "confidence_score": confidence_score,
        "probabilities": {
            label_encoder.inverse_transform([i])[0]: float(probabilities[i])
            for i in range(len(probabilities))
        },
        "top_features": top_features
    }
