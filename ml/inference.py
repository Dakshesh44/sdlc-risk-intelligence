import os
import joblib
import numpy as np
import shap

# --------------------------------------------------
# 🔹 PATH CONFIGURATION
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "model", "xgb_sdlc_model.pkl")
ENCODER_PATH = os.path.join(BASE_DIR, "model", "label_encoder.pkl")

# --------------------------------------------------
# 🔹 LOAD MODEL + ENCODER (ONCE)
# --------------------------------------------------
model = joblib.load(MODEL_PATH)
label_encoder = joblib.load(ENCODER_PATH)

# Initialize SHAP explainer once
explainer = shap.TreeExplainer(model)

# --------------------------------------------------
# 🔹 STRICT FEATURE ORDER (FREEZE THIS)
# --------------------------------------------------
FEATURE_ORDER = [
    "requirements_volatility",
    "requirements_clarity_score",
    "automation_maturity_score",
    "overall_uncertainty_index",
    "risk_management_maturity",
    "team_capacity_index",
    "technical_complexity_index",
    "schedule_pressure_index",
    "time_to_market_pressure",
    "budget_adequacy_ratio",
    "stakeholder_involvement_index",
    "documentation_rigor_score",
    "testing_maturity_score",
    "integration_complexity_score",
    "deployment_frequency_index",
    "change_request_rate",
    "project_scale_index",
    "legacy_dependency_score",
    "innovation_level_index",
    "regulatory_constraint_index",
    "cross_team_dependency_index",
    "security_sensitivity_score",
    "client_feedback_frequency",
    "defect_density_estimate",
    "devops_tooling_score",
    "architecture_stability_index",
    "requirement_ambiguity_index",
    "delivery_iteration_speed"
]

# --------------------------------------------------
# 🔹 INPUT VALIDATION
# --------------------------------------------------
def _validate_input(features_dict: dict):
    missing = [f for f in FEATURE_ORDER if f not in features_dict]
    if missing:
        raise ValueError(f"Missing features: {missing}")

    for key in FEATURE_ORDER:
        val = features_dict[key]
        if not isinstance(val, (int, float)):
            raise ValueError(f"Feature '{key}' must be numeric.")
        if val < 0 or val > 1:
            raise ValueError(f"Feature '{key}' must be between 0 and 1.")

# --------------------------------------------------
# 🔹 MAIN PREDICTION FUNCTION
# --------------------------------------------------
def predict_project(features_dict: dict) -> dict:
    """
    Input: dict of 28 normalized feature values (0-1)
    Output: structured prediction dictionary
    """

    _validate_input(features_dict)

    # Arrange in strict order
    input_array = np.array([[features_dict[f] for f in FEATURE_ORDER]])

    # Predict probabilities
    probabilities = model.predict_proba(input_array)[0]

    # Get predicted class
    predicted_index = np.argmax(probabilities)
    predicted_sdlc = label_encoder.inverse_transform([predicted_index])[0]

    # Confidence score
    confidence_score = float(np.max(probabilities))

    # Build probability dictionary
    prob_dict = {
        label_encoder.inverse_transform([i])[0]: float(probabilities[i])
        for i in range(len(probabilities))
    }

    # --------------------------------------------------
    # 🔹 SHAP EXPLANATION
    # --------------------------------------------------
    shap_values = explainer.shap_values(input_array)

    # Multi-class: shap_values is list per class
    class_shap = shap_values[predicted_index][0]

    # Get top 3 contributing features
    feature_impacts = list(zip(FEATURE_ORDER, class_shap))
    feature_impacts_sorted = sorted(
        feature_impacts,
        key=lambda x: abs(x[1]),
        reverse=True
    )

    top_features = [
        {
            "feature": feat,
            "impact": float(impact)
        }
        for feat, impact in feature_impacts_sorted[:3]
    ]

    return {
        "predicted_sdlc": predicted_sdlc,
        "confidence_score": confidence_score,
        "probabilities": prob_dict,
        "top_features": top_features
    }

if __name__ == "__main__":
    # Generate random valid input
    test_input = {f: 0.5 for f in FEATURE_ORDER}

    result = predict_project(test_input)

    print("\nTest Prediction Output:")
    print(result)
