import React from 'react';

const Loader = ({ message = "Analyzing Project Details..." }) => (
    <div className="flex flex-col items-center justify-center p-12 space-y-6">
        <div className="relative w-24 h-24">
            <div className="absolute inset-0 border-4 border-primary/20 rounded-full"></div>
            <div className="absolute inset-0 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
            <div className="absolute inset-4 border-2 border-indigo-400 border-b-transparent rounded-full animate-spin-slow"></div>
        </div>
        <div className="text-center space-y-2">
            <h3 className="text-xl font-bold animate-pulse">{message}</h3>
            <p className="text-sm text-muted-foreground max-w-xs mx-auto">
                Please wait while our AI engine evaluates your project parameters against historical SDLC models.
            </p>
        </div>
    </div>
);

export default Loader;
