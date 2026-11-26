import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, AlertTriangle, CheckCircle2, RefreshCw } from 'lucide-react';
import { getDetailSynchronisation } from '../../fonction/synchronisationFonction';
import PageLayout from '../../components/PageLayout';
import '../../css/liste.css';

const fmtDate = (d) => (d ? new Date(d).toLocaleString('fr-FR') : '-');

function DetailSynchronisation() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [detail, setDetail] = useState(null);

    useEffect(() => {
        getDetailSynchronisation(id).then(setDetail);
    }, [id]);

    if (!detail) {
        return <div className="text-zinc-400 p-6">Chargement…</div>;
    }

    const journal = detail.journal || {};

    return (
        <PageLayout
            title={`Synchronisation #${detail.id}`}
            subtitle="Détails, journal et logs de la synchronisation"
            titleIcon={RefreshCw}
        >
            <div className="space-y-6">
                <button
                    onClick={() => navigate(-1)}
                    className="flex items-center gap-2 text-zinc-400 hover:text-zinc-100 text-sm"
                >
                    <ArrowLeft className="w-4 h-4" /> Retour
                </button>

                <div className="glass-panel rounded-2xl p-5 grid grid-cols-2 md:grid-cols-3 gap-3 text-xs">
                    <div><span className="text-zinc-500">Source</span><br />{detail.source}</div>
                    <div><span className="text-zinc-500">Statut</span><br />{detail.statut}</div>
                    <div><span className="text-zinc-500">Durée</span><br />{detail.duree_s != null ? `${Number(detail.duree_s).toFixed(1)} s` : '-'}</div>
                    <div><span className="text-zinc-500">Date début</span><br />{fmtDate(detail.date_debut)}</div>
                    <div><span className="text-zinc-500">Date fin</span><br />{fmtDate(detail.date_fin)}</div>
                    <div><span className="text-zinc-500">Lignes</span><br />{detail.nb_lignes}</div>
                    <div><span className="text-zinc-500">Fenêtre début</span><br />{fmtDate(detail.fenetre_debut)}</div>
                    <div><span className="text-zinc-500">Fenêtre fin</span><br />{fmtDate(detail.fenetre_fin)}</div>
                </div>

                <div className="glass-panel rounded-2xl p-5">
                    <h4 className="text-sm font-semibold text-zinc-200 mb-2">Compteurs</h4>
                    <pre className="text-[11px] bg-black/30 rounded-lg p-3 overflow-x-auto text-cyan-300">
{JSON.stringify(journal.compteurs || {}, null, 2)}
                    </pre>
                </div>

                <div className="glass-panel rounded-2xl p-5">
                    <h4 className="text-sm font-semibold text-zinc-200 mb-2">Durées par étape (s)</h4>
                    <pre className="text-[11px] bg-black/30 rounded-lg p-3 overflow-x-auto text-zinc-300">
{JSON.stringify(journal.etapes_s || {}, null, 2)}
                    </pre>
                </div>

                <div className="glass-panel rounded-2xl p-5">
                    <h4 className="text-sm font-semibold text-zinc-200 mb-2 flex items-center gap-2">
                        <AlertTriangle className="w-4 h-4 text-amber-400" />
                        Erreurs ({(journal.erreurs || []).length})
                    </h4>
                    {(journal.erreurs || []).length === 0 ? (
                        <p className="text-xs text-emerald-400 flex items-center gap-1">
                            <CheckCircle2 className="w-3.5 h-3.5" /> Aucune erreur
                        </p>
                    ) : (
                        (journal.erreurs || []).map((err, i) => (
                            <div key={i} className="text-[11px] bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2 text-red-300 mb-1">
                                <span className="font-semibold">[{err.etape}]</span>
                                {err.reference ? ` ${err.reference} —` : ''} {err.message}
                            </div>
                        ))
                    )}
                </div>

                <div className="glass-panel rounded-2xl p-5">
                    <h4 className="text-sm font-semibold text-zinc-200 mb-2">Logs ({(journal.logs || []).length})</h4>
                    <pre className="text-[11px] bg-black/40 rounded-lg p-3 max-h-80 overflow-auto text-zinc-400 whitespace-pre-wrap">
{(journal.logs || []).map((l) => `${l.ts} [${l.niveau}] ${l.message}`).join('\n') || 'Aucun log'}
                    </pre>
                </div>

                {detail.message && (
                    <div className="text-xs text-red-300 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2">
                        {detail.message}
                    </div>
                )}
            </div>
        </PageLayout>
    );
}

export default DetailSynchronisation;
