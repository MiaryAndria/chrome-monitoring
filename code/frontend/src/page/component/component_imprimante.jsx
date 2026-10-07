import { Printer } from "lucide-react";

function ImprimanteCard({ imp }) {
    return (
        <div className="device-card group bg-amber-500/5 border-amber-500/20" 
             style={{ 
                 '--card-glow': 'radial-gradient(circle at top right, rgba(245, 158, 11, 0.08), transparent 70%)',
                 '--card-border-hover': 'rgba(245, 158, 11, 0.5)',
                 '--card-shadow': 'rgba(245, 158, 11, 0.2)'
             }}>
            {/* Icône + fabricant */}
            <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center flex-shrink-0 group-hover:bg-amber-500/20 transition-colors">
                    <Printer className="w-5 h-5 text-amber-400" />
                </div>
                <div className="min-w-0">
                    <p className="text-sm font-bold text-zinc-200 group-hover:text-amber-300 transition-colors truncate">
                        {imp.vendor || <span className="text-zinc-600 font-normal">Fabricant inconnu</span>}
                    </p>
                    <p className="text-xs text-zinc-500 truncate mt-0.5">
                        {imp.nom || "Modèle inconnu"}
                    </p>
                </div>
            </div>

            {/* Séparateur */}
            <div className="border-t border-white/5" />

            {/* VID / PID */}
            <div className="grid grid-cols-2 gap-2 mt-3">
                <div className="bg-zinc-800/50 rounded-lg p-2.5 text-center border border-white/5">
                    <p className="text-[10px] text-zinc-500 uppercase font-semibold mb-0.5">VID</p>
                    <p className="text-xs font-mono font-bold text-zinc-300">
                        {imp.vid ?? <span className="text-zinc-600">—</span>}
                    </p>
                </div>
                <div className="bg-zinc-800/50 rounded-lg p-2.5 text-center border border-white/5">
                    <p className="text-[10px] text-zinc-500 uppercase font-semibold mb-0.5">PID</p>
                    <p className="text-xs font-mono font-bold text-zinc-300">
                        {imp.pid ?? <span className="text-zinc-600">—</span>}
                    </p>
                </div>
            </div>

            {/* ID interne */}
            <p className="text-[10px] text-zinc-600 font-mono text-center mt-2">
                #{imp.id}
            </p>
        </div>
    );
}
export default ImprimanteCard