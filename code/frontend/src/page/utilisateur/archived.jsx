import { useState } from 'react';
import { getListeArchiverPage, restaurerUtilisateur } from '../../fonction/userFonction';
import { Archive, RotateCcw } from 'lucide-react';
import PageLayout from '../../components/PageLayout';
import GenericTable from '../../components/GenericTable';
import Pagination from '../../components/Pagination';
import TableSkeleton from '../../components/skeletons/TableSkeleton';
import usePaginatedData from '../../hooks/usePaginatedData';
import '../../css/liste.css';
import '../../css/configuration.css';

function ArchivedUtilisateur() {
    const [currentPage, setCurrentPage] = useState(1);
    const [pageSize, setPageSize] = useState(10);
    const [refresh, setRefresh] = useState(0);

    const { items: users, total, totalPages, loading } = usePaginatedData(
        getListeArchiverPage,
        currentPage,
        pageSize,
        { refresh }
    );

    const restaurer = async (id) => {
        try {
            await restaurerUtilisateur(id);
            setRefresh(r => r + 1);
        } catch (e) {
            console.log(e);
        }
    };

    const columns = [
        { header: 'Nom', className: 'w-[22%]', render: (u) => <span className="font-bold text-zinc-100">{u.nom}</span> },
        { header: 'Email', className: 'w-[28%]', render: (u) => <span className="text-zinc-300 font-mono text-xs">{u.email}</span> },
        { header: 'Rôle', className: 'w-[18%]', render: (u) => <span className="text-zinc-300">{u.role}</span> },
        { header: 'Date', className: 'w-[12%] text-right', render: (u) => u.date ? (
            <span className="text-zinc-400 text-xs font-mono">
                <span className="block">{new Date(u.date).toLocaleDateString('fr-FR')}</span>
                <span className="block">{new Date(u.date).toLocaleTimeString('fr-FR')}</span>
            </span>
        ) : <span className="text-zinc-500">-</span> },
        {
            header: 'Actions', sticky: true, className: 'w-[20%] text-right', render: (u) => (
                <div className="config-table-actions">
                    <button onClick={() => restaurer(u.id)} className="config-btn config-btn-success" style={{ padding: '0.4rem 0.75rem', fontSize: '0.7rem' }}>
                        <RotateCcw className="w-3.5 h-3.5" /> Restaurer
                    </button>
                </div>
            )
        }
    ];

    return (
        <PageLayout
            title="Utilisateurs archivés"
            subtitle="Comptes supprimés pouvant être restaurés"
            titleIcon={Archive}
        >
            <div className="space-y-6">
                {loading && users.length === 0 ? (
                    <TableSkeleton />
                ) : !users || users.length === 0 ? (
                    <div className="empty-state">
                        <Archive className="empty-state-icon" />
                        <p className="empty-state-title">Aucun utilisateur archivé.</p>
                        <p className="empty-state-subtitle">Aucune donnée archivée n'est disponible.</p>
                    </div>
                ) : (
                    <>
                        <div className="section-header">
                            <div>
                                <h2 className="section-title">Liste des utilisateurs archivés</h2>
                                <span className="section-count">{total} archivé(s)</span>
                            </div>
                        </div>
                        <GenericTable columns={columns} data={users} />

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

export default ArchivedUtilisateur;
