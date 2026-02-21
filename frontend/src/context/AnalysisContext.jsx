import React, { createContext, useContext, useState, useEffect } from 'react';

const AnalysisContext = createContext();
const STORAGE_VERSION = '3';
const STORAGE_VERSION_KEY = 'fp_storage_version';
let storageInitialized = false;
const KEY_USER_PROFILE = 'hr_user_profile';
const KEY_PROJECTS = 'hr_projects';
const KEY_ACTIVE_PROJECT_ID = 'hr_active_project_id';
const KEY_CURRENT_RESULT = 'hr_current_result';
const KEY_HISTORY = 'hr_history';
const KEY_APP_SETTINGS = 'hr_app_settings';
const KEY_TOKEN = 'hr_token';

const initializeStorageVersion = () => {
    if (storageInitialized || typeof window === 'undefined') return;
    storageInitialized = true;

    const currentVersion = localStorage.getItem(STORAGE_VERSION_KEY);
    if (currentVersion === STORAGE_VERSION) return;

    const keysToClear = [
        'fp_user_profile',
        'fp_projects',
        'fp_active_project_id',
        'fp_current_result',
        'fp_history',
        'fp_app_settings',
        'fp_token',
        KEY_USER_PROFILE,
        KEY_PROJECTS,
        KEY_ACTIVE_PROJECT_ID,
        KEY_CURRENT_RESULT,
        KEY_HISTORY,
        KEY_APP_SETTINGS,
        KEY_TOKEN,
    ];
    keysToClear.forEach((key) => localStorage.removeItem(key));
    localStorage.setItem(STORAGE_VERSION_KEY, STORAGE_VERSION);
};

export const AnalysisProvider = ({ children }) => {
    initializeStorageVersion();

    const createId = () =>
        (typeof crypto !== 'undefined' && crypto.randomUUID)
            ? crypto.randomUUID()
            : `${Date.now()}-${Math.floor(Math.random() * 10000)}`;

    const [userProfile, setUserProfile] = useState(() => {
        const saved = localStorage.getItem(KEY_USER_PROFILE);
        return saved ? JSON.parse(saved) : null;
    });

    const [projects, setProjects] = useState(() => {
        const saved = localStorage.getItem(KEY_PROJECTS);
        return saved ? JSON.parse(saved) : [];
    });

    const [activeProjectId, setActiveProjectId] = useState(() => {
        return localStorage.getItem(KEY_ACTIVE_PROJECT_ID) || null;
    });

    const [currentResult, setCurrentResult] = useState(() => {
        const saved = localStorage.getItem(KEY_CURRENT_RESULT);
        return saved ? JSON.parse(saved) : null;
    });

    const [history, setHistory] = useState(() => {
        const saved = localStorage.getItem(KEY_HISTORY);
        return saved ? JSON.parse(saved) : [];
    });

    useEffect(() => {
        if (userProfile) {
            localStorage.setItem(KEY_USER_PROFILE, JSON.stringify(userProfile));
        } else {
            localStorage.removeItem(KEY_USER_PROFILE);
        }
    }, [userProfile]);

    useEffect(() => {
        localStorage.setItem(KEY_PROJECTS, JSON.stringify(projects));
    }, [projects]);

    useEffect(() => {
        if (activeProjectId) {
            localStorage.setItem(KEY_ACTIVE_PROJECT_ID, activeProjectId);
        } else {
            localStorage.removeItem(KEY_ACTIVE_PROJECT_ID);
        }
    }, [activeProjectId]);

    useEffect(() => {
        localStorage.setItem(KEY_HISTORY, JSON.stringify(history));
    }, [history]);

    useEffect(() => {
        if (currentResult) {
            localStorage.setItem(KEY_CURRENT_RESULT, JSON.stringify(currentResult));
        } else {
            localStorage.removeItem(KEY_CURRENT_RESULT);
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
