import { useEffect, useState } from "react";
import {
    Bell, Search, RefreshCw, Calendar, Monitor, User,
    Zap, AlertTriangle, Cpu, Layers
} from "lucide-react";
import Sidebar from "../../components/Sidebar";
import Navbar from "../../components/Navbar";
import MouseSpotlight from "../../components/MouseSpotlight";
import { getListeEvenement } from "../../fonction/eventFonction";

/* ───────────────────────────────────────────
   Styles selon type de crash / cause
─────────────────────────────────────────── */
const getStyle = (type, causeClass) => {
    const t = (type || "").toUpperCase();
    const c = (causeClass || "").toUpperCase();

    if (t.includes("KERNEL"))
        return {
            card: "border-red-500/30 bg-red-500/5",
            badge: "bg-red-500/15 text-red-400 border-red-500/30",
            icon: "text-red-400",
            dot: "bg-red-500",
            label: "Crash noyau"
        };
    if (t.includes("EMBEDDED") || t.includes("CONTROLLER") || t.includes("EC"))
        return {
            card: "border-amber-500/30 bg-amber-500/5",
            badge: "bg-amber-500/15 text-amber-400 border-amber-500/30",
            icon: "text-amber-400",
            dot: "bg-amber-500",
            label: "Ctrl embarqué"
        };
    if (t.includes("BROWSER") || t.includes("APP"))
        return {
            card: "border-purple-500/30 bg-purple-500/5",
            badge: "bg-purple-500/15 text-purple-400 border-purple-500/30",
            icon: "text-purple-400",
            dot: "bg-purple-500",
            label: "App / Navigateur"
        };
    return {
        card: "border-cyan-500/30 bg-cyan-500/5",
        badge: "bg-cyan-500/15 text-cyan-400 border-cyan-500/30",
        icon: "text-cyan-400",
        dot: "bg-cyan-500",
        label: "Autre"
    };
};

const CAUSE_LABELS = {
    "ARRET_ANORMAL": { label: "Arrêt anormal", desc: "Coupure courant / extinction forcée / plantage entre 2 sessions", color: "text-red-400" },
    "EN_SESSION":    { label: "En session",    desc: "Crash survenu pendant qu'un utilisateur était connecté",       color: "text-amber-400" },
};

const formatDate = (str) => {
    if (!str) return "—";
    try {
        return new Date(str).toLocaleString("fr-FR", {
            day: "2-digit", month: "2-digit", year: "numeric",
            hour: "2-digit", minute: "2-digit"
        });
    } catch { return str; }
};

/* ───────────────────────────────────────────
   Composant carte événement
─────────────────────────────────────────── */
function EventCard({ ev }) {
    const [open, setOpen] = useState(false);
    const style = getStyle(ev.type_evenement, ev.cause_class);
    const causeInfo = CAUSE_LABELS[ev.cause_class] || null;
    const shortType = (ev.type_evenement || "INCONNU").replace("CRASH_TYPE_", "").replace(/_/g, " ");

    return (
        <div className={`rounded-2xl border transition-all duration-200 overflow-hidden ${style.card}`}>
            {/* En-tête carte */}
            <div className="p-4">
                {/* Type + date */}
                <div className="flex items-start justify-between gap-2 mb-3">
                    <div className="flex items-center gap-2">
                        <div className={`w-2 h-2 rounded-full ${style.dot} shadow-[0_0_6px_currentColor] flex-shrink-0 mt-1`} />
                        <span className={`text-xs font-bold uppercase tracking-wide ${style.icon}`}>
                            {shortType}
                        </span>
                    </div>
                    <span className="text-[10px] text-zinc-500 whitespace-nowrap flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {formatDate(ev.date_evenement)}
                    </span>
                </div>

                {/* Cause */}
                {causeInfo && (
                    <span className={`inline-block text-[10px] font-semibold px-2 py-0.5 rounded-full border ${style.badge} mb-3`}>
                        {causeInfo.label}
                    </span>
                )}

                {/* Utilisateur */}
                {ev.last_user && (
                    <p className="text-xs text-zinc-300 flex items-center gap-1.5 mb-2 truncate">
                        <User className="w-3 h-3 text-zinc-500 flex-shrink-0" />
                        {ev.last_user}
                    </p>
                )}

                {/* Appareil */}
                <p className="text-xs font-medium text-zinc-400 flex items-center gap-1.5 truncate">
                    <Monitor className="w-3 h-3 text-zinc-600 flex-shrink-0" />
                    {ev.modele || ev.device_id || "—"}
                </p>
                {ev.serial_number && (
                    <p className="text-[10px] font-mono text-zinc-600 mt-0.5 pl-4">
                        {ev.serial_number}
                    </p>
                )}

                {/* Filiale */}
                {ev.filiale && (
                    <p className="text-[10px] text-zinc-500 mt-1 flex items-center gap-1 pl-0.5">
                        <Layers className="w-3 h-3" />
                        {ev.filiale.replace(/^\//, "")}
                    </p>
                )}
            </div>

            {/* Bouton détail */}
            <button
                onClick={() => setOpen(o => !o)}
                className="w-full px-4 py-2 border-t border-white/5 text-[10px] text-zinc-500 hover:text-zinc-300 hover:bg-white/5 transition-colors flex items-center justify-center gap-1"
            >
                {open ? "Masquer" : "Voir diagnostic"}
                <span className={`transition-transform duration-200 ${open ? "rotate-180" : ""}`}>▼</span>
            </button>

            {/* Détail expandable */}
            {open && (
                <div className="px-4 py-3 border-t border-white/5 bg-black/20 space-y-2">
                    {causeInfo && (
                        <p className="text-[11px] text-zinc-400 leading-relaxed">{causeInfo.desc}</p>
                    )}
                    {ev.cause_hint && (
                        <div className="bg-zinc-900/60 rounded-lg p-3">
                            <p className="text-[10px] text-zinc-500 uppercase font-semibold mb-1 flex items-center gap-1">
                                <Zap className="w-3 h-3" /> Analyse
                            </p>
                            <p className="text-[11px] text-zinc-300 leading-relaxed">{ev.cause_hint}</p>
                        </div>
                    )}
                    <div className="grid grid-cols-3 gap-2">
                        {ev.crash_seq != null && (
                            <div className="bg-zinc-800/50 rounded-lg p-2 text-center">
                                <p className="text-[10px] text-zinc-500">Seq.</p>
                                <p className="text-sm font-bold text-zinc-200">#{ev.crash_seq}</p>
                            </div>
                        )}
                        {ev.raw_events != null && (
                            <div className="bg-zinc-800/50 rounded-lg p-2 text-center">
                                <p className="text-[10px] text-zinc-500">Événements</p>
                                <p className="text-sm font-bold text-zinc-200">{ev.raw_events}</p>
                            </div>
                        )}
                        {ev.minutes_since_boot != null && (
                            <div className="bg-zinc-800/50 rounded-lg p-2 text-center">
                                <p className="text-[10px] text-zinc-500">Min/boot</p>
                                <p className="text-sm font-bold text-zinc-200">{Number(ev.minutes_since_boot).toFixed(0)}</p>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}

/* ───────────────────────────────────────────
   Page principale
─────────────────────────────────────────── */
function ListeEvent() {
    const [evenements, setEvenements] = useState([]);
    const [loading, setLoading] = useState(false);
    const [search, setSearch] = useState("");
    const [error, setError] = useState(null);
    const [typeFilter, setTypeFilter] = useState("TOUS");
    const [filialeFilter, setFilialeFilter] = useState("TOUS");

    const charger = async () => {
        try {
            setLoading(true);
            setError(null);
            const data = await getListeEvenement();
            setEvenements(data || []);
        } catch (e) {
            console.error(e);
            setError("Impossible de charger les événements.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { charger(); }, []);

    const types    = ["TOUS", ...new Set(evenements.map(e => e.type_evenement).filter(Boolean))];
    const filiales = ["TOUS", ...new Set(evenements.map(e => e.filiale).filter(Boolean))];

    const filtered = evenements.filter(ev => {
        const q = search.toLowerCase();
        const matchSearch = (
            (ev.type_evenement || "").toLowerCase().includes(q) ||
            (ev.cause_class || "").toLowerCase().includes(q) ||
            (ev.last_user || "").toLowerCase().includes(q) ||
            (ev.device_id || "").toLowerCase().includes(q) ||
            (ev.serial_number || "").toLowerCase().includes(q) ||
            (ev.modele || "").toLowerCase().includes(q)
        );
        const matchType    = typeFilter    === "TOUS" || ev.type_evenement === typeFilter;
        const matchFiliale = filialeFilter === "TOUS" || ev.filiale === filialeFilter;
        return matchSearch && matchType && matchFiliale;
    });

    return (
        <div className="device-layout" data-theme="dark">
            <MouseSpotlight />
            <Sidebar />

            <div className="flex-1 flex flex-col h-screen overflow-hidden relative z-10">
                <div className="bg-glow-cyan"></div>
                <div className="bg-glow-purple"></div>
                <Navbar />

                <div className="flex-1 overflow-y-auto p-6 lg:p-8 space-y-5 z-10">

                    {/* Header */}
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                        <div>
                            <h1 className="text-3xl font-bold tracking-tight text-zinc-100 flex items-center gap-3">
                                <Bell className="w-8 h-8 text-cyan-400" />
                                Événements
                            </h1>
                            <p className="text-zinc-400 mt-1 font-medium tracking-wide">
                                Journal des incidents système des appareils
                            </p>
                        </div>
                        <button onClick={charger} disabled={loading}
                            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-zinc-800/60 border border-white/10 text-zinc-300 text-sm font-medium hover:bg-zinc-700/60 transition-all disabled:opacity-50 self-start md:self-auto">
                            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
                            Actualiser
                        </button>
                    </div>

                    {/* Légende couleurs */}
                    <div className="flex flex-wrap gap-3 text-xs">
                        <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-red-500/10 border border-red-500/20 text-red-400">
                            <Cpu className="w-3 h-3" /> <strong>KERNEL</strong> — crash du noyau Linux (grave)
                        </div>
                        <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400">
                            <Zap className="w-3 h-3" /> <strong>EC</strong> — contrôleur embarqué (alim/thermique)
                        </div>
                        <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-400">
                            <Monitor className="w-3 h-3" /> <strong>BROWSER/APP</strong> — crash navigateur ou application
                        </div>
                        <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-zinc-700/40 border border-white/10 text-zinc-400">
                            <AlertTriangle className="w-3 h-3" /> <strong>ARRET_ANORMAL</strong> — coupure courant / extinction forcée&nbsp;&nbsp;|&nbsp;&nbsp; <strong>EN_SESSION</strong> — crash pendant une session active
                        </div>
                    </div>

                    {/* Filtres */}
                    <div className="space-y-3">
                        <div className="relative max-w-md">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
                            <input type="text" placeholder="Rechercher par type, utilisateur, appareil..."
                                value={search} onChange={e => setSearch(e.target.value)}
                                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-zinc-800/60 border border-white/10 text-zinc-200 text-sm placeholder-zinc-500 focus:outline-none focus:border-cyan-400/50 focus:ring-1 focus:ring-cyan-400/20 transition-all" />
                        </div>

                        {/* Pills type */}
                        <div className="flex flex-wrap gap-2 items-center">
                            <span className="text-[10px] text-zinc-500 uppercase font-semibold">Type :</span>
                            {types.map(t => (
                                <button key={t} onClick={() => setTypeFilter(t)}
                                    className={`px-3 py-1 rounded-full text-xs font-semibold border transition-all ${
                                        typeFilter === t
                                            ? "bg-cyan-500/20 text-cyan-300 border-cyan-500/40"
                                            : "bg-zinc-800/60 text-zinc-400 border-white/10 hover:bg-zinc-700/60"
                                    }`}>
                                    {(t).replace("CRASH_TYPE_", "")}
                                </button>
                            ))}
                        </div>

                        {/* Pills filiale */}
                        {filiales.length > 1 && (
                            <div className="flex flex-wrap gap-2 items-center">
                                <span className="text-[10px] text-zinc-500 uppercase font-semibold">Filiale :</span>
                                {filiales.map(f => (
                                    <button key={f} onClick={() => setFilialeFilter(f)}
                                        className={`px-3 py-1 rounded-full text-xs font-semibold border transition-all ${
                                            filialeFilter === f
                                                ? "bg-purple-500/20 text-purple-300 border-purple-500/40"
                                                : "bg-zinc-800/60 text-zinc-400 border-white/10 hover:bg-zinc-700/60"
                                        }`}>
                                        {f === "TOUS" ? "Toutes" : (f || "").replace(/^\//, "")}
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Contenu */}
                    {loading ? (
                        <div className="flex justify-center items-center py-20">
                            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-400" />
                        </div>
                    ) : error ? (
                        <div className="glass-panel p-8 text-center rounded-2xl border border-red-500/20">
                            <AlertTriangle className="w-12 h-12 text-red-400 mx-auto mb-3 opacity-50" />
                            <p className="text-red-400 font-medium">{error}</p>
                        </div>
                    ) : filtered.length === 0 ? (
                        <div className="glass-panel p-12 text-center rounded-2xl border border-white/5">
                            <Bell className="w-14 h-14 text-zinc-600 mx-auto mb-4" />
                            <p className="text-zinc-400 text-lg font-medium">Aucun événement trouvé</p>
                            <p className="text-zinc-600 text-sm mt-1">
                                {search || typeFilter !== "TOUS" || filialeFilter !== "TOUS"
                                    ? "Modifiez vos filtres" : "Aucune donnée enregistrée"}
                            </p>
                        </div>
                    ) : (
                        <>
                            <p className="text-sm text-zinc-500">
                                <span className="font-semibold text-zinc-300">{filtered.length}</span> événement{filtered.length > 1 ? "s" : ""}
                            </p>
                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                                {filtered.map((ev, idx) => (
                                    <EventCard key={ev.id ?? idx} ev={ev} />
                                ))}
                            </div>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
}

export default ListeEvent;