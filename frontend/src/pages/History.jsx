import React, { useEffect, useState } from 'react';
import { Card, Input, Button } from '../components/UI';
import { Table, TableRow, TableCell } from '../components/Table';
import { Search, Filter, MoreHorizontal, Calendar, ArrowRight } from 'lucide-react';
import { useAnalysis } from '../context/AnalysisContext';

const PAGE_SIZE = 8;

const History = ({ onOpenResults }) => {
    const { history, selectAnalysis, deleteAnalysis, clearAllHistory } = useAnalysis();
    const [searchTerm, setSearchTerm] = useState('');
    const [sortBy, setSortBy] = useState('date');
    const [dateRange, setDateRange] = useState('all');
    const [page, setPage] = useState(1);

    useEffect(() => {
        setPage(1);
    }, [searchTerm, sortBy, dateRange, history.length]);

    const isInRange = (date) => {
        if (dateRange === 'all') return true;
        const days = Number(dateRange);
        const base = new Date();
        base.setDate(base.getDate() - days);
        return new Date(`${date}T00:00:00`) >= base;
    };

    const filteredHistory = history
        .filter(item =>
            (item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                item.model.toLowerCase().includes(searchTerm.toLowerCase())) &&
            isInRange(item.date)
        )
        .sort((a, b) => {
            if (sortBy === 'confidence') return (b.confidence || 0) - (a.confidence || 0);
            return new Date(`${b.date}T00:00:00`) - new Date(`${a.date}T00:00:00`);
        });

    const totalPages = Math.max(1, Math.ceil(filteredHistory.length / PAGE_SIZE));
    const currentPage = Math.min(page, totalPages);
    const pageItems = filteredHistory.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE);

    const handleOpen = (id) => {
        const selected = selectAnalysis(id);
        if (selected) onOpenResults();
    };

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div>
                <h2 className="text-3xl font-bold tracking-tight">Analysis History</h2>
                <p className="text-muted-foreground mt-1">Review and compare past SDLC recommendations.</p>
            </div>

            <Card>
                <div className="flex flex-col md:flex-row gap-4 mb-6">
                    <div className="relative flex-1">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={18} />
                        <input
                            type="text"
                            placeholder="Filter by project name or model..."
                            className="w-full bg-accent/30 border border-border rounded-xl pl-10 pr-4 py-2.5 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                    <div className="flex gap-2">
                        <Button
                            variant="outline"
                            className="flex items-center gap-2"
                            onClick={() => setSortBy(prev => prev === 'date' ? 'confidence' : 'date')}
                        >
                            <Filter size={16} />
                            <span>{sortBy === 'date' ? 'Sort: Date' : 'Sort: Confidence'}</span>
                        </Button>
                        <Button
                            variant="outline"
                            className="flex items-center gap-2"
                            onClick={() => setDateRange(prev => prev === 'all' ? '30' : prev === '30' ? '7' : 'all')}
                        >
                            <Calendar size={16} />
                            <span>{dateRange === 'all' ? 'All Dates' : `Last ${dateRange} Days`}</span>
                        </Button>
                        <Button
                            variant="outline"
                            className="flex items-center gap-2"
                            disabled={!history.length}
                            onClick={clearAllHistory}
                        >
                            <span>Clear All</span>
                        </Button>
                    </div>
                </div>

                <Table headers={['Project Details', 'Recommended Model', 'Confidence', 'Analysis Date', 'Status', '']}>
                    {pageItems.map((item) => (
                        <TableRow key={item.id}>
                            <TableCell>
                                <div className="flex flex-col">
                                    <span className="font-bold text-sm">{item.name}</span>
                                    <span className="text-[10px] text-muted-foreground">ID: {item.id.slice(0, 8).toUpperCase()}</span>
                                </div>
                            </TableCell>
                            <TableCell>
                                <span className="text-sm font-semibold">{item.model}</span>
                            </TableCell>
                            <TableCell>
                                <div className="flex items-center gap-2 min-w-[120px]">
                                    <div className="flex-1 h-2 bg-accent rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-primary"
                                            style={{ width: `${item.confidence}%` }}
                                        ></div>
                                    </div>
                                    <span className="text-xs font-mono font-bold w-8 text-right">{item.confidence}%</span>
                                </div>
                            </TableCell>
                            <TableCell className="font-medium text-muted-foreground">{item.date}</TableCell>
                            <TableCell>
                                <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-widest ${item.status === 'Completed' ? 'bg-green-500/10 text-green-500' : 'bg-amber-500/10 text-amber-500'
                                    }`}>
                                    {item.status}
                                </span>
                            </TableCell>
                            <TableCell className="text-right">
                                <div className="flex justify-end gap-2 opacity-0 group-hover:opacity-100 transition-all">
                                    <Button
                                        variant="outline"
                                        className="h-8 w-8 p-0 flex items-center justify-center"
                                        onClick={() => handleOpen(item.id)}
                                    >
                                        <ArrowRight size={14} />
                                    </Button>
                                    <Button
                                        variant="ghost"
                                        className="h-8 w-8 p-0 flex items-center justify-center"
                                        onClick={() => deleteAnalysis(item.id)}
                                    >
                                        <MoreHorizontal size={14} />
                                    </Button>
                                </div>
                            </TableCell>
                        </TableRow>
                    ))}
                    {filteredHistory.length === 0 && (
                        <TableRow>
                            <TableCell className="text-center py-10 text-muted-foreground" colSpan={6}>
                                No analysis records found matching your search.
                            </TableCell>
                        </TableRow>
                    )}
                </Table>

                <div className="mt-8 flex items-center justify-between border-t border-border pt-6">
                    <p className="text-sm text-muted-foreground">Showing {pageItems.length} of {filteredHistory.length} analyses</p>
                    <div className="flex gap-2">
                        <Button
                            variant="outline"
                            className="px-4 py-1.5 text-xs"
                            disabled={currentPage <= 1}
                            onClick={() => setPage(prev => Math.max(1, prev - 1))}
                        >
                            Previous
                        </Button>
                        <Button
                            variant="outline"
                            className="px-4 py-1.5 text-xs"
                            disabled={currentPage >= totalPages}
                            onClick={() => setPage(prev => Math.min(totalPages, prev + 1))}
                        >
                            Next
                        </Button>
                    </div>
                </div>
            </Card>
        </div>
    );
};

export default History;
