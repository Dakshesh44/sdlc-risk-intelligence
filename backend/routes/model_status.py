from fastapi import APIRouter

from ml.model_loader import load_model

router = APIRouter()

@router.get("/model-status")
def model_status():
    try:
        load_model()
        ml_model_loaded = True
        error = None
    except Exception as e:
        ml_model_loaded = False
        error = str(e)

    return {
        "ml_model_loaded": ml_model_loaded,
        "mode": "ML_PRIMARY_WITH_FALLBACK",
        "error": error
    }
