from fastapi import APIRouter
import os

router = APIRouter()

@router.get("/model-status")
def model_status():
    model_exists = os.path.exists("backend/ml/model.pkl")

    return {
        "ml_model_loaded": model_exists,
        "mode": "ML_PRIMARY_WITH_FALLBACK"
    }
