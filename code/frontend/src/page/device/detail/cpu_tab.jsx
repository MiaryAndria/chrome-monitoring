import { useState, useEffect } from 'react';
import ScrollableChart from '../../../styles/utils/ScrollableChart';
import { Download, Gauge, Thermometer, TrendingUp } from 'lucide-react';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid,
    Tooltip as RechartsTooltip, ResponsiveContainer
} from 'recharts';
import { extractCpuSummary, getCpuLatest, getCpuSomme } from '../../../fonction/deviceFonction';
import { getTempStyle, getUtilBarColor, getUtilColor, cleanLabel, formatDate, formatDateTime, exportPdf, exportExcel } from '../../../fonction/utils/util';
import ExportModal from '../../../components/ExportModal';
import Skeleton from '../../../components/Skeleton';
import NoData from './NoData';

function CpuTab({ reports, deviceId, datetimeFrom, datetimeTo }) {
    const [modal, setModal] = useState(false);
    const [latest, setLatest] = useState(null);
    const [somme, setSomme] = useState(null);
    const [sommeLoading, setSommeLoading] = useState(false);

    useEffect(() => {
        if (!deviceId) return;
        getCpuLatest(deviceId).then(setLatest);
    }, [deviceId]);

    useEffect(() => {
        if (!deviceId || !datetimeFrom || !datetimeTo) {
            setSomme(null);
            return;
        }

        let annule = false;
        setSommeLoading(true);
        getCpuSomme(deviceId, { date_debut: datetimeFrom, date_fin: datetimeTo })
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

    const summary = extractCpuSummary(reports);
    if (!summary && !latest) return <NoData title="CPU" />;

    const latestUtil = latest?.cpu_utiliser ?? summary?.latestUtil ?? null;
    const latestUtilTime = latest?.date ?? summary?.latestUtilTime ?? null;
    const chartData = [...(summary?.utilHistory || [])].reverse();
    const handleExport = async (format) => {
        try {
            const exportFn = format === 'pdf' ? exportPdf : exportExcel;
            await exportFn({ onglet: 'cpu', id: deviceId });
        } catch (e) {
            console.error(e);
        }
    };

    return (
        <div className="mt-4 space-y-5">
            {/* Utilisation CPU */}
            {latestUtil !== null && (
                <div className="telemetry-panel">
                    <div className="flex items-center gap-2 mb-4">
                        <Gauge className="w-4 h-4 text-cyan-400" />
                        <span className="text-sm font-semibold text-zinc-200">Utilisation CPU</span>
                        <span className="text-[10px] text-zinc-500 ml-auto">
                            {formatDate(latestUtilTime)}
                        </span>
                    </div>
                    <div className="flex items-end gap-4 mb-3">
                        <span className={`text-4xl font-bold ${getUtilColor(latestUtil)}`}>
                            {latestUtil}%
                        </span>
                    </div>
                    <div className="h-3 bg-zinc-800 rounded-full overflow-hidden">
                        <div className={`h-full rounded-full transition-all duration-500 ${getUtilBarColor(latestUtil)}`}
                            style={{ width: `${Math.max(latestUtil, 2)}%` }} />
                    </div>
                </div>
            )}

            {/* Températures */}
            {summary?.latestTemps?.length > 0 && (
                <div className="telemetry-panel">
                    <div className="flex items-center gap-2 mb-4">
                        <Thermometer className="w-4 h-4 text-amber-400" />
                        <span className="text-sm font-semibold text-zinc-200">Températures des capteurs</span>
                        <span className="text-[10px] text-zinc-500 ml-auto">
                            {formatDate(summary.latestTempTime)}
                        </span>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                        {summary.latestTemps.map((sensor, i) => {
                            const s = getTempStyle(sensor.temperatureCelsius);
                            return (
                                <div key={i} className={`temp-card ${s.bg} border ${s.border}`}>
                                    <div className="text-[10px] text-zinc-400 truncate mb-1">
                                        {cleanLabel(sensor.label)}
                                    </div>
                                    <div className={`text-xl font-bold ${s.text}`}>
                                        {sensor.temperatureCelsius}°C
                                    </div>
                                    <div className="mt-2 h-1.5 bg-zinc-800/50 rounded-full overflow-hidden">
                                        <div className={`h-full rounded-full ${s.bar}`}
                                            style={{ width: `${Math.min(sensor.temperatureCelsius, 100)}%` }} />
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}

            {/* Somme CPU sur la période filtrée en haut */}
            <div className="telemetry-panel">
                <div className="flex items-center gap-2 mb-4">
                    <Gauge className="w-4 h-4 text-cyan-400" />
                    <span className="text-sm font-semibold text-zinc-200">Somme CPU sur la période</span>
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
                                <span className="text-[10px] uppercase text-zinc-500">Total</span>
                                <span className="text-2xl font-bold text-cyan-400">
                                    {Number(somme.total).toFixed(2)} %
                                </span>
                            </div>
                        )}

                        <div className="space-y-1">
                            <span className="text-[10px] uppercase text-zinc-500">
                                {somme.same_day ? 'Détail par mesure' : 'Détail par jour'}
                            </span>
                            <ul className="text-xs text-zinc-300 divide-y divide-white/5">
                                {somme.detail.map((d, i) => (
                                    <li key={i} className="flex justify-between py-1">
                                        <span>{somme.same_day ? formatDateTime(d.datetime) : d.date.split('-').reverse().join('/')}</span>
                                        {d.valeur === null || d.valeur === undefined ? (
                                            <span className="text-zinc-500">Aucune donnée</span>
                                        ) : (
                                            <span className="text-cyan-400 font-semibold">{Number(d.valeur).toFixed(2)} %</span>
                                        )}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>
                )}
            </div>

            {/* Historique utilisation */}
            {summary?.utilHistory?.length > 0 && (
                <div className="telemetry-panel">
                    <div className="flex items-center gap-2 mb-4">
                        <TrendingUp className="w-4 h-4 text-cyan-400" />
                        <span className="text-sm font-semibold text-zinc-200">
                            Historique d'utilisation CPU
                        </span>
                        <span className="text-[10px] text-zinc-500 ml-auto">
                            {chartData.length} relevé(s)
                        </span>
                    </div>

                    <ScrollableChart>
                        <div style={{ width: Math.max(chartData.length * 36, 300) }} className="h-64">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 4 }}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                                    <XAxis
                                        dataKey="time"
                                        tickFormatter={(t) => {
                                            try {
                                                const d = new Date(t);
                                                return d.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
                                            } catch { return ''; }
                                        }}
                                        stroke="#71717a" fontSize={10} tickLine={false} axisLine={false}
                                    />
                                    <YAxis stroke="#71717a"fontSize={10}tickLine={false}axisLine={false}tickFormatter={(v) => `${v}%`}domain={[0, 50]}ticks={[0, 10, 20, 30, 40, 50]}/>
                                    <RechartsTooltip
                                        contentStyle={{ backgroundColor: 'rgba(24, 24, 32, 0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                                        itemStyle={{ color: '#22d3ee' }}
                                        cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                                        labelFormatter={(t) => formatDate(t)}
                                        formatter={(val) => [`${val}%`, 'Utilisation CPU']}
                                    />
                                    <Bar
                                        dataKey="value"
                                        fill="#06b6d4"
                                        radius={[4, 4, 0, 0]}
                                        activeBar={{ fill: '#67e8f9', stroke: '#a5f3fc', strokeWidth: 1 }}
                                    />
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

export default CpuTab;