import { XCircle } from "lucide-react";

/**
 * Composant réutilisable : bouton "Réinitialiser les filtres".
 * S'affiche uniquement si `actif` est true.
 *
 * Props :
 *  - actif    : boolean — affiche le bouton si true
 *  - onClick  : fonction appelée au clic
 *  - label    : texte du bouton (défaut : "Réinitialiser")
 */
function ResetFiltreButton({ actif, onClick, label = "Réinitialiser" }) {
    if (!actif) return null;

    return (
        <button
            onClick={onClick}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-xs font-semibold hover:bg-red-500/20 hover:border-red-500/30 transition-all cursor-pointer"
        >
            <XCircle className="w-3.5 h-3.5" />
            {label}
        </button>
    );
}

export default ResetFiltreButton;
