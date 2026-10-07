import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Server, Laptop, Bell, Printer, Zap, Cpu, Monitor } from 'lucide-react';
import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";
import MouseSpotlight from "../components/MouseSpotlight";
import { getDashboardStats, getStatusStyle } from "../fonction/deviceFonction";
import { getListeEvenement } from "../fonction/eventFonction";
import { getListeImprimante } from "../fonction/imprimanteFonction";
import '../css/liste.css';
import '../css/filiale.css';

function Dashboard() {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [stats, setStats] = useState({
        total: 0,
        par_statut: {},
        par_type: {}
    });
    
    // Nouveaux states pour événements et imprimantes
    const [eventsData, setEventsData] = useState([]);
    const [printersData, setPrintersData] = useState([]);

    const fetchData = async () => {
        try {
            setLoading(true);
            const [dataStats, evData, printData] = await Promise.all([
                getDashboardStats(),
                getListeEvenement(),
                getListeImprimante()
            ]);
            
            if (dataStats) setStats(dataStats);
            if (evData) setEventsData(evData);
            if (printData) setPrintersData(printData);
            
        } catch (e) {
            console.log(e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    // Calculs événements
    const totalEvents = eventsData.length;
    const kernelEvents = eventsData.filter(e => {
        const t = (e.type_evenement || "").toUpperCase();
        return t.includes("KERNEL");
    }).length;
    const ecEvents = eventsData.filter(e => {
        const t = (e.type_evenement || "").toUpperCase();
        return t.includes("EMBEDDED") || t.includes("CONTROLLER") || t.includes("EC");
    }).length;
    const appEvents = eventsData.filter(e => {
        const t = (e.type_evenement || "").toUpperCase();
        return t.includes("BROWSER") || t.includes("APP");
    }).length;
    const otherEvents = totalEvents - kernelEvents - ecEvents - appEvents;
    
    // Calcul imprimantes
    const totalPrinters = printersData.length;


    return (
        <div className="device-layout" data-theme="dark">
            <MouseSpotlight />
            <Sidebar />

            <div className="flex-1 flex flex-col h-screen overflow-hidden relative z-10">
                <div className="bg-glow-cyan"></div>
                <div className="bg-glow-purple"></div>
                <Navbar />

                <div className="flex-1 overflow-y-auto p-6 lg:p-8 space-y-8 z-10">
                    <div className="flex justify-between items-end">
                        <div>
                            <h1 className="text-3xl font-bold tracking-tight text-zinc-100 flex items-center gap-3">
                                <Server className="w-8 h-8 text-cyan-400" />
                                Tableau de Bord
                            </h1>
                            <p className="text-zinc-400 mt-2 font-medium tracking-wide">
                                Vue d'ensemble du parc informatique
                            </p>
                        </div>
                    </div>

                    {loading ? (
                        <div className="flex justify-center p-12">
                            <span className="loading loading-infinity loading-lg text-cyan-500"></span>
                        </div>
                    ) : (
                        <div className="space-y-8">
                            
                            {/* Section Appareils */}
                            <div>
                                <div className="section-header">
                                    <h2 className="section-title">État des Appareils</h2>
                                </div>
                                <div 
                                    className="device-card group bg-cyan-500/5 border-cyan-500/30 cursor-pointer"
                                    onClick={() => navigate("/liste/device")}
                                    style={{ 
                                        '--card-glow': 'radial-gradient(circle at top right, rgba(6, 182, 212, 0.08), transparent 70%)',
                                        '--card-border-hover': 'rgba(6, 182, 212, 0.5)',
                                        '--card-shadow': 'rgba(6, 182, 212, 0.2)'
                                    }}
                                >
                                    <div className="relative z-10">
                                        <div className="flex justify-between items-start mb-4">
                                            <div className="p-3 bg-white/5 rounded-xl text-cyan-400 border border-cyan-500/20">
                                                <Laptop className="w-6 h-6" />
                                            </div>
                                        </div>
                                        <div className="text-4xl font-bold text-zinc-100 mb-1">{stats.total || 0}</div>
                                        <div className="text-sm font-medium text-zinc-400 mb-4">Tous les appareils enregistrés</div>
                                        
                                        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 mt-4 pt-4 border-t border-white/5">
                                            {stats?.par_statut && Object.entries(stats.par_statut).map(([statut, nombre], idx) => {
                                                const style = getStatusStyle(idx);
                                                const Icon = style.icon;
                                                return (
                                                    <div 
                                                        key={idx} 
                                                        className={`bg-white/5 rounded-xl p-3 text-center border border-white/5 hover:bg-white/10 transition-colors`}
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            navigate(`/liste/device?status=${statut}`);
                                                        }}
                                                    >
                                                        <Icon className={`w-5 h-5 mx-auto mb-2 ${style.colorClass}`} />
                                                        <p className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold mb-1 truncate px-1" title={statut}>
                                                            {statut}
                                                        </p>
                                                        <p className="text-lg font-bold text-zinc-200">{nombre}</p>
                                                    </div>
                                                )
                                            })}
                                        </div>

                                        {stats?.par_type && Object.keys(stats.par_type).length > 0 && (
                                            <>
                                                <div className="mt-6 mb-3 text-[10px] uppercase font-bold tracking-wider text-zinc-500">Par Type</div>
                                                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                                                    {Object.entries(stats.par_type).map(([nomType, nombre], idx) => {
                                                        const style = getStatusStyle(idx + Object.keys(stats.par_statut || {}).length);
                                                        const Icon = style.icon;
                                                        return (
                                                            <div 
                                                                key={idx} 
                                                                className={`bg-white/5 rounded-xl p-3 text-center border border-white/5 hover:bg-white/10 transition-colors`}
                                                                onClick={(e) => {
                                                                    e.stopPropagation();
                                                                    navigate(`/liste/device?type=${nomType}`);
                                                                }}
                                                            >
                                                                <Icon className={`w-5 h-5 mx-auto mb-2 ${style.colorClass}`} />
                                                                <p className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold mb-1 truncate px-1" title={nomType}>
                                                                    {nomType}
                                                                </p>
                                                                <p className="text-lg font-bold text-zinc-200">{nombre}</p>
                                                            </div>
                                                        )
                                                    })}
                                                </div>
                                            </>
                                        )}
                                    </div>
                                </div>
                            </div>
                            
                            {/* Section Événements & Imprimantes */}
                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                {/* Carte Événements */}
                                <div 
                                    className="device-card group bg-red-500/5 border-red-500/30"
                                    onClick={() => navigate("/liste/event")}
                                    style={{ 
                                        '--card-glow': 'radial-gradient(circle at top right, rgba(239, 68, 68, 0.08), transparent 70%)',
                                        '--card-border-hover': 'rgba(239, 68, 68, 0.5)',
                                        '--card-shadow': 'rgba(239, 68, 68, 0.2)'
                                    }}
                                >
                                    <div className="relative z-10">
                                        <div className="flex justify-between items-start mb-4">
                                            <div className="p-3 bg-white/5 rounded-xl text-red-400 border border-red-500/20">
                                                <Bell className="w-6 h-6" />
                                            </div>
                                        </div>
                                        <div className="text-4xl font-bold text-zinc-100 mb-1">{totalEvents}</div>
                                        <div className="text-sm font-medium text-zinc-400 mb-4">Événements d'infrastructure</div>
                                        
                                        <div className="grid grid-cols-4 gap-2 mt-4 pt-4 border-t border-white/5">
                                            <div className="bg-red-500/10 rounded-lg p-2 text-center border border-red-500/20">
                                                <Cpu className="w-4 h-4 text-red-400 mx-auto mb-1" />
                                                <p className="text-[9px] text-zinc-500 uppercase">Kernel</p>
                                                <p className="text-sm font-bold text-zinc-200">{kernelEvents}</p>
                                            </div>
                                            <div className="bg-amber-500/10 rounded-lg p-2 text-center border border-amber-500/20">
                                                <Zap className="w-4 h-4 text-amber-400 mx-auto mb-1" />
                                                <p className="text-[9px] text-zinc-500 uppercase">EC</p>
                                                <p className="text-sm font-bold text-zinc-200">{ecEvents}</p>
                                            </div>
                                            <div className="bg-purple-500/10 rounded-lg p-2 text-center border border-purple-500/20">
                                                <Monitor className="w-4 h-4 text-purple-400 mx-auto mb-1" />
                                                <p className="text-[9px] text-zinc-500 uppercase">App/Web</p>
                                                <p className="text-sm font-bold text-zinc-200">{appEvents}</p>
                                            </div>
                                            <div className="bg-cyan-500/10 rounded-lg p-2 text-center border border-cyan-500/20">
                                                <Bell className="w-4 h-4 text-cyan-400 mx-auto mb-1" />
                                                <p className="text-[9px] text-zinc-500 uppercase">Autre</p>
                                                <p className="text-sm font-bold text-zinc-200">{otherEvents}</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                {/* Carte Imprimantes */}
                                <div 
                                    className="device-card group bg-amber-500/5 border-amber-500/30"
                                    onClick={() => navigate("/liste/imprimante")}
                                    style={{ 
                                        '--card-glow': 'radial-gradient(circle at top right, rgba(245, 158, 11, 0.08), transparent 70%)',
                                        '--card-border-hover': 'rgba(245, 158, 11, 0.5)',
                                        '--card-shadow': 'rgba(245, 158, 11, 0.2)'
                                    }}
                                >
                                    <div className="relative z-10 flex flex-col h-full">
                                        <div className="flex justify-between items-start mb-4">
                                            <div className="p-3 bg-white/5 rounded-xl text-amber-400 border border-amber-500/20">
                                                <Printer className="w-6 h-6" />
                                            </div>
                                        </div>
                                        <div className="mt-auto">
                                            <div className="text-4xl font-bold text-zinc-100 mb-1">{totalPrinters}</div>
                                            <div className="text-sm font-medium text-zinc-400 mb-2">Imprimantes détectées</div>
                                            <p className="text-[11px] text-zinc-500 leading-relaxed">
                                                Visualisez et gérez l'ensemble des périphériques d'impression connectés au parc informatique.
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default Dashboard;
