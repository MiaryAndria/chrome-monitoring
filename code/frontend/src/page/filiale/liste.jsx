import { useState } from "react";
import { Building2, Laptop, ChevronRight, Server, Activity, LayoutGrid, List } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import Navbar from "../../components/Navbar";
import MouseSpotlight from "../../components/MouseSpotlight";
import GenericTable from "../../components/GenericTable";
import Pagination from "../../components/Pagination";
import CardGridSkeleton from "../../components/skeletons/CardGridSkeleton";
import usePaginatedData from "../../hooks/usePaginatedData";
import '../../css/liste.css';
import '../../css/filiale.css';
import { getListeFilialePage } from "../../fonction/filialeFonction";

const CARD_VARIANTS = ['cyan', 'purple', 'emerald', 'amber'];

function getOrgLabel(path) {
    if (!path) return 'Organisation';
    const parts = path.split('/').filter(Boolean);
    return parts[parts.length - 1] || path;
}

function getOrgDepth(path) {
    if (!path) return 0;
    return path.split('/').filter(Boolean).length;
}

function ListeFiliale() {
    const [viewMode, setViewMode] = useState('grid');
    const [currentPage, setCurrentPage] = useState(1);
    const [pageSize, setPageSize] = useState(10);
    const navigate = useNavigate();

    const { items: filiales, total, totalPages, loading } = usePaginatedData(
        getListeFilialePage,
        currentPage,
        pageSize,
        {}
    );

    const filialeColumns = [
        { header: "ID", accessor: "id" },
        { header: "Nom", render: (f) => <span className="font-bold text-zinc-100">{getOrgLabel(f.org_unit_path)}</span> },
        { header: "Chemin Complet", render: (f) => <span className="text-zinc-400 text-xs font-mono">{f.org_unit_path}</span> },
        { header: "Niveau", render: (f) => getOrgDepth(f.org_unit_path) > 1 ? <span className="badge badge-sm badge-outline text-emerald-400 border-emerald-500/30">Niveau {getOrgDepth(f.org_unit_path)}</span> : '-' },
        { header: "Actions", render: (f) => (
            <button onClick={() => navigate(`/filiale/${f.id}/devices`)} className="px-3 py-1.5 text-xs font-semibold text-zinc-300 bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 rounded-xl transition-all flex items-center gap-1">
                Voir devices <ChevronRight className="w-3.5 h-3.5" />
            </button>
        ) }
    ];

    return (
        <div className="device-layout" data-theme="dark">
            <MouseSpotlight />

            <div className="flex-1 flex flex-col h-screen overflow-hidden relative z-10">
                <div className="bg-glow-cyan"></div>
                <div className="bg-glow-purple"></div>

                <Navbar />

                <div className="flex-1 overflow-y-auto p-6 lg:p-8 space-y-8 z-10">
                    {/* Liste filiales */}
                    <div>
                        <div className="section-header flex justify-between items-center">
                            <div>
                                <h2 className="section-title">Filiales &amp; Unités Organisationnelles</h2>
                                <h3 className="section-subtitle">Cliquez sur une filiale pour voir ses devices</h3>
                                <span className="section-count">{total} unité(s)</span>
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

                        {loading && filiales.length === 0 ? (
                            <CardGridSkeleton />
                        ) : filiales.length === 0 ? (
                            <div className="empty-state">
                                <Building2 className="empty-state-icon" />
                                <p className="empty-state-title">Aucune filiale trouvée.</p>
                                <p className="empty-state-subtitle">Lancez une synchronisation pour importer les données.</p>
                            </div>
                        ) : viewMode === 'table' ? (
                            <GenericTable columns={filialeColumns} data={filiales} />
                        ) : (
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                                {filiales.map((f, index) => {
                                    const variant = CARD_VARIANTS[index % CARD_VARIANTS.length];
                                    const label = getOrgLabel(f.org_unit_path);
                                    const depth = getOrgDepth(f.org_unit_path);

                                    return (
                                        <div
                                            key={f.id}
                                            className={`filiale-card filiale-card--${variant}`}
                                            onClick={() => navigate(`/filiale/${f.id}/devices`)}
                                        >
                                            <div className="filiale-card-glow"></div>

                                            <div className="filiale-card-icon">
                                                <Building2 className="filiale-card-icon-svg" />
                                            </div>

                                            <div className="filiale-card-content">
                                                <h3 className="filiale-card-title" title={f.org_unit_path}>
                                                    {label}
                                                </h3>
                                                <p className="filiale-card-path" title={f.org_unit_path}>
                                                    {f.org_unit_path}
                                                </p>
                                                {depth > 1 && (
                                                    <span className="filiale-depth-badge">Niveau {depth}</span>
                                                )}
                                            </div>

                                            <div className="filiale-card-footer">
                                                <span className="filiale-card-id">
                                                    <Server className="w-3 h-3" /> ID #{f.id}
                                                </span>
                                                <div className="filiale-see-btn">
                                                    Voir devices <ChevronRight className="w-3.5 h-3.5" />
                                                </div>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        )}

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
                    </div>
                </div>
            </div>
        </div>
    );
}

export default ListeFiliale;
