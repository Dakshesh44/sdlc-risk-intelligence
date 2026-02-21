from fastapi import APIRouter
from backend.schemas.project_schema import ProjectInput
from backend.services.risk_engine import run_risk_engine

router = APIRouter()


@router.post("/predict")
def predict(project: ProjectInput):

    # Logging and project_id assignment are handled by run_risk_engine.
    return run_risk_engine(project)
