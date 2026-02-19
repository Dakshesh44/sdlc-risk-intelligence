import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.ml.model_loader import load_model
from backend.routes.feedback import router as feedback_router
from backend.routes.model_status import router as model_status_router
from backend.routes.predict import router as predict_router

logger = logging.getLogger(__name__)
app = FastAPI()

# Allow local frontend apps (Vite/React/Next) to call the API during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict_router)
app.include_router(feedback_router)
app.include_router(model_status_router)


@app.on_event("startup")
def startup_load_model():
    try:
        load_model()
    except Exception as e:
        # Keep API alive; risk_engine will fallback to baseline.
        logger.error(f"ML startup load failed, baseline mode active: {e}")

@app.get("/")
def root():
    return {"message": "Backend running successfully"}
