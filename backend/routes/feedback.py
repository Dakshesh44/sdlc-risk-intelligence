from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pandas as pd
import os
from datetime import datetime
from typing import Optional

router = APIRouter()

PREDICTION_FILE = "data/predictions.csv"
FEEDBACK_FILE = "data/feedback.csv"


class FeedbackInput(BaseModel):
    project_id: str
    actual_outcome: Optional[str] = None
    notes: Optional[str] = None
    actual_sdlc_used: Optional[str] = None
    success_score: Optional[int] = None
    risk_realized: Optional[str] = None
    completion_status: Optional[str] = None


@router.post("/feedback")
def submit_feedback(data: FeedbackInput):

    # Ensure predictions file exists
    if not os.path.exists(PREDICTION_FILE):
        raise HTTPException(status_code=400, detail="No predictions available.")

    df = pd.read_csv(PREDICTION_FILE)

    if "project_id" not in df.columns:
        raise HTTPException(status_code=500, detail="Prediction file corrupted.")

    if data.project_id not in df["project_id"].astype(str).values:
        raise HTTPException(status_code=400, detail="Invalid project_id.")

    # Ensure data folder exists
    os.makedirs("data", exist_ok=True)

    feedback_row = {
        "project_id": data.project_id,
        "timestamp": datetime.utcnow().isoformat(),
        "actual_outcome": data.actual_outcome or "",
        "notes": data.notes or "",
        "actual_sdlc_used": data.actual_sdlc_used or "",
        "success_score": data.success_score if data.success_score is not None else "",
        "risk_realized": data.risk_realized or "",
        "completion_status": data.completion_status or "",
    }

    # Append feedback safely
    if os.path.exists(FEEDBACK_FILE):
        feedback_df = pd.read_csv(FEEDBACK_FILE)
        feedback_df = pd.concat(
            [feedback_df, pd.DataFrame([feedback_row])],
            ignore_index=True
        )
    else:
        feedback_df = pd.DataFrame([feedback_row])

    feedback_df.to_csv(FEEDBACK_FILE, index=False)

    return {"message": "Feedback recorded successfully."}
