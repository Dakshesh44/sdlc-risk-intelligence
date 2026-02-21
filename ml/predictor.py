import logging
import os
import time
import uuid

import numpy as np

from backend.utils.prediction_logger import log_prediction
from backend.utils.preprocessing import generate_engineered_features
from backend.utils.risk_scoring import (
    calculate_feature_contributions,
    calculate_risk_scores,
)
from ml.model_loader import (
    get_class_labels,
    get_feature_order,
    load_model,
    predict_proba,
)

logger = logging.getLogger(__name__)
_SHAP_EXPLAINER = None
_SHAP_INIT_ERROR = None
_SHAP_INIT_ATTEMPTED = False


def _confidence_from_descending_scores(scores: dict, ranking: list) -> float:
    if len(ranking) <= 1:
        return 1.0
    best = scores[ranking[0]]
    second = scores[ranking[1]]
    return round(best - second, 4)


def _confidence_from_ascending_scores(scores: dict, ranking: list) -> float:
    if len(ranking) <= 1:
        return 1.0
    best = scores[ranking[0]]
    second = scores[ranking[1]]
    if second == 0:
        return 1.0
    return round((second - best) / second, 4)


def _shap_enabled() -> bool:
    raw = str(os.getenv("SDLC_ENABLE_SHAP", "1")).strip().lower()
    return raw not in {"0", "false", "no", "off"}


def _get_shap_explainer():
    global _SHAP_EXPLAINER, _SHAP_INIT_ERROR, _SHAP_INIT_ATTEMPTED

    if not _shap_enabled():
        raise RuntimeError("SHAP disabled by SDLC_ENABLE_SHAP")

    if _SHAP_EXPLAINER is not None:
        return _SHAP_EXPLAINER

    if _SHAP_INIT_ATTEMPTED and _SHAP_INIT_ERROR is not None:
        raise _SHAP_INIT_ERROR

    _SHAP_INIT_ATTEMPTED = True
    try:
        import shap  # Imported lazily to avoid hard-failing module import paths.

        _SHAP_EXPLAINER = shap.TreeExplainer(load_model())
        return _SHAP_EXPLAINER
    except Exception as error:
        _SHAP_INIT_ERROR = error
        raise


def _extract_shap_top_factors(features: dict, recommended: str, top_k: int = 3) -> list:
    feature_order = get_feature_order()
    class_labels = get_class_labels()
    feature_vector = np.array([[features[name] for name in feature_order]])
    explainer = _get_shap_explainer()
    shap_values = explainer.shap_values(feature_vector)
    class_index = class_labels.index(recommended)

    if isinstance(shap_values, list):
        class_shap_values = shap_values[class_index][0]
    else:
        values = getattr(shap_values, "values", shap_values)
        values = np.asarray(values)
        if values.ndim == 3:
            class_shap_values = values[0, :, class_index]
        elif values.ndim == 2:
            class_shap_values = values[0]
        else:
            raise ValueError("Unsupported SHAP output shape")

    impacts = sorted(
        zip(feature_order, class_shap_values),
        key=lambda pair: abs(float(pair[1])),
        reverse=True,
    )
    return [name for name, _ in impacts[:top_k]]


def _build_ml_result(project) -> tuple[dict, dict]:
    features = generate_engineered_features(project)
    feature_order = get_feature_order()
    feature_vector = [features[name] for name in feature_order]

    probabilities = predict_proba(feature_vector)
    class_labels = get_class_labels()

    if len(probabilities) != len(class_labels):
        raise ValueError("Model output size mismatch")

    risks = {
        class_labels[i]: round(float(probabilities[i]), 4)
        for i in range(len(class_labels))
    }
    ranking = sorted(risks, key=risks.get, reverse=True)
    recommended = ranking[0]
    confidence = _confidence_from_descending_scores(risks, ranking)

    try:
        top_factors = _extract_shap_top_factors(features, recommended)
        explainability_source = "shap"
    except Exception as shap_error:
        logger.warning("SHAP explainability unavailable, using weighted fallback: %s", shap_error)
        contributions = calculate_feature_contributions(features, recommended)
        top_factors = list(contributions.keys())[:3]
        explainability_source = "fallback"

    result = {
        "recommended": recommended,
        "risks": risks,
        "ranking": ranking,
        "confidence": confidence,
        "model_version": "ml_v1",
        "top_contributing_factors": top_factors,
        "explainability_source": explainability_source,
    }
    return result, features


def _build_baseline_result(project) -> tuple[dict, dict]:
    features = generate_engineered_features(project)
    risks = calculate_risk_scores(features)
    ranking = sorted(risks, key=risks.get)
    recommended = ranking[0]
    confidence = _confidence_from_ascending_scores(risks, ranking)
    top_factors = list(calculate_feature_contributions(features, recommended).keys())[:3]

    result = {
        "recommended": recommended,
        "risks": risks,
        "ranking": ranking,
        "confidence": confidence,
        "model_version": "baseline_v1",
        "top_contributing_factors": top_factors,
        "explainability_source": "fallback",
    }
    return result, features


def run_prediction(project_input):
    start = time.time()
    project_id = str(uuid.uuid4())

    try:
        result, features = _build_ml_result(project_input)
    except Exception as ml_error:
        logger.error("ML prediction failed, switching to baseline: %s", ml_error)
        result, features = _build_baseline_result(project_input)

    result["inference_time"] = round(time.time() - start, 4)
    result["project_id"] = project_id

    log_prediction(project_id, features, result)
    return result
