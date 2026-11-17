import { useEffect, useState } from "react";
import { Printer, Search, LayoutGrid, List } from "lucide-react";
import GenericTable from "../../components/GenericTable";
import PageLayout from "../../components/PageLayout";
import EmptyState from "../../components/EmptyState";
import Pagination from "../../components/Pagination";
import PrinterListSkeleton from "../../components/skeletons/PrinterListSkeleton";
import usePaginatedData from "../../hooks/usePaginatedData";
import useDebounce from "../../hooks/useDebounce";
import DateHeureFilter from "../component/DateHeureFilter";
import { getImprimantes, getVendors } from "../../fonction/imprimanteFonction";
import StatutDropdown from "../component/StatutDropdown";
import ImprimanteCard from "../component/component_imprimante";
import '../../css/liste.css';
import '../../css/filiale.css';
import { useNavigate } from 'react-router-dom';

function ListeImprimante() {
    const [search, setSearch] = useState("");
    const debouncedSearch = useDebounce(search, 300);
    const [currentPage, setCurrentPage] = useState(1);
    const [pageSize, setPageSize] = useState(10);
    const [viewMode, setViewMode] = useState('grid');
    const [dateDebut, setDateDebut] = useState('');
    const [heureDebut, setHeureDebut] = useState('00:00');
    const [dateFin, setDateFin] = useState('');
    const [heureFin, setHeureFin] = useState('23:59');
    const [datetimeFrom, setDatetimeFrom] = useState('');
    const [datetimeTo, setDatetimeTo] = useState('');
    const [vendors, setVendors] = useState([]);
    const [vendor, setVendor] = useState("");
    const [erreurFiltreDate, setErreurFiltreDate] = useState('');
    const [allImprimantes, setAllImprimantes] = useState([]);
    const [tablePage, setTablePage] = useState(1);
    const [loadingAll, setLoadingAll] = useState(false);
    const tablePageSize = 10;
    const navigate = useNavigate();

    const filtresImprimante = {
        recherche: debouncedSearch || undefined,
        vendor: vendor || undefined,
        datetime_from: datetimeFrom || undefined,
        datetime_to: datetimeTo || undefined,
    };

    const { items: imprimantes, total, totalPages, loading, error } = usePaginatedData(
        getImprimantes,
        currentPage,
        pageSize,
        filtresImprimante
    );

    const chargerToutesLesImprimantes = async () => {
        setLoadingAll(true);
        try {
            const data = await getImprimantes({ page: 1, page_size: 10000, ...filtresImprimante });
            setAllImprimantes(data?.items || []);
        } catch (e) {
            console.log(e);
            setAllImprimantes([]);
        } finally {
            setLoadingAll(false);
        }
    };

    const imprimanteColumns = [
        { header: "Fabricant", render: (imp) => <span className="font-bold text-zinc-100">{imp.vendor || '-'}</span> },
        { header: "Modèle / Nom", accessor: "nom" },
        { header: "VID", render: (imp) => <span className="font-mono text-zinc-400">{imp.vid || '-'}</span> },
        { header: "PID", render: (imp) => <span className="font-mono text-zinc-400">{imp.pid || '-'}</span> },
    ];

    const chargerVendors = async () => {
        const data = await getVendors();
        setVendors(data);
    };

    const filtrerParDate = () => {
        setErreurFiltreDate('');
        if (!dateDebut && !dateFin) {
            setDatetimeFrom('');
            setDatetimeTo('');
            setCurrentPage(1);
            return;
        }
        setDatetimeFrom(dateDebut ? `${dateDebut}T${heureDebut || '00:00'}:00` : '');
        setDatetimeTo(dateFin ? `${dateFin}T${heureFin || '23:59'}:59` : '');
        setCurrentPage(1);
    };

    const resetDate = () => {
        setErreurFiltreDate('');
        setDateDebut('');
        setHeureDebut('00:00');
        setDateFin('');
        setHeureFin('23:59');
        setDatetimeFrom('');
        setDatetimeTo('');
        setCurrentPage(1);
    };

    useEffect(() => {
        chargerVendors();
    }, []);

    useEffect(() => {
        if (error) {
            setErreurFiltreDate(error?.response?.data?.error || error?.response?.data?.detail || '');
        }
    }, [error]);

    useEffect(() => {
        setCurrentPage(1);
        setTablePage(1);
    }, [search, vendor, datetimeFrom, datetimeTo, debouncedSearch]);

    useEffect(() => {
        if (viewMode === 'table') {
            chargerToutesLesImprimantes();
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [viewMode, search, vendor, datetimeFrom, datetimeTo, debouncedSearch]);

    const tableTotal = allImprimantes.length;
    const tableTotalPages = Math.max(1, Math.ceil(tableTotal / tablePageSize));
    const tablePageCourante = Math.min(tablePage, tableTotalPages);
    const tableImprimantes = allImprimantes.slice((tablePageCourante - 1) * tablePageSize, tablePageCourante * tablePageSize);

    return (
        <PageLayout
            title="Imprimantes"
            subtitle="Périphériques d'impression détectés sur le parc"
            titleIcon={Printer}
            contentClassName="space-y-8"
        >
            {/* Recherche */}
            <div className="glass-panel rounded-2xl p-5">
                        <div className="flex flex-wrap items-center gap-4">
                            <div className="relative max-w-md flex-1 min-w-[240px]">
                                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
                                <input type="text" placeholder="Rechercher par fabricant, nom, VID, PID..."
                                    value={search} onChange={e => setSearch(e.target.value)}
                                    className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-zinc-900/60 border border-white/10 text-zinc-200 text-sm placeholder-zinc-500 focus:outline-none focus:border-amber-400/50 focus:ring-1 focus:ring-amber-400/20 transition-all" />
                            </div>
                            <div className="flex items-center gap-2">
                                <span className="text-[10px] text-zinc-500 uppercase font-semibold tracking-wider">Fabricant :</span>
                                <StatutDropdown
                                    listeStatuts={vendors.map(v => ({ nom: v }))}
                                    statut={vendor}
                                    setStatut={setVendor}
                                    labelTous="Tous les fabricants"
                                />
                            </div>
                        </div>

                        <div className="mt-4 pt-4 border-t border-white/5 space-y-3">
                            <DateHeureFilter
                                dateDebut={dateDebut}
                                heureDebut={heureDebut}
                                dateFin={dateFin}
                                heureFin={heureFin}
                                setDateDebut={setDateDebut}
                                setHeureDebut={setHeureDebut}
                                setDateFin={setDateFin}
                                setHeureFin={setHeureFin}
                                onFilter={filtrerParDate}
                                onReset={resetDate}
                            />
                            {erreurFiltreDate && (
                                <p className="text-xs text-red-400 bg-red-500/10 border border-red-500/30 p-2.5 rounded-lg">
                                    {erreurFiltreDate}
                                </p>
                            )}
                        </div>
                    </div>

                    {/* Contenu */}
                    {viewMode === 'table' ? (
                        loadingAll && allImprimantes.length === 0 ? (
                            <PrinterListSkeleton viewMode={viewMode} />
                        ) : allImprimantes.length === 0 ? (
                            <EmptyState
                                icon={Printer}
                                title="Aucune imprimante trouvée"
                                subtitle={search || vendor ? "Modifiez vos filtres" : "Aucune donnée disponible"}
                            />
                        ) : (
                            <>
                                <div className="section-header flex justify-between items-center">
                                    <div>
                                        <h2 className="section-title">Modèles détectés</h2>
                                        <span className="section-count">
                                            {tableTotal} modèle{tableTotal > 1 ? "s" : ""} — Page {tablePageCourante}/{tableTotalPages}
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
                                <GenericTable columns={imprimanteColumns} data={tableImprimantes} onRowClick={(imp) => navigate(`/imprimante/${imp.id}`)} />
                                <Pagination
                                    page={tablePageCourante}
                                    pageSize={tablePageSize}
                                    totalPages={tableTotalPages}
                                    total={tableTotal}
                                    loading={loadingAll}
                                    onPageChange={setTablePage}
                                />
                            </>
                        )
                    ) : loading && imprimantes.length === 0 ? (
                        <PrinterListSkeleton viewMode={viewMode} />
                    ) : error ? (
                        <EmptyState icon={Printer} title="Impossible de charger les imprimantes." />
                    ) : total === 0 ? (
                        <EmptyState
                            icon={Printer}
                            title="Aucune imprimante trouvée"
                            subtitle={search || vendor ? "Modifiez vos filtres" : "Aucune donnée disponible"}
                        />
                    ) : (
                        <>
                            <div className="section-header flex justify-between items-center">
                                <div>
                                    <h2 className="section-title">Modèles détectés</h2>
                                    <span className="section-count">
                                        {total} modèle{total > 1 ? "s" : ""} — Page {currentPage}/{totalPages}
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

                            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                                {imprimantes.map((imp, idx) => (
                                    <ImprimanteCard key={imp.id ?? idx} imp={imp} onClick={() => navigate(`/imprimante/${imp.id}`)} />
                                ))}
                            </div>

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
            </PageLayout>
    );
}

export default ListeImprimante;