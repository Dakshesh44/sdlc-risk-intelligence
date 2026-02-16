import random
import pandas as pd
from collections import defaultdict

# -----------------------------
# CONFIG
# -----------------------------

LEVELS = [0.1, 0.3, 0.5, 0.7, 0.9]
TARGET_PER_CLASS = 300

SDLC_CLASSES = [
    "Waterfall",
    "Agile",
    "Spiral",
    "V-Model",
    "DevOps",
    "Hybrid"
]

FEATURE_LIST = [
    "project_scale_index",
    "budget_adequacy_ratio",
    "schedule_pressure_index",
    "team_capacity_index",
    "team_experience_score",
    "domain_familiarity_score",

    "requirements_volatility",
    "requirements_clarity_score",
    "scope_complexity_index",
    "stakeholder_alignment_score",
    "change_request_intensity",

    "process_maturity_score",
    "sprint_discipline_score",
    "decision_latency_index",
    "risk_management_maturity",
    "client_engagement_score",

    "technical_complexity_index",
    "integration_risk_index",
    "automation_maturity_score",
    "toolchain_reliability_score",
    "legacy_dependency_index",

    "regulatory_risk_index",
    "domain_criticality_index",
    "external_dependency_risk",

    "time_to_market_pressure",
    "resource_stability_index",
    "risk_tolerance_index",
    "overall_uncertainty_index"
]

# -----------------------------
# SAMPLE GENERATOR
# -----------------------------

def generate_sample():
    return {feature: random.choice(LEVELS) for feature in FEATURE_LIST}


# -----------------------------
# SDLC SCORING LOGIC
# -----------------------------

def compute_sdlc_scores(s):

    waterfall_score = (
        0.25 * (1 - s["requirements_volatility"]) +
        0.20 * s["requirements_clarity_score"] +
        0.15 * (1 - s["change_request_intensity"]) +
        0.15 * (1 - s["overall_uncertainty_index"]) +
        0.15 * s["process_maturity_score"] +
        0.10 * (1 - s["integration_risk_index"])
    )

    agile_score = (
        0.30 * s["requirements_volatility"] +
        0.20 * s["client_engagement_score"] +
        0.15 * (1 - s["decision_latency_index"]) +
        0.15 * (1 - s["regulatory_risk_index"]) +
        0.10 * s["overall_uncertainty_index"] +
        0.10 * s["risk_tolerance_index"]
    )

    spiral_score = (
        0.30 * s["overall_uncertainty_index"] +
        0.20 * s["technical_complexity_index"] +
        0.15 * s["risk_management_maturity"] +
        0.15 * s["integration_risk_index"] +
        0.10 * s["scope_complexity_index"] +
        0.10 * s["regulatory_risk_index"]
    )

    vmodel_score = (
        0.30 * s["regulatory_risk_index"] +
        0.20 * s["domain_criticality_index"] +
        0.20 * s["process_maturity_score"] +
        0.15 * (1 - s["requirements_volatility"]) +
        0.15 * (1 - s["change_request_intensity"])
    )

    devops_score = (
        0.30 * s["automation_maturity_score"] +
        0.20 * s["integration_risk_index"] +
        0.20 * s["time_to_market_pressure"] +
        0.15 * (1 - s["resource_stability_index"]) +
        0.15 * s["sprint_discipline_score"]
    )

    hybrid_score = (
        1 - (
            abs(s["requirements_volatility"] - 0.5) +
            abs(s["technical_complexity_index"] - 0.5) +
            abs(s["process_maturity_score"] - 0.5) +
            abs(s["regulatory_risk_index"] - 0.5)
        ) / 4
    )

    return {
        "Waterfall": waterfall_score,
        "Agile": agile_score,
        "Spiral": spiral_score,
        "V-Model": vmodel_score,
        "DevOps": devops_score,
        "Hybrid": hybrid_score
    }


# -----------------------------
# LABEL ASSIGNMENT
# -----------------------------

def assign_label(scores):
    return max(scores, key=scores.get)


# -----------------------------
# BALANCED DATASET BUILDER
# -----------------------------

def build_balanced_dataset():

    counts = defaultdict(int)
    dataset = []

    while min(counts.get(cls, 0) for cls in SDLC_CLASSES) < TARGET_PER_CLASS:

        sample = generate_sample()
        scores = compute_sdlc_scores(sample)
        label = assign_label(scores)

        if counts[label] < TARGET_PER_CLASS:
            sample["label"] = label
            dataset.append(sample)
            counts[label] += 1

        if sum(counts.values()) % 100 == 0:
            print("Progress:", dict(counts))

    df = pd.DataFrame(dataset)
    df.to_csv("ml/dataset.csv", index=False)

    print("\nFinal Distribution:")
    print(df["label"].value_counts())
    print("\nDataset saved as ml/dataset.csv")


# -----------------------------
# MAIN
# -----------------------------

if __name__ == "__main__":
    build_balanced_dataset()
