import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { Bot, Send, X, Loader2, Sparkles } from "lucide-react";
import { IAChatStreamEvenement } from "../../fonction/iaEvenementFonction";
import { IAChatGlobalStream } from "../../fonction/iaGlobalFonction";
import MarkdownLite from "./MarkdownLite";

const SUGGESTIONS = [
    "Analyse cet événement et explique la cause probable.",
    "Comment éviter que ça se reproduise ?",
    "Quelles sont les conséquences que cela va causer si non traité?"
];

const GENERAL_SUGGESTIONS = [
    "Quels sont les types de crash ChromeOS et leurs causes ?",
    "Quelles bonnes pratiques pour prévenir les pannes ?"
];

function findSecondHeadingIndex(text) {
    const regex = /^##\s+/gm;
    let count = 0;
    let match;
    while ((match = regex.exec(text)) !== null) {
        count += 1;
        if (count === 2) return match.index;
    }
    return -1;
}

function AssistantMessage({ content, streaming }) {
    const [expanded, setExpanded] = useState(false);
    const split = !streaming && content.length > 1600 ? findSecondHeadingIndex(content) : -1;
    const preview = split > 0 ? content.slice(0, split) : content;
    const suite = split > 0 ? content.slice(split) : "";

    return (
        <div className="space-y-2">
            <MarkdownLite text={streaming ? `${preview} ▍` : preview} />
            {suite && (
                <>
                    {expanded && <MarkdownLite text={suite} />}
                    <button
                        onClick={() => setExpanded((v) => !v)}
                        className="text-xs font-semibold text-cyan-300 bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 rounded-lg px-3 py-1.5 transition-colors cursor-pointer"
                    >
                        {expanded ? "Réduire l'analyse" : "Afficher l'analyse détaillée"}
                    </button>
                </>
            )}
        </div>
    );
}

function IAChatModal({ ev = null, onClose }) {
    const general = !ev;
    const suggestions = general ? GENERAL_SUGGESTIONS : SUGGESTIONS;
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const [erreur, setErreur] = useState(null);

    const scrollRef = useRef(null);
    const inputRef = useRef(null);

    useEffect(() => {
        scrollRef.current?.scrollTo({
            top: scrollRef.current.scrollHeight,
            behavior: "smooth",
        });
    }, [messages, loading]);

    useEffect(() => {
        inputRef.current?.focus();

        const onKey = (e) => {
            if (e.key === "Escape") onClose();
        };
        window.addEventListener("keydown", onKey);
        return () => window.removeEventListener("keydown", onKey);
    }, [onClose]);

    const envoyer = async (texte) => {
        const contenu = (texte ?? input).trim();
        if (!contenu || loading) return;

        const historique = [...messages, { role: "user", content: contenu }];
        setMessages([...historique, { role: "assistant", content: "" }]);
        setInput("");
        setErreur(null);
        setLoading(true);

        let accumule = "";

        const appeler = ev
            ? (msgs, cb) => IAChatStreamEvenement(ev.id, msgs, cb)
            : (msgs, cb) => IAChatGlobalStream(msgs, cb);

        try {
            await appeler(historique, (_morceau, total) => {
                accumule = total;
                setMessages([...historique, { role: "assistant", content: total }]);
            });

            if (!accumule.trim()) {
                setMessages(historique);
                setErreur("Aucune réponse reçue. Réessayez.");
            }
        } catch (e) {
            console.log(e);
            setMessages(
                accumule.trim()
                    ? [...historique, { role: "assistant", content: accumule }]
                    : historique
            );
            setErreur(e?.message || "L'assistant est momentanément indisponible. Réessayez.");
        } finally {
            setLoading(false);
        }
    };

    const onKeyDown = (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            envoyer();
        }
    };

    return createPortal(
        <div
            className="modal-overlay"
            style={{ animation: "fadeIn 200ms ease-out" }}
            onClick={onClose}
        >
            <div
                className="relative w-full max-w-2xl h-[80vh] bg-zinc-900 border border-white/10 rounded-2xl shadow-2xl flex flex-col overflow-hidden"
                style={{ animation: "modalScaleUp 300ms cubic-bezier(0.16,1,0.3,1)" }}
                onClick={(e) => e.stopPropagation()}
            >
                <div className="p-4 border-b border-white/5 bg-white/5 flex items-start justify-between gap-4">
                    <div className="min-w-0">
                        <h3 className="text-sm font-bold text-zinc-100 flex items-center gap-2">
                            <Bot className="w-4 h-4 text-cyan-400" />
                            {general ? "Assistant IA" : "Assistant IA — Diagnostic"}
                        </h3>
                        <p className="text-[11px] text-zinc-500 mt-1 truncate">
                            {general
                                ? "ChromeOS · parc d'appareils"
                                : `${ev.type_evenement} · ${ev.serial_number || ev.modele || ev.device_id}`}
                        </p>
                    </div>
                    <button
                        onClick={onClose}
                        className="text-zinc-500 hover:text-zinc-300 transition-colors cursor-pointer"
                        aria-label="Fermer"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4">
                    {messages.length === 0 && (
                        <div className="text-center py-8 space-y-4">
                            <Sparkles className="w-8 h-8 text-cyan-400 mx-auto" />
                            <p className="text-sm text-zinc-400">
                                {general
                                    ? "Posez votre question sur ChromeOS ou le parc."
                                    : "Posez une question sur cet événement."}
                            </p>
                        </div>
                    )}

                    {messages.map((m, i) => {
                        if (m.role === "assistant" && m.content.trim() === "") return null;
                        return (
                            <div
                                key={i}
                                className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
                            >
                                <div
                                    className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${m.role === "user"
                                            ? "bg-cyan-500/15 text-cyan-100 border border-cyan-500/25 whitespace-pre-wrap"
                                            : "bg-zinc-800/80 text-zinc-200 border border-white/5"
                                        }`}
                                >
                                    {m.role === "assistant" ? (
                                        <AssistantMessage
                                            content={m.content}
                                            streaming={loading && i === messages.length - 1}
                                        />
                                    ) : (
                                        m.content
                                    )}
                                </div>
                            </div>
                        );
                    })}

                    {loading && messages[messages.length - 1]?.content?.trim() === "" && (
                        <div className="flex justify-start">
                            <div className="bg-zinc-800/80 border border-white/5 rounded-2xl px-4 py-2.5 flex items-center gap-2 text-zinc-400 text-sm">
                                <Loader2 className="w-4 h-4 animate-spin" />
                                Analyse en cours…
                            </div>
                        </div>
                    )}

                    {erreur && (
                        <p className="text-xs text-red-400 text-center">{erreur}</p>
                    )}
                </div>

                <div className="p-3 border-t border-white/5 bg-black/20 space-y-2">
                    <div className="flex flex-wrap gap-2">
                        {suggestions.map((s) => (
                            <button
                                key={s}
                                onClick={() => envoyer(s)}
                                disabled={loading}
                                className="text-[11px] text-cyan-300 bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 rounded-xl px-2.5 py-1.5 transition-colors cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
                            >
                                {s}
                            </button>
                        ))}
                    </div>
                    <div className="flex items-end gap-2">
                        <textarea
                            ref={inputRef}
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={onKeyDown}
                            rows={1}
                            placeholder="Posez votre question…"
                            className="flex-1 resize-none px-3 py-2.5 rounded-xl bg-zinc-900/60 border border-white/10 text-zinc-200 text-sm placeholder-zinc-500 focus:outline-none focus:border-cyan-400/50 focus:ring-1 focus:ring-cyan-400/20"
                        />
                        <button
                            onClick={() => envoyer()}
                            disabled={loading || !input.trim()}
                            className="px-3 py-2.5 rounded-xl bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 hover:bg-cyan-500/25 disabled:opacity-40 disabled:cursor-not-allowed transition-colors cursor-pointer"
                            aria-label="Envoyer"
                        >
                            <Send className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            </div>
        </div>,
        document.body
    );
}

export default IAChatModal;
