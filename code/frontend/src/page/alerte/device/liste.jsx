import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bell } from 'lucide-react';
import PageLayout from '../../../components/PageLayout';
import GenericTable from '../../../components/GenericTable';
import TableSkeleton from '../../../components/skeletons/TableSkeleton';
import { getListeAlerte, getListeAlertePage } from '../../../fonction/alerteFonction';
import '../../../css/liste.css';
import '../../../css/configuration.css';
import usePaginatedData from '../../../hooks/usePaginatedData';
import Pagination from '../../../components/Pagination';

function ListeDeviceAlerte() {
    const navigate = useNavigate();
    const [page, setPage] = useState(1);
    const [pageSize, setPageSize] = useState(10);
    const [dateDebut, setDateDebut] = useState('');
    const [dateFin, setDateFin] = useState('');
    const [Loading, setLoading] = useState(false);

    const { items: liste, total, totalPages, loading } = usePaginatedData(
        getListeAlertePage,
        page,
        pageSize,
        { date_debut: dateDebut || undefined, date_fin: dateFin || undefined }
    );

    // un changement de filtre repart en page 1
    useEffect(() => {
        setPage(1);
        setLoading(true);
        let annule = false;
        getListeAlerte(dateDebut || undefined, dateFin || undefined)
            .then((data) => {
                if (!annule) setListe(data ?? []);
            })
            .catch((e) => {
                if (!annule) console.log(e);
            })
            .finally(() => {
                if (!annule) setLoading(false);
            });

        return () => {
            annule = true;
        };
    }, [dateDebut, dateFin]);


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
            subtitle="Toutes les alertes détectées (filtrables par date)"
            titleIcon={Bell}
        >
            <div className="space-y-6">
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
                    <button
                        className="config-btn config-btn-ghost"
                        onClick={() => { setDateDebut(''); setDateFin(''); }}
                    >
                        Réinitialiser
                    </button>
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
