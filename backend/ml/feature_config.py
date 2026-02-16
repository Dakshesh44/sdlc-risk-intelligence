"""
FEATURE ORDER CONFIGURATION — LOCKED (v1)

This defines the exact order of the 28 engineered features.
Any change requires model retraining and version increment.
"""

FEATURE_ORDER = [
    # STRUCTURE & SCALE
    "project_scale_index",
    "budget_adequacy_ratio",
    "schedule_pressure_index",
    "team_capacity_index",
    "team_experience_score",
    "domain_familiarity_score",

    # REQUIREMENTS & SCOPE
    "requirements_volatility",
    "requirements_clarity_score",
    "scope_complexity_index",
    "stakeholder_alignment_score",
    "change_request_intensity",

    # PROCESS & GOVERNANCE
    "process_maturity_score",
    "sprint_discipline_score",
    "decision_latency_index",
    "risk_management_maturity",
    "client_engagement_score",

    # TECHNICAL RISK
    "technical_complexity_index",
    "integration_risk_index",
    "automation_maturity_score",
    "toolchain_reliability_score",
    "legacy_dependency_index",

    # ENVIRONMENT & EXTERNAL
    "regulatory_risk_index",
    "domain_criticality_index",
    "external_dependency_risk",

    # DELIVERY PRESSURE
    "time_to_market_pressure",
    "resource_stability_index",
    "risk_tolerance_index",
    "overall_uncertainty_index"
]
