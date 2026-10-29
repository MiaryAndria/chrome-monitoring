import { useState, useEffect } from 'react';
import { Download, Activity, TrendingUp } from 'lucide-react';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid,
    Tooltip as RechartsTooltip, ResponsiveContainer
} from 'recharts';
import ScrollableChart from '../../../styles/utils/ScrollableChart';
import { extractRamSummary, getRamMaxTotal, getRamLatest, getRamSomme } from '../../../fonction/deviceFonction';
import {getUtilColor, getUtilBarColor, formatDate, formatDateTime, formatBytes, exportPdf, exportExcel } from '../../../fonction/utils/util';
import ExportModal from '../../../components/ExportModal';
import Skeleton from '../../../components/Skeleton';
import NoData from './NoData';

function RamTab({ reports, device, deviceId, datetimeFrom, datetimeTo }) {
    const [modal, setModal] = useState(false);
    const [maxTotal, setMaxTotal] = useState(null);
    const [latest, setLatest] = useState(null);
    const [somme, setSomme] = useState(null);
    const [sommeLoading, setSommeLoading] = useState(false);

    useEffect(() => {
        if (!deviceId) return;
        getRamMaxTotal(deviceId).then(setMaxTotal);
        getRamLatest(deviceId).then(setLatest);
    }, [deviceId]);

    useEffect(() => {
        if (!deviceId || !datetimeFrom || !datetimeTo) {
            setSomme(null);
            return;
        }

        let annule = false;
        setSommeLoading(true);
        getRamSomme(deviceId, { date_debut: datetimeFrom, date_fin: datetimeTo })
            .then((data) => {
                if (!annule) setSomme(data);
            })
            .catch((e) => {
                if (!annule) console.error(e);
            })
            .finally(() => {
                if (!annule) setSommeLoading(false);
            });

        return () => {
            annule = true;
        };
    }, [deviceId, datetimeFrom, datetimeTo]);

    const handleExport = async (format) => {
        try {
            const exportFn = format === 'pdf' ? exportPdf : exportExcel;
            await exportFn({ onglet: 'ram', id: deviceId });
        } catch (e) {
            console.error(e);
        }
    };

    const summary = extractRamSummary(reports, maxTotal ?? device?.ram_total);
    if (!summary && !latest) return <NoData title="RAM" />;

    const total = maxTotal ?? latest?.ram_total ?? summary?.total ?? null;
    const free = latest?.ram_libre ?? summary?.free ?? null;
    const used = latest?.ram_utiliser
        ?? (total !== null && free !== null ? Math.max(total - free, 0) : null);
    const pct = latest?.utilisation_pct ?? null;
    const observedAt = latest?.date ?? summary?.time;

    return (
        <div className="mt-4 space-y-5">
            <div className="telemetry-panel">
                <div className="flex items-center gap-2 mb-4">
                    <Activity className="w-4 h-4 text-purple-400" />
                    <span className="text-sm font-semibold text-zinc-200">État de la mémoire</span>
                    <span className="text-[10px] text-zinc-500 ml-auto">{formatDate(observedAt)}</span>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    <div className="stat-card">
                        <span className="text-[10px] text-zinc-500 uppercase">Mémoire libre</span>
                        <span className="text-xl font-bold text-purple-400">{formatBytes(free)}</span>
                    </div>
                    {total !== null && (
                        <div className="stat-card">
                            <span className="text-[10px] text-zinc-500 uppercase">Mémoire totale</span>
                            <span className="text-xl font-bold text-zinc-200">{formatBytes(total)}</span>
                        </div>
                    )}
                    {used !== null && (
                        <div className="stat-card">
                            <span className="text-[10px] text-zinc-500 uppercase">Mémoire utilisée</span>
                            <span className="text-xl font-bold text-zinc-200">{formatBytes(used)}</span>
                        </div>
                    )}
                    {pct !== null && (
                        <div className="stat-card">
                            <span className="text-[10px] text-zinc-500 uppercase">Utilisation</span>
                            <span className={`text-xl font-bold ${getUtilColor(pct)}`}>{pct}%</span>
                        </div>
                    )}
                    {summary?.pageFaults !== undefined && summary?.pageFaults !== null && (
                        <div className="stat-card">
                            <span className="text-[10px] text-zinc-500 uppercase">Page faults</span>
                            <span className="text-xl font-bold text-amber-400">
                                {typeof summary.pageFaults === 'number' ? summary.pageFaults.toLocaleString() : summary.pageFaults}
                            </span>
                        </div>
                    )}
                </div>

                {pct !== null && (
                    <div>
                        <div className="flex justify-between text-[10px] text-zinc-500 mb-1">
                            <span>Utilisé</span>
                            <span>{pct}%</span>
                        </div>
                        <div className="h-3 bg-zinc-800 rounded-full overflow-hidden">
                            <div className={`h-full rounded-full transition-all duration-500 ${getUtilBarColor(pct)}`}
                                style={{ width: `${pct}%` }} />
                        </div>
                    </div>
                )}
            </div>

            {/* Somme RAM sur la période filtrée en haut */}
            <div className="telemetry-panel">
                <div className="flex items-center gap-2 mb-4">
                    <Activity className="w-4 h-4 text-purple-400" />
                    <span className="text-sm font-semibold text-zinc-200">Somme RAM sur la période</span>
                </div>

                {sommeLoading ? (
                    <Skeleton className="h-16 w-full" />
                ) : !somme ? (
                    <p className="text-xs text-zinc-500">
                        Appliquez le filtre date + heure en haut de la page pour calculer la somme.
                    </p>
                ) : !somme.detail?.some((d) => d.valeur !== null && d.valeur !== undefined) ? (
                    <p className="text-xs text-zinc-500">
                        Aucune donnée relevée sur cette période.
                    </p>
                ) : (
                    <div className="space-y-3">
                        {!somme.same_day && somme.total !== null && somme.total !== undefined && (
                            <div className="flex flex-wrap items-baseline gap-2">
                                <span className="text-[10px] uppercase text-zinc-500">Total utilisé</span>
                                <span className="text-2xl font-bold text-purple-400">
                                    {formatBytes(somme.total)}
                                </span>
                            </div>
                        )}

                        <div className="space-y-1">
                            <span className="text-[10px] uppercase text-zinc-500">
                                {somme.same_day ? 'Total utilisé par mesure' : 'Total utilisé par jour'}
                            </span>
                            <ul className="text-xs text-zinc-300 divide-y divide-white/5">
                                {somme.detail.map((d, i) => (
                                    <li key={i} className="flex justify-between py-1">
                                        <span>{somme.same_day ? formatDateTime(d.datetime) : d.date.split('-').reverse().join('/')}</span>
                                        {d.valeur === null || d.valeur === undefined ? (
                                            <span className="text-zinc-500">Aucune donnée</span>
                                        ) : (
                                            <span className="text-purple-400 font-semibold">{formatBytes(d.valeur)}</span>
                                        )}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>
                )}
            </div>

            {/* Historique RAM */}
            {summary?.freeHistory?.length > 0 && (
                <div className="telemetry-panel">
                    <div className="flex items-center gap-2 mb-4">
                        <TrendingUp className="w-4 h-4 text-purple-400" />
                        <span className="text-sm font-semibold text-zinc-200">Historique mémoire libre</span>
                        <span className="text-[10px] text-zinc-500 ml-auto">
                            {summary.freeHistory.length} relevé(s)
                        </span>
                    </div>

                    <ScrollableChart>
                        <div
                            style={{ width: Math.max(summary.freeHistory.length * 36, 300) }}
                            className="h-64"
                        >
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart
                                    data={[...summary.freeHistory].reverse()}
                                    margin={{ top: 10, right: 10, left: -10, bottom: 4 }}
                                >
                                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                                    <XAxis
                                        dataKey="time"
                                        tickFormatter={(t) => {
                                            try {
                                                return new Date(t).toLocaleTimeString('fr-FR', {
                                                    hour: '2-digit',
                                                    minute: '2-digit'
                                                });
                                            } catch {
                                                return '';
                                            }
                                        }}
                                        stroke="#71717a"
                                        fontSize={10}
                                        tickLine={false}
                                        axisLine={false}
                                    />
                                    <YAxis
                                        stroke="#71717a"
                                        fontSize={10}
                                        tickLine={false}
                                        axisLine={false}
                                        domain={total != null ? [0, total] : [0, 'auto']}
                                        tickFormatter={(v) => formatBytes(v)}
                                    />
                                    <RechartsTooltip
                                        contentStyle={{ backgroundColor: 'rgba(24, 24, 32, 0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                                        itemStyle={{ color: '#c084fc' }}
                                        cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                                        labelFormatter={(t) => formatDate(t)}
                                        formatter={(val) => [formatBytes(val), 'Libre']}
                                    />
                                    <Bar dataKey="free" fill="#a855f7" radius={[4, 4, 0, 0]} />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </ScrollableChart>
                </div>
            )}

            <button className="device-detail-btn" onClick={() => setModal(v => !v)}><Download className="w-4 h-4" /> Exporter</button>
            <ExportModal
                open={modal}
                onClose={() => setModal(false)}
                onExportPdf={() => handleExport('pdf')}
                onExportExcel={() => handleExport('excel')}
            />
        </div>
    );
}

export default RamTab;