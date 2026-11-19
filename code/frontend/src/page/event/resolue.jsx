import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircle2, Bell, Search, RefreshCw, AlertTriangle } from 'lucide-react';
import PageLayout from '../../components/PageLayout';
import GenericTable from '../../components/GenericTable';
import EmptyState from '../../components/EmptyState';
import TableSkeleton from '../../components/skeletons/TableSkeleton';
import EventListSkeleton from '../../components/skeletons/EventListSkeleton';
import Pagination from '../../components/Pagination';
import usePaginatedData from '../../hooks/usePaginatedData';
import useDebounce from '../../hooks/useDebounce';
import DateHeureFilter from '../component/DateHeureFilter';
import ResetFiltreButton from '../component/ResetFiltreButton';
import FilialeDropdown from '../component/FilialeDropdown';
import ViewModeToggle from '../component/ViewModeToggle';
import EventCard from '../component/component_event';
import { getEvenementsResolues, getListeTypeEvenement } from '../../fonction/eventFonction';
import { getListeFiliale } from '../../fonction/filialeFonction';
import { formatDateTime } from '../../fonction/utils/util';
import '../../css/liste.css';
import '../../css/detail.css';

function ListeEventResolue() {
    const navigate = useNavigate();
    const [page, setPage] = useState(1);
    const [search, setSearch] = useState('');
    const debouncedSearch = useDebounce(search, 300);
    const [pageSize, setPageSize] = useState(10);
    const [showAll, setShowAll] = useState(false);
    const [type, setType] = useState([]);
    const [TypeFiltered, setTypeFiltered] = useState('');
    const [listeFiliales, setListeFiliales] = useState([]);
    const [dateDebut, setDateDebut] = useState('');
    const [heureDebut, setHeureDebut] = useState('00:00');
    const [dateFin, setDateFin] = useState('');
    const [heureFin, setHeureFin] = useState('23:59');
    const [datetimeDebutApplique, setDatetimeDebutApplique] = useState('');
    const [datetimeFinApplique, setDatetimeFinApplique] = useState('');
    const [erreurFiltreDate, setErreurFiltreDate] = useState('');
    const [reloadKey, setReloadKey] = useState(0);
    const [filiale, setFiliale] = useState('');
    const [utilisateurRecent, setUtilisateurRecent] = useState('');
    const [viewMode, setViewMode] = useState('grid');

    const filtresEvent = {
        recherche: debouncedSearch || undefined,
        type_evenement: TypeFiltered || undefined,
        filiale: filiale || undefined,
        datetime_from: datetimeDebutApplique || undefined,
        datetime_to: datetimeFinApplique || undefined,
        utilisateur_recent: utilisateurRecent || undefined,
        reload: reloadKey,
    };

    const { items: evenements, total, totalPages, loading, error } = usePaginatedData(
        getEvenementsResolues,
        showAll ? 1 : page,
        showAll ? 10000 : pageSize,
        filtresEvent
    );

    const chargerReferences = async () => {
        try {
            const [dataTypes, dataFiliales] = await Promise.all([
                getListeTypeEvenement(),
                getListeFiliale(),
            ]);
            setType(dataTypes || []);
            setListeFiliales(dataFiliales || []);
        } catch (e) {
            console.error(e);
        }
    };

    const filtrerByDate = () => {
        setErreurFiltreDate('');
        if (!dateDebut && !dateFin) {
            setDatetimeDebutApplique('');
            setDatetimeFinApplique('');
            setPage(1);
            return;
        }
        setDatetimeDebutApplique(dateDebut ? `${dateDebut}T${heureDebut || '00:00'}:00` : '');
        setDatetimeFinApplique(dateFin ? `${dateFin}T${heureFin || '23:59'}:59` : '');
        setPage(1);
    };

    const resetDate = () => {
        setErreurFiltreDate('');
        setDateDebut('');
        setHeureDebut('00:00');
        setDateFin('');
        setHeureFin('23:59');
        setDatetimeDebutApplique('');
        setDatetimeFinApplique('');
    };

    const reinitialiserFiltres = () => {
        resetDate();
        setTypeFiltered('');
        setSearch('');
        setFiliale('');
        setUtilisateurRecent('');
        setPage(1);
    };

    const actualiser = () => {
        setReloadKey((k) => k + 1);
    };

    const filtresActifs = TypeFiltered !== "" || search !== "" || filiale !== "" || utilisateurRecent !== "" || !!datetimeDebutApplique || !!datetimeFinApplique;

    const columns = [
        {
            header: "Date",
            className: "w-[18%]",
            render: (ev) => <span className="text-zinc-400 text-xs font-mono">{formatDateTime(ev.date_evenement)}</span>,
        },
        {
            header: "Type d'Incident",
            className: "w-[18%]",
            render: (ev) => <span className="font-bold text-zinc-100">{(ev.type_evenement || '').replace('CRASH_TYPE_', '')}</span>,
        },
        {
            header: "Cause",
            className: "w-[14%]",
            render: (ev) => <span className="text-zinc-400">{ev.cause_class || '-'}</span>,
        },
        {
            header: "Utilisateur",
            className: "w-[22%]",
            render: (ev) => <span className="text-cyan-400 font-medium truncate max-w-[150px] inline-block" title={ev.last_user}>{ev.last_user || '-'}</span>,
        },
        {
            header: "Appareil",
            className: "w-[18%]",
            render: (ev) => <span className="font-mono text-zinc-300">{ev.serial_number || ev.modele || ev.device_id || '-'}</span>,
        },
        {
            header: "",
            className: "w-[10%] text-right",
            render: (ev) => (
                <button
                    onClick={() => navigate(`/event/resolue/${ev.id}`)}
                    className="px-3 py-1.5 text-xs font-semibold text-cyan-400 bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 rounded-xl transition-all"
                >
                    Voir
                </button>
            ),
        },
    ];

    useEffect(() => {
        chargerReferences();
    }, []);

    useEffect(() => {
        if (error) {
            setErreurFiltreDate(error?.response?.data?.error || error?.response?.data?.detail || '');
        }
    }, [error]);

    useEffect(() => {
        setPage(1);
    }, [search, TypeFiltered, filiale, utilisateurRecent, datetimeDebutApplique, datetimeFinApplique, debouncedSearch]);


    return (
        <PageLayout
            title="Événements résolus"
            subtitle="Événements marqués comme résolus"
            titleIcon={CheckCircle2}
            headerRight={
                <div className="flex items-center gap-3">
                    <button
                        onClick={() => navigate('/liste/event')}
                        className="config-btn config-btn-ghost"
                    >
                        <Bell className="w-4 h-4" /> Voir les actifs
                    </button>
                    <ViewModeToggle viewMode={viewMode} setViewMode={setViewMode} />
                </div>
            }
        >
            <div className="space-y-6">
                <div className="glass-panel rounded-2xl p-5 space-y-4 relative z-50">
                    <div className="relative max-w-md">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
                        <input
                            type="text"
                            placeholder="Rechercher par numéro de série…"
                            value={search}
                            onChange={e => setSearch(e.target.value)}
                            className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-zinc-900/60 border border-white/10 text-zinc-200 text-sm placeholder-zinc-500 focus:outline-none focus:border-cyan-400/50 focus:ring-1 focus:ring-cyan-400/20 transition-all"
                        />
                    </div>

                    <div className="flex flex-wrap items-center gap-3">
                        <span className="text-[10px] text-zinc-500 uppercase font-semibold tracking-wider">Filiale :</span>
                        <FilialeDropdown
                            listeFiliales={listeFiliales}
                            filiale={filiale}
                            setFiliale={setFiliale}
                        />

                        <span className="text-[10px] text-zinc-500 uppercase font-semibold tracking-wider ml-2">Utilisateur récent :</span>
                        <div className="relative w-64">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
                            <input
                                type="text"
                                placeholder="Rechercher un utilisateur (email)…"
                                value={utilisateurRecent}
                                onChange={(e) => setUtilisateurRecent(e.target.value)}
                                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-zinc-900/60 border border-white/10 text-zinc-200 text-sm placeholder-zinc-500 focus:outline-none focus:border-cyan-400/50 focus:ring-1 focus:ring-cyan-400/20 transition-all"
                            />
                        </div>
                    </div>

                    <DateHeureFilter
                        dateDebut={dateDebut}
                        heureDebut={heureDebut}
                        dateFin={dateFin}
                        heureFin={heureFin}
                        setDateDebut={setDateDebut}
                        setHeureDebut={setHeureDebut}
                        setDateFin={setDateFin}
                        setHeureFin={setHeureFin}
                        onFilter={filtrerByDate}
                        onReset={resetDate}
                    />
                    {erreurFiltreDate && (
                        <p className="text-xs text-red-400 bg-red-500/10 border border-red-500/30 p-2.5 rounded-lg">
                            {erreurFiltreDate}
                        </p>
                    )}

                    <div className="flex flex-wrap items-center gap-3">
                        <span className="text-[10px] text-zinc-500 uppercase font-semibold tracking-wider">Type :</span>
                        {[{ type: '' }, ...type].map((t) => {
                            const value = t.type || '';
                            const label = value ? value.replace('CRASH_TYPE_', '') : 'Tous';
                            return (
                                <button
                                    key={t.id ?? 'tous'}
                                    onClick={() => setTypeFiltered(value)}
                                    className={`px-3 py-1.5 rounded-xl text-xs font-semibold border transition-all duration-200 cursor-pointer ${TypeFiltered === value
                                        ? "bg-cyan-500/15 text-cyan-300 border-cyan-500/40 shadow-[0_0_12px_rgba(6,182,212,0.15)]"
                                        : "bg-zinc-900/60 text-zinc-400 border-white/10 hover:bg-zinc-800/80 hover:text-zinc-300 hover:border-white/15"
                                        }`}
                                >
                                    {label}
                                </button>
                            );
                        })}

                        <ResetFiltreButton actif={filtresActifs} onClick={reinitialiserFiltres} />
                    </div>
                </div>

                {loading && evenements.length === 0 ? (
                    <EventListSkeleton viewMode={viewMode} />
                ) : error ? (
                    <EmptyState icon={AlertTriangle} title="Impossible de charger les événements résolus." />
                ) : total === 0 ? (
                    <EmptyState
                        icon={CheckCircle2}
                        title={error ? "Impossible de charger les événements résolus" : "Aucun événement résolu trouvé"}
                        subtitle={error
                            ? "Une erreur est survenue lors du chargement."
                            : (filtresActifs ? "Aucun résultat pour ces filtres." : "Aucun événement n'a encore été marqué résolu.")}
                        action={
                            <div className="flex flex-wrap justify-center gap-2">
                                {filtresActifs && (
                                    <button type="button" onClick={reinitialiserFiltres} className="config-btn config-btn-ghost text-xs">
                                        Réinitialiser les filtres
                                    </button>
                                )}
                                <button type="button" onClick={actualiser} className="config-btn config-btn-primary text-xs flex items-center gap-1.5">
                                    <RefreshCw className="w-3.5 h-3.5" /> Actualiser
                                </button>
                            </div>
                        }
                    />
                ) : (
                    <>
                        <div className="section-header">
                            <div>
                                <h2 className="section-title">Événements résolus</h2>
                                <span className="section-count">
                                    {total} événement{total > 1 ? "s" : ""}{!showAll ? ` — Page ${page}/${totalPages}` : ""}
                                </span>
                            </div>
                        </div>

                        {viewMode === 'table' ? (
                            <GenericTable columns={columns} data={evenements} />
                        ) : (
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                                {evenements.map((ev, idx) => (
                                    <EventCard key={ev.id ?? idx} ev={ev} resolu />
                                ))}
                            </div>
                        )}

                        {loading && evenements.length > 0 && (
                            <div className="mt-4">
                                <TableSkeleton rows={2} />
                            </div>
                        )}

                        <Pagination
                            page={page}
                            pageSize={pageSize}
                            totalPages={totalPages}
                            total={total}
                            loading={loading}
                            showAll={showAll}
                            onPageChange={setPage}
                            onPageSizeChange={(size) => {
                                if (size === 'all') {
                                    setShowAll(true);
                                    setPage(1);
                                } else {
                                    setShowAll(false);
                                    setPageSize(size);
                                    setPage(1);
                                }
                            }}
                        />
                    </>
                )}
            </div>
        </PageLayout>
    );
}

export default ListeEventResolue;
