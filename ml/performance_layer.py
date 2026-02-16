"""
Performance Layer - Converts risk scores to performance metrics
Formula: performance = 0.4*success - 0.3*cost - 0.2*timeline - 0.1*risk_escal
"""

import numpy as np
from typing import Dict


def performance_from_risk(risk_score: float) -> Dict[str, float]:
    """
    Convert risk score (0-1) to performance metrics.
    
    Args:
        risk_score: Risk between 0-1
        
    Returns:
        Dict with success_prob, cost_overrun, timeline_dev, risk_escal, performance
        
    Examples:
        Low risk (0.2):  performance = +0.22
        High risk (0.8): performance = -0.12
    """
    if not (0 <= risk_score <= 1):
        raise ValueError(f"Risk {risk_score} must be in [0,1]")
    
    # 1. SUCCESS PROBABILITY (inverse)
    # Low risk → High success
    success_prob = 1.0 - (0.75 * risk_score)
    success_prob = max(0.1, min(0.95, success_prob))
    
    # 2. COST OVERRUN (quadratic - risk²)
    # Low risk (0.2) → 8% overrun
    # High risk (0.8) → 128% overrun
    cost_overrun = 2.0 * (risk_score ** 2)
    cost_overrun = max(0.0, min(2.0, cost_overrun))
    
    # 3. TIMELINE DEVIATION (linear)
    # Low risk (0.2) → 15% delay
    # High risk (0.8) → 120% delay
    timeline_dev = 1.5 * risk_score
    timeline_dev = max(0.0, min(1.5, timeline_dev))
    
    # 4. RISK ESCALATION (exponential)
    risk_escal = 1.0 - np.exp(-2.0 * risk_score)
    risk_escal = max(0.0, min(1.0, risk_escal))
    
    # 5. COMPOSITE PERFORMANCE
    # Formula: 0.4*success - 0.3*cost - 0.2*timeline - 0.1*risk_escal
    performance = (
        0.4 * success_prob -
        0.3 * cost_overrun -
        0.2 * timeline_dev -
        0.1 * risk_escal
    )
    
    return {
        'success_probability': round(success_prob, 4),
        'cost_overrun_ratio': round(cost_overrun, 4),
        'timeline_deviation_ratio': round(timeline_dev, 4),
        'risk_escalation_index': round(risk_escal, 4),
        'performance_score': round(performance, 4)
    }


def categorize_risk(risk_score: float) -> str:
    """Categorize risk: Low/Medium/High"""
    if risk_score < 0.35:
        return 'Low'
    elif risk_score < 0.65:
        return 'Medium'
    else:
        return 'High'