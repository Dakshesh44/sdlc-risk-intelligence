import React from 'react';
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell,
    LineChart,
    Line,
    AreaChart,
    Area
} from 'recharts';

export const ChartContainer = ({ children, height = 300 }) => (
    <div style={{ width: '100%', height }}>
        <ResponsiveContainer>
            {children}
        </ResponsiveContainer>
    </div>
);

export const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
        return (
            <div className="bg-card/95 backdrop-blur-sm border border-border p-3 rounded-lg shadow-xl shadow-black/20">
                <p className="text-xs font-bold uppercase tracking-wider text-muted-foreground mb-1">{label}</p>
                {payload.map((entry, index) => (
                    <div key={index} className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }}></div>
                        <p className="text-sm font-semibold">
                            <span className="opacity-70">{entry.name}:</span> {entry.value}%
                        </p>
                    </div>
                ))}
            </div>
        );
    }
    return null;
};
