import csv
import os
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
LOG_PATH = BASE_DIR / "data" / "predictions.csv"


def log_prediction(project_id: str, features: dict, result: dict):

    file_exists = LOG_PATH.exists()

    row = {
        "project_id": project_id,
        "timestamp": datetime.utcnow().isoformat(),
        **features,
        "recommended": result["recommended"],
        "confidence": result["confidence"],
        "model_version": result["model_version"],
        "inference_time": result["inference_time"],
    }

    # Add per-model probabilities
    for model, score in result["risks"].items():
        row[f"prob_{model}"] = score

    with open(LOG_PATH, mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=row.keys())

        if not file_exists:
            writer.writeheader()

        writer.writerow(row)
