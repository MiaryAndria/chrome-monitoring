import { useEffect, useState } from "react";
import { Laptop, Network, User, Users, X, Copy, Check, ChevronLeft, Building2, Server } from 'lucide-react';
import { useParams, useNavigate } from 'react-router-dom';
import Sidebar from "../../components/Sidebar";
import Navbar from "../../components/Navbar";
import MouseSpotlight from "../../components/MouseSpotlight";
import '../../css/liste.css';
import '../../css/filiale.css';
import { getDevicesByFiliale, getListeFiliale } from "../../fonction/filialeFonction";

function getStatusClass(status) {
    if (!status) return 'status-badge--unknown';
    const s = status.toUpperCase();
    if (s === 'ACTIVE') return 'status-badge--active';
    if (s === 'DEPROVISIONED') return 'status-badge--deprovisioned';
    if (s === 'INACTIVE') return 'status-badge--inactive';
    if (s === 'DISABLED') return 'status-badge--disabled';
    return 'status-badge--unknown';
}

function getDeviceStats(devices) {
    const active = devices.filter(d => (d.status || '').toUpperCase() === 'ACTIVE').length;
    return { active, other: devices.length - active };
}

function ListeDeviceFiliale() {
    const { id_filiale } = useParams();
    const navigate = useNavigate();

    const [devices, setDevices] = useState([]);
    const [filialeInfo, setFilialeInfo] = useState(null);
    const [loading, setLoading] = useState(false);
    const [currentPage, setCurrentPage] = useState(1);
    const [selectedDevice, setSelectedDevice] = useState(null);
    const [copiedSN, setCopiedSN] = useState(null);

    const deviceParPage = 8;
    const indexLastDevice = currentPage * deviceParPage;
    const indexFirstDevice = indexLastDevice - deviceParPage;
    const currentDevices = devices.slice(indexFirstDevice, indexLastDevice);
    const totalPages = Math.ceil(devices.length / deviceParPage) || 1;

    const handleCopySN = (serialNumber) => {
        if (!serialNumber) return;
        navigator.clipboard.writeText(serialNumber);
        setCopiedSN(serialNumber);
        setTimeout(() => setCopiedSN(null), 2000);
    };

    const fetchData = async () => {
        try {
            setLoading(true);
            const filiales = await getListeFiliale();
            if (filiales) {
                const current = filiales.find(f => f.id === parseInt(id_filiale));
                if (current) setFilialeInfo(current);
            }

            const data = await getDevicesByFiliale(id_filiale);
            setDevices(data || []);
        } catch (e) {
            console.log(e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
        setCurrentPage(1);
    }, [id_filiale]);

    const stats = getDeviceStats(devices);


    return (
        <div className="device-layout" data-theme="dark">
            <MouseSpotlight />
            <Sidebar />

            <div className="flex-1 flex flex-col h-screen overflow-hidden relative z-10">
                <div className="bg-glow-cyan"></div>
                <div className="bg-glow-purple"></div>

                <Navbar />

                <div className="flex-1 overflow-y-auto p-6 lg:p-8 space-y-8 z-10">

                    {/* Breadcrumb */}
                    <div className="breadcrumb-container">
                        <button className="breadcrumb-back-btn" onClick={() => navigate('/filiale')}>
                            <ChevronLeft className="w-3.5 h-3.5" />
                            Filiales
                        </button>
                        <span className="breadcrumb-separator">/</span>
                        <div className="breadcrumb-current" title={filialeInfo ? filialeInfo.org_unit_path : ''}>
                            <Building2 className="w-3.5 h-3.5" />
                            {filialeInfo ? (
                                <span className="truncate max-w-[200px]">
                                    {filialeInfo.org_unit_path.split('/').pop() || filialeInfo.org_unit_path}
                                </span>
                            ) : (
                                `Filiale #${id_filiale}`
                            )}
                        </div>
                    </div>

                    {/* Stats */}
                    <div className="stats stats-container glass-panel">
                        <div className="stat place-items-center">
                            <div className="stat-title text-zinc-400">Total Devices</div>
                            <div className="stat-value neon-text-cyan text-4xl">{devices.length}</div>
                            <div className="stat-desc text-zinc-500 flex items-center gap-1 mt-1">
                                <Server className="w-3 h-3 text-emerald-500" /> Dans cette filiale
                            </div>
                        </div>
                        <div className="stat place-items-center border-t md:border-t-0 md:border-l border-white/5">
                            <div className="stat-title text-zinc-400">Actifs</div>
                            <div className="stat-value text-emerald-400 text-4xl">{stats.active}</div>
                            <div className="stat-desc text-zinc-500">État ACTIVE</div>
                        </div>
                        <div className="stat place-items-center border-t md:border-t-0 md:border-l border-white/5">
                            <div className="stat-title text-zinc-400">Autres états</div>
                            <div className="stat-value text-purple-400 text-4xl">{stats.other}</div>
                            <div className="stat-desc text-zinc-500">Inactifs / Autres</div>
                        </div>
                    </div>

                    <div>
                        <div className="section-header">
                            <h2 className="section-title">Devices de la filiale</h2>
                            <span className="section-count">{devices.length} device(s)</span>
                        </div>

                        {loading ? (
                            <div className="flex justify-center p-12">
                                <span className="loading loading-infinity loading-lg text-cyan-500"></span>
                            </div>
                        ) : devices.length === 0 ? (
                            <div className="empty-state">
                                <Laptop className="empty-state-icon" />
                                <p className="empty-state-title">Aucun device trouvé dans cette filiale.</p>
                            </div>
                        ) : (
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                                {currentDevices.map((d) => (
                                    <div key={d.id || d.serial_number} className="device-card">
                                        <div className="flex justify-between items-start mb-4">
                                            <div className="p-2.5 bg-white/5 rounded-xl text-zinc-300">
                                                <Laptop className="w-5 h-5" />
                                            </div>
                                            <span className="text-zinc-500 text-xs flex items-center gap-1">
                                                <Users className="w-3.5 h-3.5 text-cyan-400" /> Device #{d.id}
                                            </span>
                                            <span className={`status-badge ${getStatusClass(d.status)}`}>
                                                {d.status || 'N/A'}
                                            </span>
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
                                                        className="copy-btn"
                                                        title="Copier le numéro de série"
                                                    >
                                                        {copiedSN === d.serial_number
                                                            ? <Check className="w-3.5 h-3.5 text-emerald-400" />
                                                            : <Copy className="w-3.5 h-3.5" />
                                                        }
                                                    </button>
                                                </div>
                                            </div>
                                            <div className="flex justify-between">
                                                <span>OS Version</span>
                                                <span className="text-zinc-300">{d.chromeos_version || 'N/A'}</span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span>Chrome</span>
                                                <span className="text-zinc-300">{d.chrome_version || 'N/A'}</span>
                                            </div>
                                            <div className="flex justify-between mt-2 pt-2 border-t border-white/5">
                                                <span className="flex items-center gap-1">
                                                    <Network className="w-3 h-3" /> MAC
                                                </span>
                                                <span className="text-zinc-300 font-mono truncate max-w-[140px]">
                                                    {d.mac_adress || 'N/A'}
                                                </span>
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
                                                <button
                                                    onClick={() => setSelectedDevice(d)}
                                                    className="device-detail-btn"
                                                >
                                                    Voir liste utilisateurs récents
                                                </button>
                                                <button
                                                    onClick={() => navigate(`/device/${d.id}`)}
                                                >
                                                    Voir détails
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    {devices.length > deviceParPage && (
                        <div className="flex justify-center items-center gap-4 mt-8 pb-4">
                            <button
                                className="pagination-btn"
                                disabled={currentPage === 1}
                                onClick={() => setCurrentPage(currentPage - 1)}
                            >
                                Previous
                            </button>
                            <div className="pagination-indicator">
                                {currentPage} <span className="pagination-separator">/</span> {totalPages}
                            </div>
                            <button
                                className="pagination-btn"
                                disabled={currentPage === totalPages}
                                onClick={() => setCurrentPage(currentPage + 1)}
                            >
                                Next
                            </button>
                        </div>
                    )}
                </div>
            </div>

            {selectedDevice && (
                <div className="modal-overlay" onClick={() => setSelectedDevice(null)}>
                    <h3 className="text-base font-bold text-zinc-100">
                        Historique des Utilisateurs Récents
                    </h3>
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

                    <div className="modal-footer">
                        <button className="modal-close-action-btn" onClick={() => setSelectedDevice(null)}>
                            Fermer
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}

export default ListeDeviceFiliale;
