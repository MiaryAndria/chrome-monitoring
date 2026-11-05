import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { GitCompare, Repeat, ArrowLeftRight } from "lucide-react";
import PageLayout from "../../components/PageLayout";
import { listeComparaison } from "../../fonction/comparaisonFonction";
import "../../css/liste.css";
import "../../css/filiale.css";

function Comparaison() {
    const navigate = useNavigate();
    const [liste, setListe] = useState([]);
    const [chargement, setChargement] = useState(true);

    const chargerHistorique = async () => {
        try {
            const data = await listeComparaison();
            setListe(data || []);
        } catch (e) {
            console.log(e);
        } finally {
            setChargement(false);
        }
    };

    useEffect(() => {
        chargerHistorique();
    }, []);

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

            <div className="glass-panel rounded-2xl p-5">
                <h2 className="section-title mb-3">Historique</h2>
                {chargement ? (
                    <p className="text-sm text-zinc-500">Chargement…</p>
                ) : liste.length === 0 ? (
                    <p className="text-sm text-zinc-500">Aucune comparaison enregistrée.</p>
                ) : (
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
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </PageLayout>
    );
}

export default Comparaison;
