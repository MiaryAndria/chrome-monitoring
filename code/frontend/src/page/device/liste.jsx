import { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { Laptop, Network, User, Users, X, Copy, Check } from 'lucide-react';
import GenericTable from "../../components/GenericTable";
import PageLayout from "../../components/PageLayout";
import EmptyState from "../../components/EmptyState";
import FilialeDropdown from "../component/FilialeDropdown";
import StatutDropdown from "../component/StatutDropdown";
import ResetFiltreButton from "../component/ResetFiltreButton";
import ViewModeToggle from "../component/ViewModeToggle";
import '../../css/liste.css';
import '../../css/filiale.css';
import { getListeDevice, getBadgeClass, searchDevices, getListeStatut } from "../../fonction/deviceFonction";
import { getListeFiliale } from "../../fonction/filialeFonction";

function ListeDevice() {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const filterStatus = searchParams.get("status");
    const filterType = searchParams.get("type");
    const filterSearch = searchParams.get("search");
    
    const [device, setDevice] = useState([]);
    const [loading, setLoading] = useState(false);
    const [currentPage, setCurrentPage] = useState(1);
    const [selectedDevice, setSelectedDevice] = useState(null);
    const [copiedSN, setCopiedSN] = useState(null);
    const [viewMode, setViewMode] = useState('grid');

    // Filtre filiale
    const [listeFiliales, setListeFiliales] = useState([]);
    const [filiale, setFiliale] = useState("");

    // Filtre statut
    const [listeStatuts, setListeStatuts] = useState([]);
    const [statut, setStatut] = useState("");

    const deviceColumns = [
        { header: "Modèle", accessor: "modele" },
        { header: "N° Série", render: (d) => <span className="font-mono text-zinc-300">{d.serial_number}</span> },
        { header: "Statut", render: (d) => <span className={`badge badge-sm ${getBadgeClass(d.status || d.nom_statut || 'UNKNOWN')}`}>{d.status || d.nom_statut || 'UNKNOWN'}</span> },
        { header: "Adresse IP", render: (d) => <span className="font-mono text-zinc-400">{d.ip_adress || 'N/A'}</span> },
        { header: "OS", accessor: "chromeos_version" },
        { header: "Assigné à", accessor: "utilisateur_email" },
        {
            header: "Actions", render: (d) => (
                <div className="flex gap-2">
                    <button onClick={() => navigate(`/device/${d.id || d.id_device}`)} className="px-3 py-1.5 text-xs font-semibold text-zinc-300 bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 rounded-xl transition-all">
                        Détails
                    </button>
                </div>
            )
        }
    ];

    const deviceParPage = 8;

    const getStatut = async () => {
        try {
            const data = await getListeStatut();
            setListeStatuts(data || []);
        } catch (e) {
            console.log(e);
        }
    };

    const getFiliale = async () => {
        try {
            const data = await getListeFiliale();
            setListeFiliales(data || []);
        } catch (e) {
            console.log(e);
        }
    };

    useEffect(() => {
        getFiliale();
        getStatut();
    }, []);

    // Revenir à la page 1 quand un filtre change
    useEffect(() => {
        setCurrentPage(1);
    }, [filiale, statut]);

    const filtresActifs = filiale !== "" || statut !== "";

    const reinitialiserFiltres = () => {
        setFiliale("");
        setStatut("");
        setCurrentPage(1);
    };

    const filteredDevices = device.filter(d => {
        if (filterStatus) {
            const s = (d.status || d.nom_statut || '').toUpperCase();
            if (s !== filterStatus.toUpperCase()) return false;
        }
        if (filterType) {
            const t = (d.type_appareil || d.nom_type || d.modele || '').toUpperCase();
            if (!t.includes(filterType.toUpperCase())) return false;
        }
        // Filtre filiale (adapte le nom du champ si besoin)
        if (filiale && (d.filiale ?? d.org_unit_path) !== filiale) return false;
        // AJOUT : filtre statut
        if (statut && (d.status || d.nom_statut || '').toUpperCase() !== statut.toUpperCase()) return false;
        return true;
    });

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
            setLoading(true);
            let d;

            if (filterSearch) {
                d = await searchDevices(filterSearch);
            } else {
                d = await getListeDevice();
            }
            setDevice(d || []);
            setLoading(false);
        } catch (e) {
            console.log(e);
        }
    };

    useEffect(() => {
        RecuperationListeDevice();
    }, [filterSearch, filterStatus, filterType]);

    return (
        <PageLayout
            title="Appareils"
            subtitle="Parc informatique et statuts associés"
            titleIcon={Laptop}
            contentClassName="space-y-6"
            headerRight={<ViewModeToggle viewMode={viewMode} setViewMode={setViewMode} />}
        >

                    {/* Filtres : filiale + statut */}
                    <div className="glass-panel rounded-2xl p-5 relative z-50">
                        <div className="flex flex-wrap items-center gap-3">
                            <span className="text-[10px] text-zinc-500 uppercase font-semibold tracking-wider">Filiale :</span>

                            <FilialeDropdown
                                listeFiliales={listeFiliales}
                                filiale={filiale}
                                setFiliale={setFiliale}
                            />

                            <span className="text-[10px] text-zinc-500 uppercase font-semibold tracking-wider ml-2">Statut :</span>

                            <StatutDropdown
                                listeStatuts={listeStatuts}
                                statut={statut}
                                setStatut={setStatut}
                            />

                            <ResetFiltreButton actif={filtresActifs} onClick={reinitialiserFiltres} />
                        </div>
                    </div>

                    <div>
                        {loading && device.length === 0 ? (
                            <div className="flex justify-center p-12">
                                <span className="loading loading-infinity loading-lg text-cyan-500"></span>
                            </div>
                        ) : currentDevices.length === 0 ? (
                            <EmptyState
                                icon={Laptop}
                                title="Aucun appareil trouvé"
                                subtitle={filterSearch || filterStatus || filterType || filtresActifs ? "Modifiez vos filtres" : "Aucune donnée disponible"}
                            />
                        ) : viewMode === 'table' ? (
                            <GenericTable columns={deviceColumns} data={currentDevices} />
                        ) : (
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                                {currentDevices.map((d) => {
                                    const status = d.status || 'UNKNOWN';

                                    return (
                                        <div key={d.id_device || d.serial_number} className="device-card">
                                            <div className="flex justify-between items-start mb-4">
                                                <div className="p-2.5 bg-white/5 rounded-xl text-zinc-300">
                                                    <Laptop className="w-5 h-5" />
                                                </div>
                                                <div className={`badge badge-sm ${getBadgeClass(status)} font-medium tracking-wide`}>
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
                                                    <span>Filiale</span>
                                                    <span className="text-zinc-300 font-mono">{d.filiale}</span>
                                                </div>
                                                <div className="flex justify-between">
                                                    <span>Création/Synchro</span>
                                                    <span className="text-zinc-300 font-mono">{d.date}</span>
                                                </div>
                                                <div className="flex justify-between">
                                                    <span>OS</span>
                                                    <span className="text-zinc-300">{d.chromeos_version}</span>
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
                                                        className="px-3 py-1.5 text-xs font-semibold text-cyan-400 bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 hover:border-cyan-500/50 rounded-xl transition-all flex items-center gap-1 cursor-pointer shadow-sm"
                                                    >
                                                        Voir tout
                                                    </button>
                                                    <button
                                                        onClick={() => navigate(`/device/${d.id || d.id_device}`)}
                                                        className="px-3 py-1.5 text-xs font-semibold text-zinc-300 bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 rounded-xl transition-all flex items-center gap-1 cursor-pointer"
                                                    >
                                                        Voir détails
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        )}
                    </div>

                    {totalPages > 1 && (
                        <div className="flex justify-center items-center gap-4 mt-8 pb-4">
                            <button
                                className="pagination-btn"
                                disabled={currentPage === 1}
                                onClick={() => setCurrentPage(currentPage - 1)}
                            >
                                Précédent
                            </button>
                            <div className="pagination-indicator">
                                {currentPage} <span className="pagination-separator">/</span> {totalPages}
                            </div>
                            <button
                                className="pagination-btn"
                                disabled={currentPage === totalPages}
                                onClick={() => setCurrentPage(currentPage + 1)}
                            >
                                Suivant
                            </button>
                        </div>
                    )}

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
        </PageLayout>
    );
}

export default ListeDevice;