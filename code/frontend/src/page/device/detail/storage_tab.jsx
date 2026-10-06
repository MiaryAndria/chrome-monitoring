import { useState } from 'react';
import { HardDrive, TrendingUp } from 'lucide-react';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid,
    Tooltip as RechartsTooltip, ResponsiveContainer
} from 'recharts';
import { extractStorageSummary } from '../../../fonction/deviceFonction';
import { getUtilBarColor, getUtilColor, formatBytes, formatDate, usagePercent, exportPdf, exportExcel } from '../../../fonction/utils/util';
import ExportModal from '../../../components/ExportModal';
import NoData from './NoData';

function StorageTab({ reports, device, deviceId }) {
    const [modal, setModal] = useState(false);
    const handleExport = async (format) => {
        try {
            const exportFn = format === 'pdf' ? exportPdf : exportExcel;
            await exportFn({ onglet: 'stockage', id: deviceId });
        } catch (e) {
            console.error(e);
        }
    };

    const summary = extractStorageSummary(reports);
    const disks = summary?.disks ?? [];

    if (!disks.length) {
        return <NoData title="Stockage" />;
    }

    return (
        <div className="mt-4 space-y-5">
            {/* Volumes de stockage */}
            <div className="telemetry-panel">
                <div className="flex items-center gap-2 mb-4">
                    <HardDrive className="w-4 h-4 text-amber-400" />
                    <span className="text-sm font-semibold text-zinc-200">Volumes de stockage</span>
                    <span className="text-[10px] text-zinc-500 ml-auto">{formatDate(summary?.time)}</span>
                </div>
                <div className="space-y-4">
                    {disks.map((disk, i) => {
                        const total = device?.disk_total ?? null;
                        const freeFromDisk = disk.storageFreeBytes ?? null;
                        const usedFromDisk = disk.storageUsedBytes ?? null;
                        const free = freeFromDisk ?? (total !== null && usedFromDisk !== null ? Math.max(total - usedFromDisk, 0) : device?.disk_free ?? null);
                        const used = usedFromDisk ?? (total !== null && free !== null ? Math.max(total - free, 0) : device?.disk_used ?? null);
                        const pct = total !== null && free !== null ? usagePercent(free, total) : null;
                        return (
                            <div key={i} className="p-4 rounded-xl bg-zinc-800/40 border border-white/5">
                                <div className="flex items-center justify-between mb-3">
                                    <span className="text-sm font-mono text-zinc-200">
                                        {disk.volumeId || `Volume ${i + 1}`}
                                    </span>
                                    {pct !== null && (
                                        <span className={`text-sm font-bold ${getUtilColor(pct)}`}>{pct}% utilisé</span>
                                    )}
                                </div>
                                <div className="grid grid-cols-3 gap-3 mb-3">
                                    <div className="stat-card-sm">
                                        <span className="text-[10px] text-zinc-500">Total</span>
                                        <span className="text-sm font-bold text-zinc-200">
                                            {formatBytes(total)}
                                        </span>
                                    </div>
                                    <div className="stat-card-sm">
                                        <span className="text-[10px] text-zinc-500">Libre</span>
                                        <span className="text-sm font-bold text-emerald-400">
                                            {formatBytes(free)}
                                        </span>
                                    </div>
                                    <div className="stat-card-sm">
                                        <span className="text-[10px] text-zinc-500">Utilisé</span>
                                        <span className="text-sm font-bold text-amber-400">
                                            {formatBytes(used)}
                                        </span>
                                    </div>
                                </div>
                                {pct !== null && (
                                    <div className="h-2.5 bg-zinc-800 rounded-full overflow-hidden">
                                        <div className={`h-full rounded-full transition-all duration-500 ${getUtilBarColor(pct)}`}
                                            style={{ width: `${pct}%` }} />
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Historique Stockage */}
            {summary?.history && summary.history.length > 0 && (
                <div className="telemetry-panel">
                    <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-2">
                            <TrendingUp className="w-4 h-4 text-amber-400" />
                            <span className="text-sm font-semibold text-zinc-200">Historique stockage libre</span>
                        </div>
                        <span className="text-[10px] text-zinc-500">
                            {summary.history.length} relevé(s)
                        </span>
                    </div>

                    <div className="h-64 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={[...summary.history].reverse()} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
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
                                    itemStyle={{ color: '#fbbf24' }}
                                    cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                                    labelFormatter={(t) => formatDate(t)}
                                    formatter={(val) => [formatBytes(val), 'Libre']}
                                />
                                <Bar dataKey="free" fill="#f59e0b" radius={[4, 4, 0, 0]} />
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

export default StorageTab;