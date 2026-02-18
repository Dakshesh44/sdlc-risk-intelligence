"""
Feature configuration for SDLC ML model.
This order MUST match the training feature order exactly.
All features are normalized between 0 and 1.
"""

FEATURE_ORDER = [

    # Project Scale & Structure
    "project_scale_index",
    "team_capacity_index",
    "budget_adequacy_ratio",

    # Requirements & Volatility
    "requirements_volatility",
    "requirements_clarity_score",
    "change_frequency_index",

    # Risk & Uncertainty
    "overall_uncertainty_index",
    "risk_management_maturity",

    # Technical Complexity
    "technical_complexity_index",
    "integration_complexity_score",
    "legacy_dependency_index",

    # Delivery Pressure
    "schedule_pressure_index",
    "time_to_market_pressure",
    "deadline_strictness_index",

    # Automation & DevOps
    "automation_maturity_score",
    "ci_cd_presence_score",
    "testing_rigor_index",

    # Governance & Compliance
    "documentation_maturity_score",
    "regulatory_constraint_score",
    "governance_rigidity_index",

    # Stakeholder & Collaboration
    "stakeholder_engagement_score",
    "client_involvement_index",
    "cross_team_dependency_score",

    # Engineering Maturity
    "codebase_stability_index",
    "release_frequency_index",
    "defect_density_proxy",
    "developer_experience_index",

    # Operational Readiness
    "deployment_frequency_index",
]
