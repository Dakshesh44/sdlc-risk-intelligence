MODEL_PROFILES = {

    "Waterfall": {
        "requirements_volatility": 0.35,
        "regulatory_risk_index": 0.25,
        "schedule_pressure_index": 0.15,
        "technical_complexity_index": 0.15,
        "integration_risk_index": 0.10
    },

    "Agile": {
        "requirements_volatility": 0.15,
        "client_engagement_score": 0.25,
        "schedule_pressure_index": 0.20,
        "technical_complexity_index": 0.20,
        "integration_risk_index": 0.20
    },

    "Spiral": {
        "overall_uncertainty_index": 0.30,
        "technical_complexity_index": 0.25,
        "integration_risk_index": 0.20,
        "risk_management_maturity": 0.15,
        "schedule_pressure_index": 0.10
    },

    "V-Model": {
        "regulatory_risk_index": 0.30,
        "domain_criticality_index": 0.25,
        "technical_complexity_index": 0.20,
        "integration_risk_index": 0.15,
        "requirements_clarity_score": 0.10
    },

    "DevOps": {
        "automation_maturity_score": 0.30,
        "integration_risk_index": 0.25,
        "schedule_pressure_index": 0.20,
        "technical_complexity_index": 0.15,
        "client_engagement_score": 0.10
    },

    "Hybrid": {
        "requirements_volatility": 0.20,
        "technical_complexity_index": 0.20,
        "schedule_pressure_index": 0.20,
        "integration_risk_index": 0.20,
        "client_engagement_score": 0.20
    }
}
