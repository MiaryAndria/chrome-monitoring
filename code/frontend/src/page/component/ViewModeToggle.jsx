import { LayoutGrid, List } from "lucide-react";

/**
 * Composant réutilisable : toggle grille / tableau.
 *
 * Props :
 *  - viewMode    : "grid" | "table"
 *  - setViewMode : setter du mode de vue
 */
function ViewModeToggle({ viewMode, setViewMode }) {
    return (
        <div className="flex bg-zinc-900 rounded-lg p-1 border border-white/10">
            <button
                onClick={() => setViewMode("grid")}
                className={`p-1.5 rounded-md transition-colors ${
                    viewMode === "grid"
                        ? "bg-cyan-500/20 text-cyan-400"
                        : "text-zinc-500 hover:text-zinc-300"
                }`}
                title="Vue en grille"
            >
                <LayoutGrid className="w-4 h-4" />
            </button>
            <button
                onClick={() => setViewMode("table")}
                className={`p-1.5 rounded-md transition-colors ${
                    viewMode === "table"
                        ? "bg-cyan-500/20 text-cyan-400"
                        : "text-zinc-500 hover:text-zinc-300"
                }`}
                title="Vue en tableau"
            >
                <List className="w-4 h-4" />
            </button>
        </div>
    );
}

export default ViewModeToggle;
