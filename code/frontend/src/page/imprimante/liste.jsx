import { useEffect, useState } from "react";
import { Printer, Search, RefreshCw, Hash, Tag } from "lucide-react";
import Sidebar from "../../components/Sidebar";
import Navbar from "../../components/Navbar";
import MouseSpotlight from "../../components/MouseSpotlight";
import { getListeImprimante } from "../../fonction/imprimanteFonction";

function ImprimanteCard({ imp }) {
    return (
        <div className="glass-panel rounded-2xl border border-white/5 p-5 flex flex-col gap-3 hover:border-amber-500/20 hover:bg-amber-500/[0.03] transition-all duration-200 group">
            {/* Icône + fabricant */}
            <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center flex-shrink-0 group-hover:bg-amber-500/20 transition-colors">
                    <Printer className="w-5 h-5 text-amber-400" />
                </div>
                <div className="min-w-0">
                    <p className="text-sm font-bold text-zinc-200 group-hover:text-amber-300 transition-colors truncate">
                        {imp.vendor || <span className="text-zinc-600 font-normal">Fabricant inconnu</span>}
                    </p>
                    <p className="text-xs text-zinc-500 truncate mt-0.5">
                        {imp.nom || "Modèle inconnu"}
                    </p>
                </div>
            </div>

            {/* Séparateur */}
            <div className="border-t border-white/5" />

            {/* VID / PID */}
            <div className="grid grid-cols-2 gap-2">
                <div className="bg-zinc-800/50 rounded-lg p-2.5 text-center border border-white/5">
                    <p className="text-[10px] text-zinc-500 uppercase font-semibold mb-0.5">VID</p>
                    <p className="text-xs font-mono font-bold text-zinc-300">
                        {imp.vid ?? <span className="text-zinc-600">—</span>}
                    </p>
                </div>
                <div className="bg-zinc-800/50 rounded-lg p-2.5 text-center border border-white/5">
                    <p className="text-[10px] text-zinc-500 uppercase font-semibold mb-0.5">PID</p>
                    <p className="text-xs font-mono font-bold text-zinc-300">
                        {imp.pid ?? <span className="text-zinc-600">—</span>}
                    </p>
                </div>
            </div>

            {/* ID interne */}
            <p className="text-[10px] text-zinc-600 font-mono text-center">
                #{imp.id}
            </p>
        </div>
    );
}

function ListeImprimante() {
    const [imprimantes, setImprimantes] = useState([]);
    const [loading, setLoading] = useState(false);
    const [search, setSearch] = useState("");
    const [error, setError] = useState(null);

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

    const filtered = imprimantes.filter(imp => {
        const q = search.toLowerCase();
        return (
            (imp.vendor || "").toLowerCase().includes(q) ||
            (imp.nom || "").toLowerCase().includes(q) ||
            String(imp.vid || "").includes(q) ||
            String(imp.pid || "").includes(q)
        );
    });

    return (
        <div className="device-layout" data-theme="dark">
            <MouseSpotlight />
            <Sidebar />

            <div className="flex-1 flex flex-col h-screen overflow-hidden relative z-10">
                <div className="bg-glow-cyan"></div>
                <div className="bg-glow-purple"></div>
                <Navbar />

                <div className="flex-1 overflow-y-auto p-6 lg:p-8 space-y-6 z-10">
                    {/* Header */}
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                        <div>
                            <h1 className="text-3xl font-bold tracking-tight text-zinc-100 flex items-center gap-3">
                                <Printer className="w-8 h-8 text-amber-400" />
                                Imprimantes
                            </h1>
                            <p className="text-zinc-400 mt-1 font-medium tracking-wide">
                                Modèles uniques détectés via télémétrie USB
                            </p>
                        </div>
                        <button onClick={charger} disabled={loading}
                            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-zinc-800/60 border border-white/10 text-zinc-300 text-sm font-medium hover:bg-zinc-700/60 transition-all disabled:opacity-50 self-start md:self-auto">
                            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
                            Actualiser
                        </button>
                    </div>

                    {/* Recherche */}
                    <div className="relative max-w-md">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
                        <input type="text" placeholder="Rechercher par fabricant, nom, VID, PID..."
                            value={search} onChange={e => setSearch(e.target.value)}
                            className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-zinc-800/60 border border-white/10 text-zinc-200 text-sm placeholder-zinc-500 focus:outline-none focus:border-amber-400/50 focus:ring-1 focus:ring-amber-400/20 transition-all" />
                    </div>

                    {/* Contenu */}
                    {loading ? (
                        <div className="flex justify-center items-center py-20">
                            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-400" />
                        </div>
                    ) : error ? (
                        <div className="glass-panel p-8 text-center rounded-2xl border border-red-500/20">
                            <Printer className="w-12 h-12 text-red-400 mx-auto mb-3 opacity-50" />
                            <p className="text-red-400 font-medium">{error}</p>
                        </div>
                    ) : filtered.length === 0 ? (
                        <div className="glass-panel p-12 text-center rounded-2xl border border-white/5">
                            <Printer className="w-14 h-14 text-zinc-600 mx-auto mb-4" />
                            <p className="text-zinc-400 text-lg font-medium">Aucune imprimante trouvée</p>
                            <p className="text-zinc-600 text-sm mt-1">
                                {search ? "Modifiez votre recherche" : "Aucune donnée disponible"}
                            </p>
                        </div>
                    ) : (
                        <>
                            <p className="text-sm text-zinc-500">
                                <span className="font-semibold text-zinc-300">{filtered.length}</span>
                                {" "}modèle{filtered.length > 1 ? "s" : ""} unique{filtered.length > 1 ? "s" : ""}
                            </p>
                            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
                                {filtered.map((imp, idx) => (
                                    <ImprimanteCard key={imp.id ?? idx} imp={imp} />
                                ))}
                            </div>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
}

export default ListeImprimante;