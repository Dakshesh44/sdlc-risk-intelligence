import { useMemo, useState } from 'react';
import { Card, Button, Alert } from '../components/UI';
import { ChartContainer, CustomTooltip } from '../components/Chart';
import { Table, TableRow, TableCell } from '../components/Table';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
    Cell, PieChart, Pie
} from 'recharts';
import {
    CheckCircle2, AlertTriangle, ShieldCheck,
    Download, Share2, TrendingUp, Info
} from 'lucide-react';
import { useAnalysis } from '../context/AnalysisContext';
import { AnalysisService } from '../services/analysisService';

const toPercent = (value) => Math.max(0, Math.min(100, Math.round(Number(value) || 0)));

const modelFitLabel = (suitability) => {
    if (suitability >= 75) return 'highly compatible';
    if (suitability >= 55) return 'moderately compatible';
    return 'low compatibility';
};

const modelTimeLabel = (suitability) => {
    if (suitability >= 70) return 'accelerated delivery';
    if (suitability >= 55) return 'steady delivery';
    return 'slower delivery';
};

const modelLoadLabel = (suitability) => {
    if (suitability >= 70) return 'medium resource load';
    if (suitability >= 55) return 'high resource load';
    return 'very high resource load';
};

const Results = () => {
    const { currentResult } = useAnalysis();
    const [selectedAlternative, setSelectedAlternative] = useState(null);
    const [feedbackForm, setFeedbackForm] = useState({ actualOutcome: '', notes: '' });
    const [feedbackMsg, setFeedbackMsg] = useState(null);
    const [feedbackErr, setFeedbackErr] = useState(null);
    const [submittingFeedback, setSubmittingFeedback] = useState(false);

    if (!currentResult) {
        return (
            <div className="flex flex-col items-center justify-center p-20 text-center animate-in fade-in duration-500">
                <div className="w-20 h-20 bg-accent rounded-full flex items-center justify-center text-muted-foreground mb-6">
                    <Info size={40} />
                </div>
                <h2 className="text-2xl font-bold">No Active Analysis</h2>
                <p className="text-muted-foreground mt-2 max-w-sm">
                    Please complete a "New Analysis" form to view AI-generated SDLC recommendations here.
                </p>
            </div>
        );
    }

    const modelScores = useMemo(() => {
        if (currentResult.modelScores?.length) return currentResult.modelScores;
        return [{ name: currentResult.model, suitability: currentResult.confidence }];
    }, [currentResult]);

    const riskData = modelScores.map((item) => ({
        name: item.name,
        risk: Math.max(0, 100 - (item.suitability || 0)),
        color: item.name === currentResult.model ? '#4F46E5' : '#f59e0b',
    }));

    const suitabilityData = [
        { name: currentResult.model, value: currentResult.confidence },
        { name: 'Others', value: Math.max(0, 100 - currentResult.confidence) },
    ];

    const COLORS = ['#4F46E5', '#1e1b4b'];

    const handleExport = async () => {
        try {
            const { jsPDF } = await import('jspdf');
            const doc = new jsPDF({ unit: 'pt', format: 'a4' });
            const pageWidth = doc.internal.pageSize.getWidth();
            const pageHeight = doc.internal.pageSize.getHeight();
            const margin = 44;
            const contentWidth = pageWidth - (margin * 2);
            let y = 52;

            const ensureSpace = (required = 20) => {
                if (y + required > pageHeight - margin) {
                    doc.addPage();
                    y = margin;
                }
            };

            const addHeading = (text) => {
                ensureSpace(28);
                doc.setFont('helvetica', 'bold');
                doc.setFontSize(14);
                doc.text(text, margin, y);
                y += 22;
            };

            const addParagraph = (text, size = 11) => {
                if (!text) return;
                doc.setFont('helvetica', 'normal');
                doc.setFontSize(size);
                const lines = doc.splitTextToSize(String(text), contentWidth);
                ensureSpace((lines.length * 14) + 8);
                doc.text(lines, margin, y);
                y += (lines.length * 14) + 8;
            };

            const addRow = (label, value) => {
                const text = `${label}: ${value ?? 'N/A'}`;
                addParagraph(text, 10);
            };

            const confidence = toPercent(currentResult.confidence);
            const ranking = [...modelScores].sort((a, b) => (b.suitability || 0) - (a.suitability || 0));
            const generatedAt = currentResult.generatedAt
                ? new Date(currentResult.generatedAt).toLocaleString()
                : new Date().toLocaleString();

            doc.setFont('helvetica', 'bold');
            doc.setFontSize(20);
            doc.text('HelixRisk SDLC Analysis Report', margin, y);
            y += 28;
            doc.setFont('helvetica', 'normal');
            doc.setFontSize(10);
            doc.text(`Generated: ${generatedAt}`, margin, y);
            y += 18;
            doc.text(`Project: ${currentResult.name || 'Untitled Project'}`, margin, y);
            y += 26;

            addHeading('Executive Summary');
            addParagraph(
                `${currentResult.model} is the recommended SDLC method with a confidence score of ${confidence}%. ` +
                `This recommendation is based on your submitted project constraints, delivery pressure, complexity profile, and team readiness signals.`
            );

            addHeading('Final Recommendation');
            addRow('Recommended method', currentResult.model);
            addRow('Confidence score', `${confidence}%`);
            addRow('Project reference', currentResult.predictionProjectId || currentResult.projectId || 'N/A');

            addHeading('Model Ranking and Risk Comparison');
            ranking.forEach((item, index) => {
                const suitability = toPercent(item.suitability);
                const risk = Math.max(0, 100 - suitability);
                addParagraph(
                    `${index + 1}. ${item.name}: suitability ${suitability}% and projected risk ${risk}%.`,
                    10
                );
            });

            addHeading('Why This Method Was Chosen');
            if (currentResult.explainability?.length) {
                currentResult.explainability.slice(0, 8).forEach((item, index) => {
                    addParagraph(`${index + 1}. ${item.title}: ${item.text}`, 10);
                });
            } else {
                addParagraph('No feature-level explainability details were available for this prediction.', 10);
            }

            addHeading('Why Other Methods Were Not Selected');
            const alternativeMethods = ranking.filter((item) => item.name !== currentResult.model);
            if (alternativeMethods.length) {
                alternativeMethods.forEach((item, index) => {
                    const suitability = toPercent(item.suitability);
                    const gap = Math.max(0, confidence - suitability);
                    addParagraph(
                        `${index + 1}. ${item.name} was not selected because it scored ${suitability}% (${gap} points below ${currentResult.model}). ` +
                        `For this project profile, it appears ${modelFitLabel(suitability)} with ${modelTimeLabel(suitability)} and ${modelLoadLabel(suitability)}.`,
                        10
                    );
                });
            } else {
                addParagraph('No alternative method data was available to compare against the selected recommendation.', 10);
            }

            addHeading('Inference Transparency');
            addRow('Model version', currentResult.modelVersion || 'Unknown');
            addRow(
                'Inference time',
                currentResult.inferenceTime !== null && currentResult.inferenceTime !== undefined
                    ? `${Math.round(Number(currentResult.inferenceTime) * 1000)} ms`
                    : 'Unknown'
            );
            addRow('Explainability source', currentResult.explainabilitySource || 'Unknown');

            const safeName = (currentResult.name || 'project').replace(/[^a-z0-9-_ ]/gi, '').trim() || 'project';
            doc.save(`${safeName}_SDLC_Report.pdf`);
        } catch (_error) {
            window.alert('PDF export failed. Install frontend dependencies and try again.');
        }
    };

    const handleShare = async () => {
        const summary = `${currentResult.name}: ${currentResult.model} (${currentResult.confidence}% confidence)`;
        try {
            if (navigator.share) {
                await navigator.share({
                    title: 'SDLC Analysis Result',
                    text: summary,
                });
                return;
            }

            if (navigator.clipboard?.writeText) {
                await navigator.clipboard.writeText(summary);
            }
        } catch (_error) {
            // Ignore cancelled share attempts.
        }
    };

    const alternatives = modelScores
        .filter((item) => item.name !== currentResult.model)
        .sort((a, b) => (b.suitability || 0) - (a.suitability || 0))
        .slice(0, 3);

    const handleFeedbackSubmit = async (e) => {
        e.preventDefault();
        setFeedbackErr(null);
        setFeedbackMsg(null);

        if (!currentResult.predictionProjectId) {
            setFeedbackErr('Missing project_id for this analysis result.');
            return;
        }
        if (!feedbackForm.actualOutcome) {
            setFeedbackErr('Please choose actual outcome.');
            return;
        }

        try {
            setSubmittingFeedback(true);
            await AnalysisService.submitFeedback({
                project_id: currentResult.predictionProjectId,
                actual_outcome: feedbackForm.actualOutcome,
                notes: feedbackForm.notes || '',
                actual_sdlc_used: currentResult.model,
                success_score: feedbackForm.actualOutcome === 'success' ? 9 : 4,
                risk_realized: feedbackForm.actualOutcome === 'success' ? 'Low' : 'High',
                completion_status: feedbackForm.actualOutcome === 'success' ? 'Completed' : 'At Risk',
            });
            setFeedbackMsg('Feedback submitted successfully.');
            setFeedbackForm({ actualOutcome: '', notes: '' });
        } catch (error) {
            setFeedbackErr(error.message || 'Failed to submit feedback.');
        } finally {
            setSubmittingFeedback(false);
        }
    };

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">Analysis Results</h2>
                    <p className="text-muted-foreground mt-1">Project: <span className="text-foreground font-bold">{currentResult.name}</span></p>
                </div>
                <div className="flex gap-3">
                    <Button variant="outline" className="flex items-center gap-2" onClick={handleShare}>
                        <Share2 size={16} />
                        <span>Share</span>
                    </Button>
                    <Button onClick={handleExport} className="flex items-center gap-2">
                        <Download size={16} />
                        <span>Export Report</span>
                    </Button>
                </div>
            </div>

            <Card className="bg-gradient-to-br from-primary/10 via-background to-background border-primary/20 overflow-hidden relative">
                <div className="absolute top-0 right-0 p-8 opacity-5">
                    <CheckCircle2 size={200} />
                </div>
                <div className="flex flex-col md:flex-row gap-8 items-center relative z-10">
                    <div className="w-32 h-32 rounded-3xl bg-primary flex items-center justify-center text-white shadow-2xl shadow-primary/40">
                        <CheckCircle2 size={64} />
                    </div>
                    <div className="flex-1 text-center md:text-left">
                        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/20 text-primary text-xs font-bold uppercase tracking-wider mb-2">
                            Best Match found
                        </div>
                        <h3 className="text-4xl font-extrabold tracking-tight">{currentResult.model}</h3>
                        <p className="text-muted-foreground mt-2 max-w-2xl text-lg">
                            Based on your specific project parameters, an iterative {currentResult.model} approach is highly recommended for optimal stability and delivery.
                        </p>
                    </div>
                    <div className="flex flex-col items-center justify-center px-8 border-l border-border/50">
                        <span className="text-5xl font-black text-primary">{currentResult.confidence}%</span>
                        <span className="text-xs font-bold uppercase tracking-widest text-muted-foreground mt-1">Confidence Score</span>
                    </div>
                </div>
            </Card>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <Card title="Risk Comparison" subtitle="Projected risk level across models" className="lg:col-span-2">
                    <ChartContainer height={300}>
                        <BarChart data={riskData} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#333" />
                            <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#888', fontSize: 12 }} dy={10} />
                            <YAxis axisLine={false} tickLine={false} tick={{ fill: '#888', fontSize: 12 }} label={{ value: 'Risk Level %', angle: -90, position: 'insideLeft', fill: '#888', dy: 50 }} />
                            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.05)' }} />
                            <Bar dataKey="risk" radius={[8, 8, 0, 0]} barSize={50}>
                                {riskData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={entry.color} />
                                ))}
                            </Bar>
                        </BarChart>
                    </ChartContainer>
                </Card>

                <Card title="Confidence Meter" subtitle="Model suitability breakdown">
                    <ChartContainer height={220}>
                        <PieChart>
                            <Pie
                                data={suitabilityData}
                                cx="50%"
                                cy="50%"
                                innerRadius={60}
                                outerRadius={80}
                                paddingAngle={5}
                                dataKey="value"
                            >
                                {suitabilityData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                            </Pie>
                            <Tooltip />
                        </PieChart>
                    </ChartContainer>
                    <div className="mt-4 space-y-3">
                        <div className="flex items-center justify-between text-sm">
                            <span className="text-muted-foreground flex items-center gap-2">
                                <div className="w-2 h-2 rounded-full bg-primary"></div> {currentResult.model}
                            </span>
                            <span className="font-bold">{currentResult.confidence}%</span>
                        </div>
                        <div className="flex items-center justify-between text-sm">
                            <span className="text-muted-foreground flex items-center gap-2">
                                <div className="w-2 h-2 rounded-full bg-indigo-950"></div> Others
                            </span>
                            <span className="font-bold">{100 - currentResult.confidence}%</span>
                        </div>
                    </div>
                </Card>

                <Card title="Explainability Panel" subtitle="Why this model was chosen" className="lg:col-span-3">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {(currentResult.explainability || []).map((item, i) => (
                            <div key={i} className="p-4 rounded-xl bg-accent/30 border border-border">
                                <div className="flex items-center gap-3 mb-3 text-primary">
                                    {i === 0 ? <TrendingUp size={18} /> : i === 1 ? <AlertTriangle size={18} className="text-amber-500" /> : <ShieldCheck size={18} className="text-green-500" />}
                                    <h4 className="font-bold">{item.title}</h4>
                                </div>
                                <p className="text-sm text-muted-foreground leading-relaxed">
                                    {item.text}
                                </p>
                            </div>
                        ))}
                        {!currentResult.explainability?.length && (
                            <div className="p-4 rounded-xl bg-accent/30 border border-border md:col-span-3">
                                <p className="text-sm text-muted-foreground">
                                    Explainability details are not available for this result.
                                </p>
                            </div>
                        )}
                    </div>
                </Card>

                <Card title="Inference Transparency" subtitle="Runtime and explainability metadata" className="lg:col-span-3">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                        <div className="p-4 rounded-xl bg-accent/30 border border-border">
                            <p className="text-xs uppercase tracking-wider text-muted-foreground">Model Version</p>
                            <p className="font-semibold mt-1">{currentResult.modelVersion || 'Unknown'}</p>
                        </div>
                        <div className="p-4 rounded-xl bg-accent/30 border border-border">
                            <p className="text-xs uppercase tracking-wider text-muted-foreground">Inference Time</p>
                            <p className="font-semibold mt-1">
                                {currentResult.inferenceTime !== null && currentResult.inferenceTime !== undefined
                                    ? `${Math.round(Number(currentResult.inferenceTime) * 1000)} ms`
                                    : 'Unknown'}
                            </p>
                        </div>
                        <div className="p-4 rounded-xl bg-accent/30 border border-border">
                            <p className="text-xs uppercase tracking-wider text-muted-foreground">Explainability</p>
                            <p className="font-semibold mt-1 uppercase">{currentResult.explainabilitySource || 'unknown'}</p>
                        </div>
                    </div>
                </Card>

                <Card title="Submit Actual Outcome" subtitle="Close the loop with real project feedback" className="lg:col-span-3">
                    <form onSubmit={handleFeedbackSubmit} className="space-y-4">
                        {feedbackMsg && <Alert variant="success">{feedbackMsg}</Alert>}
                        {feedbackErr && <Alert variant="error">{feedbackErr}</Alert>}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <label className="text-xs font-bold tracking-wider uppercase opacity-70">Actual Outcome</label>
                                <select
                                    value={feedbackForm.actualOutcome}
                                    onChange={(e) => setFeedbackForm((prev) => ({ ...prev, actualOutcome: e.target.value }))}
                                    className="w-full bg-accent/30 border border-border rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all"
                                >
                                    <option value="">Select outcome</option>
                                    <option value="success">Success</option>
                                    <option value="failure">Failure</option>
                                </select>
                            </div>
                            <div className="space-y-2">
                                <label className="text-xs font-bold tracking-wider uppercase opacity-70">Notes (Optional)</label>
                                <input
                                    value={feedbackForm.notes}
                                    onChange={(e) => setFeedbackForm((prev) => ({ ...prev, notes: e.target.value }))}
                                    className="w-full bg-accent/30 border border-border rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all"
                                    placeholder="Any key observations..."
                                />
                            </div>
                        </div>
                        <div className="flex justify-end">
                            <Button type="submit" disabled={submittingFeedback}>
                                {submittingFeedback ? 'Submitting...' : 'Submit Feedback'}
                            </Button>
                        </div>
                    </form>
                </Card>

                <Card title="Alternative Models" subtitle="Comparison of secondary options" className="lg:col-span-3">
                    <Table headers={['Model Name', 'Suitability', 'Time to Market', 'Resource Load', '']}>
                        {alternatives.map((item, i) => {
                            const suitLabel = item.suitability >= 75 ? 'Highly Compatible' : item.suitability >= 55 ? 'Compatible' : 'Low Fit';
                            const timeLabel = item.suitability >= 70 ? 'Accelerated' : item.suitability >= 55 ? 'Steady' : 'Slow';
                            const loadLabel = item.suitability >= 70 ? 'Medium' : item.suitability >= 55 ? 'High' : 'Very High';
                            return (
                            <TableRow key={i}>
                                <TableCell className="font-medium">{item.name}</TableCell>
                                <TableCell>
                                    <span className={`px-2 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${suitLabel.includes('Highly') ? 'bg-primary/10 text-primary' : 'bg-muted text-muted-foreground'
                                        }`}>
                                        {suitLabel}
                                    </span>
                                </TableCell>
                                <TableCell className="text-muted-foreground">{timeLabel}</TableCell>
                                <TableCell className="text-muted-foreground">{loadLabel}</TableCell>
                                <TableCell className="text-right">
                                    <button
                                        className="p-1 px-3 text-xs bg-accent rounded-lg opacity-0 group-hover:opacity-100 transition-all font-bold"
                                        onClick={() => setSelectedAlternative(item)}
                                    >
                                        Details
                                    </button>
                                </TableCell>
                            </TableRow>
                        )})}
                        {!alternatives.length && (
                            <TableRow>
                                <TableCell className="text-center py-8 text-muted-foreground" colSpan={5}>
                                    No alternative model data available.
                                </TableCell>
                            </TableRow>
                        )}
                    </Table>
                    {selectedAlternative && (
                        <div className="mt-4 p-4 rounded-xl bg-accent/30 border border-border">
                            <h4 className="font-bold text-sm">{selectedAlternative.name}</h4>
                            <p className="text-sm text-muted-foreground mt-2">
                                Suitability score: {selectedAlternative.suitability}%. This option is lower ranked than {currentResult.model} for your current project signals.
                            </p>
                        </div>
                    )}
                </Card>
            </div>
        </div>
    );
};

export default Results;
