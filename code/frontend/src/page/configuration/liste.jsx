import { useState } from 'react';
import { getListeConfigurationPage, deleteConfiguration } from '../../fonction/configurationFonction';
import { useNavigate } from 'react-router-dom';
import { Settings, Plus, Pencil, Trash2 } from 'lucide-react';
import PageLayout from '../../components/PageLayout';
import GenericTable from '../../components/GenericTable';
import Pagination from '../../components/Pagination';
import TableSkeleton from '../../components/skeletons/TableSkeleton';
import usePaginatedData from '../../hooks/usePaginatedData';
import '../../css/liste.css';
import '../../css/configuration.css';

function ConfigurationListe() {
    const navigate = useNavigate();
    const [currentPage, setCurrentPage] = useState(1);
    const [pageSize, setPageSize] = useState(10);
    const [refresh, setRefresh] = useState(0);

    const { items: conf, total, totalPages, loading } = usePaginatedData(
        getListeConfigurationPage,
        currentPage,
        pageSize,
        { refresh }
    );

    const supprimerConfiguration = async (id) => {
        try {
            await deleteConfiguration(id);
            setRefresh(r => r + 1);
        } catch (e) {
            console.log(e);
        }
    };

    const columns = [
        { header: 'Type', className: 'w-[18%]', render: (c) => <span className="font-bold text-zinc-100">{c.type}</span> },
        { header: 'Valeur', className: 'w-[55%]', render: (c) => <span className="text-zinc-300">{c.valeur}</span> },
        { header: 'Date', className: 'w-[12%] text-right', render: (c) => c.date ? (
            <span className="text-zinc-400 text-xs font-mono">
                <span className="block">{new Date(c.date).toLocaleDateString('fr-FR')}</span>
                <span className="block">{new Date(c.date).toLocaleTimeString('fr-FR')}</span>
            </span>
        ) : <span className="text-zinc-500">-</span> },
        {
            header: 'Actions', sticky: true, className: 'w-[15%] text-right', render: (c) => (
                <div className="config-table-actions">
                    <button onClick={() => navigate(`/update/configuration/${c.id}`)} className="config-btn config-btn-primary" style={{ padding: '0.4rem 0.75rem', fontSize: '0.7rem' }}>
                        <Pencil className="w-3.5 h-3.5" /> Modifier
                    </button>
                    <button onClick={() => supprimerConfiguration(c.id)} className="config-btn config-btn-danger" style={{ padding: '0.4rem 0.75rem', fontSize: '0.7rem' }}>
                        <Trash2 className="w-3.5 h-3.5" /> Supprimer
                    </button>
                </div>
            )
        }
    ];

    return (
        <PageLayout
            title="Configurations"
            subtitle="Gérer les configurations du système"
            titleIcon={Settings}
            headerRight={
                <button onClick={() => navigate('/creer/configuration')} className="config-btn config-btn-primary">
                    <Plus className="w-4 h-4" /> Créer configuration
                </button>
            }
        >
            <div className="space-y-6">
                {loading && conf.length === 0 ? (
                    <TableSkeleton />
                ) : !conf || conf.length === 0 ? (
                    <div className="empty-state">
                        <Settings className="empty-state-icon" />
                        <p className="empty-state-title">Aucune configuration trouvée.</p>
                        <p className="empty-state-subtitle">Aucune donnée de configuration n'est disponible.</p>
                    </div>
                ) : (
                    <>
                        <div className="section-header">
                            <div>
                                <h2 className="section-title">Liste des configurations</h2>
                                <span className="section-count">{total} configuration(s)</span>
                            </div>
                        </div>
                        <GenericTable columns={columns} data={conf} />

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

export default ConfigurationListe;
