import React, { useState } from 'react';
import { useLocation, Link } from 'react-router-dom';
import { resetData, synchData } from '../fonction/deviceFonction';
import {
Building2,
    Laptop,
    Printer,
    BarChart3,
    Bell,
    TrendingUp,
    GitCompare,
    Settings,
    Activity,
    RefreshCw,
    RotateCcw
} from 'lucide-react';

export default function Sidebar() {
    const location = useLocation();
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');

    const menuItems = [
        { path: '/filiale', label: 'Filiales', icon: Building2 },
        { path: '/liste/device', label: 'Tous les Devices', icon: Laptop },
        { path: '/imprimantes', label: 'Imprimantes', icon: Printer },
        { path: '/liste/event', label: 'Liste evenements', icon: Bell },
        { path: '/dashboard', label: 'Dashboard', icon: BarChart3 },
        // { path: '/dashboard', label: 'Alertes', icon: Bell },
        // { path: '/dashboard', label: 'Statistiques', icon: TrendingUp },
        // { path: '/dashboard', label: 'Comparaison', icon: GitCompare },
        // { path: '/dashboard', label: 'Configuration', icon: Settings },
    ];

    const synch = async () => {
        try {
            setLoading(true);
            setMessage("Synchronisation des données en cours...");
            await synchData();
            window.location.reload();
        } catch (e) {
            console.log(e);
        } finally {
            setLoading(false);
            setMessage("");
        }
    };

    const resetAll = async () => {
        if (!window.confirm("Êtes-vous sûr de vouloir réinitialiser toutes les données ?")) return;
        try {
            setLoading(true);
            setMessage("Réinitialisation des données en cours...");
            await resetData();
            window.location.reload();
        } catch (e) {
            console.log(e);
        } finally {
            setLoading(false);
            setMessage("");
        }
    };

    return (
        <>
            <aside className="sidebar-container glass-panel flex flex-col justify-between">
                <div>
                    <div className="sidebar-header">
                        <div className="p-2 bg-cyan-500/10 border border-cyan-500/30 rounded-xl flex items-center justify-center shadow-[0_0_12px_rgba(6,182,212,0.25)]">
                            <Activity className="w-5 h-5 text-cyan-400 animate-pulse" />
                        </div>
                        <span className="sidebar-title hidden lg:block bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent font-extrabold tracking-wider">
                            GT
                        </span>
                    </div>

                    <nav className="mt-6 flex flex-col gap-1.5 px-2 lg:px-3">
                        {menuItems.map((item) => {
                            const Icon = item.icon;
                            const isActive = location.pathname === item.path
                                || (item.path === '/filiale' && location.pathname.startsWith('/filiale'));

                            return (
                                <Link
                                    key={item.path}
                                    to={item.path}
                                    className={isActive ? "nav-link-active" : "nav-link"}
                                >
                                    <Icon className={`w-5 h-5 flex-shrink-0 ${isActive ? 'text-cyan-400' : 'text-zinc-400'}`} />
                                    <span className="hidden lg:block font-medium text-sm tracking-wide">
                                        {item.label}
                                    </span>
                                </Link>
                            );
                        })}
                    </nav>
                </div>

                <div className="p-3 border-t border-white/5 space-y-2">
                    <button
                        onClick={synch}
                        disabled={loading}
                        className="w-full px-3 py-2 text-xs font-semibold text-cyan-400 bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 hover:border-cyan-500/50 rounded-xl transition-all flex items-center justify-center lg:justify-start gap-2 cursor-pointer disabled:opacity-50"
                        title="Synchroniser données"
                    >
                        <RefreshCw className={`w-4 h-4 text-cyan-400 ${loading ? 'animate-spin' : ''}`} />
                        <span className="hidden lg:block truncate">Synchroniser données</span>
                    </button>

                    <button
                        onClick={resetAll}
                        disabled={loading}
                        className="w-full px-3 py-2 text-xs font-semibold text-red-400 bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 hover:border-red-500/50 rounded-xl transition-all flex items-center justify-center lg:justify-start gap-2 cursor-pointer disabled:opacity-50"
                        title="Réinitialiser données"
                    >
                        <RotateCcw className="w-4 h-4 text-red-400" />
                        <span className="hidden lg:block truncate">Réinitialiser données</span>
                    </button>

                    <div className="pt-2 flex justify-center lg:justify-start items-center gap-3">
                        <div className="relative flex items-center justify-center">
                            <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.8)]"></div>
                            <div className="absolute w-4 h-4 rounded-full bg-emerald-500/30 animate-ping"></div>
                        </div>
                        <span className="hidden lg:block text-[10px] font-semibold tracking-wider text-zinc-400 uppercase">
                            Système de suivi
                        </span>
                    </div>
                </div>
            </aside>

            {/* Animation de chargement et de progression sur l'écran lors de la synch ou du reset */}
            {loading && (
                <div className="fixed inset-0 bg-black/80 backdrop-blur-md flex flex-col items-center justify-center z-50 animate-fadeIn">
                    <div className="p-8 bg-zinc-900/90 border border-cyan-500/40 rounded-2xl shadow-[0_0_50px_rgba(6,182,212,0.3)] flex flex-col items-center max-w-sm text-center">
                        <div className="relative mb-6">
                            <div className="w-16 h-16 rounded-full border-4 border-cyan-500/20 border-t-cyan-400 animate-spin"></div>
                            <RefreshCw className="w-6 h-6 text-cyan-400 absolute inset-0 m-auto animate-pulse" />
                        </div>
                        <h3 className="text-lg font-bold text-zinc-100 mb-2">{message}</h3>
                        <p className="text-xs text-zinc-400 mb-4">Veuillez patienter pendant le traitement...</p>

                        <div className="w-full bg-zinc-800 rounded-full h-2.5 overflow-hidden border border-white/10 relative">
                            <div className="progress-bar-animated"></div>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}
