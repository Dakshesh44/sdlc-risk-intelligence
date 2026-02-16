import numpy as np

FEATURE_LIST = [
    'schedule_pressure_index',
    'budget_adequacy_ratio',
    'project_scale_index',
    'team_capacity_index',
    'team_experience_score',
    'requirements_volatility',
    'requirements_clarity_score',
    'change_request_intensity',
    'scope_complexity_index',
    'process_maturity_score',
    'client_engagement_score',
    'decision_latency_index',
    'risk_management_maturity',
    'sprint_discipline_score',
    'technical_complexity_index',
    'integration_risk_index',
    'automation_maturity_score',
    'legacy_dependency_index',
    'toolchain_reliability_score',
    'regulatory_risk_index',
    'domain_criticality_index',
    'external_dependency_risk',
    'time_to_market_pressure',
    'resource_stability_index',
    'risk_tolerance_index',
    'overall_uncertainty_index',
    'stakeholder_alignment_score',
    'domain_familiarity_score'
]


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def generate_risk(project_features: dict, sdlc_type: str) -> float:
    """
    Stochastic risk generator with ANTI-OVERFITTING NOISE
    Input: 28 normalized features (0–1)
    Output: risk_score ∈ [0,1]
    
    FIX: Added driver-level noise + increased final noise to prevent 98% overfitting
    """
    centered = {k: v - 0.5 for k, v in project_features.items()}

    # ANTI-OVERFITTING FIX #1: Add per-driver noise (8% std dev)
    driver_noise = np.random.normal(0, 0.08, 6)
    
    # 1️⃣ LATENT DRIVERS (with chaos added)
    structural_stress = (
        0.3 * centered['schedule_pressure_index']**2 +
        0.25 * (-centered['budget_adequacy_ratio']) +
        0.2 * centered['project_scale_index'] +
        0.15 * (-centered['team_capacity_index']) +
        0.1 * (-centered['team_experience_score'])
    ) + driver_noise[0]

    volatility_stress = (
        0.3 * centered['requirements_volatility'] +
        0.25 * (-centered['requirements_clarity_score']) +
        0.25 * centered['change_request_intensity'] +
        0.2 * centered['scope_complexity_index']
    ) + driver_noise[1]

    governance_weakness = (
        0.25 * (-centered['process_maturity_score']) +
        0.2 * (-centered['client_engagement_score']) +
        0.2 * centered['decision_latency_index']**2 +
        0.15 * (-centered['risk_management_maturity']) +
        0.1 * (-centered['sprint_discipline_score'])
    ) + driver_noise[2]

    technical_overload = (
        0.25 * centered['technical_complexity_index'] +
        0.2 * centered['integration_risk_index'] +
        0.2 * (-centered['automation_maturity_score']) +
        0.15 * centered['legacy_dependency_index'] +
        0.1 * (-centered['toolchain_reliability_score'])
    ) + driver_noise[3]

    environmental_pressure = (
        0.4 * centered['regulatory_risk_index'] +
        0.3 * centered['domain_criticality_index'] +
        0.3 * centered['external_dependency_risk']
    ) + driver_noise[4]

    delivery_pressure = (
        0.4 * centered['time_to_market_pressure'] +
        0.3 * (-centered['resource_stability_index']) +
        0.2 * centered['risk_tolerance_index'] +
        0.1 * centered['overall_uncertainty_index']
    ) + driver_noise[5]

    # 2️⃣ BASE RISK
    base_risk = (
        0.25 * structural_stress +
        0.20 * volatility_stress +
        0.20 * technical_overload +
        0.15 * governance_weakness +
        0.10 * environmental_pressure +
        0.10 * delivery_pressure
    )

    # 3️⃣ SDLC-SPECIFIC ADJUSTMENT
    if sdlc_type == 'Waterfall':
        sdlc_adjust = volatility_stress * (1 + 1.2 * governance_weakness)

    elif sdlc_type == 'Agile':
        sdlc_adjust = structural_stress * (
            1 - 0.7 * project_features['stakeholder_alignment_score']
        )

    elif sdlc_type == 'Hybrid':
        waterfall_component = volatility_stress * (1 + 0.8 * governance_weakness)
        agile_component = structural_stress * (
            1 - 0.7 * project_features['stakeholder_alignment_score']
        )
        sdlc_adjust = 0.5 * waterfall_component + 0.5 * agile_component

    elif sdlc_type == 'DevOps':
        sdlc_adjust = technical_overload * (
            1 - project_features['automation_maturity_score']**2
        )

    elif sdlc_type == 'V-Model':
        sdlc_adjust = environmental_pressure * project_features['technical_complexity_index']

    elif sdlc_type == 'Spiral':
        sdlc_adjust = 1.5 * governance_weakness * (
            1 - project_features['risk_management_maturity']
        )

    else:
        raise ValueError("Invalid SDLC type")

    # 4️⃣ CROSS-FEATURE INTERACTIONS
    team_domain_mismatch = (
        project_features['project_scale_index'] *
        (1 - project_features['domain_familiarity_score'])
    )

    scope_integration = (
        project_features['scope_complexity_index'] *
        project_features['integration_risk_index']
    )

    pressure_decision = (
        project_features['time_to_market_pressure'] *
        project_features['decision_latency_index']**2
    )

    interactions = (
        0.3 * team_domain_mismatch +
        0.3 * scope_integration +
        0.2 * pressure_decision
    )

    # 5️⃣ FINAL RISK
    # ANTI-OVERFITTING FIX #2: Increase final noise from 0.05 → 0.10
    noise = np.random.normal(loc=0.0, scale=0.10)

    risk_raw = base_risk + (1.2 * sdlc_adjust) + (0.5 * interactions) + noise

    risk_score = sigmoid(3.5 * risk_raw)

    return float(np.clip(risk_score, 0, 1))