import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Server, Laptop, Network, User, Users, X, Copy, Check } from 'lucide-react';
import Sidebar from "../../components/Sidebar";
import Navbar from "../../components/Navbar";
import MouseSpotlight from "../../components/MouseSpotlight";
import '../../css/liste.css';
import '../../css/filiale.css';
import { getDeviceStats, getListeDevice } from "../../fonction/deviceFonction";

function getStatusClass(status) {
    if (!status) return 'status-badge--unknown';
    const s = status.toUpperCase();
    if (s === 'ACTIVE') return 'status-badge--active';
    if (s === 'DEPROVISIONED') return 'status-badge--deprovisioned';
    if (s === 'INACTIVE') return 'status-badge--inactive';
    if (s === 'DISABLED') return 'status-badge--disabled';
    return 'status-badge--unknown';
}

function ListeDevice() {
    const [searchParams] = useSearchParams();
    const filterStatus = searchParams.get("status");

    const [device, setDevice] = useState([]);
    const [loading, setLoading] = useState(false);
    const [currentPage, setCurrentPage] = useState(1);
    const [selectedDevice, setSelectedDevice] = useState(null);
    const [copiedSN, setCopiedSN] = useState(null);

    const deviceParPage = 8;


    const filteredDevices = filterStatus 
        ? device.filter(d => (d.status || '').toUpperCase() === filterStatus.toUpperCase())
        : device;

    const indexLastDevice = currentPage * deviceParPage;
    const indexFirstDevice = indexLastDevice - deviceParPage;
    const currentDevices = filteredDevices.slice(indexFirstDevice, indexLastDevice);
    const totalPages = Math.ceil(filteredDevices.length / deviceParPage) || 1;

    const handleCopySN = (serialNumber) => {
        if (!serialNumber) return;
        navigator.clipboard.writeText(serialNumber);
        setCopiedSN(serialNumber);
        setTimeout(() => setCopiedSN(null), 2000);
    };

    const RecuperationListeDevice = async () => {
        try {
            setLoading(true)
            const d = await getListeDevice()
            setDevice(d)
            setLoading(false)
        } catch (e) {
            console.log(e)
        }
    }

    useEffect(() => {
        RecuperationListeDevice();
    }, [])

    const stats = getDeviceStats(device)

    return (
        <div className="device-layout" data-theme="dark">
            <MouseSpotlight />

            <Sidebar />

            <div className="flex-1 flex flex-col h-screen overflow-hidden relative z-10">
                <div className="bg-glow-cyan"></div>
                <div className="bg-glow-purple"></div>

                <Navbar />

                <div className="flex-1 overflow-y-auto p-6 lg:p-8 space-y-8 z-10">
                    <div className="stats stats-container glass-panel">
                        <div className="stat place-items-center">
                            <div className="stat-title text-zinc-400">Total Devices</div>
                            <div className="stat-value neon-text-cyan text-4xl">{device.length}</div>
                            <div className="stat-desc text-zinc-500 flex items-center gap-1 mt-1">
                                <Server className="w-3 h-3 text-emerald-500" /> Inventoried
                            </div>
                        </div>

                        <div className="stat place-items-center border-t md:border-t-0 md:border-l border-white/5">
                            <div className="stat-title text-zinc-400">Active Devices</div>
                            <div className="stat-value text-emerald-400 text-4xl">{stats.activeacounts}</div>
                            <div className="stat-desc text-zinc-500">Currently in ACTIVE state</div>
                        </div>

                        <div className="stat place-items-center border-t md:border-t-0 md:border-l border-white/5">
                            <div className="stat-title text-zinc-400">Other States</div>
                            <div className="stat-value text-purple-400 text-4xl">{stats.notactiveacounts}</div>
                            <div className="stat-desc text-zinc-500">Devices not active</div>
                        </div>
                    </div>
                    <div>
                        <div className="flex justify-between items-center mb-6">
                            <h2 className="text-lg font-medium text-zinc-100">Monitored Infrastructure</h2>
                        </div>

                        {loading && device.length === 0 ? (
                            <div className="flex justify-center p-12">
                                <span className="loading loading-infinity loading-lg text-cyan-500"></span>
                            </div>
                        ) : (
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                                {currentDevices.map((d) => {
                                    const status = d.status || 'UNKNOWN';

                                    const badgeClass = status === 'ACTIVE'
                                        ? "badge-success bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                                        : (status === 'INACTIVE' || status === 'DEPROVISIONED')
                                            ? "badge-error bg-red-500/10 text-red-400 border-red-500/20"
                                            : "badge-warning bg-amber-500/10 text-amber-400 border-amber-500/20";

                                    return (
                                        <div key={d.id_device || d.serial_number} className="device-card">
                                            <div className="flex justify-between items-start mb-4">
                                                <div className="p-2.5 bg-white/5 rounded-xl text-zinc-300">
                                                    <Laptop className="w-5 h-5" />
                                                </div>
                                                <div className={`badge badge-sm ${badgeClass} font-medium tracking-wide`}>
                                                    {status}
                                                </div>
                                            </div>

                                            <div className="card-title text-base text-zinc-100 mb-1 line-clamp-1" title={d.modele}>
                                                {d.modele || 'Unknown Model'}
                                            </div>
                                            <div className="text-xs text-zinc-500 font-mono mb-4 flex items-center gap-1">
                                                <Network className="w-3 h-3" /> {d.ip_adress || 'N/A'}
                                            </div>

                                            <div className="flex flex-col gap-2 mt-auto text-xs text-zinc-400">
                                                <div className="flex justify-between items-center">
                                                    <span>S/N</span>
                                                    <div className="flex items-center gap-1.5">
                                                        <span className="text-zinc-300 font-mono">{d.serial_number}</span>
                                                        <button
                                                            onClick={() => handleCopySN(d.serial_number)}
                                                            className="text-zinc-500 hover:text-cyan-400 transition-colors p-0.5 cursor-pointer"
                                                            title="Copier le numéro de série"
                                                        >
                                                            {copiedSN === d.serial_number ? (
                                                                <Check className="w-3.5 h-3.5 text-emerald-400" />
                                                            ) : (
                                                                <Copy className="w-3.5 h-3.5" />
                                                            )}
                                                        </button>
                                                    </div>
                                                </div>
                                                <div className="flex justify-between">
                                                    <span>Création/Synchro</span>
                                                    <span className="text-zinc-300 font-mono">{d.date}</span>
                                                </div>
                                                <div className="flex justify-between">
                                                    <span>OS</span>
                                                    <span className="text-zinc-300">{d.chromeos_version}</span>
                                                </div>
                                                <div className="flex justify-between mt-2 pt-2 border-t border-white/5">
                                                    <span className="flex items-center gap-1"><User className="w-3 h-3" /> Assigné</span>
                                                    <span className="truncate max-w-[120px]" title={d.utilisateur_email || 'N/A'}>{d.utilisateur_email || 'N/A'}</span>
                                                </div>
                                                <div className="flex justify-between mt-2 pt-2 border-t border-white/5">
                                                    <span className="flex items-center gap-1"><Users className="w-3 h-3 text-cyan-400" /> Récents</span>
                                                    <span className="text-cyan-400 truncate max-w-[150px]" title={d.utilisateurs_recents?.length > 0 ? d.utilisateurs_recents.join(", ") : 'Aucun'}>
                                                        {d.utilisateurs_recents?.length > 0 ? d.utilisateurs_recents.join(", ") : 'Aucun'}
                                                    </span>
                                                </div>
                                                <div className="flex justify-between items-center mt-3 pt-3 border-t border-white/5">
                                                    <span className="text-zinc-500 text-xs flex items-center gap-1">
                                                    </span>
                                                    <button
                                                        onClick={() => setSelectedDevice(d)}
                                                        className="px-3 py-1.5 text-xs font-semibold text-cyan-400 bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 hover:border-cyan-500/50 rounded-xl transition-all flex items-center gap-1 cursor-pointer shadow-sm"
                                                    >
                                                        Voir tout
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        )}
                    </div>

                    <div className="flex justify-center items-center gap-4 mt-8 pb-4">
                        <button
                            className="px-4 py-2 text-xs font-semibold tracking-wide rounded-xl bg-zinc-900/80 border border-white/10 text-zinc-300 hover:bg-cyan-500/20 hover:text-cyan-300 hover:border-cyan-500/40 disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-md cursor-pointer"
                            disabled={currentPage === 1}
                            onClick={() => setCurrentPage(currentPage - 1)}
                        >
                            Previous
                        </button>

                        <div className="px-4 py-1.5 rounded-xl bg-zinc-900/90 border border-cyan-500/30 text-cyan-400 font-mono text-sm tracking-widest shadow-[0_0_12px_rgba(6,182,212,0.2)]">
                            {currentPage} <span className="text-zinc-600">/</span> {totalPages}
                        </div>
                        {/* <button onClick={synchData}>Synchroniser donnée</button> */}
                        <button
                            className="px-4 py-2 text-xs font-semibold tracking-wide rounded-xl bg-zinc-900/80 border border-white/10 text-zinc-300 hover:bg-cyan-500/20 hover:text-cyan-300 hover:border-cyan-500/40 disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-md cursor-pointer"
                            disabled={currentPage === totalPages}
                            onClick={() => setCurrentPage(currentPage + 1)}
                        >
                            Next
                        </button>
                    </div>

                </div>
            </div>

            {selectedDevice && (
                <div className="modal-overlay" onClick={() => setSelectedDevice(null)}>
                    <div className="modal-content">
                        <div className="p-5 border-b border-white/10 flex justify-between items-center bg-zinc-900/60">
                            <div className="flex items-center gap-3">
                                <div className="p-2.5 bg-cyan-500/10 border border-cyan-500/30 rounded-xl text-cyan-400 shadow-[0_0_15px_rgba(6,182,212,0.2)]">
                                    <Users className="w-5 h-5" />
                                </div>
                                <div>
                                    <h3 className="text-base font-bold text-zinc-100">
                                        Historique des Utilisateurs Récents
                                    </h3>
                                    <p className="text-xs text-zinc-400 mt-0.5">
                                        {selectedDevice.modele || 'Device'} <span className="text-zinc-500 font-mono">({selectedDevice.serial_number})</span>
                                    </p>
                                </div>
                            </div>
                            <button
                                onClick={() => setSelectedDevice(null)}
                                className="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-white/10 transition-colors cursor-pointer"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        <div className="p-5 space-y-2.5 max-h-[60vh] overflow-y-auto">
                            {selectedDevice.utilisateurs_recents && selectedDevice.utilisateurs_recents.length > 0 ? (
                                selectedDevice.utilisateurs_recents.map((u, index) => {
                                    const userEmail = typeof u === 'string' ? u : (u.email || u.userEmail || 'Inconnu');
                                    const isLatest = index === selectedDevice.utilisateurs_recents.length - 1;
                                    return (
                                        <div key={index} className="user-item">
                                            <div className="flex items-center gap-3">
                                                <div className={`p-2 rounded-lg ${isLatest ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30' : 'bg-white/5 text-zinc-400'}`}>
                                                    <User className="w-4 h-4" />
                                                </div>
                                                <div>
                                                    <p className="text-xs font-medium text-zinc-200">{userEmail}</p>
                                                    {isLatest && (
                                                        <span className="text-[10px] text-cyan-400 font-semibold uppercase tracking-wider">
                                                            Dernier connecté
                                                        </span>
                                                    )}
                                                </div>
                                            </div>
                                            <span className="text-[11px] text-zinc-500 font-mono bg-zinc-900/60 px-2 py-0.5 rounded-md border border-white/5">
                                                #{index + 1}
                                            </span>
                                        </div>
                                    );
                                })
                            ) : (
                                <div className="text-center py-8 border border-dashed border-white/10 rounded-xl bg-white/[0.01]">
                                    <User className="w-8 h-8 text-zinc-600 mx-auto mb-2 opacity-50" />
                                    <p className="text-xs text-zinc-400">Aucun utilisateur récent enregistré pour ce périphérique.</p>
                                </div>
                            )}
                        </div>

                        <div className="p-4 border-t border-white/10 bg-zinc-900/60 flex justify-end">
                            <button
                                onClick={() => setSelectedDevice(null)}
                                className="px-4 py-2 text-xs font-semibold rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 hover:bg-cyan-500/20 hover:border-cyan-500/50 transition-all cursor-pointer shadow-md"
                            >
                                Fermer
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default ListeDevice;