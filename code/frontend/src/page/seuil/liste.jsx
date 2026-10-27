import { useState } from 'react';
import { getListeSeuilPage, deleteSeuil } from '../../fonction/seuilFonction';
import { useNavigate } from 'react-router-dom';
import { Gauge, Plus, Pencil, Trash2 } from 'lucide-react';
import PageLayout from '../../components/PageLayout';
import GenericTable from '../../components/GenericTable';
import Pagination from '../../components/Pagination';
import TableSkeleton from '../../components/skeletons/TableSkeleton';
import usePaginatedData from '../../hooks/usePaginatedData';
import '../../css/liste.css';
import '../../css/configuration.css';

function SeuilListe() {
    const navigate = useNavigate();
    const [currentPage, setCurrentPage] = useState(1);
    const [pageSize, setPageSize] = useState(10);
    const [refresh, setRefresh] = useState(0);

    const { items: seuils, total, totalPages, loading } = usePaginatedData(
        getListeSeuilPage,
        currentPage,
        pageSize,
        { refresh }
    );

    const supprimerSeuil = async (id) => {
        try {
            await deleteSeuil(id);
            setRefresh(r => r + 1);
        } catch (e) {
            console.log(e);
        }
    };

    const columns = [
        { header: 'Clé', className: 'w-[18%]', render: (s) => <span className="font-bold text-zinc-100">{s.cle}</span> },
        { header: 'Valeur', className: 'w-[55%]', render: (s) => <span className="text-zinc-300">{s.valeur}</span> },
        { header: 'Date', className: 'w-[12%] text-right', render: (s) => s.date ? (
            <span className="text-zinc-400 text-xs font-mono">
                <span className="block">{new Date(s.date).toLocaleDateString('fr-FR')}</span>
                <span className="block">{new Date(s.date).toLocaleTimeString('fr-FR')}</span>
            </span>
        ) : <span className="text-zinc-500">-</span> },
        {
            header: 'Actions', sticky: true, className: 'w-[15%] text-right', render: (s) => (
                <div className="config-table-actions">
                    <button onClick={() => navigate(`/update/seuil/${s.id}`)} className="config-btn config-btn-primary" style={{ padding: '0.4rem 0.75rem', fontSize: '0.7rem' }}>
                        <Pencil className="w-3.5 h-3.5" /> Modifier
                    </button>
                    <button onClick={() => supprimerSeuil(s.id)} className="config-btn config-btn-danger" style={{ padding: '0.4rem 0.75rem', fontSize: '0.7rem' }}>
                        <Trash2 className="w-3.5 h-3.5" /> Supprimer
                    </button>
                </div>
            )
        }
    ];

    return (
        <PageLayout
            title="Seuils"
            subtitle="Gérer les seuils du système"
            titleIcon={Gauge}
            headerRight={
                <button onClick={() => navigate('/creer/seuil')} className="config-btn config-btn-primary">
                    <Plus className="w-4 h-4" /> Créer seuil
                </button>
            }
        >
            <div className="space-y-6">
                {loading && seuils.length === 0 ? (
                    <TableSkeleton />
                ) : !seuils || seuils.length === 0 ? (
                    <div className="empty-state">
                        <Gauge className="empty-state-icon" />
                        <p className="empty-state-title">Aucun seuil trouvé.</p>
                        <p className="empty-state-subtitle">Aucune donnée de seuil n'est disponible.</p>
                    </div>
                ) : (
                    <>
                        <div className="section-header">
                            <div>
                                <h2 className="section-title">Liste des seuils</h2>
                                <span className="section-count">{total} seuil(s)</span>
                            </div>
                        </div>
                        <GenericTable columns={columns} data={seuils} />

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
            </div>
        </PageLayout>
    );
}

export default SeuilListe;
