import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { useNavigate } from "react-router-dom";
import { Users, Search, Laptop, X, Building2, ChevronRight } from "lucide-react";
import PageLayout from "../../components/PageLayout";
import GenericTable from "../../components/GenericTable";
import Pagination from "../../components/Pagination";
import EmptyState from "../../components/EmptyState";
import Skeleton from "../../components/Skeleton";
import TableSkeleton from "../../components/skeletons/TableSkeleton";
import ViewModeToggle from "../component/ViewModeToggle";
import FilialeDropdown from "../component/FilialeDropdown";
import ResetFiltreButton from "../component/ResetFiltreButton";
import usePaginatedData from "../../hooks/usePaginatedData";
import useDebounce from "../../hooks/useDebounce";
import { getListeFiliale } from "../../fonction/filialeFonction";
import { getUtilisateursRecentPage, getUtilisateurRecentDevices } from "../../fonction/utilisateurFonction";
import { formatDateTime } from "../../fonction/utils/util";
import '../../css/liste.css';
import '../../css/filiale.css';

const filialeCourte = (path) => (path || "").split("/").pop() || path;

function ListeUtilisateursEntreprise() {
    const navigate = useNavigate();
    const [listeFiliales, setListeFiliales] = useState([]);
    const [filiale, setFiliale] = useState("");
    const [search, setSearch] = useState("");
    const debouncedSearch = useDebounce(search, 300);
    const [currentPage, setCurrentPage] = useState(1);
    const [pageSize, setPageSize] = useState(12);
    const [viewMode, setViewMode] = useState("grid");
    const [selectedUser, setSelectedUser] = useState(null);
    const [devicesByUser, setDevicesByUser] = useState({});
    const [loadingDevices, setLoadingDevices] = useState(false);

    const { items: utilisateurs, total, totalPages, loading, error, firstLoadDone } = usePaginatedData(
        getUtilisateursRecentPage,
        currentPage,
        pageSize,
        {
            filiale: filiale || undefined,
            recherche: debouncedSearch || undefined,
        }
    );

    const filtresCharges = useRef(false);
    useEffect(() => {
        if (!firstLoadDone || filtresCharges.current) return;
        filtresCharges.current = true;
        getListeFiliale().then((data) => setListeFiliales(data || []));
    }, [firstLoadDone]);

    const filtresActifs = filiale !== "" || search !== "";

    const reinitialiserFiltres = () => {
        setFiliale("");
        setSearch("");
        setCurrentPage(1);
    };

    const ouvrirDevices = async (user) => {
        setSelectedUser(user);
        if (devicesByUser[user.id]) return;

        setLoadingDevices(true);
        try {
            const devices = await getUtilisateurRecentDevices(user.id);
            setDevicesByUser((prev) => ({ ...prev, [user.id]: devices || [] }));
        } finally {
            setLoadingDevices(false);
        }
    };

    const columns = [
        {
            header: "Utilisateur", className: "w-[32%]", render: (u) => (
                <span className="font-semibold text-zinc-100">{u.email}</span>
            )
        },
        {
            header: "Appareils", className: "w-[12%]", render: (u) => (
                <span className="text-zinc-300">{u.nb_devices}</span>
            )
        },
        {
            header: "Filiales", className: "w-[28%]", render: (u) => (
                <div className="flex flex-wrap gap-1">
                    {(u.filiales || []).slice(0, 3).map((f) => (
                        <span key={f} className="px-2 py-0.5 rounded text-[10px] bg-purple-500/10 text-purple-300 border border-purple-500/20">
                            {filialeCourte(f)}
                        </span>
                    ))}
                </div>
            )
        },
        {
            header: "Dernière activité", className: "w-[16%]", render: (u) => (
                <span className="text-xs text-zinc-400">{formatDateTime(u.derniere_observation)}</span>
            )
        },
        {
            header: "Actions", sticky: true, className: "w-[12%] text-right", render: (u) => (
                <button
                    onClick={() => ouvrirDevices(u)}
                    className="config-btn config-btn-primary"
                    style={{ padding: "0.4rem 0.75rem", fontSize: "0.7rem" }}
                >
                    <Laptop className="w-3.5 h-3.5" /> Appareils
                </button>
            )
        },
    ];

    const devicesSelectionnes = selectedUser ? (devicesByUser[selectedUser.id] || []) : [];

    return (
        <PageLayout
            title="Utilisateurs"
            subtitle="Utilisateurs récents du parc et leurs appareils"
            titleIcon={Users}
            contentClassName="space-y-8"
            headerRight={<ViewModeToggle viewMode={viewMode} setViewMode={setViewMode} />}
        >
            <div className="glass-panel rounded-2xl p-5 space-y-4 relative z-40">
                <div className="relative max-w-md">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
                    <input
                        type="text"
                        placeholder="Rechercher un utilisateur (email)…"
                        value={search}
                        onChange={(e) => { setSearch(e.target.value); setCurrentPage(1); }}
                        className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-zinc-900/60 border border-white/10 text-zinc-200 text-sm placeholder-zinc-500 focus:outline-none focus:border-cyan-400/50 focus:ring-1 focus:ring-cyan-400/20 transition-all"
                    />
                </div>

                <div className="flex flex-wrap items-center gap-3">
                    <span className="text-[10px] text-zinc-500 uppercase font-semibold tracking-wider flex items-center gap-1.5">
                        <Building2 className="w-3.5 h-3.5" /> Filiale :
                    </span>
                    <FilialeDropdown
                        listeFiliales={listeFiliales}
                        filiale={filiale}
                        setFiliale={(valeur) => { setFiliale(valeur); setCurrentPage(1); }}
                    />
                    <ResetFiltreButton actif={filtresActifs} onClick={reinitialiserFiltres} />
                </div>
            </div>

            {loading && utilisateurs.length === 0 ? (
                viewMode === "table" ? (
                    <TableSkeleton />
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                        {Array.from({ length: 8 }).map((_, i) => (
                            <Skeleton key={i} className="h-44" />
                        ))}
                    </div>
                )
            ) : error ? (
                <EmptyState icon={Users} title="Impossible de charger les utilisateurs." />
            ) : total === 0 ? (
                <EmptyState
                    icon={Users}
                    title="Aucun utilisateur trouvé"
                    subtitle={filtresActifs ? "Modifiez vos filtres" : "Aucune donnée enregistrée"}
                />
            ) : (
                <>
                    <div className="section-header flex justify-between items-center">
                        <div>
                            <h2 className="section-title">Utilisateurs récents</h2>
                            <span className="section-count">
                                {total} utilisateur{total > 1 ? "s" : ""} — Page {currentPage}/{totalPages}
                            </span>
                        </div>
                    </div>

                    {viewMode === "table" ? (
                        <GenericTable columns={columns} data={utilisateurs} />
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                            {utilisateurs.map((u) => (
                                <div key={u.id} className="device-card group bg-cyan-500/5 border-cyan-500/30">
                                    <div className="relative z-10">
                                        <div className="flex items-center gap-3 mb-3">
                                            <div className="p-2.5 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                                                <Users className="w-5 h-5" />
                                            </div>
                                            <div className="min-w-0">
                                                <p className="text-sm font-bold text-zinc-100 truncate" title={u.email}>{u.email}</p>
                                                <p className="text-[10px] text-zinc-500">{u.nb_devices} appareil(s)</p>
                                            </div>
                                        </div>

                                        <div className="flex flex-wrap gap-1 mb-3 min-h-[22px]">
                                            {(u.filiales || []).slice(0, 3).map((f) => (
                                                <span key={f} className="px-2 py-0.5 rounded text-[10px] bg-purple-500/10 text-purple-300 border border-purple-500/20">
                                                    {filialeCourte(f)}
                                                </span>
                                            ))}
                                        </div>

                                        <p className="text-[10px] text-zinc-500 mb-4">
                                            Dernière activité : {formatDateTime(u.derniere_observation)}
                                        </p>

                                        <button
                                            onClick={() => ouvrirDevices(u)}
                                            className="w-full flex items-center justify-between gap-2 px-3 py-2 rounded-xl text-xs font-semibold text-cyan-300 bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 transition-all"
                                        >
                                            Voir ses appareils
                                            <ChevronRight className="w-4 h-4" />
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}

                    <Pagination
                        page={currentPage}
                        pageSize={pageSize}
                        totalPages={totalPages}
                        total={total}
                        loading={loading}
                        onPageChange={setCurrentPage}
                        onPageSizeChange={(size) => {
                            setPageSize(size);
                            setCurrentPage(1);
                        }}
                    />
                </>
            )}

            {selectedUser && createPortal(
                <div className="modal-overlay" onClick={() => setSelectedUser(null)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <div className="modal-header-left">
                                <div className="modal-icon">
                                    <Users className="w-5 h-5" />
                                </div>
                                <div className="min-w-0">
                                    <div className="modal-title truncate" title={selectedUser.email}>{selectedUser.email}</div>
                                    <div className="modal-subtitle">Appareils utilisés récemment</div>
                                </div>
                            </div>
                            <button type="button" className="modal-close-btn" onClick={() => setSelectedUser(null)} aria-label="Fermer">
                                <X className="w-4 h-4" />
                            </button>
                        </div>

                        <div className="p-5 space-y-3 max-h-[60vh] overflow-y-auto">
                            {loadingDevices && devicesSelectionnes.length === 0 ? (
                                <p className="text-sm text-zinc-500">Chargement…</p>
                            ) : devicesSelectionnes.length === 0 ? (
                                <p className="text-sm text-zinc-500">Aucun appareil récent pour cet utilisateur.</p>
                            ) : (
                                devicesSelectionnes.map((d) => (
                                    <button
                                        key={d.id}
                                        onClick={() => { setSelectedUser(null); navigate(`/device/${d.id}`); }}
                                        className="w-full flex items-center justify-between gap-3 rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-left hover:border-cyan-400/50 hover:bg-cyan-500/10 transition-all"
                                    >
                                        <span className="flex items-center gap-3 min-w-0">
                                            <Laptop className="w-4 h-4 text-cyan-400 shrink-0" />
                                            <span className="min-w-0">
                                                <span className="block text-sm font-semibold text-zinc-100 truncate">
                                                    {d.modele || d.device_id || `Appareil #${d.id}`}
                                                </span>
                                                <span className="block text-[10px] text-zinc-500 font-mono truncate">
                                                    {d.serial_number || d.device_id || "—"}
                                                </span>
                                            </span>
                                        </span>
                                        <span className="text-[10px] text-zinc-500 whitespace-nowrap">
                                            {formatDateTime(d.derniere_observation)}
                                        </span>
                                    </button>
                                ))
                            )}
                        </div>

                        <div className="modal-footer">
                            <button type="button" className="modal-close-action-btn" onClick={() => setSelectedUser(null)}>
                                Fermer
                            </button>
                        </div>
                    </div>
                </div>,
                document.body
            )}
        </PageLayout>
    );
}

export default ListeUtilisateursEntreprise;
