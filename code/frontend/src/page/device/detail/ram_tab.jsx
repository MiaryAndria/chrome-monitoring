import { useState } from 'react';
import { Activity, TrendingUp } from 'lucide-react';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid,
    Tooltip as RechartsTooltip, ResponsiveContainer
} from 'recharts';
import { extractRamSummary } from '../../../fonction/deviceFonction';
import { usagePercent, getUtilColor, getUtilBarColor, formatDate, formatBytes, exportPdf, exportExcel } from '../../../fonction/utils/util';
import ExportModal from '../../../components/ExportModal';
import NoData from './NoData';

function RamTab({ reports, device, deviceId }) {
    const [modal, setModal] = useState(false);

    const handleExport = async (format) => {
        try {
            const exportFn = format === 'pdf' ? exportPdf : exportExcel;
            await exportFn({ onglet: 'ram', id: deviceId });
        } catch (e) {
            console.error(e);
        }
    };

    const summary = extractRamSummary(reports, device?.ram_total);
    if (!summary) return <NoData title="RAM" />;

    const total = summary.total ?? null;
    const free = summary.free ?? null;
    const used = total !== null && free !== null ? Math.max(total - free, 0) : null;
    const pct = total !== null && free !== null ? usagePercent(free, total) : null;

    return (
        <div className="mt-4 space-y-5">
            <div className="telemetry-panel">
                <div className="flex items-center gap-2 mb-4">
                    <Activity className="w-4 h-4 text-purple-400" />
                    <span className="text-sm font-semibold text-zinc-200">État de la mémoire</span>
                    <span className="text-[10px] text-zinc-500 ml-auto">{formatDate(summary.time)}</span>
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
                    {summary.pageFaults !== undefined && summary.pageFaults !== null && (
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

            {/* Historique RAM */}
            {summary.freeHistory && summary.freeHistory.length > 0 && (
                <div className="telemetry-panel">
                    <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-2">
                            <TrendingUp className="w-4 h-4 text-purple-400" />
                            <span className="text-sm font-semibold text-zinc-200">Historique mémoire libre</span>
                        </div>
                        <span className="text-[10px] text-zinc-500">
                            {summary.freeHistory.length} relevé(s)
                        </span>
                    </div>

                    <div className="h-64 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={[...summary.freeHistory].reverse()} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                                <XAxis
                                    dataKey="time"
                                    tickFormatter={(t) => {
                                        try { return new Date(t).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }); }
                                        catch { return ''; }
                                    }}
                                    stroke="#71717a" fontSize={10} tickLine={false} axisLine={false}
                                />
                                <YAxis stroke="#71717a" fontSize={10} tickLine={false} axisLine={false} tickFormatter={(v) => formatBytes(v)} />
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
                </div>
            )}

            <button className="device-detail-btn" onClick={() => setModal(v => !v)}>Exporter</button>
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