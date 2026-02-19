"""
ML PRIMARY RISK ENGINE (Stable Version)

- ML is primary decision engine.
- Baseline remains as fallback.
- No recursion.
- Consistent response contract.
- Inference timing included.
"""

import logging
import time
import uuid

from backend.utils.prediction_logger import log_prediction
from backend.ml.model_loader import predict_proba, get_class_labels, get_feature_order
from backend.utils.preprocessing import generate_engineered_features
from backend.utils.risk_scoring import (
    calculate_risk_scores,
    calculate_feature_contributions
)

logger = logging.getLogger(__name__)


# ===============================
# ML ENGINE
# ===============================

def run_ml_engine(features: dict):

    feature_order = get_feature_order()
    feature_vector = [features[name] for name in feature_order]

    if len(feature_vector) != len(feature_order):
        raise ValueError("Feature vector length mismatch")

    probabilities = predict_proba(feature_vector)
    class_labels = get_class_labels()

    if len(probabilities) != len(class_labels):
        raise ValueError("Model output size mismatch")

    scores = {
        class_labels[i]: round(float(probabilities[i]), 4)
        for i in range(len(class_labels))
    }

    ranking = sorted(scores, key=scores.get, reverse=True)
    recommended = ranking[0]

    if len(ranking) > 1:
        best = scores[ranking[0]]
        second = scores[ranking[1]]
        confidence = round(best - second, 4)
    else:
        confidence = 1.0

    risk_band = {
        model: (
            "Low" if score > 0.66 else
            "Medium" if score > 0.33 else
            "High"
        )
        for model, score in scores.items()
    }

    return {
        "risks": scores,
        "ranking": ranking,
        "recommended": recommended,
        "confidence": confidence,
        "risk_band": risk_band,
        "top_contributing_factors": [],  # Placeholder (SHAP later)
        "model_version": "ml_v1"
    }


# ===============================
# BASELINE ENGINE (FALLBACK)
# ===============================

def classify_risk(score: float) -> str:
    if score < 0.33:
        return "Low"
    elif score < 0.66:
        return "Medium"
    else:
        return "High"


def run_baseline_engine(features: dict):

    scores = calculate_risk_scores(features)

    ranking = sorted(scores, key=scores.get)
    recommended = ranking[0]

    if len(ranking) > 1:
        best_score = scores[ranking[0]]
        second_score = scores[ranking[1]]
        confidence = (
            round((second_score - best_score) / second_score, 4)
            if second_score != 0
            else 1.0
        )
    else:
        confidence = 1.0

    risk_band = {
        model: classify_risk(score)
        for model, score in scores.items()
    }

    contributions = calculate_feature_contributions(features, recommended)
    top_factors = list(contributions.keys())[:3]

    return {
        "risks": scores,
        "ranking": ranking,
        "recommended": recommended,
        "confidence": confidence,
        "risk_band": risk_band,
        "top_contributing_factors": top_factors,
        "model_version": "baseline_v1"
    }


# ===============================
# ORCHESTRATOR
# ===============================

def run_risk_engine(project):

    start_time = time.time()
    features = generate_engineered_features(project)
    project_id = str(uuid.uuid4())

    try:
        result = run_ml_engine(features)
        result["inference_time"] = round(time.time() - start_time, 4)
        result["project_id"] = project_id

        log_prediction(project_id, features, result)

        return result

    except Exception as e:
        logger.error(f"ML engine failed: {e}")
        fallback = run_baseline_engine(features)
        fallback["inference_time"] = round(time.time() - start_time, 4)
        fallback["project_id"] = project_id
        fallback["ml_error"] = str(e)

        log_prediction(project_id, features, fallback)

        return fallback
