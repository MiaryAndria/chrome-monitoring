import { useEffect, useState } from "react";
import { Printer, Search, LayoutGrid, List } from "lucide-react";
import GenericTable from "../../components/GenericTable";
import PageLayout from "../../components/PageLayout";
import EmptyState from "../../components/EmptyState";
import { getListeImprimante } from "../../fonction/imprimanteFonction";
import ImprimanteCard from "../component/component_imprimante";
import '../../css/liste.css';
import '../../css/filiale.css';

function ListeImprimante() {
    const [imprimantes, setImprimantes] = useState([]);
    const [loading, setLoading] = useState(false);
    const [search, setSearch] = useState("");
    const [error, setError] = useState(null);
    const [currentPage, setCurrentPage] = useState(1);
    const [viewMode, setViewMode] = useState('grid');
    const itemsPerPage = 20;

    const imprimanteColumns = [
        { header: "Fabricant", render: (imp) => <span className="font-bold text-zinc-100">{imp.vendor || '-'}</span> },
        { header: "Modèle / Nom", accessor: "nom" },
        { header: "VID", render: (imp) => <span className="font-mono text-zinc-400">{imp.vid || '-'}</span> },
        { header: "PID", render: (imp) => <span className="font-mono text-zinc-400">{imp.pid || '-'}</span> },
    ];

    const charger = async () => {
        try {
            setLoading(true);
            setError(null);
            const data = await getListeImprimante();
            setImprimantes(data || []);
        } catch (e) {
            console.error(e);
            setError("Impossible de charger les imprimantes.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { charger(); }, []);

    // Reset pagination when search changes
    useEffect(() => {
        setCurrentPage(1);
    }, [search]);

    const filtered = imprimantes.filter(imp => {
        const q = search.toLowerCase();
        return (
            (imp.vendor || "").toLowerCase().includes(q) ||
            (imp.nom || "").toLowerCase().includes(q) ||
            String(imp.vid || "").includes(q) ||
            String(imp.pid || "").includes(q)
        );
    });

    const totalPages = Math.ceil(filtered.length / itemsPerPage) || 1;
    const indexOfLastItem = currentPage * itemsPerPage;
    const indexOfFirstItem = indexOfLastItem - itemsPerPage;
    const currentItems = filtered.slice(indexOfFirstItem, indexOfLastItem);

    return (
        <PageLayout
            title="Imprimantes"
            subtitle="Périphériques d'impression détectés sur le parc"
            titleIcon={Printer}
            contentClassName="space-y-8"
        >
            {/* Recherche */}
            <div className="glass-panel rounded-2xl p-5">
                        <div className="relative max-w-md">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
                            <input type="text" placeholder="Rechercher par fabricant, nom, VID, PID..."
                                value={search} onChange={e => setSearch(e.target.value)}
                                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-zinc-900/60 border border-white/10 text-zinc-200 text-sm placeholder-zinc-500 focus:outline-none focus:border-amber-400/50 focus:ring-1 focus:ring-amber-400/20 transition-all" />
                        </div>
                    </div>

                    {/* Contenu */}
                    {loading ? (
                        <div className="flex justify-center p-12">
                            <span className="loading loading-infinity loading-lg text-amber-500"></span>
                        </div>
                    ) : error ? (
                        <EmptyState icon={Printer} title={error} />
                    ) : filtered.length === 0 ? (
                        <EmptyState
                            icon={Printer}
                            title="Aucune imprimante trouvée"
                            subtitle={search ? "Modifiez votre recherche" : "Aucune donnée disponible"}
                        />
                    ) : (
                        <>
                            <div className="section-header flex justify-between items-center">
                                <div>
                                    <h2 className="section-title">Modèles détectés</h2>
                                    <span className="section-count">
                                        {filtered.length} modèle{filtered.length > 1 ? "s" : ""} — Page {currentPage}/{totalPages}
                                    </span>
                                </div>
                                <div className="flex bg-zinc-900 rounded-lg p-1 border border-white/10">
                                    <button 
                                        onClick={() => setViewMode('grid')}
                                        className={`p-1.5 rounded-md transition-colors ${viewMode === 'grid' ? 'bg-cyan-500/20 text-cyan-400' : 'text-zinc-500 hover:text-zinc-300'}`}
                                        title="Vue en grille"
                                    >
                                        <LayoutGrid className="w-4 h-4" />
                                    </button>
                                    <button 
                                        onClick={() => setViewMode('table')}
                                        className={`p-1.5 rounded-md transition-colors ${viewMode === 'table' ? 'bg-cyan-500/20 text-cyan-400' : 'text-zinc-500 hover:text-zinc-300'}`}
                                        title="Vue en tableau"
                                    >
                                        <List className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>

                            {viewMode === 'table' ? (
                                <GenericTable columns={imprimanteColumns} data={currentItems} />
                            ) : (
                                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                                    {currentItems.map((imp, idx) => (
                                        <ImprimanteCard key={imp.id ?? idx} imp={imp} />
                                    ))}
                                </div>
                            )}

                            {/* Pagination */}
                            {totalPages > 1 && (
                                <div className="flex justify-center items-center gap-4 mt-8 pb-4">
                                    <button
                                        className="pagination-btn"
                                        disabled={currentPage === 1}
                                        onClick={() => setCurrentPage(currentPage - 1)}
                                    >
                                        Précédent
                                    </button>
                                    <div className="pagination-indicator">
                                        {currentPage} <span className="pagination-separator">/</span> {totalPages}
                                    </div>
                                    <button
                                        className="pagination-btn"
                                        disabled={currentPage === totalPages}
                                        onClick={() => setCurrentPage(currentPage + 1)}
                                    >
                                        Suivant
                                    </button>
                                </div>
                            )}
                        </>
                    )}
            </PageLayout>
    );
}

export default ListeImprimante;