import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bell, CheckCircle2, BarChart3, Search, RefreshCw } from 'lucide-react';
import { PieChart, Pie, Cell, Tooltip as RechartsTooltip, ResponsiveContainer } from 'recharts';
import PageLayout from '../../../components/PageLayout';
import GenericTable from '../../../components/GenericTable';
import EmptyState from '../../../components/EmptyState';
import TableSkeleton from '../../../components/skeletons/TableSkeleton';
import { getListeAlertePage, getNombreAlerteType, getListeType, ALERTE_META } from '../../../fonction/alerteFonction';
import '../../../css/liste.css';
import '../../../css/configuration.css';
import '../../../css/detail.css';
import usePaginatedData from '../../../hooks/usePaginatedData';
import useDebounce from '../../../hooks/useDebounce';
import DateHeureFilter from '../../component/DateHeureFilter';
import ResetFiltreButton from '../../component/ResetFiltreButton';
import Pagination from '../../../components/Pagination';

function ListeDeviceAlerte() {
    const navigate = useNavigate();
    const [page, setPage] = useState(1);
    const [pageSize, setPageSize] = useState(10);
    const [showAll, setShowAll] = useState(false);
    const [search, setSearch] = useState('');
    const debouncedSearch = useDebounce(search, 300);
    const [type, setType] = useState([]);
    const [stats, setStats] = useState({});
    const [TypeFiltered, setTypeFiltered] = useState('');
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

    const { items: liste, total, totalPages, loading, error } = usePaginatedData(
        getListeAlertePage,
        showAll ? 1 : page,
        showAll ? 10000 : pageSize,
        { date_debut: datetimeDebutApplique || undefined, date_fin: datetimeFinApplique || undefined, type: TypeFiltered || undefined, search: debouncedSearch || undefined, filiale: filiale || undefined, utilisateur_recent: utilisateurRecent || undefined, refresh: reloadKey }
    );

    const getType = async () => {
        try {
            const response = await getListeType()
            setType(response)
        } catch (e) {
            console.log(e)
        }
    }

    const chargerStats = async () => {
        const resultat = {};
        await Promise.all(type.map(async (t) => {
            resultat[t.type] = await getNombreAlerteType(
                t.type, 1, datetimeDebutApplique || undefined, datetimeFinApplique || undefined
            );
        }));
        setStats(resultat);
    }

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
        setPage(1);
    };
    // Un changement de filtre repart en page 1 (le hook refetch tout seul).
    const filtresActifs = TypeFiltered !== "" || search !== "" || filiale !== "" || utilisateurRecent !== "" || !!datetimeDebutApplique || !!datetimeFinApplique;

    const totalActives = Number(total) || 0;

    const statsParType = [];
    for (const t of type) {
        const valeur = Number(stats[t.type]) || 0;
        const meta = ALERTE_META[t.type];
        if (meta && valeur > 0) {
            statsParType.push({ type: t.type, ...meta, value: valeur });
        }
    }

    const donutData = [];
    for (const s of statsParType) {
        if (TypeFiltered && s.type !== TypeFiltered || s.value <= 0) {
            continue;
        } else if (s.value === 0) {
            continue;
        }
        donutData.push({ name: s.label, value: s.value, color: s.color });
    }

    const columns = [
        {
            header: 'Numéro de série',
            className: 'w-[20%]',
            render: (a) =>
                <div className="flex gap-2">
                    <button onClick={() => navigate(`/device/${a.id_device}`)} className="px-3 py-1.5 text-xs font-semibold text-zinc-300 bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 rounded-xl transition-all">
                        <div><span className="font-mono font-bold text-zinc-100">{a.serial_number}</span></div>
                    </button>
                </div>
        },
        {
            header: 'Type',
            className: 'w-[14%]',
            render: (a) => (
                <span className="text-xs font-bold uppercase text-amber-400">
                    {a.type?.replace('ALERTE_', '')}
                </span>
            ),
        },
        {
            header: 'Utilisateur',
            className: 'w-[22%]',
            render: (a) => <span className="text-zinc-300">{a.utilisateur_recent ?? '—'}</span>,
        },
        {
            header: 'Message',
            className: 'w-[26%]',
            render: (a) => <span className="text-zinc-400 text-xs">{a.message ?? '—'}</span>,
        },
        {
            header: 'Date',
            className: 'w-[18%] text-right',
            render: (a) => a.date ? (
                <span className="text-zinc-400 text-xs font-mono">
                    <span className="block">{new Date(a.date).toLocaleDateString('fr-FR')}</span>
                    <span className="block">{new Date(a.date).toLocaleTimeString('fr-FR')}</span>
                </span>
            ) : <span className="text-zinc-500">-</span>,
        },
    ];

    useEffect(() => {
        getType();
    }, []);

    useEffect(() => {
        if (type.length > 0) {
            chargerStats();
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [type, datetimeDebutApplique, datetimeFinApplique]);

    useEffect(() => {
        setPage(1);
    }, [search, TypeFiltered, datetimeDebutApplique, datetimeFinApplique]);

    useEffect(() => {
        if (error) {
            setErreurFiltreDate(error?.response?.data?.error || error?.response?.data?.detail || '');
        }
    }, [error]);

    return (
        <PageLayout
            title="Alertes des appareils"
            subtitle="Alertes actives (filtrables par date)"
            titleIcon={Bell}
            headerRight={
                <button
                    onClick={() => navigate('/alerte/device/resolue')}
                    className="config-btn config-btn-ghost"
                >
                    <CheckCircle2 className="w-4 h-4" /> Voir les résolues
                </button>
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
                        <input
                            type="text"
                            placeholder="Filiale…"
                            value={filiale}
                            onChange={(e) => setFiliale(e.target.value)}
                            className="w-56 px-4 py-2.5 rounded-xl bg-zinc-900/60 border border-white/10 text-zinc-200 text-sm placeholder-zinc-500 focus:outline-none focus:border-cyan-400/50 focus:ring-1 focus:ring-cyan-400/20 transition-all"
                        />
                        <span className="text-[10px] text-zinc-500 uppercase font-semibold tracking-wider">Utilisateur récent :</span>
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
                        {[{ id: 'tous', type: '' }, ...type].map((t) => {
                            const value = t.type || '';
                            const label = value ? value.replace('ALERTE_', '') : 'Tous';
                            return (
                                <button
                                    key={t.id}
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

                {loading && liste.length === 0 ? (
                    <TableSkeleton />
                ) : !liste || liste.length === 0 ? (
                    <EmptyState
                        icon={Bell}
                        title={error ? "Impossible de charger les alertes" : "Aucune alerte trouvée"}
                        subtitle={error
                            ? "Une erreur est survenue lors du chargement. Vérifiez la connexion puis réessayez."
                            : (filtresActifs ? "Aucun résultat pour ces filtres. Essayez de les réinitialiser." : "Aucune alerte active pour le moment.")}
                        action={
                            <div className="flex flex-wrap justify-center gap-2">
                                {filtresActifs && (
                                    <button type="button" onClick={reinitialiserFiltres} className="config-btn config-btn-ghost text-xs">
                                        Réinitialiser les filtres
                                    </button>
                                )}
                                <button type="button" onClick={() => setReloadKey((k) => k + 1)} className="config-btn config-btn-primary text-xs flex items-center gap-1.5">
                                    <RefreshCw className="w-3.5 h-3.5" /> Actualiser
                                </button>
                            </div>
                        }
                    />
                ) : (
                    <>
                        <div className="section-header">
                            <div>
                                <h2 className="section-title">Liste des alertes</h2>
                                <span className="section-count">{liste.length} alerte(s)</span>
                            </div>
                        </div>
                        <GenericTable columns={columns} data={liste} />
                    </>
                )}

                <div className="telemetry-panel">
                    <div className="flex items-center gap-2 mb-4">
                        <BarChart3 className="w-4 h-4 text-cyan-400" />
                        <span className="text-sm font-semibold text-zinc-200">Statistiques des alertes actives</span>
                        <span className="text-[10px] text-zinc-500 ml-auto">
                            {datetimeDebutApplique || datetimeFinApplique ? 'Période filtrée' : 'Toutes périodes'}
                        </span>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                        <div className="stat-card">
                            <div className="flex items-center gap-2 text-zinc-400">
                                <Bell className="w-4 h-4" />
                                <span className="text-[10px] uppercase tracking-wider font-semibold">Total</span>
                            </div>
                            <span className="text-2xl font-bold text-zinc-100">{totalActives}</span>
                        </div>
                        {statsParType.map(({ label, value, text, Icon }) => (
                            <div key={label} className="stat-card">
                                <div className="flex items-center gap-2 text-zinc-400">
                                    <Icon className={`w-4 h-4 ${text}`} />
                                    <span className="text-[10px] uppercase tracking-wider font-semibold">{label}</span>
                                </div>
                                <span className={`text-2xl font-bold ${text}`}>{value}</span>
                            </div>
                        ))}
                    </div>

                    {totalActives > 0 ? (
                        <div className="flex flex-col sm:flex-row items-center justify-center gap-8">
                            <div className="relative h-60 w-60 shrink-0">
                                <ResponsiveContainer width="100%" height="100%">
                                    <PieChart>
                                        <Pie
                                            data={donutData}
                                            dataKey="value"
                                            nameKey="name"
                                            cx="50%"
                                            cy="50%"
                                            innerRadius={58}
                                            outerRadius={88}
                                            paddingAngle={3}
                                            stroke="none"
                                        >
                                            {donutData.map((d) => (
                                                <Cell key={d.name} fill={d.color} />
                                            ))}
                                        </Pie>
                                        <RechartsTooltip
                                            contentStyle={{ backgroundColor: 'rgba(24, 24, 32, 0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                                            itemStyle={{ color: '#e4e4e7' }}
                                            formatter={(val, name) => [val, name]}
                                        />
                                    </PieChart>
                                </ResponsiveContainer>
                                <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                                    <span className="text-2xl font-bold text-zinc-100">{totalActives}</span>
                                    <span className="text-[10px] uppercase tracking-wider text-zinc-500">Alertes</span>
                                </div>
                            </div>

                            <ul className="w-full max-w-xs shrink-0 space-y-3">
                                {donutData.map((d) => {
                                    const pct = totalActives > 0 ? Math.round((d.value / totalActives) * 100) : 0;
                                    return (
                                        <li key={d.name} className="flex items-center gap-3 text-xs">
                                            <span className="w-3 h-3 rounded-sm shrink-0" style={{ backgroundColor: d.color }} />
                                            <span className="text-zinc-300 flex-1">{d.name}</span>
                                            <span className="text-zinc-400 font-semibold tabular-nums">{d.value}</span>
                                            <span className="text-zinc-500 w-10 text-right tabular-nums">{pct}%</span>
                                        </li>
                                    );
                                })}
                            </ul>
                        </div>
                    ) : (
                        <p className="text-xs text-zinc-500">Aucune alerte active sur cette période.</p>
                    )}
                </div>
            </div>
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
        </PageLayout>
    );
}

export default ListeDeviceAlerte;
