from fastapi import FastAPI
from backend.routes.predict import router as predict_router

app = FastAPI()

app.include_router(predict_router)

@app.get("/")
def root():
    return {"message": "Backend running successfully"}
