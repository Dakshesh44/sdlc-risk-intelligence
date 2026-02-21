import React, { createContext, useContext, useState, useEffect } from 'react';

const AnalysisContext = createContext();

export const AnalysisProvider = ({ children }) => {
    const createId = () =>
        (typeof crypto !== 'undefined' && crypto.randomUUID)
            ? crypto.randomUUID()
            : `${Date.now()}-${Math.floor(Math.random() * 10000)}`;

    const [userProfile, setUserProfile] = useState(() => {
        const saved = localStorage.getItem('fp_user_profile');
        return saved ? JSON.parse(saved) : null;
    });

    const [projects, setProjects] = useState(() => {
        const saved = localStorage.getItem('fp_projects');
        return saved ? JSON.parse(saved) : [];
    });

    const [activeProjectId, setActiveProjectId] = useState(() => {
        return localStorage.getItem('fp_active_project_id') || null;
    });

    const [currentResult, setCurrentResult] = useState(() => {
        const saved = localStorage.getItem('fp_current_result');
        return saved ? JSON.parse(saved) : null;
    });

    const [history, setHistory] = useState(() => {
        const saved = localStorage.getItem('fp_history');
        return saved ? JSON.parse(saved) : [];
    });

    useEffect(() => {
        if (userProfile) {
            localStorage.setItem('fp_user_profile', JSON.stringify(userProfile));
        } else {
            localStorage.removeItem('fp_user_profile');
        }
    }, [userProfile]);

    useEffect(() => {
        localStorage.setItem('fp_projects', JSON.stringify(projects));
    }, [projects]);

    useEffect(() => {
        if (activeProjectId) {
            localStorage.setItem('fp_active_project_id', activeProjectId);
        } else {
            localStorage.removeItem('fp_active_project_id');
        }
    }, [activeProjectId]);

    useEffect(() => {
        localStorage.setItem('fp_history', JSON.stringify(history));
    }, [history]);

    useEffect(() => {
        if (currentResult) {
            localStorage.setItem('fp_current_result', JSON.stringify(currentResult));
        } else {
            localStorage.removeItem('fp_current_result');
        }
    }, [currentResult]);

    const login = (profileData) => {
        setUserProfile(profileData);
    };

    const logout = () => {
        setUserProfile(null);
        setActiveProjectId(null);
        setCurrentResult(null);
    };

    const createProject = (name, description) => {
        const newProject = {
            id: createId(),
            name,
            description,
            createdAt: new Date().toISOString(),
        };
        setProjects(prev => [newProject, ...prev]);
        return newProject;
    };

    const deleteProject = (id) => {
        setProjects(prev => prev.filter(p => p.id !== id));
        setHistory(prev => prev.filter(h => h.projectId !== id));
        if (activeProjectId === id) {
            setActiveProjectId(null);
            setCurrentResult(null);
        }
    };

    // Scoped History Interactions
    const activeProjectHistory = history.filter(item => item.projectId === activeProjectId);

    const addAnalysis = (formData, result) => {
        if (!activeProjectId) throw new Error("No active project selected");

        const newEntry = {
            id: createId(),
            projectId: activeProjectId,
            name: formData.projectName || 'Untitled Analysis',
            model: result.model,
            confidence: result.confidence,
            date: new Date().toISOString().split('T')[0],
            status: 'Completed',
            explainability: result.explainability || [],
            modelScores: result.modelScores || [],
            predictionProjectId: result.projectId || null,
            modelVersion: result.modelVersion || null,
            inferenceTime: result.inferenceTime ?? null,
            explainabilitySource: result.explainabilitySource || null,
            generatedAt: result.generatedAt || new Date().toISOString(),
            ...formData
        };
        setHistory(prev => [newEntry, ...prev]);
        setCurrentResult(newEntry);
        return newEntry;
    };

    const selectAnalysis = (id) => {
        const selected = history.find(item => item.id === id && item.projectId === activeProjectId);
        if (selected) setCurrentResult(selected);
        return selected || null;
    };

    const deleteAnalysis = (id) => {
        setHistory(prev => prev.filter(item => item.id !== id));
        setCurrentResult(prev => (prev && prev.id === id ? null : prev));
    };

    const clearActiveProjectHistory = () => {
        setHistory(prev => prev.filter(item => item.projectId !== activeProjectId));
        setCurrentResult(null);
    };

    return (
        <AnalysisContext.Provider value={{
            userProfile,
            login,
            logout,
            projects,
            createProject,
            deleteProject,
            activeProjectId,
            setActiveProjectId,
            currentResult,
            history: activeProjectHistory,
            addAnalysis,
            setCurrentResult,
            selectAnalysis,
            deleteAnalysis,
            clearAllHistory: clearActiveProjectHistory
        }}>
            {children}
        </AnalysisContext.Provider>
    );
};

export const useAnalysis = () => {
    const context = useContext(AnalysisContext);
    if (!context) throw new Error('useAnalysis must be used within an AnalysisProvider');
    return context;
};
