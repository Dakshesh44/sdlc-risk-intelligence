from fastapi import APIRouter
from backend.schemas.project_schema import ProjectInput
from backend.utils.preprocessing import generate_engineered_features
from backend.services.risk_engine import calculate_risk_scores
from backend.services.risk_engine import run_risk_engine

router = APIRouter()

@router.post("/predict")
@router.post("/predict")
def predict(project: ProjectInput):
    result = run_risk_engine(project)
    return result