function DateFilter({ dateDebut, dateFin, setDateDebut, setDateFin, onFilter, onReset }) {
    const inputClass =
        "bg-zinc-900 border border-white/10 rounded-lg px-3 py-1.5 text-xs text-zinc-300 outline-none focus:border-cyan-500/50";

    return (
        <div className="flex flex-wrap items-end gap-3">
            <div className="flex flex-col gap-1">
                <span className="text-[10px] text-zinc-500">Date de début</span>
                <input
                    type="date"
                    value={dateDebut}
                    max={dateFin || undefined}
                    onChange={(e) => setDateDebut(e.target.value)}
                    className={inputClass}
                />
            </div>

            <div className="flex flex-col gap-1">
                <span className="text-[10px] text-zinc-500">Date de fin</span>
                <input
                    type="date"
                    value={dateFin}
                    min={dateDebut || undefined}
                    onChange={(e) => setDateFin(e.target.value)}
                    className={inputClass}
                />
            </div>

            <button
                onClick={onFilter}
                disabled={!dateDebut || !dateFin}
                className="px-4 py-1.5 rounded-lg text-xs font-medium bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 hover:bg-cyan-500/30 transition-all disabled:opacity-40 disabled:cursor-not-allowed"
            >
                Filtrer
            </button>

            <button
                onClick={onReset}
                className="px-4 py-1.5 rounded-lg text-xs font-medium text-zinc-400 border border-white/10 hover:bg-white/5 hover:text-zinc-200 transition-all"
            >
                Réinitialiser
            </button>
        </div>
    );
}

export default DateFilter;