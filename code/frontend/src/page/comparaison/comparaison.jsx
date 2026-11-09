import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { GitCompare, Repeat, ArrowLeftRight } from "lucide-react";
import PageLayout from "../../components/PageLayout";
import Pagination from "../../components/Pagination";
import DateHeureFilter from "../component/DateHeureFilter";
import usePaginatedData from "../../hooks/usePaginatedData";
import { listeComparaisonPage } from "../../fonction/comparaisonFonction";
import "../../css/liste.css";
import "../../css/filiale.css";

function Comparaison() {
    const navigate = useNavigate();
    const [currentPage, setCurrentPage] = useState(1);
    const [pageSize, setPageSize] = useState(10);

    const [dateDebut, setDateDebut] = useState('');
    const [heureDebut, setHeureDebut] = useState('00:00');
    const [dateFin, setDateFin] = useState('');
    const [heureFin, setHeureFin] = useState('23:59');
    const [datetimeDebutApplique, setDatetimeDebutApplique] = useState('');
    const [datetimeFinApplique, setDatetimeFinApplique] = useState('');

    const { items: liste, total, totalPages, loading } = usePaginatedData(
        listeComparaisonPage,
        currentPage,
        pageSize,
        {
            datetime_from: datetimeDebutApplique || undefined,
            datetime_to: datetimeFinApplique || undefined,
        }
    );

    const filtrer = () => {
        if (!dateDebut || !dateFin) {
            window.alert("Choisissez une date de début et une date de fin.");
            return;
        }
        if (dateDebut > dateFin || (dateDebut === dateFin && heureDebut > heureFin)) {
            window.alert("L'heure de début doit être antérieure ou égale à l'heure de fin.");
            return;
        }
        setDatetimeDebutApplique(`${dateDebut}T${heureDebut || '00:00'}:00`);
        setDatetimeFinApplique(`${dateFin}T${heureFin || '23:59'}:59`);
        setCurrentPage(1);
    };

    const reinitialiser = () => {
        setDateDebut('');
        setHeureDebut('00:00');
        setDateFin('');
        setHeureFin('23:59');
        setDatetimeDebutApplique('');
        setDatetimeFinApplique('');
        setCurrentPage(1);
    };

    return (
        <PageLayout
            title="Comparaisons"
            subtitle="Historique et nouvelle comparaison"
            titleIcon={GitCompare}
            contentClassName="space-y-6"
        >
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <button
                    onClick={() => navigate("/comparaison/single")}
                    className="glass-panel rounded-2xl p-5 text-left border border-white/10 hover:border-cyan-400/40 transition-all cursor-pointer"
                >
                    <Repeat className="w-5 h-5 text-cyan-300 mb-2" />
                    <div className="font-semibold text-zinc-100">Comparaison simple</div>
                    <div className="text-xs text-zinc-400 mt-1">Un appareil, deux versions de ChromeOS.</div>
                </button>
                <button
                    onClick={() => navigate("/comparaison/double")}
                    className="glass-panel rounded-2xl p-5 text-left border border-white/10 hover:border-purple-400/40 transition-all cursor-pointer"
                >
                    <ArrowLeftRight className="w-5 h-5 text-purple-300 mb-2" />
                    <div className="font-semibold text-zinc-100">Comparaison double</div>
                    <div className="text-xs text-zinc-400 mt-1">Deux appareils, une version chacun.</div>
                </button>
            </div>

            <div className="glass-panel rounded-2xl p-5 relative z-50">
                <DateHeureFilter
                    dateDebut={dateDebut}
                    heureDebut={heureDebut}
                    dateFin={dateFin}
                    heureFin={heureFin}
                    setDateDebut={setDateDebut}
                    setHeureDebut={setHeureDebut}
                    setDateFin={setDateFin}
                    setHeureFin={setHeureFin}
                    onFilter={filtrer}
                    onReset={reinitialiser}
                />
            </div>

            <div className="glass-panel rounded-2xl p-5">
                <h2 className="section-title mb-3">Historique</h2>
                {loading && liste.length === 0 ? (
                    <p className="text-sm text-zinc-500">Chargement…</p>
                ) : liste.length === 0 ? (
                    <p className="text-sm text-zinc-500">Aucune comparaison enregistrée.</p>
                ) : (
                    <>
                        <div className="overflow-x-auto">
                            <table className="w-full text-left text-sm text-zinc-300">
                                <thead className="text-[10px] uppercase bg-white/5 text-zinc-400 border-b border-white/10 tracking-wider font-semibold">
                                    <tr>
                                        <th className="px-4 py-3">Type</th>
                                        <th className="px-4 py-3">Appareil A</th>
                                        <th className="px-4 py-3">Version A</th>
                                        <th className="px-4 py-3">Appareil B</th>
                                        <th className="px-4 py-3">Version B</th>
                                        <th className="px-4 py-3">Date</th>
                                        <th className="px-4 py-3">Verdict</th>
                                        <th className="px-4 py-3 text-right">Actions</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-white/5">
                                    {liste.map((c) => (
                                        <tr key={c.id} className="hover:bg-white/5">
                                            <td className="px-4 py-3">{c.id_type_comparaison === 1 ? "Simple" : "Double"}</td>
                                            <td className="px-4 py-3 font-mono text-zinc-400">{c.device_a}</td>
                                            <td className="px-4 py-3 font-mono text-zinc-400">{c.version_a}</td>
                                            <td className="px-4 py-3 font-mono text-zinc-400">{c.device_b}</td>
                                            <td className="px-4 py-3 font-mono text-zinc-400">{c.version_b}</td>
                                            <td className="px-4 py-3 text-zinc-400">
                                                {c.date_comparaison ? new Date(c.date_comparaison).toLocaleString("fr-FR") : "—"}
                                            </td>
                                            <td className="px-4 py-3 text-zinc-300">{c.resultat?.verdict?.resume || "—"}</td>
                                            <td className="px-4 py-3 text-right">
                                                <button
                                                    onClick={() => navigate(`/comparaison/detail/${c.id}`)}
                                                    className="px-3 py-1.5 text-xs font-semibold text-cyan-300 bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 rounded-xl transition-all"
                                                >
                                                    Voir
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
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
            </div>
        </PageLayout>
    );
}

export default Comparaison;
