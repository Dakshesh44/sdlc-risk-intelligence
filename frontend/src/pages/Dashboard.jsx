import React from 'react';
import { Card, Button } from '../components/UI';
import {
    Rocket,
    TrendingUp,
    Activity,
    Layers,
    CalendarDays
} from 'lucide-react';
import { ChartContainer, CustomTooltip } from '../components/Chart';
import { Table, TableRow, TableCell } from '../components/Table';
import { AreaChart, Area, XAxis, YAxis, Tooltip } from 'recharts';
import { useAnalysis } from '../context/AnalysisContext';

const ranges = {
    week: 7,
    month: 30,
    all: null
};

const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

const Dashboard = ({ onOpenResults }) => {
    const { history, selectAnalysis } = useAnalysis();
    const [range, setRange] = React.useState('month');

    const now = new Date();
    const daysWindow = ranges[range];
    const filteredHistory = history.filter((item) => {
        if (!daysWindow) return true;
        const itemDate = new Date(`${item.date}T00:00:00`);
        if (Number.isNaN(itemDate.getTime())) return false;
        const cutoff = new Date(now);
        cutoff.setDate(cutoff.getDate() - daysWindow);
        return itemDate >= cutoff;
    });

    const totalConfidence = filteredHistory.reduce((sum, item) => sum + (Number(item.confidence) || 0), 0);
    const avgConfidence = filteredHistory.length ? Math.round(totalConfidence / filteredHistory.length) : 0;
    const modelCount = new Set(filteredHistory.map((item) => item.model)).size;
    const projectCount = new Set(filteredHistory.map((item) => item.name)).size;

    const stats = [
        { label: 'Total Analyses', value: filteredHistory.length.toString(), icon: <Rocket size={18} />, color: 'bg-primary' },
        { label: 'Avg Confidence', value: `${avgConfidence}%`, icon: <TrendingUp size={18} />, color: 'bg-green-500' },
        { label: 'Active Projects', value: projectCount.toString(), icon: <Activity size={18} />, color: 'bg-indigo-500' },
        { label: 'Models Used', value: modelCount.toString(), icon: <Layers size={18} />, color: 'bg-amber-500' },
    ];

    const activityMap = dayNames.reduce((acc, day) => ({ ...acc, [day]: 0 }), {});
    filteredHistory.forEach((item) => {
        const date = new Date(`${item.date}T00:00:00`);
        if (!Number.isNaN(date.getTime())) {
            activityMap[dayNames[date.getDay()]] += 1;
        }
    });
    const activityData = dayNames.map((day) => ({ name: day, count: activityMap[day] }));

    const modelFrequency = filteredHistory.reduce((acc, item) => {
        acc[item.model] = (acc[item.model] || 0) + 1;
        return acc;
    }, {});
    const sortedModels = Object.entries(modelFrequency).sort((a, b) => b[1] - a[1]);
    const topModel = sortedModels[0];

    const handleExport = () => {
        const payload = {
            exportedAt: new Date().toISOString(),
            filter: range,
            records: filteredHistory,
        };
        const dataStr = `data:text/json;charset=utf-8,${encodeURIComponent(JSON.stringify(payload, null, 2))}`;
        const link = document.createElement('a');
        link.setAttribute('href', dataStr);
        link.setAttribute('download', `sdlc-analysis-export-${range}.json`);
        document.body.appendChild(link);
        link.click();
        link.remove();
    };

    const openResult = (id) => {
        const selected = selectAnalysis(id);
        if (selected) onOpenResults();
    };

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">System Overview</h2>
                    <p className="text-muted-foreground mt-1">Welcome back. Here is what's happening with your SDLC analyses.</p>
                </div>
                <div className="flex gap-2">
                    <Button
                        variant="outline"
                        className="text-xs h-9 flex items-center gap-2"
                        onClick={() => setRange((prev) => prev === 'month' ? 'week' : prev === 'week' ? 'all' : 'month')}
                    >
                        <CalendarDays size={14} />
                        {range === 'month' ? 'Last 30 Days' : range === 'week' ? 'Last 7 Days' : 'All Time'}
                    </Button>
                    <Button variant="outline" className="text-xs h-9" onClick={handleExport} disabled={!filteredHistory.length}>
                        Export Data
                    </Button>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {stats.map((stat, i) => (
                    <Card key={i} className="relative overflow-hidden group">
                        <div className="flex items-center gap-4">
                            <div className={`w-12 h-12 rounded-2xl ${stat.color} text-white flex items-center justify-center shadow-lg shadow-black/10 transition-transform group-hover:scale-110`}>
                                {stat.icon}
                            </div>
                            <div>
                                <p className="text-xs font-bold uppercase tracking-widest text-muted-foreground">{stat.label}</p>
                                <p className="text-2xl font-bold">{stat.value}</p>
                            </div>
                        </div>
                        <div className="mt-4 flex items-center gap-1 text-[10px] font-bold text-green-500 uppercase tracking-tighter">
                            <span>{filteredHistory.length ? 'Based on current analysis history' : 'No analyses yet'}</span>
                        </div>
                    </Card>
                ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <Card title="Analysis Activity" subtitle="Daily volume of recommendations generated" className="lg:col-span-2">
                    <ChartContainer height={300}>
                        <AreaChart data={activityData}>
                            <defs>
                                <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#4F46E5" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#4F46E5" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#888', fontSize: 12 }} dy={10} />
                            <YAxis hide />
                            <Tooltip content={<CustomTooltip />} />
                            <Area
                                type="monotone"
                                dataKey="count"
                                stroke="#4F46E5"
                                strokeWidth={3}
                                fillOpacity={1}
                                fill="url(#colorCount)"
                                animationBegin={500}
                                animationDuration={1500}
                            />
                        </AreaChart>
                    </ChartContainer>
                </Card>

                <Card title="Recent Insights" subtitle="Derived from your project history">
                    <div className="space-y-6">
                        <div className="flex gap-4 p-4 rounded-xl bg-accent/30 border border-border group hover:border-primary/50 transition-all cursor-pointer">
                            <div className="w-10 h-10 rounded-lg bg-indigo-500/10 text-indigo-500 flex items-center justify-center flex-shrink-0">
                                <Rocket size={20} />
                            </div>
                            <div>
                                <h4 className="font-bold text-sm">Top Recommended Model</h4>
                                <p className="text-xs text-muted-foreground mt-1 leading-relaxed">
                                    {topModel ? `${topModel[0]} appears most often (${topModel[1]} recommendations).` : 'Create your first analysis to unlock trend insights.'}
                                </p>
                            </div>
                        </div>
                        <div className="flex gap-4 p-4 rounded-xl bg-accent/30 border border-border group hover:border-amber-500/50 transition-all cursor-pointer">
                            <div className="w-10 h-10 rounded-lg bg-amber-500/10 text-amber-500 flex items-center justify-center flex-shrink-0">
                                <TrendingUp size={20} />
                            </div>
                            <div>
                                <h4 className="font-bold text-sm">Confidence Trend</h4>
                                <p className="text-xs text-muted-foreground mt-1 leading-relaxed">
                                    {filteredHistory.length ? `Average confidence in this range is ${avgConfidence}%.` : 'Confidence analytics will appear after running analyses.'}
                                </p>
                            </div>
                        </div>
                    </div>
                </Card>

                <Card title="Latest Analyses" subtitle="Track your most recent project evaluations" className="lg:col-span-3">
                    <Table headers={['Project Name', 'Model', 'Confidence', 'Date', '']}>
                        {filteredHistory.slice(0, 3).map((item, i) => (
                            <TableRow key={i}>
                                <TableCell className="font-medium">{item.name}</TableCell>
                                <TableCell className="text-primary">{item.model}</TableCell>
                                <TableCell className="font-mono text-green-500">{item.confidence}%</TableCell>
                                <TableCell className="text-muted-foreground">{item.date}</TableCell>
                                <TableCell className="text-right">
                                    <Button variant="ghost" className="h-8 px-3 text-xs" onClick={() => openResult(item.id)}>
                                        View Result
                                    </Button>
                                </TableCell>
                            </TableRow>
                        ))}
                        {!filteredHistory.length && (
                            <TableRow>
                                <TableCell className="text-center py-10 text-muted-foreground" colSpan={5}>
                                    No analyses available for the selected date range.
                                </TableCell>
                            </TableRow>
                        )}
                    </Table>
                </Card>
            </div>
        </div>
    );
};

export default Dashboard;
