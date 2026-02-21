import React from 'react';

export const Table = ({ headers, children, className = '' }) => (
    <div className={`overflow-x-auto ${className}`}>
        <table className="w-full text-left">
            <thead>
                <tr className="border-b border-border text-xs font-bold uppercase tracking-widest text-muted-foreground">
                    {headers.map((header, i) => (
                        <th key={i} className="pb-4 pt-2">{header}</th>
                    ))}
                </tr>
            </thead>
            <tbody className="divide-y divide-border/50">
                {children}
            </tbody>
        </table>
    </div>
);

export const TableRow = ({ children, onClick, className = '' }) => (
    <tr
        onClick={onClick}
        className={`group hover:bg-accent/20 transition-all cursor-pointer ${className}`}
    >
        {children}
    </tr>
);

export const TableCell = ({ children, className = '' }) => (
    <td className={`py-4 text-sm ${className}`}>
        {children}
    </td>
);
