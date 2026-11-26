import { useState, useEffect } from 'react';
import { getListeArchiverPage, restaurerSeuil, supprimerSeuil } from '../../fonction/seuilFonction';
import { Archive, RotateCcw, Trash2 } from 'lucide-react';
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
    const [showAll, setShowAll] = useState(false);
    const [refresh, setRefresh] = useState(0);
    const [selectedItem, setSelectedItem] = useState([]);
    const [deleteStatut, setDelete] = useState(false);
    const [restoreStatut, setRestaurer] = useState(false);
    const [columns, setColumns] = useState([]);
    const { items: seuils, total, totalPages, loading } = usePaginatedData(
        getListeArchiverPage,
        showAll ? 1 : currentPage,
        showAll ? 10000 : pageSize,
        { refresh }
    );

    const restaurer = async () => {
        for (const id of selectedItem) {
            try {
                await restaurerSeuil(id);
            } catch (e) {
                console.log(e);
            }
        }
        setSelectedItem([]);
        setRefresh(r => r + 1);
        setRestaurer(false);
    };

    const deleteSeuil = async () => {
        if (deleteStatut === true) {
            setDelete(false)
        } else {
            setDelete(true)
        }
    }

    const RestoreSeuil = async () => {
        if (restoreStatut === true) {
            setRestaurer(false)
        } else {
            setRestaurer(true)
        }
    }


    const handleCheckboxChange = (id) => {
        setSelectedItem(prev => {
            if (prev.includes(id)) {
                return prev.filter(item => item !== id);
            } else {
                return [...prev, id];
            }
        });
    };

    const supprimer = async () => {
        if (!window.confirm("Êtes-vous sûr de supprimer ces seuils ?")) {
            return
        }
        for (const id of selectedItem) {
            try {
                await supprimerSeuil(id);
            } catch (e) {
                console.log(e)
            }
        }
        setSelectedItem([]);
        setRefresh(r => r + 1);
        setDelete(false);
    }

    useEffect(() => {
        if (deleteStatut ==true || restoreStatut == true) {
            setColumns([
                {
                    header: '', className: 'w-[15%]', render: (s) =>
                        <input type="checkbox"
                            checked={selectedItem.includes(s.id)}
                            onChange={() => handleCheckboxChange(s.id)
                            }
                        />
                },
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
            ]);
        }
        else if (deleteStatut ==true || restoreStatut === false) {
            setColumns([
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
            ]);
        }
    }, [selectedItem, restoreStatut, deleteStatut])


    return (
        <PageLayout
            title="Seuils archivés"
            subtitle="Seuils supprimés pouvant être restaurés"
            titleIcon={Archive}
        >
            {restoreStatut ? (
                <button onClick={restaurer} className="config-btn config-btn-success" style={{ padding: '0.4rem 0.75rem', fontSize: '0.7rem' }}>
                    <RotateCcw className="w-3.5 h-3.5" /> Restaurer {selectedItem.length} seuils
                </button>
            ) : (
                <button onClick={RestoreSeuil} className="config-btn config-btn-success" style={{ padding: '0.4rem 0.75rem', fontSize: '0.7rem' }}>
                    <RotateCcw className="w-3.5 h-3.5" /> Restaurer seuil
                </button>
            )}
            {deleteStatut ? (
                <button onClick={supprimer} className="config-btn config-btn-danger" style={{ padding: '0.4rem 0.75rem', fontSize: '0.7rem' }}>
                    <Trash2 className="w-3.5 h-3.5" /> Supprimer {selectedItem.length} seuils
                </button>
            ) : (
                <button onClick={deleteSeuil} className="config-btn config-btn-danger" style={{ padding: '0.4rem 0.75rem', fontSize: '0.7rem' }}>
                    <Trash2 className="w-3.5 h-3.5" /> Supprimer seuil
                </button>
            )}
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

export default ArchivedSeuil;
