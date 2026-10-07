import { useState } from "react";
import {
    Calendar, Monitor, User,
    Zap, AlertTriangle, Cpu, Layers
} from "lucide-react";
import { formatDate } from "../../fonction/utils/util";

const CAUSE_LABELS = {
    "ARRET_ANORMAL": { 
        label: "Arrêt anormal", 
        desc: "Coupure courant / extinction forcée / plantage entre 2 sessions", 
        color: "text-red-400",
        explication: "Le Chromebook s'est éteint brusquement sans suivre la procédure d'arrêt normale. Cela se produit souvent lorsqu'un utilisateur force l'extinction en maintenant le bouton d'alimentation enfoncé, ou si la batterie s'est vidée complètement de façon soudaine.",
        solution: "Vérifiez l'état de la batterie de l'appareil. Sensibilisez les utilisateurs à utiliser le bouton 'Arrêter' de l'interface plutôt que de forcer l'arrêt matériel."
    },
    "EN_SESSION": { 
        label: "En session",    
        desc: "Crash survenu pendant qu'un utilisateur était connecté",       
        color: "text-amber-400",
        explication: "Le système a subi une défaillance critique (Kernel Panic ou crash système) alors qu'une session utilisateur était active. Cela indique généralement un problème logiciel sévère, un conflit matériel, ou une surcharge de la mémoire.",
        solution: "Vérifiez si l'appareil manque de mémoire RAM. Assurez-vous que la version de ChromeOS est à jour. Si le problème persiste, il peut s'agir d'un défaut matériel (RAM ou carte mère)."
    },
};

const getStyle = (type, causeClass) => {
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
            label: "Crash noyau",
            explication: "Un Crash Kernel (Kernel Panic) est une erreur critique au niveau du cœur du système d'exploitation. L'OS n'a pas pu récupérer d'une erreur interne et s'est arrêté par sécurité.",
            solution: "Généralement résolu par une mise à jour de ChromeOS. Si récurrent sur un même appareil, effectuez un Powerwash (réinitialisation d'usine). Si cela ne suffit pas, une réparation matérielle est nécessaire."
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
            label: "Ctrl embarqué",
            explication: "Le contrôleur embarqué (EC) est une puce qui gère le clavier, le pavé tactile, la batterie et l'alimentation. Un crash de l'EC signifie que cette puce a cessé de répondre et a redémarré.",
            solution: "Ce type de crash est souvent lié à la batterie ou au chargeur. Essayez de réaliser un Hard Reset (Actualiser + Power). Si l'erreur se reproduit, la batterie ou la carte mère pourrait être défectueuse."
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
            label: "App / Navigateur",
            explication: "Le navigateur Chrome ou une application web (ou Android) a crashé (Out Of Memory ou erreur fatale de rendu), forçant la session à se fermer.",
            solution: "L'utilisateur avait probablement trop d'onglets ouverts simultanément, dépassant la capacité de la mémoire RAM de l'appareil. Demandez-lui de limiter le nombre d'onglets ou désactivez certaines extensions gourmandes."
        };
    return {
        card: "border-cyan-500/30 bg-cyan-500/5",
        badge: "bg-cyan-500/15 text-cyan-400 border-cyan-500/30",
        icon: "text-cyan-400",
        dot: "bg-cyan-500",
        glow: "radial-gradient(circle at top right, rgba(6, 182, 212, 0.08), transparent 70%)",
        hoverBorder: "rgba(6, 182, 212, 0.5)",
        shadow: "rgba(6, 182, 212, 0.2)",
        label: "Autre",
        explication: "Ce type d'événement est classé comme inconnu ou divers. Il peut s'agir d'un redémarrage normal demandé par le système (mise à jour) ou d'un comportement non surveillé.",
        solution: "Aucune action urgente requise sauf si cela se produit de manière cyclique sur le même appareil."
    };
};

function EventCard({ ev, onOpenModal }) {
    const [open, setOpen] = useState(false);
    const style = getStyle(ev.type_evenement, ev.cause_class);
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

            {/* En-tête carte */}
            <div className="relative z-10">
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
                className="w-full px-4 py-2 mt-3 border-t border-white/5 text-[10px] text-zinc-500 hover:text-cyan-300 hover:bg-cyan-500/5 transition-colors flex items-center justify-center gap-1 cursor-pointer rounded-b-xl"
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
                        <div className="bg-zinc-900/60 rounded-lg p-3 border border-white/5">
                            <p className="text-[10px] text-zinc-500 uppercase font-semibold mb-1 flex items-center gap-1">
                                <Zap className="w-3 h-3" /> Analyse
                            </p>
                            <p className="text-[11px] text-zinc-300 leading-relaxed">{ev.cause_hint}</p>
                        </div>
                    )}
                    <div className="grid grid-cols-3 gap-2">
                        {ev.crash_seq != null && (
                            <div className="bg-zinc-800/50 rounded-lg p-2 text-center border border-white/5">
                                <p className="text-[10px] text-zinc-500">Seq.</p>
                                <p className="text-sm font-bold text-zinc-200">#{ev.crash_seq}</p>
                            </div>
                        )}
                        {ev.raw_events != null && (
                            <div className="bg-zinc-800/50 rounded-lg p-2 text-center border border-white/5">
                                <p className="text-[10px] text-zinc-500">Événements</p>
                                <p className="text-sm font-bold text-zinc-200">{ev.raw_events}</p>
                            </div>
                        )}
                        {ev.minutes_since_boot != null && (
                            <div className="bg-zinc-800/50 rounded-lg p-2 text-center border border-white/5">
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
export default EventCard