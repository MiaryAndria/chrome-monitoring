import { useState, useEffect } from 'react';
import { getListeConfigurationPage, deleteConfiguration, getListeCategorieConfiguration } from '../../fonction/configurationFonction';
import { useNavigate } from 'react-router-dom';
import { Settings, Plus, Pencil, Trash2 } from 'lucide-react';
import PageLayout from '../../components/PageLayout';
import SelectDropdown from '../component/SelectDropdown';
import GenericTable from '../../components/GenericTable';
import Pagination from '../../components/Pagination';
import TableSkeleton from '../../components/skeletons/TableSkeleton';
import usePaginatedData from '../../hooks/usePaginatedData';
import useDebounce from '../../hooks/useDebounce';
import ResetFiltreButton from '../component/ResetFiltreButton';
import '../../css/liste.css';
import '../../css/configuration.css';

function ConfigurationListe() {
    const navigate = useNavigate();
    const [currentPage, setCurrentPage] = useState(1);
    const [pageSize, setPageSize] = useState(10);
    const [showAll, setShowAll] = useState(false);
    const [refresh, setRefresh] = useState(0);
    const [categorie, setCategorie] = useState('');
    const [categories, setCategories] = useState([]);
    const [type, setType] = useState('');
    const [deleteStatut, setDelete] = useState(false);
    const debouncedType = useDebounce(type, 300);
    const [selectedItem, setSelectedItem] = useState([]);
    const [error, setError] = useState(null);
    const filtresActifs = type !== "" || categorie !== "";
    const [columns, setColumns] = useState([]);

    const { items: conf, total, totalPages, loading } = usePaginatedData(
        getListeConfigurationPage,
        showAll ? 1 : currentPage,
        showAll ? 10000 : pageSize,
        { refresh, categorie: categorie || undefined, type: debouncedType || undefined }
    );

    const chargerCategories = async () => {
        try {
            const data = await getListeCategorieConfiguration();
            setCategories(data || []);
        } catch (e) {
            setError(e.response?.data?.error);
        }
    };

    const deleteConfig = async () => {
        if (deleteStatut === true) {
            setDelete(false)
        } else {
            setDelete(true)
        }
    }

    const supprimerConfiguration = async () => {
        for (const id of selectedItem) {
            try {
                await deleteConfiguration(id);
                setRefresh(r => r + 1)
            } catch (e) {
                setError(e.response?.data?.error);
            }
        }
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

    const reinitialiserFiltres = () => {
        setCategorie("");
        setType("");
    };

    useEffect(() => {
        if (deleteStatut === true) {
            setColumns([
                {
                    header: "",
                    className: "w-10",
                    render: (c) => (
                        <input
                            type="checkbox"
                            checked={selectedItem.includes(c.id)}
                            onChange={() => handleCheckboxChange(c.id)}
                        />
                    )
                },
                { header: 'Catégorie', className: 'w-[18%]', render: (c) => <span className="text-zinc-400">{c.categorie}</span> },
                { header: 'Type', className: 'w-[25%]', render: (c) => <span className="font-bold text-zinc-100">{c.cle}</span> },
                { header: 'Valeur', className: 'w-[15%]', render: (c) => <span className="text-zinc-300">{c.valeur}</span> },
                {
                    header: 'Date',
                    className: 'w-[15%] text-right',
                    render: (c) => c.date ? (
                        <span className="text-zinc-400 text-xs font-mono">
                            <span className="block">{new Date(c.date).toLocaleDateString('fr-FR')}</span>
                            <span className="block">{new Date(c.date).toLocaleTimeString('fr-FR')}</span>
                        </span>
                    ) : <span className="text-zinc-500">-</span>
                },
                {
                    header: 'Actions',
                    sticky: true,
                    className: 'w-[15%] text-right',
                    render: (c) => (
                        <div className="config-table-actions">
                            <button onClick={() => navigate(`/update/configuration/${c.id}`)} className="config-btn config-btn-primary" style={{ padding: '0.4rem 0.75rem', fontSize: '0.7rem' }}>
                                <Pencil className="w-3.5 h-3.5" /> Modifier
                            </button>
                        </div>
                    )
                }
            ]);

        } else {
            setColumns([
                { header: 'Catégorie', className: 'w-[18%]', render: (c) => <span className="text-zinc-400">{c.categorie}</span> },
                { header: 'Type', className: 'w-[25%]', render: (c) => <span className="font-bold text-zinc-100">{c.cle}</span> },
                { header: 'Valeur', className: 'w-[15%]', render: (c) => <span className="text-zinc-300">{c.valeur}</span> },
                {
                    header: 'Date',
                    className: 'w-[15%] text-right',
                    render: (c) => c.date ? (
                        <span className="text-zinc-400 text-xs font-mono">
                            <span className="block">{new Date(c.date).toLocaleDateString('fr-FR')}</span>
                            <span className="block">{new Date(c.date).toLocaleTimeString('fr-FR')}</span>
                        </span>
                    ) : <span className="text-zinc-500">-</span>
                },
                {
                    header: 'Actions',
                    sticky: true,
                    className: 'w-[15%] text-right',
                    render: (c) => (
                        <div className="config-table-actions">
                            <button onClick={() => navigate(`/update/configuration/${c.id}`)} className="config-btn config-btn-primary" style={{ padding: '0.4rem 0.75rem', fontSize: '0.7rem' }}>
                                <Pencil className="w-3.5 h-3.5" /> Modifier
                            </button>
                        </div>
                    )
                }
            ]);
        }
    }, [deleteStatut, selectedItem, navigate]);


    useEffect(() => {
        chargerCategories();
    }, []);

    useEffect(() => {
        setCurrentPage(1);
    }, [categorie, type, debouncedType]);

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
                {error && (
                    <div className="text-xs text-red-400 bg-red-500/10 border border-red-500/30 p-2.5 rounded-lg">
                        {error}
                    </div>
                )}
                <div className="glass-panel rounded-2xl p-5 relative z-50">
                    <div className="flex flex-wrap items-end gap-3">
                        <div>
                            <label className="config-form-label">Catégorie</label>
                            <SelectDropdown
                                options={categories.map((c) => ({ value: c.categorie, label: c.categorie }))}
                                value={categorie}
                                onChange={(value) => setCategorie(value)}
                                labelTous="Toutes les catégories"
                            />
                        </div>
                        <div className="min-w-[240px]">
                            <label className="config-form-label">Type de configuration</label>
                            <input
                                type="text"
                                placeholder="Rechercher un type…"
                                value={type}
                                onChange={(e) => setType(e.target.value)}
                                className="w-full px-3 py-2 rounded-lg bg-zinc-900/60 border border-white/10 text-zinc-200 text-sm placeholder-zinc-500 focus:outline-none focus:border-cyan-400/50"
                            />
                        </div>
                        {deleteStatut ? (
                            <button onClick={supprimerConfiguration}className="config-btn config-btn-danger" style={{ padding: '0.4rem 0.75rem', fontSize: '0.7rem' }}>
                                <Trash2 className="w-3.5 h-3.5" />Supprimer les {selectedItem.length} configurations sélectionnées
                            </button>
                        ) : (
                            <button onClick={deleteConfig}className="config-btn config-btn-danger" style={{ padding: '0.4rem 0.75rem', fontSize: '0.7rem' }}>
                                <Trash2 className="w-3.5 h-3.5" />Supprimer Configuration
                            </button>
                        )}
                        <ResetFiltreButton actif={filtresActifs} onClick={reinitialiserFiltres} />
                    </div>
                </div>

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
                        <GenericTable columns={columns} data={conf} onRowClick={conf.id} />

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

export default ConfigurationListe;
