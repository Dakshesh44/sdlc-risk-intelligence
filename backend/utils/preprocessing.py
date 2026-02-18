from backend.schemas.project_schema import ProjectInput


def preprocess_inputs(project: ProjectInput) -> dict:

    return {
        # Raw numeric
        "project_budget": project.project_budget,
        "project_duration_months": project.project_duration_months,
        "team_size": project.team_size,
        "number_of_integrations": project.number_of_integrations,

        # Normalized 1–5 scale inputs
        "team_experience_level": normalize_scale(project.team_experience_level),
        "agile_maturity_level": normalize_scale(project.agile_maturity_level),
        "requirement_clarity": normalize_scale(project.requirement_clarity),
        "client_involvement_level": normalize_scale(project.client_involvement_level),
        "regulatory_strictness": normalize_scale(project.regulatory_strictness),
        "system_complexity": normalize_scale(project.system_complexity),
        "automation_level": normalize_scale(project.automation_level),
        "delivery_urgency": normalize_scale(project.delivery_urgency),

        # Dropdown (treated same as scale)
        "requirement_change_frequency": normalize_scale(project.requirement_change_frequency),
        "decision_making_speed": normalize_scale(project.decision_making_speed),
        "domain_criticality": normalize_scale(project.domain_criticality),
        "risk_tolerance_level": normalize_scale(project.risk_tolerance_level),
    }

def normalize_scale(value: int) -> float:
    """
    Normalize 1–5 scale to 0–1 range.
    """
    return (value - 1) / 4


def normalize_numeric(value: float, max_value: float) -> float:
    """
    Basic numeric normalization.
    Prevents exploding values.
    """
    return value / max_value
def generate_engineered_features(project: ProjectInput) -> dict:
    data = preprocess_inputs(project)

    # --- STRUCTURE & SCALE ---
    project_scale_index = (data["project_budget"] / 1_000_000) + (data["team_size"] / 50)
    budget_adequacy_ratio = data["project_budget"] / (data["team_size"] * 10000)
    schedule_pressure_index = data["delivery_urgency"] / (project.project_duration_months / 12)
    team_capacity_index = data["team_size"] * data["team_experience_level"]
    team_experience_score = data["team_experience_level"]
    domain_familiarity_score = 1 - data["domain_criticality"]

    # --- REQUIREMENTS & SCOPE ---
    requirements_volatility = data["requirement_change_frequency"]
    requirements_clarity_score = data["requirement_clarity"]
    scope_complexity_index = data["system_complexity"]
    stakeholder_alignment_score = data["client_involvement_level"]
    change_request_intensity = data["requirement_change_frequency"]

    # --- PROCESS & GOVERNANCE ---
    process_maturity_score = data["agile_maturity_level"]
    sprint_discipline_score = data["agile_maturity_level"]
    decision_latency_index = 1 - data["decision_making_speed"]
    risk_management_maturity = data["agile_maturity_level"]
    client_engagement_score = data["client_involvement_level"]

    # --- TECHNICAL RISK ---
    technical_complexity_index = data["system_complexity"]
    integration_risk_index = project.number_of_integrations / 20
    automation_maturity_score = data["automation_level"]
    toolchain_reliability_score = data["automation_level"]
    legacy_dependency_index = data["system_complexity"]

    # --- ENVIRONMENT & EXTERNAL ---
    regulatory_risk_index = data["regulatory_strictness"]
    domain_criticality_index = data["domain_criticality"]
    external_dependency_risk = project.number_of_integrations / 20

    # --- DELIVERY PRESSURE ---
    time_to_market_pressure = data["delivery_urgency"]
    resource_stability_index = data["team_experience_level"]
    risk_tolerance_index = data["risk_tolerance_level"]
    overall_uncertainty_index = (
        requirements_volatility +
        technical_complexity_index +
        regulatory_risk_index
    ) / 3

    return {
        "project_scale_index": project_scale_index,
        "budget_adequacy_ratio": budget_adequacy_ratio,
        "schedule_pressure_index": schedule_pressure_index,
        "team_capacity_index": team_capacity_index,
        "team_experience_score": team_experience_score,
        "domain_familiarity_score": domain_familiarity_score,

        "requirements_volatility": requirements_volatility,
        "requirements_clarity_score": requirements_clarity_score,
        "scope_complexity_index": scope_complexity_index,
        "stakeholder_alignment_score": stakeholder_alignment_score,
        "change_request_intensity": change_request_intensity,

        "process_maturity_score": process_maturity_score,
        "sprint_discipline_score": sprint_discipline_score,
        "decision_latency_index": decision_latency_index,
        "risk_management_maturity": risk_management_maturity,
        "client_engagement_score": client_engagement_score,

        "technical_complexity_index": technical_complexity_index,
        "integration_risk_index": integration_risk_index,
        "automation_maturity_score": automation_maturity_score,
        "toolchain_reliability_score": toolchain_reliability_score,
        "legacy_dependency_index": legacy_dependency_index,

        "regulatory_risk_index": regulatory_risk_index,
        "domain_criticality_index": domain_criticality_index,
        "external_dependency_risk": external_dependency_risk,

        "time_to_market_pressure": time_to_market_pressure,
        "resource_stability_index": resource_stability_index,
        "risk_tolerance_index": risk_tolerance_index,
        "overall_uncertainty_index": overall_uncertainty_index,
    }
