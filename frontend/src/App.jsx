import React, { useEffect, useState } from 'react';
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import NewAnalysis from './pages/NewAnalysis';
import Results from './pages/Results';
import History from './pages/History';
import Settings from './pages/Settings';
import Login from './pages/Login';
import ProjectSelection from './pages/ProjectSelection';
import { ThemeProvider } from './context/ThemeContext';
import { AnalysisProvider, useAnalysis } from './context/AnalysisContext';
import MouseGlow from './components/MouseGlow';
import ErrorBoundary from './components/ErrorBoundary';
import { AnalysisService } from './services/analysisService';

function AppContent() {
    const { userProfile, activeProjectId } = useAnalysis();
    const [activeTab, setActiveTab] = useState('Home');
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const [modelHealth, setModelHealth] = useState({ loading: true, ml_model_loaded: false });

    useEffect(() => {
        let mounted = true;
        AnalysisService.getModelStatus()
            .then((data) => {
                if (mounted) setModelHealth({ loading: false, ...data });
            })
            .catch(() => {
                if (mounted) setModelHealth({ loading: false, ml_model_loaded: false, error: 'unreachable' });
            });
        return () => {
            mounted = false;
        };
    }, []);

    // State Machine Routing
    if (!userProfile) {
        return <Login />;
    }

    if (!activeProjectId) {
        return <ProjectSelection />;
    }

    const renderContent = () => {
        switch (activeTab) {
            case 'Home': return <Dashboard onOpenResults={() => setActiveTab('Results Dashboard')} />;
            case 'New Analysis': return <NewAnalysis onAnalyze={() => setActiveTab('Results Dashboard')} />;
            case 'Results Dashboard': return <Results />;
            case 'History': return <History onOpenResults={() => setActiveTab('Results Dashboard')} />;
            case 'Settings': return <Settings />;
            default: return <Dashboard onOpenResults={() => setActiveTab('Results Dashboard')} />;
        }
    };

    return (
        <div className="flex min-h-screen bg-background text-foreground transition-colors duration-300 animate-in fade-in duration-500 relative">
            <MouseGlow />
            <Sidebar
                activeTab={activeTab}
                setActiveTab={(tab) => {
                    setActiveTab(tab);
                    setSidebarOpen(false);
                }}
                isOpen={sidebarOpen}
                onClose={() => setSidebarOpen(false)}
            />

            <div className="flex-1 flex flex-col min-w-0">
                <Navbar
                    activeTab={activeTab}
                    onMenuToggle={() => setSidebarOpen(true)}
                    onOpenResults={() => setActiveTab('Results Dashboard')}
                    onOpenHistory={() => setActiveTab('History')}
                    modelHealth={modelHealth}
                />

                <main className="flex-1 overflow-y-auto p-4 md:p-8 outline-none">
                    <div className="max-w-7xl mx-auto space-y-6">
                        {renderContent()}
                    </div>
                </main>
            </div>
        </div>
    );
}

function App() {
    return (
        <ThemeProvider>
            <AnalysisProvider>
                <ErrorBoundary>
                    <AppContent />
                </ErrorBoundary>
            </AnalysisProvider>
        </ThemeProvider>
    );
}

export default App;
