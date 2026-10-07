import { useEffect, useState } from "react";
import {
    Bell, Search, Monitor,
    Zap, AlertTriangle, Cpu, XCircle
} from "lucide-react";
import DateFilter from "../component/dateFilter";
import GenericTable from "../../components/GenericTable";
import PageLayout from "../../components/PageLayout";
import EmptyState from "../../components/EmptyState";
import { getListeEvenement, getListeTypeEvenement } from "../../fonction/eventFonction";
import EventCard from "../component/component_event";
import { getListeFiliale } from "../../fonction/filialeFonction";
import { toText } from "../../fonction/utils/util";
import FilialeDropdown from "../component/FilialeDropdown";
import ResetFiltreButton from "../component/ResetFiltreButton";
import ViewModeToggle from "../component/ViewModeToggle";
import '../../css/liste.css';
import '../../css/filiale.css';

function ListeEvent() {
    const [evenements, setEvenements] = useState([]);
    const [listeTypes, setListeTypes] = useState([]);
    const [listeFiliales, setListeFiliales] = useState([]);
    const [loading, setLoading] = useState(false);
    const [search, setSearch] = useState("");
    const [dateDebut, setDateDebut] = useState('');
    const [dateFin, setDateFin] = useState('');
    const [dateDebutApplique, setDateDebutApplique] = useState('');
    const [dateFinApplique, setDateFinApplique] = useState('');
    const [error, setError] = useState(null);
    const [typeEvenement, setTypeEvenement] = useState("TOUS");
    const [filiale, setFiliale] = useState("");
    const [selectedExplanation, setSelectedExplanation] = useState(null);
    const [currentPage, setCurrentPage] = useState(1);
    const [viewMode, setViewMode] = useState('grid');
    const itemsPerPage = 12;

    const eventColumns = [
        { header: "Date", accessor: "date" },
        { header: "Type d'Incident", render: (ev) => <span className="font-bold text-zinc-100">{ev.type_evenement}</span> },
        { header: "Cause", render: (ev) => <span className="text-zinc-400">{ev.cause_class || '-'}</span> },
        { header: "Utilisateur", render: (ev) => <span className="text-cyan-400 font-medium truncate max-w-[150px] inline-block" title={ev.last_user}>{ev.last_user || '-'}</span> },
        { header: "Appareil", render: (ev) => <span className="font-mono text-zinc-300">{ev.serial_number || ev.modele || ev.device_id || '-'}</span> }
    ];

    const charger = async () => {
        try {
            setLoading(true);
            setError(null);

            const dataEvenements = await getListeEvenement();
            setEvenements(dataEvenements || []);

            const dataTypes = await getListeTypeEvenement();
            setListeTypes(dataTypes || []);

            const dataFiliales = await getListeFiliale();
            setListeFiliales(dataFiliales || []);

        } catch (e) {
            console.error(e);
            setError("Impossible de charger les événements.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        charger();
    }, []);

    const filtrerByDate = () => {
        if (dateDebut && dateFin && dateDebut > dateFin) {
            alert("La date de début doit être antérieure ou égale à la date de fin.");
            return;
        }

        setDateDebutApplique(dateDebut);
        setDateFinApplique(dateFin);
        setCurrentPage(1);
    };

    const reinitialiserFiltres = () => {
        setSearch("");
        setTypeEvenement("TOUS");
        setFiliale("");
        setDateDebut('');
        setDateFin('');
        setDateDebutApplique('');
        setDateFinApplique('');
        setCurrentPage(1);
    };

    const resetDate = () => {
        setDateDebut('');
        setDateFin('');
        setDateDebutApplique('');
        setDateFinApplique('');
    };

    const filtresActifs = search !== "" || typeEvenement !== "TOUS" || filiale !== "" || !!dateDebutApplique || !!dateFinApplique;

    useEffect(() => {
        setCurrentPage(1);
    }, [search, typeEvenement, filiale, dateDebutApplique, dateFinApplique]);

    const filtered = evenements.filter(ev => {
        const q = search.toLowerCase();
        const matchSearch = (
            toText(ev.type_evenement || "").toLowerCase().includes(q) ||
            toText(ev.cause_class || "").toLowerCase().includes(q) ||
            toText(ev.last_user || "").toLowerCase().includes(q) ||
            toText(ev.device_id || "").toLowerCase().includes(q) ||
            toText(ev.serial_number || "").toLowerCase().includes(q) ||
            toText(ev.modele || "").toLowerCase().includes(q)
        );

        const eventDate = String(ev.date_evenement || "").slice(0, 10);
        const matchDate = (() => {
            if (!dateDebutApplique && !dateFinApplique) return true;
            if (dateDebutApplique && !dateFinApplique) return eventDate >= dateDebutApplique;
            if (!dateDebutApplique && dateFinApplique) return eventDate <= dateFinApplique;
            return eventDate >= dateDebutApplique && eventDate <= dateFinApplique;
        })();

        const matchType = typeEvenement === "TOUS" || ev.type_evenement === typeEvenement;
        const matchFiliale = filiale === "" || ev.filiale === filiale;
        return matchSearch && matchType && matchFiliale && matchDate;
    });

    const totalPages = Math.ceil(filtered.length / itemsPerPage) || 1;
    const indexOfLastItem = currentPage * itemsPerPage;
    const indexOfFirstItem = indexOfLastItem - itemsPerPage;
    const currentItems = filtered.slice(indexOfFirstItem, indexOfLastItem);

    return (
        <PageLayout
            title="Événements"
            subtitle="Journal des incidents système des appareils"
            titleIcon={Bell}
            contentClassName="space-y-8"
            headerRight={<ViewModeToggle viewMode={viewMode} setViewMode={setViewMode} />}
        >

            {/* Légende couleurs cliquables */}
            <div className="flex flex-wrap gap-3 text-xs">
                <button
                    onClick={() => setSelectedExplanation({
                        label: "Crash noyau (KERNEL)",
                        color: "text-red-400",
                        explication: "Un Crash Kernel (Kernel Panic) est une erreur critique au niveau du cœur du système d'exploitation. L'OS n'a pas pu récupérer d'une erreur interne et s'est arrêté par sécurité.",
                        solution: "Généralement résolu par une mise à jour de ChromeOS. Si récurrent sur un même appareil, effectuez un Powerwash (réinitialisation d'usine). Si cela ne suffit pas, une réparation matérielle est nécessaire."
                    })}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-red-500/10 border border-red-500/20 text-red-400 hover:bg-red-500/20 transition-colors cursor-pointer"
                >
                    <Cpu className="w-3 h-3" /> <strong>KERNEL</strong> — crash du noyau OS
                </button>
                <button
                    onClick={() => setSelectedExplanation({
                        label: "Contrôleur embarqué (EC)",
                        color: "text-amber-400",
                        explication: "Le contrôleur embarqué (EC) est une puce qui gère le clavier, le pavé tactile, la batterie et l'alimentation. Un crash de l'EC signifie que cette puce a cessé de répondre et a redémarré.",
                        solution: "Ce type de crash est souvent lié à la batterie ou au chargeur. Essayez de réaliser un Hard Reset (Actualiser + Power). Si l'erreur se reproduit, la batterie ou la carte mère pourrait être défectueuse."
                    })}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 hover:bg-amber-500/20 transition-colors cursor-pointer"
                >
                    <Zap className="w-3 h-3" /> <strong>EC</strong> — contrôleur embarqué
                </button>
                <button
                    onClick={() => setSelectedExplanation({
                        label: "App / Navigateur",
                        color: "text-purple-400",
                        explication: "Le navigateur Chrome ou une application web (ou Android) a crashé (Out Of Memory ou erreur fatale de rendu), forçant la session à se fermer.",
                        solution: "L'utilisateur avait probablement trop d'onglets ouverts simultanément, dépassant la capacité de la mémoire RAM de l'appareil. Demandez-lui de limiter le nombre d'onglets ou désactivez certaines extensions gourmandes."
                    })}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-400 hover:bg-purple-500/20 transition-colors cursor-pointer"
                >
                    <Monitor className="w-3 h-3" /> <strong>BROWSER/APP</strong> — crash navigateur
                </button>
                <button
                    onClick={() => setSelectedExplanation({
                        label: "Arrêt Anormal / En Session",
                        color: "text-zinc-400",
                        explication: "L'appareil s'est éteint brusquement (coupure de courant, plantage) ou un crash est survenu pendant qu'un utilisateur était connecté.",
                        solution: "Vérifiez l'état de la batterie. Sensibilisez les utilisateurs à éteindre correctement. Vérifiez s'il y a un manque de RAM si c'est en session."
                    })}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-zinc-700/40 border border-white/10 text-zinc-400 hover:bg-zinc-700/60 transition-colors cursor-pointer"
                >
                    <AlertTriangle className="w-3 h-3" /> <strong>ARRET_ANORMAL</strong> | <strong>EN_SESSION</strong>
                </button>
            </div>

            {/* Filtres */}
            <div className="glass-panel rounded-2xl p-5 space-y-4 relative z-50">
                {/* Recherche */}
                <div className="relative max-w-md">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
                    <input type="text" placeholder="Rechercher par type, utilisateur, appareil..."
                        value={search} onChange={e => setSearch(e.target.value)}
                        className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-zinc-900/60 border border-white/10 text-zinc-200 text-sm placeholder-zinc-500 focus:outline-none focus:border-cyan-400/50 focus:ring-1 focus:ring-cyan-400/20 transition-all" />
                </div>

                <DateFilter
                    dateDebut={dateDebut}
                    dateFin={dateFin}
                    setDateDebut={setDateDebut}
                    setDateFin={setDateFin}
                    onFilter={filtrerByDate}
                    onReset={resetDate}
                />

                {/* Pills type */}
                <div className="flex flex-wrap gap-2 items-center">
                    <span className="text-[10px] text-zinc-500 uppercase font-semibold tracking-wider">Type :</span>
                    {["TOUS", ...listeTypes].map((t) => {
                        const typeValue = typeof t === "string" ? t : t?.type ?? "";
                        const typeLabel = typeValue === "TOUS" ? "Tous" : typeValue.replace("CRASH_TYPE_", "");

                        return (
                            <button
                                key={typeof t === "string" ? t : t.id}
                                onClick={() => setTypeEvenement(typeValue)}
                                className={`px-3 py-1.5 rounded-xl text-xs font-semibold border transition-all duration-200 cursor-pointer ${typeEvenement === typeValue
                                    ? "bg-cyan-500/15 text-cyan-300 border-cyan-500/40 shadow-[0_0_12px_rgba(6,182,212,0.15)]"
                                    : "bg-zinc-900/60 text-zinc-400 border-white/8 hover:bg-zinc-800/80 hover:text-zinc-300 hover:border-white/15"
                                    }`}
                            >
                                {typeLabel}
                            </button>
                        );
                    })}
                </div>

                {/* Filiale autocomplete dropdown + Réinitialiser */}
                <div className="flex flex-wrap items-center gap-3">
                    <span className="text-[10px] text-zinc-500 uppercase font-semibold tracking-wider">Filiale :</span>

                    <FilialeDropdown
                        listeFiliales={listeFiliales}
                        filiale={filiale}
                        setFiliale={setFiliale}
                    />

                    <ResetFiltreButton actif={filtresActifs} onClick={reinitialiserFiltres} />
                </div>
            </div>

            {/* Contenu */}
            {loading ? (
                <div className="flex justify-center p-12">
                    <span className="loading loading-infinity loading-lg text-cyan-500"></span>
                </div>
            ) : error ? (
                <EmptyState icon={AlertTriangle} title={error} />
            ) : filtered.length === 0 ? (
                <EmptyState
                    icon={Bell}
                    title="Aucun événement trouvé"
                    subtitle={filtresActifs ? "Modifiez vos filtres" : "Aucune donnée enregistrée"}
                />
            ) : (
                <>
                    <div className="section-header flex justify-between items-center">
                        <div>
                            <h2 className="section-title">
                                Incidents détectés
                            </h2>
                            <span className="section-count">
                                {filtered.length} événement{filtered.length > 1 ? "s" : ""} — Page {currentPage}/{totalPages}
                            </span>
                        </div>
                        <ViewModeToggle viewMode={viewMode} setViewMode={setViewMode} />
                    </div>

                    {viewMode === 'table' ? (
                        <GenericTable columns={eventColumns} data={currentItems} />
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                            {currentItems.map((ev, idx) => (
                                <EventCard key={ev.id ?? idx} ev={ev} />
                            ))}
                        </div>
                    )}

                    {/* Modal d'explication */}
                    {selectedExplanation && (
                        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm"
                            style={{ animation: "fadeIn 200ms ease-out" }}
                            onClick={() => setSelectedExplanation(null)}>
                            <div
                                className="relative w-full max-w-md bg-zinc-900 border border-white/10 rounded-2xl shadow-2xl overflow-hidden"
                                style={{ animation: "modalScaleUp 300ms cubic-bezier(0.16,1,0.3,1)" }}
                                onClick={e => e.stopPropagation()}
                            >
                                <div className="p-6 border-b border-white/5 bg-white/5">
                                    <div className="flex justify-between items-start gap-4">
                                        <h3 className="text-lg font-bold text-zinc-100 flex items-center gap-2">
                                            <AlertTriangle className={`w-5 h-5 ${selectedExplanation.color || 'text-cyan-400'}`} />
                                            {selectedExplanation.label}
                                        </h3>
                                        <button onClick={() => setSelectedExplanation(null)} className="text-zinc-500 hover:text-zinc-300 transition-colors">
                                            <XCircle className="w-5 h-5" />
                                        </button>
                                    </div>
                                    {selectedExplanation.desc && (
                                        <p className="mt-2 text-sm text-zinc-400 font-medium">
                                            {selectedExplanation.desc}
                                        </p>
                                    )}
                                </div>
                                <div className="p-6 space-y-5">
                                    <div>
                                        <h4 className="text-xs uppercase font-bold tracking-wider text-zinc-500 mb-2">Explication</h4>
                                        <p className="text-sm text-zinc-300 leading-relaxed">
                                            {selectedExplanation.explication}
                                        </p>
                                    </div>
                                    {selectedExplanation.solution && (
                                        <div>
                                            <h4 className="text-xs uppercase font-bold tracking-wider text-zinc-500 mb-2">Pistes / Solutions</h4>
                                            <div className="bg-cyan-500/10 border border-cyan-500/20 rounded-xl p-4">
                                                <p className="text-sm text-cyan-100 leading-relaxed">
                                                    {selectedExplanation.solution}
                                                </p>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Pagination */}
                    {totalPages > 1 && (
                        <div className="flex justify-center items-center gap-4 mt-8 pb-4">
                            <button
                                className="pagination-btn"
                                disabled={currentPage === 1}
                                onClick={() => setCurrentPage(currentPage - 1)}
                            >
                                Précédent
                            </button>
                            <div className="pagination-indicator">
                                {currentPage} <span className="pagination-separator">/</span> {totalPages}
                            </div>
                            <button
                                className="pagination-btn"
                                disabled={currentPage === totalPages}
                                onClick={() => setCurrentPage(currentPage + 1)}
                            >
                                Suivant
                            </button>
                        </div>
                    )}
                </>
            )}
        </PageLayout>
    );
}

export default ListeEvent;