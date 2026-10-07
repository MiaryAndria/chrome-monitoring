import { useRef, useEffect, useState } from "react";
import { ChevronDown } from "lucide-react";

/**
 * Composant réutilisable : dropdown de sélection de statut.
 *
 * Props :
 *  - listeStatuts : tableau d'objets { nom, id? }
 *  - statut       : valeur sélectionnée (nom du statut), "" = tous
 *  - setStatut    : setter de la valeur
 *  - labelTous    : label de l'option "tous" (défaut : "Tous les statuts")
 */
function StatutDropdown({
    listeStatuts = [],
    statut,
    setStatut,
    labelTous = "Tous les statuts",
}) {
    const dropdownRef = useRef(null);
    // État interne — inutile de l'exposer au parent
    const [open, setOpen] = useState(false);

    // Fermer en cliquant à l'extérieur
    useEffect(() => {
        const handleClickOutside = (e) => {
            if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
                setOpen(false);
            }
        };
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    const handleSelect = (nom) => {
        setStatut(nom);
        setOpen(false);
    };

    return (
        <div className="relative" ref={dropdownRef}>
            <button
                type="button"
                onClick={() => setOpen(!open)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-xl text-sm border transition-all duration-200 cursor-pointer focus:outline-none ${
                    statut
                        ? "bg-purple-500/15 text-purple-300 border-purple-500/40 shadow-[0_0_12px_rgba(168,85,247,0.15)]"
                        : "bg-zinc-900/60 text-zinc-400 border-white/10 hover:bg-zinc-800/80 hover:border-white/15"
                }`}
            >
                <span className="flex-1 text-left truncate">
                    {statut || labelTous}
                </span>
                <ChevronDown
                    className={`w-3.5 h-3.5 transition-transform duration-200 ${open ? "rotate-180" : ""}`}
                />
            </button>

            {open && (
                <div
                    className="absolute top-full left-0 mt-2 w-56 max-h-48 overflow-y-auto p-1 rounded-xl bg-zinc-900/95 backdrop-blur-xl border border-white/10 shadow-[0_20px_50px_-10px_rgba(0,0,0,0.8),0_0_30px_rgba(168,85,247,0.1)] z-[100]"
                    style={{ animation: "modalScaleUp 150ms cubic-bezier(0.16,1,0.3,1)" }}
                >
                    {/* Option "Tous" */}
                    <button
                        onClick={() => handleSelect("")}
                        className={`w-full text-left px-3 py-2 rounded-lg text-xs transition-all cursor-pointer ${
                            statut === ""
                                ? "bg-purple-500/15 text-purple-300"
                                : "text-zinc-400 hover:bg-white/5 hover:text-zinc-200"
                        }`}
                    >
                        {labelTous}
                    </button>

                    {listeStatuts.map((s, i) => {
                        const nom = s.nom || "";
                        return (
                            <button
                                key={s.id ?? i}
                                onClick={() => handleSelect(nom)}
                                className={`w-full text-left px-3 py-2 rounded-lg text-xs transition-all cursor-pointer ${
                                    statut === nom
                                        ? "bg-purple-500/15 text-purple-300"
                                        : "text-zinc-400 hover:bg-white/5 hover:text-zinc-200"
                                }`}
                            >
                                <span className="font-medium">{nom}</span>
                            </button>
                        );
                    })}

                    {listeStatuts.length === 0 && (
                        <p className="text-xs text-zinc-600 text-center py-3">
                            Aucun statut trouvé
                        </p>
                    )}
                </div>
            )}
        </div>
    );
}

export default StatutDropdown;
