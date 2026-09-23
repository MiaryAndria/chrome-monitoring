import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Server, Laptop, Activity, XOctagon, ShieldAlert, CheckCircle2 } from 'lucide-react';
import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";
import MouseSpotlight from "../components/MouseSpotlight";
import { getDeviceStats, getListeDevice} from "../fonction/deviceFonction";
import '../css/liste.css'; 
import '../css/filiale.css';

function Dashboard() {
    const navigate = useNavigate();
    const [devices, setDevices] = useState([]);
    const [loading, setLoading] = useState(false);
    const [stats, setStats] = useState({
        total: 0,
        active: 0,
        inactive: 0,
        deprovisioned: 0,
        disabled: 0,
        unknown: 0
    });

    const fetchData = async () => {
        try {
            setLoading(true);
            const data = await getListeDevice();
            if (data) {
                setDevices(data);
                setStats(getDeviceStats(data));
            }
        } catch (e) {
            console.log(e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const statCards = [
        {
            title: "Tous les appareils",
            value: stats.total,
            icon: Laptop,
            colorClass: "text-cyan-400",
            bgClass: "bg-cyan-500/10",
            borderClass: "border-cyan-500/30",
            hoverClass: "hover:bg-cyan-500/20 hover:border-cyan-500/50",
            onClick: () => navigate("/liste/device")
        },
        {
            title: "Actifs",
            value: stats.active,
            icon: CheckCircle2,
            colorClass: "text-emerald-400",
            bgClass: "bg-emerald-500/10",
            borderClass: "border-emerald-500/30",
            hoverClass: "hover:bg-emerald-500/20 hover:border-emerald-500/50",
            onClick: () => navigate("/liste/device?status=ACTIVE")
        },
        {
            title: "Inactifs",
            value: stats.inactive,
            icon: Activity,
            colorClass: "text-amber-400",
            bgClass: "bg-amber-500/10",
            borderClass: "border-amber-500/30",
            hoverClass: "hover:bg-amber-500/20 hover:border-amber-500/50",
            onClick: () => navigate("/liste/device?status=INACTIVE")
        },
        {
            title: "Déprovisionnés",
            value: stats.deprovisioned,
            icon: XOctagon,
            colorClass: "text-red-400",
            bgClass: "bg-red-500/10",
            borderClass: "border-red-500/30",
            hoverClass: "hover:bg-red-500/20 hover:border-red-500/50",
            onClick: () => navigate("/liste/device?status=DEPROVISIONED")
        },
        {
            title: "Désactivés",
            value: stats.disabled,
            icon: ShieldAlert,
            colorClass: "text-purple-400",
            bgClass: "bg-purple-500/10",
            borderClass: "border-purple-500/30",
            hoverClass: "hover:bg-purple-500/20 hover:border-purple-500/50",
            onClick: () => navigate("/liste/device?status=DISABLED")
        }
    ];

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
                            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-400"></div>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
                            {statCards.map((card, idx) => {
                                const Icon = card.icon;
                                return (
                                    <div 
                                        key={idx}
                                        onClick={card.onClick}
                                        className={`glass-panel p-6 rounded-2xl border ${card.borderClass} ${card.bgClass} ${card.hoverClass} cursor-pointer transition-all duration-300 transform hover:-translate-y-1`}
                                    >
                                        <div className="flex justify-between items-start mb-4">
                                            <div className={`p-3 bg-white/5 rounded-xl ${card.colorClass}`}>
                                                <Icon className="w-6 h-6" />
                                            </div>
                                        </div>
                                        <div>
                                            <div className="text-4xl font-bold text-zinc-100 mb-1">{card.value}</div>
                                            <div className="text-sm font-medium text-zinc-400">{card.title}</div>
                                        </div>
                                    </div>
                                )
                            })}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default Dashboard;
