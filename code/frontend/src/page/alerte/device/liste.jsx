import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bell, CheckCircle2, BarChart3, Cpu, MemoryStick, Thermometer ,Search} from 'lucide-react';
import { PieChart, Pie, Cell, Tooltip as RechartsTooltip, ResponsiveContainer } from 'recharts';
import PageLayout from '../../../components/PageLayout';
import GenericTable from '../../../components/GenericTable';
import TableSkeleton from '../../../components/skeletons/TableSkeleton';
import { getListeAlertePage, getNombreAlerteCpuActive, getNombreAlerteRamActive, getNombreAlerteTemperatureActive, getListeType } from '../../../fonction/alerteFonction';
import '../../../css/liste.css';
import '../../../css/configuration.css';
import '../../../css/detail.css';
import usePaginatedData from '../../../hooks/usePaginatedData';
import Pagination from '../../../components/Pagination';

function ListeDeviceAlerte() {
    const navigate = useNavigate();
    const [page, setPage] = useState(1);
    const [pageSize, setPageSize] = useState(10);
    const [search, setSearch] = useState('');
    const [totalActiveCpu, setTotalActiveCpu] = useState('');
    const [type, setType] = useState([]);
    const [TypeFiltered, setTypeFiltered] = useState('');
    const [totalActiveRam, setTotalActiveRam] = useState('');
    const [totalActiveTemperature, setTotalActiveTemperature] = useState('');
    const [dateDebut, setDateDebut] = useState('');
    const [dateFin, setDateFin] = useState('');

    const { items: liste, total, totalPages, loading } = usePaginatedData(
        getListeAlertePage,
        page,
        pageSize,
        { date_debut: dateDebut || undefined, date_fin: dateFin || undefined, type: TypeFiltered || undefined, search: search }
    );

    const getAlerteCpuActive = async (dateDebut, dateFin) => {
        try {
            const response = await getNombreAlerteCpuActive(dateDebut, dateFin)
            setTotalActiveCpu(response)
        } catch (e) {
            console.log(e)
        }
    }

    const getAlerteRamActive = async (dateDebut, dateFin) => {
        try {
            const response = await getNombreAlerteRamActive(dateDebut, dateFin)
            setTotalActiveRam(response)
        } catch (e) {
            console.log(e)
        }
    }

    const getType = async () => {
        try {
            const response = await getListeType()
            setType(response)
        } catch (e) {
            console.log(e)
        }
    }

    const getAlerteTemperatureActive = async (dateDebut, dateFin) => {
        try {
            const response = await getNombreAlerteTemperatureActive(dateDebut, dateFin)
            setTotalActiveTemperature(response)
        } catch (e) {
            console.log(e)
        }
    }

    const reset = () => {
        setDateDebut('');
        setDateFin('');
        setTypeFiltered('');
        setSearch('');
    }

    useEffect(() => {
        getType()
    }, []);

    useEffect(() => {
        getAlerteCpuActive(dateDebut || undefined, dateFin || undefined)
        getAlerteRamActive(dateDebut || undefined, dateFin || undefined)
        getAlerteTemperatureActive(dateDebut || undefined, dateFin || undefined)
    }, [dateDebut, dateFin])

    // Un changement de filtre repart en page 1 (le hook refetch tout seul).
    useEffect(() => {
        setPage(1);
    }, [dateDebut, dateFin, TypeFiltered, search]);

    const totalActives = Number(total) || 0;
    const statsActives = [
        { label: 'CPU', value: Number(totalActiveCpu) || 0, color: '#22d3ee', text: 'text-cyan-400', Icon: Cpu },
        { label: 'RAM', value: Number(totalActiveRam) || 0, color: '#a78bfa', text: 'text-violet-400', Icon: MemoryStick },
        { label: 'Température', value: Number(totalActiveTemperature) || 0, color: '#f59e0b', text: 'text-amber-400', Icon: Thermometer },
    ];
    let donutData = statsActives.map(({ label, value, color }) => ({ name: label, value, color }));
    if (TypeFiltered === 'ALERTE_CPU') {
        donutData = [donutData[0]];
    } else if (TypeFiltered === 'ALERTE_RAM') {
        donutData = [donutData[1]];
    } else if (TypeFiltered === 'ALERTE_TEMPERATURE') {
        donutData = [donutData[2]];
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
                <div className="glass-panel rounded-2xl p-5 relative z-50">
                    <div className="relative max-w-md mb-4">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
                        <input
                            type="text"
                            placeholder="Rechercher par numéro de série…"
                            value={search}
                            onChange={e => setSearch(e.target.value)}
                            className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-zinc-900/60 border border-white/10 text-zinc-200 text-sm placeholder-zinc-500 focus:outline-none focus:border-cyan-400/50"
                        />
                    </div>

                    <div className="flex flex-wrap items-end gap-3">
                        <div>
                            <label className="config-form-label">Début (date et heure)</label>
                            <input
                                type="datetime-local"
                                className="config-form-input"
                                value={dateDebut}
                                onChange={(e) => setDateDebut(e.target.value)}
                            />
                        </div>
                        <div>
                            <label className="config-form-label">Fin (date et heure)</label>
                            <input
                                type="datetime-local"
                                className="config-form-input"
                                value={dateFin}
                                onChange={(e) => setDateFin(e.target.value)}
                            />
                        </div>
                        <div>
                            <label className="config-form-label">Type</label>
                            <select
                                className="config-form-input"
                                value={TypeFiltered}
                                onChange={(e) => setTypeFiltered(e.target.value)}
                            >
                                <option value="">Tous les types</option>
                                {type.map((t) => (
                                    <option key={t.id} value={t.type}>
                                        {t.type?.replace('ALERTE_', '')}
                                    </option>
                                ))}
                            </select>
                        </div>
                        <button
                            className="config-btn config-btn-ghost"
                            onClick={() => reset()}
                        >
                            Réinitialiser
                        </button>
                    </div>
                </div>

                {loading && liste.length === 0 ? (
                    <TableSkeleton />
                ) : !liste || liste.length === 0 ? (
                    <div className="empty-state">
                        <Bell className="empty-state-icon" />
                        <p className="empty-state-title">Aucune alerte trouvée.</p>
                        <p className="empty-state-subtitle">Aucune alerte sur cette période.</p>
                    </div>
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
                            {dateDebut || dateFin ? 'Période filtrée' : 'Toutes périodes'}
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
                        {statsActives.map(({ label, value, text, Icon }) => (
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
                onPageChange={setPage}
                onPageSizeChange={(size) => { setPageSize(size); setPage(1); }}
            />
        </PageLayout>
    );
}

export default ListeDeviceAlerte;
