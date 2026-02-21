import React from 'react';
import { Sun, Moon, Bell, Search, User, Menu, FolderKanban } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import { useAnalysis } from '../context/AnalysisContext';

const Navbar = ({ activeTab, onMenuToggle, onOpenResults, onOpenHistory, modelHealth }) => {
    const { darkMode, toggleTheme } = useTheme();
    const { history, selectAnalysis, userProfile, setActiveProjectId, projects, activeProjectId } = useAnalysis();

    // UI State
    const [hasUnread, setHasUnread] = React.useState(true);
    const [searchTerm, setSearchTerm] = React.useState('');
    const [showSearchResults, setShowSearchResults] = React.useState(false);
    const [showProfileMenu, setShowProfileMenu] = React.useState(false);

    const activeProject = projects.find(p => p.id === activeProjectId);

    const filteredResults = history
        .filter((item) =>
            item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            item.model.toLowerCase().includes(searchTerm.toLowerCase())
        )
        .slice(0, 5);

    const openSearchResult = (id) => {
        const selected = selectAnalysis(id);
        if (selected) onOpenResults();
        setShowSearchResults(false);
        setSearchTerm('');
    };

    const handleSearchSubmit = (event) => {
        if (event.key !== 'Enter') return;
        event.preventDefault();
        if (filteredResults.length) {
            openSearchResult(filteredResults[0].id);
            return;
        }
        onOpenHistory();
    };

    const toggleNotifications = () => {
        setHasUnread(false);
        alert("No new notifications at this time.");
    };

    return (
        <header className="h-16 border-b border-border bg-background/80 backdrop-blur-md sticky top-0 z-10 px-4 md:px-8 flex items-center justify-between">
            <div className="flex items-center gap-4">
                <button
                    onClick={onMenuToggle}
                    className="p-2 -ml-2 rounded-lg hover:bg-accent md:hidden text-muted-foreground transition-all"
                >
                    <Menu size={20} />
                </button>
                <h2 className="text-lg font-semibold">{activeTab}</h2>
                <div className="h-4 w-[1px] bg-border mx-2 hidden md:block"></div>
                <div className="hidden md:flex items-center gap-2 text-sm text-muted-foreground">
                    <button
                        onClick={() => setActiveProjectId(null)}
                        className="hover:text-primary transition-colors flex items-center gap-1"
                    >
                        <FolderKanban size={14} />
                        <span>{activeProject?.name || 'Workspace'}</span>
                    </button>
                    <span className="opacity-50">/</span>
                    <span className="text-foreground font-medium">{activeTab}</span>
                </div>
                <div className="hidden md:flex items-center ml-2">
                    {modelHealth?.loading ? (
                        <span className="text-xs px-2 py-1 rounded-full bg-accent text-muted-foreground">Model Checking</span>
                    ) : modelHealth?.ml_model_loaded ? (
                        <span className="text-xs px-2 py-1 rounded-full bg-green-500/15 text-green-500">Model Ready</span>
                    ) : (
                        <span className="text-xs px-2 py-1 rounded-full bg-red-500/15 text-red-500">Model Error</span>
                    )}
                </div>
            </div>

            <div className="flex items-center gap-3 md:gap-4 relative">
                <div className="hidden lg:flex items-center bg-accent/50 rounded-full px-4 py-1.5 border border-border group focus-within:border-primary transition-all relative">
                    <Search size={16} className="text-muted-foreground group-focus-within:text-primary" />
                    <input
                        type="text"
                        placeholder="Search project analyses..."
                        className="bg-transparent border-none outline-none text-sm px-2 w-48"
                        value={searchTerm}
                        onChange={(e) => {
                            setSearchTerm(e.target.value);
                            setShowSearchResults(Boolean(e.target.value.trim()));
                        }}
                        onFocus={() => setShowSearchResults(Boolean(searchTerm.trim()))}
                        onBlur={() => setTimeout(() => setShowSearchResults(false), 150)}
                        onKeyDown={handleSearchSubmit}
                    />
                    {showSearchResults && (
                        <div className="absolute top-12 left-0 w-full rounded-xl border border-border bg-card shadow-xl p-2 z-20">
                            {filteredResults.length ? (
                                filteredResults.map((item) => (
                                    <button
                                        key={item.id}
                                        className="w-full text-left p-2 rounded-lg hover:bg-accent transition-all animate-in fade-in"
                                        onClick={() => openSearchResult(item.id)}
                                    >
                                        <p className="text-sm font-semibold truncate">{item.name}</p>
                                        <p className="text-xs text-muted-foreground">{item.model} • {item.date}</p>
                                    </button>
                                ))
                            ) : (
                                <button
                                    className="w-full text-left p-2 rounded-lg hover:bg-accent transition-all text-sm text-muted-foreground"
                                    onClick={onOpenHistory}
                                >
                                    No direct matches. Open History.
                                </button>
                            )}
                        </div>
                    )}
                </div>

                <div className="h-4 w-[1px] bg-border hidden lg:block mx-1"></div>

                <button
                    onClick={toggleTheme}
                    className="p-2 rounded-full hover:bg-accent text-muted-foreground hover:text-foreground transition-all"
                    title={darkMode ? "Switch to Light Mode" : "Switch to Dark Mode"}
                >
                    {darkMode ? <Sun size={20} /> : <Moon size={20} />}
                </button>

                <button
                    className="relative p-2 rounded-full hover:bg-accent text-muted-foreground hover:text-foreground transition-all"
                    onClick={toggleNotifications}
                    title="Notifications"
                >
                    <Bell size={20} />
                    {hasUnread && (
                        <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-primary rounded-full border-2 border-background animate-pulse"></span>
                    )}
                </button>

                <div className="h-8 w-[1px] bg-border mx-1"></div>

                <div className="relative pl-2">
                    <button
                        className="flex items-center gap-3 text-left focus:outline-none group"
                        onClick={() => setShowProfileMenu(prev => !prev)}
                        onBlur={() => setTimeout(() => setShowProfileMenu(false), 200)}
                    >
                        <div className="hidden sm:block">
                            <p className="text-sm font-semibold leading-none group-hover:text-primary transition-colors">{userProfile?.fullName || 'User'}</p>
                            <p className="text-[10px] text-muted-foreground uppercase tracking-wider mt-1 truncate max-w-[100px]">{userProfile?.organization || 'Workspace'}</p>
                        </div>
                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-indigo-600 flex items-center justify-center text-white border-2 border-background group-hover:border-primary/20 transition-all overflow-hidden">
                            <User size={20} />
                        </div>
                    </button>

                    {showProfileMenu && (
                        <div className="absolute top-12 right-0 w-48 rounded-xl border border-border bg-card shadow-xl p-2 z-20 animate-in fade-in slide-in-from-top-2">
                            <button
                                className="w-full text-left p-2 text-sm text-muted-foreground rounded-lg hover:bg-accent hover:text-primary transition-all flex items-center gap-2"
                                onClick={() => setActiveProjectId(null)}
                            >
                                <FolderKanban size={16} /> Switch Project
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </header>
    );
};

export default Navbar;
