import React from 'react';
import { useState, useEffect } from 'react';
import { useLocation, Link } from 'react-router-dom';
import { resetData, synchData } from '../fonction/deviceFonction';
import { getListeFiliale } from '../fonction/filialeFonction';
import {
    Building2,
    Laptop,
    Printer,
    BarChart3,
    Bell,
    TrendingUp,
    GitCompare,
    Settings,
    Activity
} from 'lucide-react';

export default function Sidebar() {
    const location = useLocation();
    const [filiale, setFiliale] = useState([])
    const menuItems = [
        { path: '/filiale', label: 'Filiales', icon: Building2 },
        { path: '/liste/device', label: 'Tous les Devices', icon: Laptop },
        { path: '/imprimantes', label: 'Imprimantes', icon: Printer },
        { path: '/dashboard', label: 'Dashboard', icon: BarChart3 },
        { path: '/alerts', label: 'Alertes', icon: Bell },
        { path: '/statistiques', label: 'Statistiques', icon: TrendingUp },
        { path: '/comparaison', label: 'Comparaison', icon: GitCompare },
        { path: '/configuration', label: 'Configuration', icon: Settings },
    ];
    const synch = async () => {
        try {
            await synchData();
        } catch (e) {
            console.log(e);
        }
    };

    const resetAll = async () => {
        try {
            await resetData();
        } catch (e) {
            console.log(e)
        }
    }

    return (
        <aside className="sidebar-container glass-panel">
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

            <button onClick={synch}>Synchroniser données</button>
            <button onClick={resetAll}>Reinitialiser données</button>

            <div className="p-4 border-t border-white/5 flex justify-center lg:justify-start items-center gap-3 bg-zinc-900/40">
                <div className="relative flex items-center justify-center">
                    <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.8)]"></div>
                    <div className="absolute w-4 h-4 rounded-full bg-emerald-500/30 animate-ping"></div>
                </div>
                <span className="hidden lg:block text-xs font-semibold tracking-wider text-zinc-400 uppercase">
                    Systeme de suivi
                </span>
            </div>
        </aside>
    );
}

