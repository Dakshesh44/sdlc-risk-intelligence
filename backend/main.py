import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ml.model_loader import load_model
from backend.routes.feedback import router as feedback_router
from backend.routes.model_status import router as model_status_router
from backend.routes.predict import router as predict_router

logger = logging.getLogger(__name__)
app = FastAPI()

# Allow local and deployed frontend apps to call the API.
cors_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,https://helix-risk.onrender.com,https://helixrisk.vercel.app",
)
allow_origins = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]
cors_origin_regex = os.getenv("CORS_ORIGIN_REGEX", r"https://.*\.(onrender\.com|vercel\.app)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_origin_regex=cors_origin_regex,
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
