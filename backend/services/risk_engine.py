"""
ML PRIMARY RISK ENGINE (Transition Phase)

- ML is primary decision engine.
- Baseline remains as fallback.
- No recursion.
"""

from backend.ml.feature_config import FEATURE_ORDER
from backend.ml.model_loader import predict_proba
from backend.utils.preprocessing import generate_engineered_features
from backend.utils.risk_scoring import (
    calculate_risk_scores,
    calculate_feature_contributions
)

SDLC_CLASSES = [
    "Waterfall",
    "Agile",
    "Spiral",
    "V-Model",
    "DevOps",
    "Hybrid"
]


# ===============================
# ML ENGINE
# ===============================

def run_ml_engine(features: dict):

    feature_vector = [features[name] for name in FEATURE_ORDER]
    if len(feature_vector) != 28:
        raise ValueError("Feature vector length mismatch")
    probabilities = predict_proba(feature_vector)

    scores = {
        SDLC_CLASSES[i]: round(float(probabilities[i]), 4)
        for i in range(len(SDLC_CLASSES))
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


def run_baseline_engine(project):

    features = generate_engineered_features(project)
    scores = calculate_risk_scores(features)

    ranking = sorted(scores, key=scores.get)
    recommended = ranking[0]

    if len(ranking) > 1:
        best_score = scores[ranking[0]]
        second_score = scores[ranking[1]]
        confidence = round(
            (second_score - best_score) / second_score,
            4
        ) if second_score != 0 else 1.0
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

    features = generate_engineered_features(project)

    try:
        return run_ml_engine(features)
    except Exception:
        # If ML fails, use deterministic baseline
        return run_baseline_engine(project)
