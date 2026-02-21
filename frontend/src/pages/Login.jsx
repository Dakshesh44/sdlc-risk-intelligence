import React, { useState } from 'react';
import { Card, Input, Button, Alert } from '../components/UI';
import { Shield, Lock, User, AtSign, ArrowRight } from 'lucide-react';
import { useAnalysis } from '../context/AnalysisContext';

const Login = () => {
    const { login } = useAnalysis();
    const [formData, setFormData] = useState({ fullName: '', email: '', password: '' });
    const [error, setError] = useState(null);

    const handleChange = (field, value) => {
        setFormData(prev => ({ ...prev, [field]: value }));
        setError(null);
    };

    const handleLogin = (e) => {
        e.preventDefault();

        if (!formData.fullName.trim() || !formData.email.trim() || !formData.password.trim()) {
            setError("All fields are required to continue.");
            return;
        }

        if (!formData.email.includes('@')) {
            setError("Please enter a valid email address.");
            return;
        }

        // Simulate login
        login({
            fullName: formData.fullName.trim(),
            email: formData.email.trim(),
            organization: 'HelixRisk Workspace'
        });
    };

    return (
        <div className="min-h-screen w-full flex items-center justify-center bg-background p-4 animate-in fade-in duration-1000">
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute -top-40 -right-40 w-96 h-96 bg-primary/20 rounded-full blur-[100px]"></div>
                <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-indigo-500/20 rounded-full blur-[100px]"></div>
            </div>

            <div className="w-full max-w-md relative z-10">
                <div className="text-center mb-8">
                    <div className="w-16 h-16 bg-gradient-to-br from-primary to-indigo-600 rounded-2xl mx-auto flex items-center justify-center text-white shadow-xl shadow-primary/20 mb-4">
                        <Shield size={32} />
                    </div>
                    <h1 className="text-3xl font-bold tracking-tight">HelixRisk V3</h1>
                    <p className="text-muted-foreground mt-2">SDLC Recommendation System</p>
                </div>

                <Card className="shadow-2xl shadow-black/10">
                    <form onSubmit={handleLogin} className="space-y-6">
                        {error && (
                            <Alert variant="error">
                                <span>{error}</span>
                            </Alert>
                        )}

                        <div className="space-y-4">
                            <Input
                                label="Full Name"
                                placeholder="John Doe"
                                value={formData.fullName}
                                onChange={(e) => handleChange('fullName', e.target.value)}
                                className="w-full"
                            />

                            <Input
                                label="Work Email"
                                type="email"
                                placeholder="john@example.com"
                                value={formData.email}
                                onChange={(e) => handleChange('email', e.target.value)}
                                className="w-full"
                            />

                            <div className="space-y-1">
                                <label className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Password</label>
                                <div className="relative">
                                    <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                                    <input
                                        type="password"
                                        placeholder="••••••••"
                                        value={formData.password}
                                        onChange={(e) => handleChange('password', e.target.value)}
                                        className="w-full bg-accent/30 border border-border rounded-xl pl-10 pr-4 py-2.5 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all"
                                    />
                                </div>
                            </div>
                        </div>

                        <Button type="submit" className="w-full h-12 flex items-center justify-center gap-2">
                            <span>Secure Login</span>
                            <ArrowRight size={18} />
                        </Button>
                    </form>

                    <div className="mt-6 pt-6 border-t border-border text-center">
                        <p className="text-xs text-muted-foreground">
                            Secure environment. Authorized access only.
                        </p>
                    </div>
                </Card>
            </div>
        </div>
    );
};

export default Login;
