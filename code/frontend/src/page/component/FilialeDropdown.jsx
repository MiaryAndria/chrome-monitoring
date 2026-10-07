import { useRef, useEffect, useState } from "react";
import { ChevronDown } from "lucide-react";

/**
 * Composant réutilisable : dropdown de sélection de filiale avec recherche interne.
 *
 * Props :
 *  - listeFiliales : tableau d'objets { org_unit_path, id? }
 *  - filiale       : valeur sélectionnée (org_unit_path), "" = toutes
 *  - setFiliale    : setter de la valeur
 */
function FilialeDropdown({
    listeFiliales = [],
    filiale,
    setFiliale,
}) {
    const dropdownRef = useRef(null);
    // États internes — inutile de les exposer au parent
    const [open, setOpen] = useState(false);
    const [filialeSearch, setFilialeSearch] = useState("");

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

    const filialeOptions = listeFiliales.filter((f) =>
        (f.org_unit_path || "").toLowerCase().includes((filialeSearch || "").toLowerCase())
    );

    const selectedLabel = filiale ? (filiale.split("/").pop() || filiale) : "";

    const handleSelect = (path) => {
        setFiliale(path);
        setOpen(false);
        setFilialeSearch("");
    };

    return (
        <div className="relative" ref={dropdownRef}>
            <button
                type="button"
                onClick={() => setOpen(!open)}
                className={`flex items-center gap-2 min-w-[200px] px-3 py-1.5 rounded-xl text-sm border transition-all duration-200 cursor-pointer ${
                    filiale
                        ? "bg-purple-500/15 text-purple-300 border-purple-500/40 shadow-[0_0_12px_rgba(168,85,247,0.15)]"
                        : "bg-zinc-900/60 text-zinc-400 border-white/8 hover:bg-zinc-800/80 hover:border-white/15"
                }`}
            >
                <span className="flex-1 text-left truncate">
                    {selectedLabel || "Toutes les filiales"}
                </span>
                <ChevronDown
                    className={`w-3.5 h-3.5 transition-transform duration-200 ${open ? "rotate-180" : ""}`}
                />
            </button>

            {open && (
                <div
                    className="absolute top-full left-0 mt-2 w-72 max-h-64 rounded-xl bg-zinc-900/95 backdrop-blur-xl border border-white/10 shadow-[0_20px_50px_-10px_rgba(0,0,0,0.8),0_0_30px_rgba(168,85,247,0.1)] z-[100] overflow-hidden"
                    style={{ animation: "modalScaleUp 150ms cubic-bezier(0.16,1,0.3,1)" }}
                >
                    {/* Champ de recherche */}
                    <div className="p-2 border-b border-white/5">
                        <input
                            type="text"
                            value={filialeSearch}
                            onChange={(e) => setFilialeSearch(e.target.value)}
                            placeholder="Rechercher une filiale..."
                            autoFocus
                            className="w-full px-3 py-1.5 rounded-lg bg-zinc-800/60 border border-white/5 text-zinc-200 text-xs placeholder-zinc-500 focus:outline-none focus:border-purple-400/40 transition-all"
                        />
                    </div>

                    {/* Liste des options */}
                    <div className="max-h-48 overflow-y-auto p-1">
                        {/* Option "Toutes" */}
                        <button
                            onClick={() => handleSelect("")}
                            className={`w-full text-left px-3 py-2 rounded-lg text-xs transition-all cursor-pointer ${
                                filiale === ""
                                    ? "bg-purple-500/15 text-purple-300"
                                    : "text-zinc-400 hover:bg-white/5 hover:text-zinc-200"
                            }`}
                        >
                            Toutes les filiales
                        </button>

                        {filialeOptions.map((f, idx) => {
                            const path = f.org_unit_path || "";
                            const label = path.split("/").pop() || path;
                            return (
                                <button
                                    key={f.id ?? idx}
                                    onClick={() => handleSelect(path)}
                                    className={`w-full text-left px-3 py-2 rounded-lg text-xs transition-all cursor-pointer ${
                                        filiale === path
                                            ? "bg-purple-500/15 text-purple-300"
                                            : "text-zinc-400 hover:bg-white/5 hover:text-zinc-200"
                                    }`}
                                >
                                    <span className="font-medium">{label}</span>
                                    <span className="block text-[10px] text-zinc-600 font-mono mt-0.5 truncate">
                                        {path}
                                    </span>
                                </button>
                            );
                        })}

                        {filialeOptions.length === 0 && (
                            <p className="text-xs text-zinc-600 text-center py-3">
                                Aucune filiale trouvée
                            </p>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}

export default FilialeDropdown;
