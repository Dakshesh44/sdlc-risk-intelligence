import React from 'react';
import {
    Home,
    PlusCircle,
    BarChart2,
    History,
    Settings,
    Cpu,
    ChevronRight,
    X
} from 'lucide-react';

const Sidebar = ({ activeTab, setActiveTab, isOpen, onClose }) => {
    const menuItems = [
        { name: 'Home', icon: <Home size={20} /> },
        { name: 'New Analysis', icon: <PlusCircle size={20} /> },
        { name: 'Results Dashboard', icon: <BarChart2 size={20} /> },
        { name: 'History', icon: <History size={20} /> },
        { name: 'Settings', icon: <Settings size={20} /> },
    ];

    return (
        <>
            {/* Mobile Backdrop */}
            {isOpen && (
                <div
                    className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 md:hidden"
                    onClick={onClose}
                ></div>
            )}

            {/* Sidebar Content */}
            <div className={`
        fixed md:static inset-y-0 left-0 w-64 bg-card border-r border-border flex flex-col z-50 transition-transform duration-300 transform
        ${isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
      `}>
                <div className="p-6 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center text-white shadow-lg shadow-primary/30">
                            <Cpu size={24} />
                        </div>
                        <div>
                            <h1 className="text-xl font-bold tracking-tight">FlowPilot</h1>
                            <p className="text-[10px] uppercase tracking-widest text-muted-foreground font-semibold opacity-60">SDLC Engine</p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 -mr-2 rounded-lg hover:bg-accent md:hidden text-muted-foreground transition-all"
                    >
                        <X size={20} />
                    </button>
                </div>

                <nav className="flex-1 px-4 py-6 space-y-2">
                    {menuItems.map((item) => (
                        <button
                            key={item.name}
                            onClick={() => setActiveTab(item.name)}
                            className={`w-full flex items-center justify-between px-4 py-3 rounded-lg transition-all duration-200 group ${activeTab === item.name
                                ? 'bg-primary text-white shadow-md shadow-primary/20'
                                : 'text-muted-foreground hover:bg-accent hover:text-foreground'
                                }`}
                        >
                            <div className="flex items-center gap-3">
                                <span className={`${activeTab === item.name ? 'text-white' : 'text-primary'}`}>
                                    {item.icon}
                                </span>
                                <span className="font-medium">{item.name}</span>
                            </div>
                            {activeTab === item.name && (
                                <ChevronRight size={16} className="text-white/70" />
                            )}
                        </button>
                    ))}
                </nav>

                <div className="p-4 mt-auto">
                    <div className="p-4 rounded-xl bg-accent/50 border border-border flex flex-col gap-2">
                        <button
                            className="text-xs text-primary font-bold hover:underline text-left"
                            onClick={() => window.open('mailto:support@flowpilot.ai', '_blank')}
                        >
                            Support Center
                        </button>
                    </div>
                </div>
            </div>
        </>
    );
};

export default Sidebar;
