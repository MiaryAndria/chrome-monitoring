import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { Bot, Send, X, Loader2, Sparkles, Paperclip } from "lucide-react";
import { IAChatStreamEvenement } from "../../fonction/iaEvenementFonction";
import { IAChatGlobalStream } from "../../fonction/iaGlobalFonction";
import MarkdownLite from "./MarkdownLite";

const TAILLE_MAX_PIECE = 10 * 1024 * 1024;
const TAILLE_MAX_TOTALE = 18 * 1024 * 1024;
const MAX_PIECES = 10;

const MIME_PAR_EXTENSION = {
    pdf: "application/pdf",
    png: "image/png",
    jpg: "image/jpeg",
    jpeg: "image/jpeg",
    webp: "image/webp",
    gif: "image/gif",
    bmp: "image/bmp",
    svg: "image/svg+xml",
    txt: "text/plain",
    log: "text/plain",
    md: "text/markdown",
    csv: "text/csv",
    json: "application/json",
    xml: "application/xml",
    html: "text/html",
    docx: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    xlsx: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    pptx: "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    odt: "application/vnd.oasis.opendocument.text",
    rtf: "application/rtf",
    mp3: "audio/mp3",
    wav: "audio/wav",
    ogg: "audio/ogg",
    flac: "audio/flac",
    aac: "audio/aac",
    mp4: "video/mp4",
    webm: "video/webm",
    mov: "video/mov",
    avi: "video/avi",
};

const SUGGESTIONS = [
    {
        label: "Diagnostic complet de l'événement",
        description: "Cause probable · Prévention · Conséquences",
        prompt: "Analyse cet événement et réponds aux trois points suivants : Quelle est la cause probable ? Comment éviter que cela se reproduise ? Quelles seraient les conséquences si le problème n’était pas traité ?",
    },
];

const GENERAL_SUGGESTIONS = [
    {
        label: "Types de crash ChromeOS",
        description: "Causes et explications",
        prompt: "Quels sont les types de crash ChromeOS et leurs causes ?",
    },
    {
        label: "Prévenir les pannes",
        description: "Bonnes pratiques",
        prompt: "Quelles bonnes pratiques pour prévenir les pannes ?",
    },
];

function formaterTaille(octets) {
    if (octets < 1024) return `${octets} o`;
    if (octets < 1024 * 1024) return `${Math.round(octets / 1024)} Ko`;
    return `${(octets / (1024 * 1024)).toFixed(1)} Mo`;
}

function trouverMime(fichier) {
    if (fichier.type) return fichier.type;
    const nom = fichier.name || "";
    if (!nom.includes(".")) return "application/octet-stream";
    const extension = nom.split(".").pop().toLowerCase();
    return MIME_PAR_EXTENSION[extension] || "application/octet-stream";
}

function lireFichierBase64(fichier) {
    return new Promise((resolve, reject) => {
        const lecteur = new FileReader();
        lecteur.onload = () => {
            const resultat = lecteur.result || "";
            const index = resultat.indexOf(",");
            resolve(index >= 0 ? resultat.slice(index + 1) : resultat);
        };
        lecteur.onerror = () => reject(new Error("Lecture du fichier impossible."));
        lecteur.readAsDataURL(fichier);
    });
}

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
    const [pieces, setPieces] = useState([]);
    const [erreurPiece, setErreurPiece] = useState(null);
    const [survol, setSurvol] = useState(false);

    const scrollRef = useRef(null);
    const inputRef = useRef(null);
    const fichierRef = useRef(null);

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

    const ajouterFichiers = async (listeFichiers) => {
        const fichiers = Array.from(listeFichiers || []);
        if (fichiers.length === 0) return;
        setErreurPiece(null);

        let total = 0;
        for (const piece of pieces) {
            total += piece.size;
        }
        let nombre = pieces.length;
        const nouvelles = [];

        for (const fichier of fichiers) {
            if (nombre >= MAX_PIECES) {
                setErreurPiece(`Maximum ${MAX_PIECES} fichiers par message.`);
                break;
            }
            if (fichier.size > TAILLE_MAX_PIECE) {
                setErreurPiece(`« ${fichier.name} » dépasse 10 Mo.`);
                continue;
            }
            if (total + fichier.size > TAILLE_MAX_TOTALE) {
                setErreurPiece("Le total des pièces jointes est limité à 18 Mo.");
                break;
            }
            try {
                const data = await lireFichierBase64(fichier);
                nouvelles.push({
                    id: `${Date.now()}-${nombre}-${fichier.name}`,
                    name: fichier.name,
                    mime_type: trouverMime(fichier),
                    size: fichier.size,
                    data,
                });
                total += fichier.size;
                nombre += 1;
            } catch (e) {
                setErreurPiece(e?.message || "Lecture du fichier impossible.");
            }
        }

        if (nouvelles.length > 0) {
            setPieces((precedent) => [...precedent, ...nouvelles]);
        }
        if (fichierRef.current) fichierRef.current.value = "";
    };

    const retirerPiece = (id) => {
        setPieces((precedent) => precedent.filter((piece) => piece.id !== id));
    };

    const envoyer = async (texte) => {
        const contenu = (texte ?? input).trim();
        if ((!contenu && pieces.length === 0) || loading) return;

        const piecesMessage = pieces.map((piece) => ({
            name: piece.name,
            mime_type: piece.mime_type,
            data: piece.data,
        }));
        const historique = [
            ...messages,
            { role: "user", content: contenu, attachments: piecesMessage },
        ];
        setMessages([...historique, { role: "assistant", content: "" }]);
        setInput("");
        setPieces([]);
        setErreur(null);
        setErreurPiece(null);
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
                        <div className="h-full flex flex-col items-center justify-center gap-3 text-center">
                            <div className="w-12 h-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center">
                                <Sparkles className="w-6 h-6 text-cyan-400" />
                            </div>
                            <p className="text-sm font-medium text-zinc-200">
                                {general
                                    ? "Posez votre question sur ChromeOS ou le parc."
                                    : "Posez une question sur cet événement."}
                            </p>
                            <p className="text-xs text-zinc-500">
                                {general
                                    ? "Expliquez un crash, comparez des appareils ou demandez conseil."
                                    : "Analysez les causes et les conséquences en un clic."}
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
                                        <div className="space-y-1.5">
                                            {m.attachments?.length > 0 && (
                                                <div className="flex flex-wrap gap-1.5">
                                                    {m.attachments.map((piece, j) => (
                                                        <span
                                                            key={j}
                                                            className="flex items-center gap-1 text-[11px] text-cyan-200/90 bg-cyan-500/10 border border-cyan-500/20 rounded-md px-1.5 py-0.5"
                                                        >
                                                            <Paperclip className="w-3 h-3 shrink-0" />
                                                            <span className="truncate max-w-[160px]">{piece.name}</span>
                                                        </span>
                                                    ))}
                                                </div>
                                            )}
                                            {m.content}
                                        </div>
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

                <div
                    className={`p-3 border-t border-white/5 space-y-2 transition-colors ${survol ? "bg-cyan-500/10" : "bg-black/20"}`}
                    onDragOver={(e) => {
                        e.preventDefault();
                        setSurvol(true);
                    }}
                    onDragLeave={() => setSurvol(false)}
                    onDrop={(e) => {
                        e.preventDefault();
                        setSurvol(false);
                        ajouterFichiers(e.dataTransfer.files);
                    }}
                >
                    <div className="flex flex-wrap gap-2">
                        {suggestions.map((s) => (
                            <button
                                key={s.label}
                                onClick={() => envoyer(s.prompt)}
                                disabled={loading}
                                title={s.description}
                                className="flex items-center gap-1.5 text-[11px] text-cyan-300 bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 rounded-xl px-2.5 py-1.5 transition-colors cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
                            >
                                <Sparkles className="w-3 h-3 shrink-0" />
                                {s.label}
                            </button>
                        ))}
                    </div>
                    {pieces.length > 0 && (
                        <div className="flex flex-wrap gap-1.5">
                            {pieces.map((piece) => (
                                <span
                                    key={piece.id}
                                    className="flex items-center gap-1.5 max-w-full text-[11px] text-zinc-300 bg-white/5 border border-white/10 rounded-lg px-2 py-1"
                                >
                                    <Paperclip className="w-3 h-3 text-cyan-400 shrink-0" />
                                    <span className="truncate max-w-[170px]">{piece.name}</span>
                                    <span className="text-zinc-500 shrink-0">{formaterTaille(piece.size)}</span>
                                    <button
                                        onClick={() => retirerPiece(piece.id)}
                                        className="text-zinc-500 hover:text-zinc-200 transition-colors cursor-pointer"
                                        aria-label={`Retirer ${piece.name}`}
                                    >
                                        <X className="w-3 h-3" />
                                    </button>
                                </span>
                            ))}
                        </div>
                    )}
                    {erreurPiece && <p className="text-[11px] text-red-400">{erreurPiece}</p>}
                    <div className="flex items-end gap-2">
                        <input
                            ref={fichierRef}
                            type="file"
                            multiple
                            className="hidden"
                            onChange={(e) => ajouterFichiers(e.target.files)}
                        />
                        <button
                            onClick={() => fichierRef.current?.click()}
                            disabled={loading}
                            className="px-3 py-2.5 rounded-xl bg-white/5 text-zinc-400 border border-white/10 hover:bg-white/10 hover:text-zinc-200 disabled:opacity-40 disabled:cursor-not-allowed transition-colors cursor-pointer"
                            aria-label="Joindre des fichiers"
                            title="Joindre des fichiers (PDF, images, documents…)"
                        >
                            <Paperclip className="w-4 h-4" />
                        </button>
                        <textarea
                            ref={inputRef}
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={onKeyDown}
                            rows={1}
                            placeholder={survol ? "Déposez vos fichiers ici…" : "Posez votre question…"}
                            className="flex-1 resize-none px-3 py-2.5 rounded-xl bg-zinc-900/60 border border-white/10 text-zinc-200 text-sm placeholder-zinc-500 focus:outline-none focus:border-cyan-400/50 focus:ring-1 focus:ring-cyan-400/20"
                        />
                        <button
                            onClick={() => envoyer()}
                            disabled={loading || (!input.trim() && pieces.length === 0)}
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
