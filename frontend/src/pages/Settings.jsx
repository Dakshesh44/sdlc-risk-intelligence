import React, { useState, useEffect } from 'react';
import { Card, Button, Input, Dropdown, Alert } from '../components/UI';
import { User, Shield, Bell, Database, Cpu, HardDrive } from 'lucide-react';
import { useAnalysis } from '../context/AnalysisContext';

const Settings = () => {
    const { userProfile, login } = useAnalysis();
    const initialSettings = {
        analysisModel: 'v3',
        explainabilityEnabled: true,
    };
    const [activeSection, setActiveSection] = useState('General');
    const [saveMessage, setSaveMessage] = useState('');
    const [settings, setSettings] = useState(() => {
        const stored = localStorage.getItem('fp_app_settings');
        const appData = stored ? JSON.parse(stored) : {};
        return {
            ...initialSettings,
            ...appData,
            fullName: userProfile?.fullName || '',
            email: userProfile?.email || '',
            organization: userProfile?.organization || '',
        };
    });

    useEffect(() => {
        if (userProfile) {
            setSettings(prev => ({
                ...prev,
                fullName: userProfile.fullName || prev.fullName,
                email: userProfile.email || prev.email,
                organization: userProfile.organization || prev.organization
            }));
        }
    }, [userProfile]);

    const sections = [
        { label: 'General', icon: <User size={18} /> },
        { label: 'Security', icon: <Shield size={18} /> },
        { label: 'Notifications', icon: <Bell size={18} /> },
        { label: 'Data & Storage', icon: <Database size={18} /> },
        { label: 'AI Engine', icon: <Cpu size={18} /> },
    ];

    const updateField = (key, value) => {
        setSettings(prev => ({ ...prev, [key]: value }));
        setSaveMessage('');
    };

    const handleSave = () => {
        localStorage.setItem('fp_app_settings', JSON.stringify({
            analysisModel: settings.analysisModel,
            explainabilityEnabled: settings.explainabilityEnabled
        }));

        login({
            ...userProfile,
            fullName: settings.fullName || 'User',
            email: settings.email || '',
            organization: settings.organization || '',
        });

        setSaveMessage('Settings saved successfully.');
        setTimeout(() => setSaveMessage(''), 3000);
    };

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div>
                <h2 className="text-3xl font-bold tracking-tight">System Settings</h2>
                <p className="text-muted-foreground mt-1">Manage your account and engine preferences.</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-1 space-y-4">
                    {sections.map((item, i) => (
                        <button
                            key={i}
                            onClick={() => setActiveSection(item.label)}
                            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all ${activeSection === item.label ? 'bg-primary text-white shadow-lg shadow-primary/20' : 'hover:bg-accent text-muted-foreground hover:text-foreground'
                                } `}
                        >
                            {item.icon}
                            {item.label}
                        </button>
                    ))}
                </div>

                <div className="lg:col-span-2 space-y-8">
                    {saveMessage && (
                        <Alert variant="success" className="animate-in fade-in slide-in-from-top-2">
                            <span>{saveMessage}</span>
                        </Alert>
                    )}

                    {activeSection === 'General' && (
                        <Card title="Profile Information" subtitle="Update your personal and organizational details">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <Input
                                    label="Full Name"
                                    value={settings.fullName}
                                    onChange={(e) => updateField('fullName', e.target.value)}
                                />
                                <Input
                                    label="Email Address"
                                    value={settings.email}
                                    onChange={(e) => updateField('email', e.target.value)}
                                />
                                <Input
                                    label="Organization"
                                    className="md:col-span-2"
                                    value={settings.organization}
                                    onChange={(e) => updateField('organization', e.target.value)}
                                />
                            </div>
                            <div className="mt-8 flex justify-end">
                                <Button onClick={handleSave}>Save Changes</Button>
                            </div>
                        </Card>
                    )}

                    {activeSection === 'AI Engine' && (
                        <Card title="Engine Preferences" subtitle="Configure how the AI evaluates project parameters">
                            <div className="space-y-6">
                                <Dropdown
                                    label="Analysis Model"
                                    options={[
                                        { label: 'FlowEngine V3 (Latest)', value: 'v3' },
                                        { label: 'Legacy V2.4', value: 'v2' },
                                    ]}
                                    value={settings.analysisModel}
                                    onChange={(e) => updateField('analysisModel', e.target.value)}
                                />
                                <div className="flex items-center justify-between p-4 rounded-xl bg-accent/30 border border-border">
                                    <div className="flex items-center gap-4">
                                        <HardDrive size={24} className="text-primary" />
                                        <div>
                                            <h4 className="font-bold text-sm">Enhanced Explainability</h4>
                                            <p className="text-xs text-muted-foreground">Provide detailed reasoning for all recommendations.</p>
                                        </div>
                                    </div>
                                    <button
                                        className={`w-12 h-6 rounded-full flex items-center px-1 transition-all ${settings.explainabilityEnabled ? 'bg-primary' : 'bg-border'} `}
                                        onClick={() => updateField('explainabilityEnabled', !settings.explainabilityEnabled)}
                                    >
                                        <div className={`w-4 h-4 bg-white rounded-full transition-all ${settings.explainabilityEnabled ? 'ml-auto' : ''} `}></div>
                                    </button>
                                </div>
                                <div className="mt-8 flex justify-end">
                                    <Button onClick={handleSave}>Save AI Settings</Button>
                                </div>
                            </div>
                        </Card>
                    )}

                    {['Security', 'Notifications', 'Data & Storage'].includes(activeSection) && (
                        <Card className="flex flex-col items-center justify-center py-16 text-center shadow-none border-dashed border-2">
                            <div className="w-16 h-16 rounded-full bg-accent/50 flex items-center justify-center text-muted-foreground mb-4">
                                {sections.find(s => s.label === activeSection)?.icon}
                            </div>
                            <h3 className="text-lg font-bold">{activeSection} Settings</h3>
                            <p className="text-sm text-muted-foreground mt-2 max-w-sm">
                                This section is locked by your organization's policy. Contact your workspace administrator to request changes.
                            </p>
                        </Card>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Settings;
