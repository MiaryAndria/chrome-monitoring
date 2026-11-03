import { useRef, useEffect, useState } from "react";
import { ChevronDown } from "lucide-react";

/**
 * Composant reutilisable : dropdown generique (meme style que StatutDropdown).
 *
 * Props :
 *  - options   : tableau d'objets { value, label }
 *  - value     : valeur selectionnee
 *  - onChange  : setter appele avec la nouvelle valeur
 *  - placeholder : texte affiche quand rien n'est selectionne
 *  - labelTous : si fourni, ajoute une option vide "labelTous" en premier
 */
function SelectDropdown({ options = [], value, onChange, placeholder = "Selectionner", labelTous = null }) {
    const dropdownRef = useRef(null);
    const [open, setOpen] = useState(false);

    useEffect(() => {
        const handleClickOutside = (e) => {
            if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
                setOpen(false);
            }
        };
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    let label = placeholder;
    for (const option of options) {
        if (String(option.value) === String(value)) {
            label = option.label;
        }
    }
    if ((value === "" || value === null || value === undefined) && labelTous) {
        label = labelTous;
    }

    const actif = value !== "" && value !== null && value !== undefined;

    const choisir = (valeur) => {
        onChange(valeur);
        setOpen(false);
    };

    return (
        <div className="relative" ref={dropdownRef}>
            <button
                type="button"
                onClick={() => setOpen(!open)}
                className={`flex items-center gap-2 w-full min-w-[180px] px-3 py-1.5 rounded-xl text-sm border transition-all duration-200 cursor-pointer focus:outline-none ${
                    actif
                        ? "bg-purple-500/15 text-purple-300 border-purple-500/40 shadow-[0_0_12px_rgba(168,85,247,0.15)]"
                        : "bg-zinc-900/60 text-zinc-400 border-white/10 hover:bg-zinc-800/80 hover:border-white/15"
                }`}
            >
                <span className="flex-1 text-left truncate">{label}</span>
                <ChevronDown
                    className={`w-3.5 h-3.5 transition-transform duration-200 ${open ? "rotate-180" : ""}`}
                />
            </button>

            {open && (
                <div className="absolute top-full left-0 mt-2 w-full max-h-48 overflow-y-auto p-1 rounded-xl bg-zinc-900/95 backdrop-blur-xl border border-white/10 shadow-[0_20px_50px_-10px_rgba(0,0,0,0.8),0_0_30px_rgba(168,85,247,0.1)] z-[100]">
                    {labelTous && (
                        <button
                            onClick={() => choisir("")}
                            className={`w-full text-left px-3 py-2 rounded-lg text-xs transition-all cursor-pointer ${
                                value === ""
                                    ? "bg-purple-500/15 text-purple-300"
                                    : "text-zinc-400 hover:bg-white/5 hover:text-zinc-200"
                            }`}
                        >
                            {labelTous}
                        </button>
                    )}

                    {options.map((option) => (
                        <button
                            key={option.value}
                            onClick={() => choisir(option.value)}
                            className={`w-full text-left px-3 py-2 rounded-lg text-xs transition-all cursor-pointer ${
                                String(value) === String(option.value)
                                    ? "bg-purple-500/15 text-purple-300"
                                    : "text-zinc-400 hover:bg-white/5 hover:text-zinc-200"
                            }`}
                        >
                            {option.label}
                        </button>
                    ))}

                    {options.length === 0 && (
                        <p className="text-xs text-zinc-600 text-center py-3">Aucune option</p>
                    )}
                </div>
            )}
        </div>
    );
}

export default SelectDropdown;
