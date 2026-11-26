import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { RefreshCw, Activity, Loader2, Filter } from 'lucide-react';
import {
    getListeSynchronisation,
    getSynchronisationEnCours,
    getStatutsSynchronisation,
} from '../../fonction/synchronisationFonction';
import PageLayout from '../../components/PageLayout';
import SelectDropdown from '../component/SelectDropdown';
import GenericTable from '../../components/GenericTable';
import Pagination from '../../components/Pagination';
import TableSkeleton from '../../components/skeletons/TableSkeleton';
import usePaginatedData from '../../hooks/usePaginatedData';
import ResetFiltreButton from '../component/ResetFiltreButton';
import '../../css/liste.css';

const fmtDate = (d) => (d ? new Date(d).toLocaleString('fr-FR') : '-');

const badgeStatut = (statut) => {
    if (statut === 'TERMINER') return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30';
    if (statut === 'ECHEC') return 'text-red-400 bg-red-500/10 border-red-500/30';
    if (statut === 'EN_COURS' || statut === 'COMMENCER') return 'text-amber-400 bg-amber-500/10 border-amber-500/30';
    return 'text-zinc-400 bg-white/5 border-white/10';
};

const inputDateClass = "px-3 py-2 rounded-lg bg-zinc-900/60 border border-white/10 text-zinc-200 text-sm outline-none focus:border-cyan-400/50";

function SynchronisationListe() {
    const navigate = useNavigate();
    const [currentPage, setCurrentPage] = useState(1);
    const [pageSize, setPageSize] = useState(10);
    const [showAll, setShowAll] = useState(false);
    const [statut, setStatut] = useState('');
    const [date_debut, setDateDebut] = useState('');
    const [date_fin, setDateFin] = useState('');
    const [fenetre_debut, setFenetreDebut] = useState('');
    const [fenetre_fin, setFenetreFin] = useState('');
    const [statuts, setStatuts] = useState([]);
    const [enCours, setEnCours] = useState(null);
    // Filtres réellement appliqués (envoyés à l'API) — ne changent qu'au clic sur "Filtrer"
    const [applied, setApplied] = useState({});

    const { items: synch, total, totalPages, loading } = usePaginatedData(
        getListeSynchronisation,
        showAll ? 1 : currentPage,
        showAll ? 10000 : pageSize,
        filtreSynchronisation
        
    );

    // Statuts alimentés par l'API (jamais figés dans le code)
    useEffect(() => {
        getStatutsSynchronisation().then((data) =>
            setStatuts((data || []).map((s) => ({ value: s, label: s })))
        );
    }, []);

    // Suivi de la synchro en cours (polling léger)
    useEffect(() => {
        let actif = true;
        const charger = async () => {
            const data = await getSynchronisationEnCours();
            if (actif) setEnCours(data);
        };
        charger();
        const timer = setInterval(charger, 2000);
        const onVisible = () => {
            if (document.visibilityState === 'visible') charger();
        };
        document.addEventListener('visibilitychange', onVisible);
        return () => {
            actif = false;
            clearInterval(timer);
            document.removeEventListener('visibilitychange', onVisible);
        };
    }, []);

    useEffect(() => {
        setCurrentPage(1);
    }, []);

    const filtresActifs = statut !== "" || date_debut !== "" || date_fin !== "" || fenetre_debut !== "" || fenetre_fin !== "";

    const filtreSynchronisation =  {
            statut: statut || undefined,
            date_debut: date_debut || undefined,
            date_fin: date_fin || undefined,
            fenetre_debut: fenetre_debut || undefined,
            fenetre_fin: fenetre_fin || undefined,
    };

    const resetFilter = () => {
        setDateDebut('');
        setDateFin('');
        setFenetreDebut('');
        setFenetreFin('');
        setStatut('');
        setCurrentPage(1);
    };

    useEffect(()=>{
        setCurrentPage(1);
    },[date_debut,date_fin,fenetre_debut,fenetre_fin])

    // La synchro en cours est affichée en haut ; on la retire du tableau
    const liste = enCours ? synch.filter((s) => s.id !== enCours.id) : synch;

    const columns = [
        { header: 'Source', className: 'w-[8%]', render: (s) => <span className="font-mono text-zinc-400">{s.source}</span> },
        {
            header: 'Statut', className: 'w-[10%]', render: (s) => (
                <span className={`px-2 py-0.5 rounded-full border text-[11px] font-semibold ${badgeStatut(s.statut)}`}>
                    {s.statut || '-'}
                </span>
            )
        },
        { header: 'Date début', className: 'w-[14%]', render: (s) => <span className="text-zinc-300 text-xs">{fmtDate(s.date_debut)}</span> },
        { header: 'Date fin', className: 'w-[14%]', render: (s) => <span className="text-zinc-300 text-xs">{fmtDate(s.date_fin)}</span> },
        { header: 'Lignes', className: 'w-[7%]', render: (s) => <span className="text-zinc-100">{s.nb_lignes}</span> },
        { header: 'Fenêtre début', className: 'w-[13%]', render: (s) => <span className="text-zinc-400 text-xs">{fmtDate(s.fenetre_debut)}</span> },
        { header: 'Fenêtre fin', className: 'w-[13%]', render: (s) => <span className="text-zinc-400 text-xs">{fmtDate(s.fenetre_fin)}</span> },
        {
            header: 'Message', className: 'w-[11%]', render: (s) => (
                s.message ? <span className="text-red-400 text-xs">{s.message}</span> : <span className="text-zinc-500 text-xs">-</span>
            )
        },
        {
            header: 'Action', sticky: true, className: 'w-[10%] text-right', render: (s) => (
                <div className="config-table-actions">
                    <button
                        onClick={() => navigate(`/liste/synchronisation/${s.id}`)}
                        className="config-btn config-btn-primary"
                        style={{ padding: '0.4rem 0.75rem', fontSize: '0.7rem' }}
                    >
                        Voir détails
                    </button>
                </div>
            )
        },
    ];

    const progression = enCours?.journal?.progression ?? 0;

    return (
        <PageLayout
            title="Synchronisation"
            subtitle="Consulter liste et historique des synchronisations"
            titleIcon={Activity}
        >
            <div className="space-y-6">

                {/* Synchronisation en cours : barre de progression + logs + message */}
                {enCours && (
                    <div className="glass-panel rounded-2xl p-5 border border-cyan-500/25">
                        <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
                            <h2 className="section-title flex items-center gap-2">
                                <Loader2 className="w-4 h-4 animate-spin text-cyan-400" />
                                Synchronisation en cours #{enCours.id}
                            </h2>
                            <span className="text-xs text-zinc-400">Démarrée : {fmtDate(enCours.date_debut)}</span>
                        </div>

                        <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden mb-2">
                            <div className="h-full bg-cyan-500 transition-all duration-500" style={{ width: `${progression}%` }} />
                        </div>
                        <div className="text-[11px] text-zinc-500 mb-3">
                            {progression}% {enCours.message ? `• ${enCours.message}` : '• en cours…'}
                        </div>

                        {enCours.journal?.compteurs && (
                            <div className="flex flex-wrap gap-4 text-xs text-zinc-400 mb-3">
                                <span>devices : {enCours.journal.compteurs.devices ?? 0}</span>
                                <span>télémétrie : {enCours.journal.compteurs.telemetrie ?? 0}</span>
                                <span>événements : {enCours.journal.compteurs.evenements ?? 0}</span>
                            </div>
                        )}

                        <pre className="text-[11px] bg-black/40 rounded-lg p-3 max-h-56 overflow-auto text-zinc-400 whitespace-pre-wrap">
{(enCours.journal?.logs || []).map((l) => `${l.ts} [${l.niveau}] ${l.message}`).join('\n') || 'En attente de logs…'}
                        </pre>
                    </div>
                )}

                {/* Filtres : statut (API) + plage de dates + fenêtre */}
                <div className="glass-panel rounded-2xl p-5 relative z-50">
                    <div className="flex flex-wrap items-end gap-3">
                        <div>
                            <label className="config-form-label">Statut</label>
                            <SelectDropdown
                                options={statuts}
                                value={statut}
                                onChange={setStatut}
                                labelTous="Tous les statuts"
                            />
                        </div>
                        <div>
                            <label className="config-form-label">Date début</label>
                            <input type="date" value={date_debut} onChange={(e) => setDateDebut(e.target.value)} className={inputDateClass} />
                        </div>
                        <div>
                            <label className="config-form-label">Date fin</label>
                            <input type="date" value={date_fin} onChange={(e) => setDateFin(e.target.value)} className={inputDateClass} />
                        </div>
                        <div>
                            <label className="config-form-label">Fenêtre début</label>
                            <input type="date" value={fenetre_debut} onChange={(e) => setFenetreDebut(e.target.value)} className={inputDateClass} />
                        </div>
                        <div>
                            <label className="config-form-label">Fenêtre fin</label>
                            <input type="date" value={fenetre_fin} onChange={(e) => setFenetreFin(e.target.value)} className={inputDateClass} />
                        </div>
                        <button onClick={filtrer} className="config-btn config-btn-primary">
                            <Filter className="w-4 h-4" /> Filtrer
                        </button>
                        <ResetFiltreButton actif={!!filtresActifs} onClick={resetFilter} />
                    </div>
                </div>

                {/* Historique */}
                {loading && liste.length === 0 ? (
                    <TableSkeleton />
                ) : liste.length === 0 ? (
                    <div className="empty-state">
                        <RefreshCw className="empty-state-icon" />
                        <p className="empty-state-title">Aucune synchronisation trouvée.</p>
                        <p className="empty-state-subtitle">Aucune donnée de synchronisation n'est disponible.</p>
                    </div>
                ) : (
                    <>
                        <div className="section-header">
                            <div>
                                <h2 className="section-title">Liste des synchronisations</h2>
                                <span className="section-count">{total} synchronisation(s)</span>
                            </div>
                        </div>
                        <GenericTable columns={columns} data={liste} />
                        <Pagination
                            page={currentPage}
                            pageSize={pageSize}
                            totalPages={totalPages}
                            total={total}
                            loading={loading}
                            showAll={showAll}
                            onPageChange={setCurrentPage}
                            onPageSizeChange={(size) => {
                                if (size === 'all') {
                                    setShowAll(true);
                                    setCurrentPage(1);
                                } else {
                                    setShowAll(false);
                                    setPageSize(size);
                                    setCurrentPage(1);
                                }
                            }}
                        />
                    </>
                )}
            </div>
        </PageLayout>
    );
}

export default SynchronisationListe;
