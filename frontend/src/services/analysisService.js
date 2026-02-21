const API_BASE_URL = import.meta.env.VITE_API_URL || null;
const API_ANALYZE_PATH = import.meta.env.VITE_API_ANALYZE_PATH || "/analyze";
const API_PAYLOAD_STYLE = (import.meta.env.VITE_API_PAYLOAD_STYLE || "snake").toLowerCase();

const toNumber = (value, fallback = 0) => {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
};

const clampPercentage = (value) => Math.max(0, Math.min(100, Math.round(toNumber(value))));

const toSnakePayload = (data) => ({
  project_name: data.projectName,
  project_description: data.projectDescription,
  project_budget: toNumber(data.projectBudget),
  project_duration_months: toNumber(data.projectDurationMonths),
  team_size: toNumber(data.teamSize),
  number_of_integrations: toNumber(data.numberOfIntegrations),
  team_experience_level: toNumber(data.teamExperienceLevel),
  agile_maturity_level: toNumber(data.agileMaturityLevel),
  requirement_clarity: toNumber(data.requirementClarity),
  client_involvement_level: toNumber(data.clientInvolvementLevel),
  regulatory_strictness: toNumber(data.regulatoryStrictness),
  system_complexity: toNumber(data.systemComplexity),
  automation_level: toNumber(data.automationLevel),
  delivery_urgency: toNumber(data.deliveryUrgency),
  requirement_change_frequency: toNumber(data.requirementChangeFrequency),
  decision_making_speed: toNumber(data.decisionMakingSpeed),
  domain_criticality: toNumber(data.domainCriticality),
  risk_tolerance_level: toNumber(data.riskToleranceLevel)
});

const createRequestPayload = (data) => {
  if (API_PAYLOAD_STYLE === "camel") {
    return data;
  }

  if (API_PAYLOAD_STYLE === "both") {
    return {
      ...data,
      ...toSnakePayload(data),
    };
  }

  return toSnakePayload(data);
};

const extractExplainability = (raw) => {
  const source = raw.explainability || raw.explanations || raw.reasons || raw.insights || [];

  if (Array.isArray(source)) {
    return source.map((item, index) => {
      if (typeof item === "string") {
        return { title: `Insight ${index + 1}`, text: item };
      }
      return {
        title: item.title || item.label || `Insight ${index + 1}`,
        text: item.text || item.reason || item.description || "",
      };
    });
  }

  if (source && typeof source === "object") {
    return Object.entries(source).map(([title, text]) => ({
      title,
      text: String(text ?? ""),
    }));
  }

  return [];
};

const extractModelScores = (raw, selectedModel, confidence) => {
  const alternatives =
    raw.model_scores ||
    raw.modelScores ||
    raw.alternatives ||
    raw.candidates ||
    [];

  if (Array.isArray(alternatives) && alternatives.length) {
    return alternatives.map((item) => ({
      name: item.name || item.model || item.label || "Unknown Model",
      suitability: clampPercentage(
        item.suitability ??
        item.score ??
        (toNumber(item.probability) <= 1 ? toNumber(item.probability) * 100 : item.probability) ??
        0
      ),
    }));
  }

  if (alternatives && typeof alternatives === "object") {
    return Object.entries(alternatives).map(([name, value]) => ({
      name,
      suitability: clampPercentage(toNumber(value) <= 1 ? toNumber(value) * 100 : value),
    }));
  }

  return [{ name: selectedModel, suitability: confidence }];
};

const normalizeResponse = (raw) => {
  const model =
    raw.model ||
    raw.recommended_model ||
    raw.recommendedModel ||
    raw.predicted_model ||
    raw.predictedModel ||
    raw.sdlc_model ||
    raw.sdlcModel;

  const baseConfidence =
    raw.confidence ??
    raw.confidence_score ??
    raw.confidenceScore ??
    raw.score ??
    raw.probability ??
    raw.prediction_probability;

  const confidence = clampPercentage(toNumber(baseConfidence) <= 1 ? toNumber(baseConfidence) * 100 : baseConfidence);

  if (!model) {
    throw new Error("Backend response missing model field (expected model/recommended_model/predicted_model).");
  }

  return {
    model,
    confidence: confidence || 0,
    explainability: extractExplainability(raw),
    modelScores: extractModelScores(raw, model, confidence || 0),
    generatedAt: raw.generated_at || raw.generatedAt || new Date().toISOString(),
  };
};

const parseErrorMessage = async (response) => {
  try {
    const data = await response.json();
    return data?.message || data?.error || data?.detail || `Request failed with status ${response.status}`;
  } catch (_error) {
    return `Request failed with status ${response.status}`;
  }
};

export const AnalysisService = {
  async analyzeProject(data) {
    if (!API_BASE_URL) {
      throw new Error("Analysis failed: Backend is not configured. (VITE_API_URL missing)");
    }

    const token = localStorage.getItem("fp_token");
    const headers = { "Content-Type": "application/json" };
    if (token) headers.Authorization = `Bearer ${token}`;

    try {
      const response = await fetch(`${API_BASE_URL}${API_ANALYZE_PATH}`, {
        method: "POST",
        headers,
        body: JSON.stringify(createRequestPayload(data)),
      });

      if (!response.ok) {
        throw new Error(await parseErrorMessage(response));
      }

      const raw = await response.json();
      return normalizeResponse(raw);
    } catch (error) {
      if (error.message.includes('Failed to fetch')) {
        throw new Error(`Connection Error: Unable to reach the backend at ${API_BASE_URL}. Ensure the service is running.`);
      }
      throw error;
    }
  },
};
