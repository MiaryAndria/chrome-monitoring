import {
    Calendar, Monitor, User,
    Zap, Layers
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { formatDateTime } from "../../fonction/utils/util";

const CAUSE_LABELS = {
    "ARRET_ANORMAL": {
        label: "Arrêt anormal",
        desc: "Coupure courant / extinction forcée / plantage entre 2 sessions",
        color: "text-red-400",
    },
    "EN_SESSION": {
        label: "En session",
        desc: "Crash survenu pendant qu'un utilisateur était connecté",
        color: "text-amber-400",
    },
};

const getStyle = (type) => {
    const t = (type || "").toUpperCase();

    if (t.includes("KERNEL"))
        return {
            card: "border-red-500/30 bg-red-500/5",
            badge: "bg-red-500/15 text-red-400 border-red-500/30",
            icon: "text-red-400",
            dot: "bg-red-500",
            glow: "radial-gradient(circle at top right, rgba(239, 68, 68, 0.08), transparent 70%)",
            hoverBorder: "rgba(239, 68, 68, 0.5)",
            shadow: "rgba(239, 68, 68, 0.2)",
        };
    if (t.includes("EMBEDDED") || t.includes("CONTROLLER") || t.includes("EC"))
        return {
            card: "border-amber-500/30 bg-amber-500/5",
            badge: "bg-amber-500/15 text-amber-400 border-amber-500/30",
            icon: "text-amber-400",
            dot: "bg-amber-500",
            glow: "radial-gradient(circle at top right, rgba(245, 158, 11, 0.08), transparent 70%)",
            hoverBorder: "rgba(245, 158, 11, 0.5)",
            shadow: "rgba(245, 158, 11, 0.2)",
        };
    if (t.includes("BROWSER") || t.includes("APP"))
        return {
            card: "border-purple-500/30 bg-purple-500/5",
            badge: "bg-purple-500/15 text-purple-400 border-purple-500/30",
            icon: "text-purple-400",
            dot: "bg-purple-500",
            glow: "radial-gradient(circle at top right, rgba(168, 85, 247, 0.08), transparent 70%)",
            hoverBorder: "rgba(168, 85, 247, 0.5)",
            shadow: "rgba(168, 85, 247, 0.2)",
        };
    return {
        card: "border-cyan-500/30 bg-cyan-500/5",
        badge: "bg-cyan-500/15 text-cyan-400 border-cyan-500/30",
        icon: "text-cyan-400",
        dot: "bg-cyan-500",
        glow: "radial-gradient(circle at top right, rgba(6, 182, 212, 0.08), transparent 70%)",
        hoverBorder: "rgba(6, 182, 212, 0.5)",
        shadow: "rgba(6, 182, 212, 0.2)",
    };
};

function EventCard({ ev }) {
    const navigate = useNavigate();
    const style = getStyle(ev.type_evenement);
    const causeInfo = CAUSE_LABELS[ev.cause_class] || null;
    const shortType = (ev.type_evenement || "INCONNU").replace("CRASH_TYPE_", "").replace(/_/g, " ");

    return (
        <div
            className={`device-card group ${style.card}`}
            style={{
                "--card-glow": style.glow,
                "--card-border-hover": style.hoverBorder,
                "--card-shadow": style.shadow
            }}
        >
            <div className="relative z-10">
                <div className="flex items-start justify-between gap-2 mb-3">
                    <div className="flex items-center gap-2">
                        <div className={`w-2 h-2 rounded-full ${style.dot} shadow-[0_0_6px_currentColor] flex-shrink-0 mt-1`} />
                        <span className={`text-xs font-bold uppercase tracking-wide ${style.icon}`}>
                            {shortType}
                        </span>
                    </div>
                    <span className="text-[10px] text-zinc-500 whitespace-nowrap flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {formatDateTime(ev.date_evenement)}
                    </span>
                </div>

                {causeInfo && (
                    <span className={`inline-block text-[10px] font-semibold px-2 py-0.5 rounded-full border ${style.badge} mb-3`}>
                        {causeInfo.label}
                    </span>
                )}

                {ev.last_user && (
                    <p className="text-xs text-zinc-300 flex items-center gap-1.5 mb-2 truncate">
                        <User className="w-3 h-3 text-zinc-500 flex-shrink-0" />
                        {ev.last_user}
                    </p>
                )}

                <p className="text-xs font-medium text-zinc-400 flex items-center gap-1.5 truncate">
                    <Monitor className="w-3 h-3 text-zinc-600 flex-shrink-0" />
                    {ev.modele || ev.device_id || "—"}
                </p>
                {ev.serial_number && (
                    <p className="text-[10px] font-mono text-zinc-600 mt-0.5 pl-4">
                        {ev.serial_number}
                    </p>
                )}

                {ev.filiale && (
                    <p className="text-[10px] text-zinc-500 mt-1 flex items-center gap-1 pl-0.5">
                        <Layers className="w-3 h-3" />
                        {ev.filiale.replace(/^\//, "")}
                    </p>
                )}

                {ev.cause_hint && (
                    <div className="mt-3 bg-zinc-900/60 rounded-lg p-3 border border-white/5">
                        <p className="text-[10px] text-zinc-500 uppercase font-semibold mb-1 flex items-center gap-1">
                            <Zap className="w-3 h-3" /> Analyse
                        </p>
                        <p className="text-[11px] text-zinc-300 leading-relaxed">{ev.cause_hint}</p>
                    </div>
                )}
            </div>

            <button
                onClick={() => navigate(`/event/${ev.id}`)}
                className="w-full px-4 py-2 mt-3 border-t border-white/5 text-[10px] text-zinc-500 hover:text-cyan-300 hover:bg-cyan-500/5 transition-colors flex items-center justify-center gap-1 cursor-pointer rounded-b-xl"
            >
                Voir diagnostic
                <span>→</span>
            </button>
        </div>
    );
}
export default EventCard
