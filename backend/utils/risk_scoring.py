from backend.utils.model_profiles import MODEL_PROFILES

def calculate_feature_contributions(features: dict, model: str):
    weights = MODEL_PROFILES[model]

    contributions = {}

    for feature_name, weight in weights.items():
        contributions[feature_name] = round(features.get(feature_name, 0) * weight, 4)

    # Sort descending by impact
    sorted_contributions = dict(
        sorted(contributions.items(), key=lambda x: x[1], reverse=True)
    )

    return sorted_contributions


def calculate_risk_scores(features: dict):

    scores = {}

    for model, weights in MODEL_PROFILES.items():

        score = 0

        for feature_name, weight in weights.items():
            feature_value = features.get(feature_name, 0)
            score += feature_value * weight

        scores[model] = round(score, 4)

    return scores
