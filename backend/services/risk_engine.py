"""
SOURCE OF TRUTH — BASELINE RISK ENGINE (v1)

This file defines the canonical risk computation logic.
All ML training pipelines must use this engine as teacher.
Any modification requires version upgrade.

Deterministic. No randomness allowed.
"""

from backend.utils.preprocessing import generate_engineered_features
from backend.utils.risk_scoring import (
    calculate_risk_scores,
    calculate_feature_contributions
)


def classify_risk(score: float) -> str:
    """
    Classify risk score into categorical band.
    """
    if score < 0.33:
        return "Low"
    elif score < 0.66:
        return "Medium"
    else:
        return "High"


def run_risk_engine(project):
    """
    Main orchestration function for baseline risk evaluation.

    Steps:
    1. Feature engineering
    2. Risk scoring per SDLC
    3. Ranking
    4. Confidence computation
    5. Risk band classification
    6. Explainability (top contributing factors)
    """

    # 1️⃣ Feature Engineering
    features = generate_engineered_features(project)

    # 2️⃣ Risk Calculation
    scores = calculate_risk_scores(features)

    if not scores:
        raise ValueError("Risk scores could not be computed.")

    # 3️⃣ Ranking (Lower score = lower risk)
    ranking = sorted(scores, key=scores.get)

    if len(ranking) < 1:
        raise ValueError("Ranking failed. No SDLC models available.")

    recommended = ranking[0]

    # 4️⃣ Confidence Calculation
    if len(ranking) < 2:
        confidence = 1.0
    else:
        best_score = scores[ranking[0]]
        second_score = scores[ranking[1]]

        if second_score == 0:
            confidence = 1.0
        else:
            confidence = round(
                (second_score - best_score) / second_score,
                4
            )

    # 5️⃣ Risk Band Classification
    risk_band = {
        model: classify_risk(score)
        for model, score in scores.items()
    }

    # 6️⃣ Explainability (Top 3 Contributing Factors)
    contributions = calculate_feature_contributions(features, recommended)
    top_factors = list(contributions.keys())[:3]

    # Final Structured Response
    return {
        "risks": scores,
        "ranking": ranking,
        "recommended": recommended,
        "confidence": confidence,
        "risk_band": risk_band,
        "top_contributing_factors": top_factors,
        "model_version": "baseline_v1"
    }
