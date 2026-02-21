import React, { useState } from 'react';
import { Card, Input, Textarea, FactorSlider, SegmentedControl, Button, Alert } from '../components/UI';
import Loader from '../components/Loader';
import { Zap, ShieldAlert } from 'lucide-react';
import { useAnalysis } from '../context/AnalysisContext';
import { AnalysisService } from '../services/analysisService';

const NewAnalysis = ({ onAnalyze }) => {
    const { addAnalysis } = useAnalysis();
    const [loading, setLoading] = useState(false);
    const [globalError, setGlobalError] = useState(null);
    const [fieldErrors, setFieldErrors] = useState({});

    const initialFormData = {
        projectName: '',
        projectDescription: '',
        projectBudget: '',
        projectDurationMonths: '',
        teamSize: '',
        numberOfIntegrations: '',
        teamExperienceLevel: 3,
        agileMaturityLevel: 3,
        requirementClarity: 3,
        clientInvolvementLevel: 3,
        regulatoryStrictness: 3,
        systemComplexity: 3,
        automationLevel: 3,
        deliveryUrgency: 3,
        requirementChangeFrequency: 3,
        decisionMakingSpeed: 3,
        domainCriticality: 3,
        riskToleranceLevel: 3
    };

    const [formData, setFormData] = useState(initialFormData);

    const strategicOptions = [
        { label: 'Low', value: 1 },
        { label: 'Medium', value: 3 },
        { label: 'High', value: 5 }
    ];

    const handleChange = (field, value) => {
        setFormData(prev => ({ ...prev, [field]: value }));
        // Clear specific field error when typing
        if (fieldErrors[field]) {
            setFieldErrors(prev => ({ ...prev, [field]: null }));
        }
    };

    const validateForm = () => {
        const errors = {};

        if (!formData.projectName || formData.projectName.trim().length < 3) errors.projectName = "At least 3 characters required.";
        if (!formData.projectDescription || formData.projectDescription.trim().length < 10) errors.projectDescription = "At least 10 characters required.";

        const budget = Number(formData.projectBudget);
        if (!formData.projectBudget || isNaN(budget) || budget <= 0) errors.projectBudget = "Must be a number > 0";

        const duration = Number(formData.projectDurationMonths);
        if (!formData.projectDurationMonths || isNaN(duration) || duration < 1 || duration > 60) errors.projectDurationMonths = "Must be between 1 and 60";

        const teamSize = Number(formData.teamSize);
        if (!formData.teamSize || isNaN(teamSize) || teamSize < 1 || teamSize > 50) errors.teamSize = "Must be between 1 and 50";

        const integrations = Number(formData.numberOfIntegrations);
        if (formData.numberOfIntegrations === '' || isNaN(integrations) || integrations < 0) errors.numberOfIntegrations = "Must be >= 0";

        setFieldErrors(errors);
        return Object.keys(errors).length === 0;
    };

    const handleAnalyze = async () => {
        setGlobalError(null);

        if (!validateForm()) {
            setGlobalError("Please correct the highlighted fields before submitting.");
            return;
        }

        try {
            setLoading(true);

            // Map state to the API requirements
            const payload = {
                projectName: formData.projectName.trim(),
                projectDescription: formData.projectDescription.trim(),
                projectBudget: Number(formData.projectBudget),
                projectDurationMonths: Number(formData.projectDurationMonths),
                teamSize: Number(formData.teamSize),
                numberOfIntegrations: Number(formData.numberOfIntegrations),
                teamExperienceLevel: Number(formData.teamExperienceLevel),
                agileMaturityLevel: Number(formData.agileMaturityLevel),
                requirementClarity: Number(formData.requirementClarity),
                clientInvolvementLevel: Number(formData.clientInvolvementLevel),
                regulatoryStrictness: Number(formData.regulatoryStrictness),
                systemComplexity: Number(formData.systemComplexity),
                automationLevel: Number(formData.automationLevel),
                deliveryUrgency: Number(formData.deliveryUrgency),
                requirementChangeFrequency: Number(formData.requirementChangeFrequency),
                decisionMakingSpeed: Number(formData.decisionMakingSpeed),
                domainCriticality: Number(formData.domainCriticality),
                riskToleranceLevel: Number(formData.riskToleranceLevel)
            };

            const result = await AnalysisService.analyzeProject(payload);
            addAnalysis(payload, result);
            onAnalyze();
        } catch (err) {
            setGlobalError(err.message || 'An error occurred during analysis.');
        } finally {
            setLoading(false);
        }
    };

    const handleCancel = () => {
        setGlobalError(null);
        setFieldErrors({});
        setFormData(initialFormData);
    };

    if (loading) return <Loader />;

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex justify-between items-end">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">New SDLC Analysis</h2>
                    <p className="text-muted-foreground mt-1">Fill out the project parameters to generate a recommendation.</p>
                </div>
                <Button onClick={handleAnalyze} disabled={loading} className="px-8 h-12 flex items-center gap-2">
                    <Zap size={18} fill="currentColor" />
                    <span>Analyze Project</span>
                </Button>
            </div>

            {globalError && (
                <Alert variant="error" className="mb-2">
                    <ShieldAlert size={18} />
                    <span>{globalError}</span>
                </Alert>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                <Card title="Project Basics" subtitle="Identification and scope" className="lg:col-span-3 border-l-4 border-l-primary/50">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                        <Input
                            label="Project Name"
                            placeholder="e.g. Phoenix Portal"
                            value={formData.projectName}
                            onChange={(e) => handleChange('projectName', e.target.value)}
                            error={fieldErrors.projectName}
                            className="lg:col-span-2"
                        />
                        <Textarea
                            label="Project Description"
                            placeholder="Describe the main goals..."
                            value={formData.projectDescription}
                            onChange={(e) => handleChange('projectDescription', e.target.value)}
                            error={fieldErrors.projectDescription}
                            className="md:col-span-2 lg:col-span-4"
                        />
                        <Input
                            type="number"
                            min="1000"
                            step="1000"
                            label="Project Budget"
                            placeholder="500000"
                            value={formData.projectBudget}
                            onChange={(e) => handleChange('projectBudget', e.target.value)}
                            error={fieldErrors.projectBudget}
                        />
                        <Input
                            type="number"
                            min="1"
                            max="60"
                            step="1"
                            label="Duration (Months)"
                            placeholder="12"
                            value={formData.projectDurationMonths}
                            onChange={(e) => handleChange('projectDurationMonths', e.target.value)}
                            error={fieldErrors.projectDurationMonths}
                        />
                        <Input
                            type="number"
                            min="1"
                            max="50"
                            step="1"
                            label="Team Size"
                            placeholder="10"
                            value={formData.teamSize}
                            onChange={(e) => handleChange('teamSize', e.target.value)}
                            error={fieldErrors.teamSize}
                        />
                        <Input
                            type="number"
                            min="0"
                            step="1"
                            label="Integrations"
                            placeholder="3"
                            value={formData.numberOfIntegrations}
                            onChange={(e) => handleChange('numberOfIntegrations', e.target.value)}
                            error={fieldErrors.numberOfIntegrations}
                        />
                    </div>
                </Card>

                <Card title="Process Factors" subtitle="Evaluate environmental vectors (1 - 5)" className="lg:col-span-2">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-8 inline-factor-borders">
                        <FactorSlider label="Team Experience Level" value={formData.teamExperienceLevel} onChange={(e) => handleChange('teamExperienceLevel', Number(e.target.value))} />
                        <FactorSlider label="Agile Maturity Level" value={formData.agileMaturityLevel} onChange={(e) => handleChange('agileMaturityLevel', Number(e.target.value))} />
                        <FactorSlider label="Requirement Clarity" value={formData.requirementClarity} onChange={(e) => handleChange('requirementClarity', Number(e.target.value))} />
                        <FactorSlider label="Client Involvement Level" value={formData.clientInvolvementLevel} onChange={(e) => handleChange('clientInvolvementLevel', Number(e.target.value))} />
                        <FactorSlider label="Regulatory Strictness" value={formData.regulatoryStrictness} onChange={(e) => handleChange('regulatoryStrictness', Number(e.target.value))} />
                        <FactorSlider label="System Complexity" value={formData.systemComplexity} onChange={(e) => handleChange('systemComplexity', Number(e.target.value))} />
                        <FactorSlider label="Automation Level" value={formData.automationLevel} onChange={(e) => handleChange('automationLevel', Number(e.target.value))} />
                        <FactorSlider label="Delivery Urgency" value={formData.deliveryUrgency} onChange={(e) => handleChange('deliveryUrgency', Number(e.target.value))} />
                    </div>
                </Card>

                <Card title="Strategic Factors" subtitle="Corporate operational vectors" className="lg:col-span-1 border-r-4 border-r-indigo-500/50">
                    <div className="grid grid-cols-1 gap-6">
                        <SegmentedControl
                            label="Requirement Change Frequency"
                            options={strategicOptions}
                            value={formData.requirementChangeFrequency}
                            onChange={(val) => handleChange('requirementChangeFrequency', val)}
                        />
                        <SegmentedControl
                            label="Decision Making Speed"
                            options={strategicOptions}
                            value={formData.decisionMakingSpeed}
                            onChange={(val) => handleChange('decisionMakingSpeed', val)}
                        />
                        <SegmentedControl
                            label="Domain Criticality"
                            options={strategicOptions}
                            value={formData.domainCriticality}
                            onChange={(val) => handleChange('domainCriticality', val)}
                        />
                        <SegmentedControl
                            label="Risk Tolerance Level"
                            options={strategicOptions}
                            value={formData.riskToleranceLevel}
                            onChange={(val) => handleChange('riskToleranceLevel', val)}
                        />
                    </div>
                </Card>
            </div>

            <div className="flex justify-end gap-4 pb-12">
                <Button variant="outline" className="px-8" onClick={handleCancel}>Cancel</Button>
                <Button onClick={handleAnalyze} className="px-12 h-12 flex items-center gap-2" disabled={loading}>
                    <Zap size={18} fill="currentColor" />
                    <span>Analyze Project</span>
                </Button>
            </div>
        </div>
    );
};

export default NewAnalysis;
