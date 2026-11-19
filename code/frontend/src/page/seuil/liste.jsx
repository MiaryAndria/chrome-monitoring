import { useState, useEffect } from 'react';
import { getListeSeuilPage, deleteSeuil, getListeCategorieSeuil } from '../../fonction/seuilFonction';
import { useNavigate } from 'react-router-dom';
import { Gauge, Plus, Pencil, Trash2 } from 'lucide-react';
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

function SeuilListe() {
    const navigate = useNavigate();
    const [currentPage, setCurrentPage] = useState(1);
    const [pageSize, setPageSize] = useState(10);
    const [showAll, setShowAll] = useState(false);
    const [refresh, setRefresh] = useState(0);
    const [categorie, setCategorie] = useState('');
    const [categories, setCategories] = useState([]);
    const [type, setType] = useState('');
    const debouncedType = useDebounce(type, 300);
    const [error, setError] = useState(null);
    const filtresActifs = type !== "" || categorie !== "";

    const { items: seuils, total, totalPages, loading } = usePaginatedData(
        getListeSeuilPage,
        showAll ? 1 : currentPage,
        showAll ? 10000 : pageSize,
        { refresh, categorie: categorie || undefined, type: debouncedType || undefined }
    );

    const chargerCategories = async () => {
        try {
            const data = await getListeCategorieSeuil();
            setCategories(data || []);
        } catch (e) {
            setError(e.response?.data?.error);
        }
    };

    const supprimerSeuil = async (id) => {
        try {
            await deleteSeuil(id);
            setRefresh(r => r + 1);
        } catch (e) {
            setError(e.response?.data?.error);
        }
    };

    const reinitialiserFiltres = () => {
        setCategorie("");
        setType("");
    };

    const columns = [
        { header: 'Catégorie', className: 'w-[15%]', render: (s) => <span className="text-zinc-400">{s.categorie}</span> },
        { header: 'Type', className: 'w-[22%]', render: (s) => <span className="font-bold text-zinc-100">{s.cle}</span> },
        { header: 'Valeur', className: 'w-[12%]', render: (s) => <span className="text-zinc-300">{s.valeur} {s.unite === '%' ? '%' : <span className="text-zinc-500 text-xs">(entier)</span>}</span> },
        { header: 'Limite', className: 'w-[12%]', render: (s) => <span className="text-zinc-300">{s.limite ?? '—'}{s.limite != null ? (s.unite === '%' ? ' %' : ' (entier)') : ''}</span> },
        { header: 'Sens', className: 'w-[8%]', render: (s) => <span className="font-mono text-zinc-300">{s.sens ?? '—'}</span> },
        {
            header: 'Date', className: 'w-[14%] text-right', render: (s) => s.date ? (
                <span className="text-zinc-400 text-xs font-mono">
                    <span className="block">{new Date(s.date).toLocaleDateString('fr-FR')}</span>
                    <span className="block">{new Date(s.date).toLocaleTimeString('fr-FR')}</span>
                </span>
            ) : <span className="text-zinc-500">-</span>
        },
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

    useEffect(() => {
        chargerCategories();
    }, []);

    useEffect(() => {
        setCurrentPage(1);
    }, [categorie, type, debouncedType]);

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
                            <label className="config-form-label">Type de seuil</label>
                            <input
                                type="text"
                                placeholder="Rechercher un type…"
                                value={type}
                                onChange={(e) => setType(e.target.value)}
                                className="w-full px-3 py-2 rounded-lg bg-zinc-900/60 border border-white/10 text-zinc-200 text-sm placeholder-zinc-500 focus:outline-none focus:border-cyan-400/50"
                            />
                        </div>
                        <ResetFiltreButton actif={filtresActifs} onClick={reinitialiserFiltres} />
                    </div>
                </div>

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

export default SeuilListe;
