import React, { useState } from 'react';
import { Input, Textarea, Button } from '../components/UI';
import { Plus, ArrowRight, Brain, Boxes, GitMerge, Activity, Rocket } from 'lucide-react';
import { useAnalysis } from '../context/AnalysisContext';

const ProjectSelection = () => {
    const { projects, createProject, setActiveProjectId } = useAnalysis();
    const [isCreating, setIsCreating] = useState(false);
    const [formData, setFormData] = useState({ name: '', description: '' });

    const handleCreateProject = () => {
        if (!formData.name.trim()) return;
        const newProject = createProject(formData.name.trim(), formData.description.trim());
        setActiveProjectId(newProject.id);
    };

    const selectProject = (id) => {
        setActiveProjectId(id);
    };

    const engineModels = [
        { name: 'Agile', icon: <Activity size={18} />, color: 'text-emerald-400', desc: 'Iterative development focusing on flexibility, customer collaboration, and rapid delivery of functional components.' },
        { name: 'Waterfall', icon: <Boxes size={18} />, color: 'text-blue-400', desc: 'Linear and sequential design approach. Best for projects with rigid, unchanging, and highly detailed requirements.' },
        { name: 'DevOps', icon: <Rocket size={18} />, color: 'text-indigo-400', desc: 'Continuous integration and delivery unifying software development and IT operations for extremely rapid cycles.' },
        { name: 'V-Model', icon: <GitMerge size={18} />, color: 'text-amber-400', desc: 'Strict validation and verification model linking each development phase directly to a corresponding testing phase.' },
        { name: 'Spiral', icon: <Brain size={18} />, color: 'text-purple-400', desc: 'Risk-driven, iterative process. Ideal for vast, complex, or highly experimental endeavors.' }
    ];

    return (
        <div className="min-h-screen w-full bg-background flex flex-col p-6 md:p-12 overflow-y-auto animate-in fade-in duration-700">
            <main className="max-w-[1400px] mx-auto w-full grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 mt-4 lg:mt-12">

                {/* Left Column */}
                <div className="lg:col-span-4 space-y-8">
                    <div>
                        <h1 className="text-4xl font-extrabold tracking-tight mb-3 text-white">Projects</h1>
                        <p className="text-sm text-foreground/80 leading-relaxed max-w-xs">
                            Select an active project workspace or create a new one to begin analysis.
                        </p>
                    </div>

                    {!isCreating ? (
                        <div className="space-y-6">
                            <button
                                className="w-full h-[48px] bg-[#5B55F6] hover:bg-[#4F49D9] text-white flex items-center justify-center gap-2 rounded-xl font-bold text-sm transition-all duration-300 shadow-lg shadow-[#5B55F6]/20 active:scale-[0.98]"
                                onClick={() => setIsCreating(true)}
                            >
                                <Plus size={18} strokeWidth={2.5} />
                                <span>Create New Project</span>
                            </button>

                            <div className="space-y-3 pt-6">
                                <h3 className="text-[11px] font-bold uppercase tracking-[0.15em] text-[#E5C07B] mb-4">Recent Projects</h3>
                                {projects.length === 0 ? (
                                    <div className="p-8 text-center border border-white/5 rounded-2xl text-muted-foreground/50 text-sm">
                                        No projects found.
                                    </div>
                                ) : (
                                    projects.map(p => (
                                        <button
                                            key={p.id}
                                            onClick={() => selectProject(p.id)}
                                            className="w-full text-left p-4 rounded-[14px] border border-white/[0.06] bg-[#161619] hover:bg-[#1A1A1E] hover:border-white/10 transition-all duration-300 group flex justify-between items-center h-[76px]"
                                        >
                                            <div className="flex flex-col justify-center">
                                                <h4 className="font-bold text-sm text-white mb-1 group-hover:text-primary transition-colors">{p.name}</h4>
                                                <p className="text-xs text-muted-foreground/70 line-clamp-1">{p.description || 'No description provided.'}</p>
                                            </div>
                                            <ArrowRight size={16} className="text-muted-foreground group-hover:text-white group-hover:translate-x-1 transition-all duration-300" />
                                        </button>
                                    ))
                                )}
                            </div>
                        </div>
                    ) : (
                        <div className="bg-[#121214] border border-white/5 rounded-3xl p-6 shadow-xl relative overflow-hidden animate-in zoom-in-95 duration-300">
                            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-[#5B55F6] to-purple-500" />
                            <h3 className="font-bold text-lg mb-6 text-white">New Project Detail</h3>
                            <div className="space-y-5">
                                <Input
                                    label="Project Name"
                                    placeholder="e.g. Project Odyssey"
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                />
                                <Textarea
                                    label="Description (Optional)"
                                    placeholder="Brief overview..."
                                    value={formData.description}
                                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                />
                                <div className="flex gap-3 pt-2">
                                    <Button variant="ghost" className="flex-1" onClick={() => setIsCreating(false)}>Cancel</Button>
                                    <button
                                        className="flex-1 py-3 px-4 bg-[#5B55F6] hover:bg-[#4F49D9] text-white rounded-[14px] font-bold text-sm transition-all disabled:opacity-50 disabled:pointer-events-none active:scale-95"
                                        onClick={handleCreateProject}
                                        disabled={!formData.name.trim()}
                                    >
                                        Create
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Right Column */}
                <div className="lg:col-span-8">
                    <div className="h-full bg-[#121214] border border-white/[0.04] rounded-[24px] p-8 lg:p-10 shadow-2xl relative overflow-hidden flex flex-col">
                        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-[#5B55F6]/5 rounded-full blur-[120px] pointer-events-none" />

                        <div className="mb-10 relative z-10">
                            <h3 className="text-xl font-bold flex items-center gap-3 mb-4 text-white">
                                <div className="w-7 h-7 rounded-sm flex items-center justify-center">
                                    <Brain className="text-[#5B55F6]" size={22} strokeWidth={2.5} />
                                </div>
                                HelixRisk V3 Capability Overview
                            </h3>
                            <p className="text-[13px] text-muted-foreground/80 leading-[1.6] max-w-3xl pl-10 pr-4">
                                Our AI-driven analysis engine evaluates 16 diverse programmatic vectors—ranging from team experience and requirement stability to risk tolerance and integration complexity—to recommend the ideal Software Development Life Cycle (SDLC) model for your specific constraints.
                            </p>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 auto-rows-fr relative z-10 flex-1 pl-10 pr-4">
                            {engineModels.map((model, i) => (
                                <div key={i} className="p-6 rounded-2xl bg-[#161619] border border-white/[0.03] hover:border-white/10 hover:bg-[#1A1A1E] transition-all duration-300 flex flex-col gap-3 group">
                                    <div className="flex items-center gap-3">
                                        <div className={`w-8 h-8 rounded-[10px] bg-white/[0.02] flex items-center justify-center ${model.color}`}>
                                            {model.icon}
                                        </div>
                                        <h4 className="font-bold text-[15px] tracking-wide text-foreground group-hover:text-white transition-colors">{model.name}</h4>
                                    </div>
                                    <p className="text-xs text-muted-foreground/80 leading-relaxed mt-1">
                                        {model.desc}
                                    </p>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

            </main>
        </div>
    );
};

export default ProjectSelection;
