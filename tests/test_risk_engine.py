from ml.risk_engine import generate_risk, FEATURE_LIST

def base_project():
    return {f: 0.5 for f in FEATURE_LIST}


def test_output_range():
    risk = generate_risk(base_project(), "Waterfall")
    assert 0 <= risk <= 1


def test_volatility_increases_waterfall_risk():
    base = base_project()

    high = base.copy()
    high['requirements_volatility'] = 0.9

    low = base.copy()
    low['requirements_volatility'] = 0.1

    assert generate_risk(high, "Waterfall") > generate_risk(low, "Waterfall")


def test_automation_reduces_devops_risk():
    base = base_project()

    high_auto = base.copy()
    high_auto['automation_maturity_score'] = 0.9

    low_auto = base.copy()
    low_auto['automation_maturity_score'] = 0.1

    assert generate_risk(low_auto, "DevOps") > generate_risk(high_auto, "DevOps")


def test_governance_affects_spiral():
    base = base_project()

    weak = base.copy()
    weak['process_maturity_score'] = 0.1

    strong = base.copy()
    strong['process_maturity_score'] = 0.9

    assert generate_risk(weak, "Spiral") > generate_risk(strong, "Spiral")


def test_extreme_pressure_high_risk():
    extreme = {f: 1.0 for f in FEATURE_LIST}
    risk = generate_risk(extreme, "Waterfall")
    assert risk > 0.8
    
def test_hybrid_does_not_crash():
    base = base_project()
    risk = generate_risk(base, "Hybrid")
    assert 0 <= risk <= 1
