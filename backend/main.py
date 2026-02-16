from fastapi import FastAPI
from backend.routes.predict import router as predict_router

app = FastAPI()

app.include_router(predict_router)

@app.get("/")
def root():
    return {"message": "Backend running successfully"}

from backend.routes.model_status import router as status_router

app.include_router(status_router)
