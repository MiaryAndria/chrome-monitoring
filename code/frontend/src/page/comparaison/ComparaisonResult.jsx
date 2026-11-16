import { formatBytes,formatFreq,Badge,Bloc,CarteRessource,ligneUsageCpu,ligneUsageRam,lignePuissanceCpu,lignePuissanceRam,formatPct } from "../../fonction/utils/util";

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
                        ecart={ram.puissance.ecart_octets != null ? formatBytes(ram.puissance.ecart_octets) : null}
                    />
                </CarteRessource>
            </div>
        </div>
    );
}

export default ComparaisonResult;
