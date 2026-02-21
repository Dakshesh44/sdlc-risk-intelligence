"""
Single-entry inference service.

All prediction orchestration lives in ml.predictor.run_prediction.
"""

from ml.predictor import run_prediction


def run_risk_engine(project):
    return run_prediction(project)
