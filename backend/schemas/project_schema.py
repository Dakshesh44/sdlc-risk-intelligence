from pydantic import BaseModel, Field
from typing import Literal


class ProjectInput(BaseModel):

    # 🟢 NUMERIC INPUTS
    project_budget: float = Field(..., gt=0)
    project_duration_months: int = Field(..., ge=1, le=60)
    team_size: int = Field(..., ge=1, le=50)
    number_of_integrations: int = Field(..., ge=0)

    # 🟢 SLIDER INPUTS (1–5 scale)
    team_experience_level: int = Field(..., ge=1, le=5)
    agile_maturity_level: int = Field(..., ge=1, le=5)
    requirement_clarity: int = Field(..., ge=1, le=5)
    client_involvement_level: int = Field(..., ge=1, le=5)
    regulatory_strictness: int = Field(..., ge=1, le=5)
    system_complexity: int = Field(..., ge=1, le=5)
    automation_level: int = Field(..., ge=1, le=5)
    delivery_urgency: int = Field(..., ge=1, le=5)

    # 🟢 DROPDOWN INPUTS (must be 1, 3, or 5 only)
    requirement_change_frequency: Literal[1, 3, 5]
    decision_making_speed: Literal[1, 3, 5]
    domain_criticality: Literal[1, 3, 5]
    risk_tolerance_level: Literal[1, 3, 5]
