import { useState } from 'react';
import { getListeStatutPage } from '../../fonction/statutFonction';
import { useNavigate } from 'react-router-dom';
import { Tags, Pencil } from 'lucide-react';
import PageLayout from '../../components/PageLayout';
import GenericTable from '../../components/GenericTable';
import Pagination from '../../components/Pagination';
import TableSkeleton from '../../components/skeletons/TableSkeleton';
import usePaginatedData from '../../hooks/usePaginatedData';
import '../../css/liste.css';
import '../../css/configuration.css';

function StatutListe() {
    const navigate = useNavigate();
    const [currentPage, setCurrentPage] = useState(1);
    const [pageSize, setPageSize] = useState(10);

    const { items: statuts, total, totalPages, loading } = usePaginatedData(
        getListeStatutPage,
        currentPage,
        pageSize,
        {}
    );

    const columns = [
        { header: 'ID', className: 'w-[10%]', render: (s) => <span className="font-mono text-zinc-400">{s.id}</span> },
        { header: 'Nom', className: 'w-[70%]', render: (s) => <span className="font-bold text-zinc-100">{s.nom}</span> },
        {
            header: 'Actions', sticky: true, className: 'w-[20%] text-right', render: (s) => (
                <div className="config-table-actions">
                    <button onClick={() => navigate(`/update/statut/${s.id}`)} className="config-btn config-btn-primary" style={{ padding: '0.4rem 0.75rem', fontSize: '0.7rem' }}>
                        <Pencil className="w-3.5 h-3.5" /> Modifier
                    </button>
                </div>
            )
        }
    ];

    return (
        <PageLayout
            title="Statuts"
            subtitle="Gérer les libellés des statuts"
            titleIcon={Tags}
        >
            <div className="space-y-6">
                {loading && statuts.length === 0 ? (
                    <TableSkeleton />
                ) : statuts.length === 0 ? (
                    <div className="empty-state">
                        <Tags className="empty-state-icon" />
                        <p className="empty-state-title">Aucun statut trouvé.</p>
                        <p className="empty-state-subtitle">Aucune donnée de statut n'est disponible.</p>
                    </div>
                ) : (
                    <>
                        <div className="section-header">
                            <div>
                                <h2 className="section-title">Liste des statuts</h2>
                                <span className="section-count">{total} statut(s)</span>
                            </div>
                        </div>
                        <GenericTable columns={columns} data={statuts} />

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

export default StatutListe;
