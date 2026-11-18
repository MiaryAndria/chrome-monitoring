import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
    ArrowLeft, Calendar, Monitor, User, Layers, Zap, AlertTriangle, Cpu
} from "lucide-react";
import PageLayout from "../../components/PageLayout";
import EmptyState from "../../components/EmptyState";
import { getDetailEvenement, updateStatutEvenement } from "../../fonction/eventFonction";
import { formatDateTime } from "../../fonction/utils/util";
import EvenementDureeVie from "../component/EvenementDureeVie";
import IAChatPanel from "../component/IAChatPanel";

const CAUSE_LABELS = {
    "ARRET_ANORMAL": {
        label: "Arrêt anormal",
        explication: "Le Chromebook s'est éteint brusquement sans suivre la procédure d'arrêt normale. Vérifiez l'état de la batterie et sensibilisez les utilisateurs à utiliser le bouton 'Arrêter' de l'interface plutôt que de forcer l'arrêt matériel.",
    },
    "EN_SESSION": {
        label: "En session",
        explication: "Le système a subi une défaillance critique (Kernel Panic ou crash système) alors qu'une session utilisateur était active. Vérifiez la RAM et la version de ChromeOS. Si le problème persiste, il peut s'agir d'un défaut matériel.",
    },
};

const getStyle = (type) => {
    const t = (type || "").toUpperCase();
    if (t.includes("KERNEL")) return { icon: "text-red-400", label: "Crash noyau" };
    if (t.includes("EMBEDDED") || t.includes("CONTROLLER") || t.includes("EC")) return { icon: "text-amber-400", label: "Contrôleur embarqué" };
    if (t.includes("BROWSER") || t.includes("APP")) return { icon: "text-purple-400", label: "App / Navigateur" };
    return { icon: "text-cyan-400", label: "Autre" };
};

function DetailEvenement() {
    const { id } = useParams();
    const navigate = useNavigate();

    const [ev, setEv] = useState(null);
    const [loading, setLoading] = useState(true);
    const [nonTrouve, setNonTrouve] = useState(false);
    const [iaOpen, setIaOpen] = useState(false);
    const [iaVisible, setIaVisible] = useState(false);
    const [resolueEnCours, setResolueEnCours] = useState(false);
    const [resolue, setResolue] = useState(false);

    const charger = async () => {
        setLoading(true);
        try {
            const data = await getDetailEvenement(id);
            if (!data) {
                setNonTrouve(true);
            } else {
                setEv(data);
            }
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        charger();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [id]);

    useEffect(() => {
        if (iaOpen) {
            const raf = requestAnimationFrame(() => setIaVisible(true));
            return () => cancelAnimationFrame(raf);
        } else {
            setIaVisible(false);
        }
    }, [iaOpen]);

    const handleMarquerResolu = async () => {
        setResolueEnCours(true);
        try {
            const res = await updateStatutEvenement(Number(id), 15);
            if (res?.ok) {
                setResolue(true);
            }
        } finally {
            setResolueEnCours(false);
        }
    };

    if (loading) {
        return (
            <PageLayout title="Événement" subtitle="Détail" titleIcon={AlertTriangle}>
                <div className="detail-card space-y-6 animate-pulse">
                    <div className="h-24 bg-zinc-800/50 rounded-2xl" />
                    <div className="h-40 bg-zinc-800/50 rounded-2xl" />
                </div>
            </PageLayout>
        );
    }

    if (nonTrouve || !ev) {
        return (
            <PageLayout title="Événement" subtitle="Détail" titleIcon={AlertTriangle}>
                <EmptyState
                    icon={AlertTriangle}
                    title="Événement introuvable"
                    subtitle="L'événement demandé n'existe pas ou a été supprimé."
                    action={
                        <button onClick={() => navigate(-1)} className="config-btn config-btn-ghost text-xs">
                            Retour
                        </button>
                    }
                />
            </PageLayout>
        );
    }

    const details = (() => {
        try {
            return typeof ev.details === "string" ? JSON.parse(ev.details) : (ev.details || {});
        } catch {
            return {};
        }
    })();

    const style = getStyle(ev.type_evenement);
    const causeInfo = CAUSE_LABELS[details.cause_class] || null;
    const shortType = (ev.type_evenement || "INCONNU").replace("CRASH_TYPE_", "").replace(/_/g, " ");

    return (
        <PageLayout
            title={iaOpen ? undefined : "Événement"}
            subtitle={iaOpen ? undefined : shortType}
            titleIcon={iaOpen ? undefined : AlertTriangle}
            headerRight={
                <button onClick={() => navigate(-1)} className="back-btn">
                    <ArrowLeft className="w-4 h-4" />
                    Retour
                </button>
            }
        >
            <div className="flex gap-6 h-[calc(100vh-10rem)]">
                {/* Colonne détail */}
                <div
                    className={`transition-all duration-500 ease-in-out overflow-y-auto ${iaOpen ? "w-1/2 pr-2" : "w-full"}`}
                >
                    <div className="detail-card space-y-6 h-full">
                        {/* En-tête */}
                        <div className="flex justify-between items-start border-b border-white/10 pb-5">
                            <div className="flex items-center gap-4">
                                <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-2xl text-red-400">
                                    <Cpu className="w-8 h-8" />
                                </div>
                                <div>
                                    <h1 className="text-2xl font-bold text-zinc-100">{shortType}</h1>
                                    <p className="text-sm text-zinc-400 flex items-center gap-2 mt-1">
                                        <Calendar className="w-4 h-4" />
                                        {formatDateTime(ev.date_evenement)}
                                    </p>
                                </div>
                            </div>
                            {resolue && (
                                <span className="px-3 py-1.5 rounded-full bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 text-xs font-semibold">
                                    Résolu
                                </span>
                            )}
                        </div>

                        {/* Infos appareil */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                            <div className="bg-zinc-900/60 rounded-xl p-4 border border-white/5">
                                <p className="text-[10px] uppercase text-zinc-500 mb-1 flex items-center gap-1">
                                    <Monitor className="w-3 h-3" /> Appareil
                                </p>
                                <p className="font-semibold text-zinc-100">{ev.modele || ev.device_id || "—"}</p>
                                <p className="text-[11px] font-mono text-zinc-500">{ev.serial_number}</p>
                            </div>
                            <div className="bg-zinc-900/60 rounded-xl p-4 border border-white/5">
                                <p className="text-[10px] uppercase text-zinc-500 mb-1 flex items-center gap-1">
                                    <User className="w-3 h-3" /> Utilisateur récent
                                </p>
                                <p className="font-semibold text-zinc-100">{details.last_user || "—"}</p>
                            </div>
                            <div className="bg-zinc-900/60 rounded-xl p-4 border border-white/5">
                                <p className="text-[10px] uppercase text-zinc-500 mb-1 flex items-center gap-1">
                                    <Layers className="w-3 h-3" /> Filiale
                                </p>
                                <p className="font-semibold text-zinc-100">{ev.filiale?.replace(/^\//, "") || "—"}</p>
                            </div>
                        </div>

                        {/* Cause / analyse */}
                        {causeInfo && (
                            <div className="bg-zinc-900/60 rounded-xl p-4 border border-white/5">
                                <p className="text-[10px] uppercase text-zinc-500 mb-1">Cause — {causeInfo.label}</p>
                                <p className="text-sm text-zinc-300 leading-relaxed">{causeInfo.explication}</p>
                            </div>
                        )}
                        {details.cause_hint && (
                            <div className="bg-zinc-900/60 rounded-xl p-4 border border-white/5">
                                <p className="text-[10px] uppercase text-zinc-500 mb-1 flex items-center gap-1">
                                    <Zap className="w-3 h-3" /> Analyse
                                </p>
                                <p className="text-sm text-zinc-300 leading-relaxed">{details.cause_hint}</p>
                            </div>
                        )}

                        {/* Métriques */}
                        <div className="grid grid-cols-3 gap-4">
                            {details.crash_seq != null && (
                                <div className="bg-zinc-800/50 rounded-lg p-3 text-center border border-white/5">
                                    <p className="text-[10px] text-zinc-500">Séquence</p>
                                    <p className="text-lg font-bold text-zinc-100">#{details.crash_seq}</p>
                                </div>
                            )}
                            {details.raw_events != null && (
                                <div className="bg-zinc-800/50 rounded-lg p-3 text-center border border-white/5">
                                    <p className="text-[10px] text-zinc-500">Événements</p>
                                    <p className="text-lg font-bold text-zinc-100">{details.raw_events}</p>
                                </div>
                            )}
                            {details.minutes_since_boot != null && (
                                <div className="bg-zinc-800/50 rounded-lg p-3 text-center border border-white/5">
                                    <p className="text-[10px] text-zinc-500">Min/boot</p>
                                    <p className="text-lg font-bold text-zinc-100">{Number(details.minutes_since_boot).toFixed(0)}</p>
                                </div>
                            )}
                        </div>

                        {/* Durée de vie */}
                        <div>
                            <p className="text-[10px] uppercase text-zinc-500 mb-2 font-semibold">Durée de vie avant extinction</p>
                            <EvenementDureeVie eventId={ev.id} />
                        </div>

                        {/* Actions */}
                        <div className="flex flex-wrap gap-3 pt-2 border-t border-white/10">
                            <button
                                onClick={() => setIaOpen((v) => !v)}
                                className={`flex-1 min-w-[180px] px-4 py-3 rounded-xl border transition-all duration-300 text-xs font-semibold flex items-center justify-center gap-2 cursor-pointer ${
                                    iaOpen
                                        ? "bg-cyan-500/25 text-cyan-200 border-cyan-500/50 shadow-[0_0_20px_rgba(6,182,212,0.25)]"
                                        : "bg-cyan-500/15 text-cyan-300 border-cyan-500/30 hover:bg-cyan-500/25"
                                }`}
                            >
                                {iaOpen ? "Masquer l'IA" : "Demander à l'IA"}
                            </button>
                            <button
                                onClick={handleMarquerResolu}
                                disabled={resolueEnCours || resolue}
                                className="flex-1 min-w-[180px] px-4 py-3 rounded-xl bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 hover:bg-emerald-500/25 transition-colors text-xs font-semibold flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
                            >
                                {resolue ? "Résolu ✓" : resolueEnCours ? "Résolution…" : "Marquer comme résolu"}
                            </button>
                        </div>
                    </div>
                </div>

                {/* Colonne IA — animation slide-in */}
                <div
                    className={`transition-all duration-500 ease-in-out overflow-hidden ${
                        iaVisible ? "w-1/2 opacity-100 translate-x-0" : "w-0 opacity-0 translate-x-8"
                    }`}
                    aria-hidden={!iaVisible}
                >
                    {iaOpen && (
                        <IAChatPanel
                            ev={ev}
                            onClose={() => setIaOpen(false)}
                        />
                    )}
                </div>
            </div>
        </PageLayout>
    );
}

export default DetailEvenement;
