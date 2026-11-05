import { formatBytes } from "../../fonction/utils/util";

function formatFreq(khz) {
    const n = Number(khz);
    if (!n) return "—";
    return `${(n / 1_000_000).toFixed(1)} GHz`;
}

function Badge({ gagnant, labels }) {
    if (gagnant === "indetermine") {
        return (
            <span className="text-[11px] px-2 py-0.5 rounded-lg bg-zinc-500/10 text-zinc-400 border border-white/10">
                Indéterminé
            </span>
        );
    }
    if (gagnant === "egal") {
        return (
            <span className="text-[11px] px-2 py-0.5 rounded-lg bg-zinc-500/10 text-zinc-300 border border-white/10">
                Égalité
            </span>
        );
    }
    return (
        <span className="text-[11px] px-2 py-0.5 rounded-lg bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
            {gagnant === "a" ? labels.a : labels.b} en tête
        </span>
    );
}

function Bloc({ titre, gagnant, labels, ligneA, ligneB, ecart }) {
    return (
        <div className="rounded-xl border border-white/10 p-4 bg-zinc-900/40 space-y-3">
            <div className="flex items-center justify-between gap-2">
                <span className="text-xs uppercase tracking-wider text-zinc-400 font-semibold">{titre}</span>
                <Badge gagnant={gagnant} labels={labels} />
            </div>
            <div className="grid grid-cols-2 gap-3">
                <div className="space-y-0.5 min-w-0">
                    <div className="text-[11px] text-zinc-500 truncate">{labels.a}</div>
                    {ligneA.map((l, i) => (
                        <div key={i} className="text-sm text-zinc-200 break-words">{l}</div>
                    ))}
                </div>
                <div className="space-y-0.5 min-w-0">
                    <div className="text-[11px] text-zinc-500 truncate">{labels.b}</div>
                    {ligneB.map((l, i) => (
                        <div key={i} className="text-sm text-zinc-200 break-words">{l}</div>
                    ))}
                </div>
            </div>
            {ecart != null && <div className="text-[11px] text-zinc-500">Écart : {ecart}</div>}
        </div>
    );
}

function CarteRessource({ titre, children }) {
    return (
        <div className="glass-panel rounded-2xl p-5 space-y-3">
            <h3 className="text-sm font-semibold text-zinc-200">{titre}</h3>
            {children}
        </div>
    );
}

function ligneUsageCpu(c) {
    if (!c || c.moyenne == null) return ["Aucune donnée relevée"];
    return [`${formatPct(c.moyenne)} (moyenne)`, `min ${formatPct(c.min)} · max ${formatPct(c.max)} · n ${c.n}`];
}

function ligneUsageRam(r) {
    if (!r || r.moyenne_pct == null) return ["Aucune donnée relevée"];
    return [`${formatPct(r.moyenne_pct)} utilisés`, `${formatBytes(r.moyenne_util) || "—"} / ${formatBytes(r.total) || "—"}`];
}

function lignePuissanceCpu(s) {
    return [s.cpu_model || "—", `${formatFreq(s.freq_max_proc)} · ${s.cpu_architecture || "—"}`, `score ${s.score ?? "—"}`];
}

function lignePuissanceRam(s) {
    return [formatBytes(s.ram_total) || "—", `score ${s.score ?? "—"}`];
}

function formatPct(value) {
    return value == null ? "—" : `${value} %`;
}

function ComparaisonResult({ resultat, labels }) {
    if (!resultat) return null;
    const { cpu, ram, verdict } = resultat;

    return (
        <div className="space-y-4">
            {verdict?.resume && (
                <div className="glass-panel rounded-2xl p-4 text-sm text-zinc-200 border-l-2 border-cyan-400/50">
                    {verdict.resume}
                </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <CarteRessource titre="CPU">
                    <Bloc
                        titre="Usage (moyenne)"
                        gagnant={cpu.usage.plus_utilise}
                        labels={labels}
                        ligneA={ligneUsageCpu(cpu.usage.a)}
                        ligneB={ligneUsageCpu(cpu.usage.b)}
                        ecart={cpu.usage.ecart_pts != null ? `${cpu.usage.ecart_pts} pts` : null}
                    />
                    <Bloc
                        titre="Puissance (specs)"
                        gagnant={cpu.puissance.plus_puissant}
                        labels={labels}
                        ligneA={lignePuissanceCpu(cpu.puissance.a)}
                        ligneB={lignePuissanceCpu(cpu.puissance.b)}
                        ecart={cpu.puissance.ecart != null ? String(cpu.puissance.ecart) : null}
                    />
                </CarteRessource>

                <CarteRessource titre="RAM">
                    <Bloc
                        titre="Usage (moyenne)"
                        gagnant={ram.usage.plus_utilise}
                        labels={labels}
                        ligneA={ligneUsageRam(ram.usage.a)}
                        ligneB={ligneUsageRam(ram.usage.b)}
                        ecart={ram.usage.ecart_pct != null ? `${ram.usage.ecart_pct} %` : null}
                    />
                    <Bloc
                        titre="Capacité"
                        gagnant={ram.puissance.plus_puissant}
                        labels={labels}
                        ligneA={lignePuissanceRam(ram.puissance.a)}
                        ligneB={lignePuissanceRam(ram.puissance.b)}
                        ecart={ram.puissance.ecart_octets != null ? formatBytes(Math.abs(ram.puissance.ecart_octets)) : null}
                    />
                </CarteRessource>
            </div>
        </div>
    );
}

export default ComparaisonResult;
