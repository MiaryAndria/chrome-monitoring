import { useState, useEffect } from 'react';
import { getListeArchiverPage, restaurerConfiguration, supprimerConfiguration } from '../../fonction/configurationFonction';
import { Archive, RotateCcw, Trash2 } from 'lucide-react';
import PageLayout from '../../components/PageLayout';
import GenericTable from '../../components/GenericTable';
import Pagination from '../../components/Pagination';
import TableSkeleton from '../../components/skeletons/TableSkeleton';
import usePaginatedData from '../../hooks/usePaginatedData';
import '../../css/liste.css';
import '../../css/configuration.css';

function ArchivedConfiguration() {
    const [currentPage, setCurrentPage] = useState(1);
    const [pageSize, setPageSize] = useState(10);
    const [showAll, setShowAll] = useState(false);
    const [refresh, setRefresh] = useState(0);
    const [selectedItem, setSelectedItem] = useState([]);
    const [deleteStatut, setDelete] = useState(false);
    const [restoreStatut, setRestaurer] = useState(false);
    const [columns, setColumns] = useState([]);

    const { items: conf, total, totalPages, loading } = usePaginatedData(
        getListeArchiverPage,
        showAll ? 1 : currentPage,
        showAll ? 10000 : pageSize,
        { refresh }
    );

    const deleteConfig = async () => {
        if (deleteStatut === true) {
            setDelete(false)
        } else {
            setDelete(true)
        }
    }

    const RestoreConfig = async () => {
        if (restoreStatut === true) {
            setRestaurer(false)
        } else {
            setRestaurer(true)
        }
    }

    const restaurer = async () => {
        for (const id of selectedItem) {
            try {
                await restaurerConfiguration(id);
            } catch (e) {
                console.log(e);
            }
        }
        setSelectedItem([]);
        setRefresh(r => r + 1)
        setRestaurer(false);
    };

    const supprimer = async () => {
        if (!window.confirm("Êtes-vous sûr de supprimer ces paramètres ?")) {
            return
        }
        for (const id of selectedItem) {
            try {
                await supprimerConfiguration(id);
            } catch (e) {
                console.log(e);
            }
        }
        setSelectedItem([]);
        setRefresh(r => r + 1)
        setDelete(false);
    };

    const handleCheckboxChange = (id) => {
        setSelectedItem(prev => {
            if (prev.includes(id)) {
                return prev.filter(item => item !== id);
            } else {
                return [...prev, id];
            }
        });
    };

    useEffect(() => {
        if (deleteStatut===true || restoreStatut === true) {
            setColumns([
                {
                    header: "",
                    className: "w-10",
                    render: (c) => < input
                        type="checkbox"
                        checked={selectedItem.includes(c.id)}
                        onChange={() => handleCheckboxChange(c.id)
                        } />

                },
                { header: 'Catégorie', className: 'w-[18%]', render: (c) => <span className="text-zinc-400">{c.categorie}</span> },
                { header: 'Type', className: 'w-[30%]', render: (c) => <span className="font-bold text-zinc-100">{c.cle}</span> },
                { header: 'Valeur', className: 'w-[15%]', render: (c) => <span className="text-zinc-300">{c.valeur}</span> },
                {
                    header: 'Date', className: 'w-[15%] text-right', render: (c) => c.date ? (
                        <span className="text-zinc-400 text-xs font-mono">
                            <span className="block">{new Date(c.date).toLocaleDateString('fr-FR')}</span>
                            <span className="block">{new Date(c.date).toLocaleTimeString('fr-FR')}</span>
                        </span>
                    ) : <span className="text-zinc-500">-</span>
                },
            ]);
        }

        else if (deleteStatut===false|| restoreStatut === false) {
            setColumns([
                { header: 'Catégorie', className: 'w-[18%]', render: (c) => <span className="text-zinc-400">{c.categorie}</span> },
                { header: 'Type', className: 'w-[30%]', render: (c) => <span className="font-bold text-zinc-100">{c.cle}</span> },
                { header: 'Valeur', className: 'w-[15%]', render: (c) => <span className="text-zinc-300">{c.valeur}</span> },
                {
                    header: 'Date', className: 'w-[15%] text-right', render: (c) => c.date ? (
                        <span className="text-zinc-400 text-xs font-mono">
                            <span className="block">{new Date(c.date).toLocaleDateString('fr-FR')}</span>
                            <span className="block">{new Date(c.date).toLocaleTimeString('fr-FR')}</span>
                        </span>
                    ) : <span className="text-zinc-500">-</span>
                },
            ]);
        }

    }, [selectedItem, restoreStatut, deleteStatut])

    return (
        <PageLayout
            title="Configurations archivées"
            subtitle="Configurations supprimées pouvant être restaurées"
            titleIcon={Archive}
        >
            {restoreStatut ? (
                <button onClick={restaurer} className="config-btn config-btn-success" style={{ padding: '0.4rem 0.75rem', fontSize: '0.7rem' }}>
                    <RotateCcw className="w-3.5 h-3.5" /> Restaurer {selectedItem.length} configurations.
                </button>
            ) : (
                <button onClick={RestoreConfig} className="config-btn config-btn-success" style={{ padding: '0.4rem 0.75rem', fontSize: '0.7rem' }}>
                    <RotateCcw className="w-3.5 h-3.5" /> Restaurer configuration
                </button>
            )}

            {deleteStatut ? (
                <button onClick={supprimer} className="config-btn config-btn-danger" style={{ padding: '0.4rem 0.75rem', fontSize: '0.7rem' }}>
                    <Trash2 className="w-3.5 h-3.5" /> Supprimer {selectedItem.length} configurations.
                </button>
            ) : (
                <button onClick={deleteConfig} className="config-btn config-btn-danger" style={{ padding: '0.4rem 0.75rem', fontSize: '0.7rem' }}>
                    <Trash2 className="w-3.5 h-3.5" /> Supprimer configuration
                </button>

            )}

            <div className="space-y-6">
                {loading && conf.length === 0 ? (
                    <TableSkeleton />
                ) : !conf || conf.length === 0 ? (
                    <div className="empty-state">
                        <Archive className="empty-state-icon" />
                        <p className="empty-state-title">Aucune configuration archivée.</p>
                        <p className="empty-state-subtitle">Aucune donnée archivée n'est disponible.</p>
                    </div>
                ) : (
                    <>
                        <div className="section-header">
                            <div>
                                <h2 className="section-title">Liste des configurations archivées</h2>
                                <span className="section-count">{total} archivée(s)</span>
                            </div>
                        </div>
                        <GenericTable columns={columns} data={conf} />

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

export default ArchivedConfiguration;
