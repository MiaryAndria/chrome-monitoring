import { useState } from 'react';
import { getListeArchiverPage, restaurerSeuil,supprimerSeuil } from '../../fonction/seuilFonction';
import { Archive, RotateCcw ,Trash2} from 'lucide-react';
import PageLayout from '../../components/PageLayout';
import GenericTable from '../../components/GenericTable';
import Pagination from '../../components/Pagination';
import TableSkeleton from '../../components/skeletons/TableSkeleton';
import usePaginatedData from '../../hooks/usePaginatedData';
import '../../css/liste.css';
import '../../css/configuration.css';

function ArchivedSeuil() {
    const [currentPage, setCurrentPage] = useState(1);
    const [pageSize, setPageSize] = useState(10);
    const [refresh, setRefresh] = useState(0);

    const { items: seuils, total, totalPages, loading } = usePaginatedData(
        getListeArchiverPage,
        currentPage,
        pageSize,
        { refresh }
    );

    const restaurer = async (id) => {
        try {
            await restaurerSeuil(id);
            setRefresh(r => r + 1);
        } catch (e) {
            console.log(e);
        }
    };

    const supprimer = async(id)=>{
        if (!window.confirm("Êtes-vous sûr de supprimer cet paramètres?")) return;
        try{
            await supprimerSeuil(id);
            setRefresh(r=>r+1);
        }catch(e){
            console.log(e)
        }
    }

    const columns = [
        { header: 'Catégorie', className: 'w-[18%]', render: (s) => <span className="text-zinc-400">{s.categorie}</span> },
        { header: 'Type', className: 'w-[30%]', render: (s) => <span className="font-bold text-zinc-100">{s.cle}</span> },
        { header: 'Valeur', className: 'w-[15%]', render: (s) => <span className="text-zinc-300">{s.valeur}</span> },
        {
            header: 'Date', className: 'w-[15%] text-right', render: (s) => s.date ? (
                <span className="text-zinc-400 text-xs font-mono">
                    <span className="block">{new Date(s.date).toLocaleDateString('fr-FR')}</span>
                    <span className="block">{new Date(s.date).toLocaleTimeString('fr-FR')}</span>
                </span>
            ) : <span className="text-zinc-500">-</span>
        },
        {
            header: 'Actions', sticky: true, className: 'w-[15%] text-right', render: (s) => (
                <div className="config-table-actions">
                    <button onClick={() => restaurer(s.id)} className="config-btn config-btn-success" style={{ padding: '0.4rem 0.75rem', fontSize: '0.7rem' }}>
                        <RotateCcw className="w-3.5 h-3.5" /> Restaurer
                    </button>
                </div>
            )
        },
        {
            header: 'Actions', sticky: true, className: 'w-[15%] text-right', render: (s) => (
                <div className="config-table-actions">
                    <button onClick={() => supprimer(s.id)} className="config-btn config-btn-danger" style={{ padding: '0.4rem 0.75rem', fontSize: '0.7rem' }}>
                        <Trash2 className="w-3.5 h-3.5" /> Supprimer
                    </button>
                </div>
            )
        }
    ];

    return (
        <PageLayout
            title="Seuils archivés"
            subtitle="Seuils supprimés pouvant être restaurés"
            titleIcon={Archive}
        >
            <div className="space-y-6">
                {loading && seuils.length === 0 ? (
                    <TableSkeleton />
                ) : !seuils || seuils.length === 0 ? (
                    <div className="empty-state">
                        <Archive className="empty-state-icon" />
                        <p className="empty-state-title">Aucun seuil archivé.</p>
                        <p className="empty-state-subtitle">Aucune donnée archivée n'est disponible.</p>
                    </div>
                ) : (
                    <>
                        <div className="section-header">
                            <div>
                                <h2 className="section-title">Liste des seuils archivés</h2>
                                <span className="section-count">{total} archivé(s)</span>
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

export default ArchivedSeuil;
