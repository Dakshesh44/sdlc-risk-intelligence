import React from 'react';

export const Card = ({ children, className = '', title, subtitle }) => (
    <div className={`bg-card/60 backdrop-blur-2xl border border-white/10 rounded-3xl p-8 shadow-[0_8px_30px_rgb(0,0,0,0.04)] dark:shadow-[0_8px_30px_rgb(0,0,0,0.1)] transition-all duration-500 ease-out hover:-translate-y-1 hover:shadow-primary/10 ${className}`}>
        {(title || subtitle) && (
            <div className="mb-6">
                {title && <h3 className="text-lg font-bold tracking-tight">{title}</h3>}
                {subtitle && <p className="text-sm text-muted-foreground">{subtitle}</p>}
            </div>
        )}
        {children}
    </div>
);

export const Alert = ({ children, variant = 'error', className = '' }) => {
    const variants = {
        error: 'bg-red-500/10 border-red-500/20 text-red-500',
        info: 'bg-primary/10 border-primary/20 text-primary',
        success: 'bg-green-500/10 border-green-500/20 text-green-500',
    };

    return (
        <div className={`p-4 rounded-xl border text-sm font-medium flex items-center gap-3 animate-in fade-in slide-in-from-top-2 min-h-[50px] ${variants[variant]} ${className}`}>
            {children}
        </div>
    );
};

export const Button = ({ children, variant = 'primary', className = '', ...props }) => {
    const variants = {
        primary: 'bg-primary text-white hover:bg-primary/90 shadow-lg shadow-primary/20',
        secondary: 'bg-accent text-foreground hover:bg-accent/80',
        outline: 'bg-transparent border border-border text-foreground hover:bg-accent',
        ghost: 'bg-transparent text-muted-foreground hover:text-foreground hover:bg-accent',
    };

    return (
        <button
            className={`px-5 py-3 rounded-2xl font-bold text-sm transition-all duration-300 ease-out active:scale-95 disabled:opacity-50 disabled:pointer-events-none ${variants[variant]} ${className}`}
            {...props}
        >
            {children}
        </button>
    );
};

export const Input = ({ label, error, className = '', ...props }) => (
    <div className={`space-y-2 ${className} group`}>
        {label && <label className="text-xs font-bold tracking-wider uppercase opacity-70 ml-1 group-focus-within:text-primary group-focus-within:opacity-100 transition-colors duration-300">{label}</label>}
        <div className="relative">
            <input
                className="w-full bg-black/20 backdrop-blur-xl border border-white/10 rounded-2xl px-5 py-3.5 text-sm focus:ring-4 focus:ring-primary/20 focus:border-primary outline-none transition-all duration-300 placeholder:text-muted-foreground/50 hover:bg-black/40 hover:border-white/20 shadow-inner peer"
                {...props}
            />
        </div>
        {error && <p className="text-xs text-red-500 font-medium">{error}</p>}
    </div>
);

export const Textarea = ({ label, error, className = '', ...props }) => (
    <div className={`space-y-2 ${className} group`}>
        {label && <label className="text-xs font-bold tracking-wider uppercase opacity-70 ml-1 group-focus-within:text-primary group-focus-within:opacity-100 transition-colors duration-300">{label}</label>}
        <div className="relative">
            <textarea
                className="w-full bg-black/20 backdrop-blur-xl border border-white/10 rounded-2xl px-5 py-3.5 text-sm focus:ring-4 focus:ring-primary/20 focus:border-primary outline-none transition-all duration-300 min-h-[120px] resize-y placeholder:text-muted-foreground/50 hover:bg-black/40 hover:border-white/20 shadow-inner peer"
                {...props}
            />
        </div>
        {error && <p className="text-xs text-red-500 font-medium">{error}</p>}
    </div>
);

export const Slider = ({ label, value, min = 0, max = 1, step = 0.1, onChange, error, className = '' }) => (
    <div className={`space-y-3 ${className}`}>
        <div className="flex justify-between items-center">
            {label && <label className="text-sm font-semibold tracking-wide uppercase opacity-70">{label}</label>}
            <span className="text-xs font-mono bg-primary/10 text-primary px-2 py-0.5 rounded-md border border-primary/20">
                {value}
            </span>
        </div>
        <input
            type="range"
            min={min}
            max={max}
            step={step}
            value={value}
            onChange={onChange}
            className="w-full h-2 bg-accent rounded-lg appearance-none cursor-pointer accent-primary"
        />
        {error && <p className="text-xs text-red-500 font-medium">{error}</p>}
    </div>
);

export const Dropdown = ({ label, options, value, onChange, error, className = '' }) => (
    <div className={`space-y-2 ${className}`}>
        {label && <label className="text-sm font-semibold tracking-wide uppercase opacity-70">{label}</label>}
        <select
            value={value}
            onChange={onChange}
            className="w-full bg-accent/30 border border-border rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all appearance-none cursor-pointer"
        >
            {options.map((opt) => (
                <option key={opt.value} value={opt.value} className="bg-card">
                    {opt.label}
                </option>
            ))}
        </select>
        {error && <p className="text-xs text-red-500 font-medium">{error}</p>}
    </div>
);

export const FactorSlider = ({ label, value, onChange, error, className = '' }) => {
    const marks = { 1: 'Very Low', 2: 'Low', 3: 'Medium', 4: 'High', 5: 'Very High' };
    return (
        <div className={`space-y-4 ${className}`}>
            <div className="flex justify-between items-end gap-4">
                {label && <label className="text-xs font-bold tracking-wider uppercase opacity-70 ml-1 leading-snug">{label}</label>}
                <span className="text-xs font-mono font-bold bg-primary/10 text-primary px-3 py-1 rounded-xl border border-primary/20 whitespace-nowrap">
                    {value} - {marks[value] || ''}
                </span>
            </div>
            <input
                type="range"
                min="1"
                max="5"
                step="1"
                value={value}
                onChange={onChange}
                className="w-full h-2 bg-accent rounded-lg appearance-none cursor-pointer accent-primary"
            />
            <div className="flex justify-between text-[10px] text-muted-foreground px-1">
                <span>1</span>
                <span>2</span>
                <span>3</span>
                <span>4</span>
                <span>5</span>
            </div>
            {error && <p className="text-xs text-red-500 font-medium">{error}</p>}
        </div>
    );
};

export const SegmentedControl = ({ label, options, value, onChange, error, className = '' }) => (
    <div className={`space-y-4 ${className}`}>
        {label && <label className="text-xs font-bold tracking-wider uppercase opacity-70 ml-1">{label}</label>}
        <div className="flex bg-accent/30 backdrop-blur-xl p-1.5 rounded-2xl border border-border/40 shadow-inner">
            {options.map((opt) => (
                <button
                    key={opt.value}
                    type="button"
                    onClick={() => onChange(opt.value)}
                    className={`flex-1 py-2 text-sm font-bold rounded-[14px] transition-all duration-300 ease-out ${value === opt.value
                        ? 'bg-primary text-white shadow-md scale-[1.02]'
                        : 'text-muted-foreground hover:text-foreground hover:bg-black/5 dark:hover:bg-white/5'
                        }`}
                >
                    {opt.label}
                </button>
            ))}
        </div>
        {error && <p className="text-xs text-red-500 font-medium">{error}</p>}
    </div>
);
