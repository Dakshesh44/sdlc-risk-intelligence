from fastapi import APIRouter
from backend.schemas.project_schema import ProjectInput

router = APIRouter()

@router.post("/predict")
def predict(project: ProjectInput):
    return {
        "message": "Validation successful"
    }
