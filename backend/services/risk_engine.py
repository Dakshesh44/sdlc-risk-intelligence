from backend.utils.preprocessing import generate_engineered_features
from backend.utils.risk_scoring import (
    calculate_risk_scores,
    calculate_feature_contributions
)

def classify_risk(score):
    if score < 0.33:
        return "Low"
    elif score < 0.66:
        return "Medium"
    else:
        return "High"

def run_risk_engine(project):

    features = generate_engineered_features(project)
    scores = calculate_risk_scores(features)

    ranking = sorted(scores, key=scores.get)
    recommended = ranking[0]

    best_score = scores[ranking[0]]
    second_score = scores[ranking[1]]

    if second_score == 0:
        confidence = 1
    else:
        confidence = round((second_score - best_score) / second_score, 4)

    risk_band = {
        model: classify_risk(score)
        for model, score in scores.items()
    }

    # 🔥 Explainability
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
