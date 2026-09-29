// const renderRamTab = () => {
//         const reports = tabData.ram;
//         const summary = extractRamSummary(reports);
//         if (!summary) return noData('RAM');

//         const pct = summary.total ? usagePercent(summary.free, summary.total) : null;

//         return (
//             <div className="mt-4 space-y-5">
//                 <div className="telemetry-panel">
//                     <div className="flex items-center gap-2 mb-4">
//                         <Activity className="w-4 h-4 text-purple-400" />
//                         <span className="text-sm font-semibold text-zinc-200">État de la mémoire</span>
//                         <span className="text-[10px] text-zinc-500 ml-auto">{formatDate(summary.time)}</span>
//                     </div>

//                     <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-4">
//                         <div className="stat-card">
//                             <span className="text-[10px] text-zinc-500 uppercase">Mémoire libre</span>
//                             <span className="text-xl font-bold text-purple-400">{formatBytes(summary.free)}</span>
//                         </div>
//                         {summary.total && (
//                             <div className="stat-card">
//                                 <span className="text-[10px] text-zinc-500 uppercase">Mémoire totale</span>
//                                 <span className="text-xl font-bold text-zinc-200">{formatBytes(summary.total)}</span>
//                             </div>
//                         )}
//                         {pct !== null && (
//                             <div className="stat-card">
//                                 <span className="text-[10px] text-zinc-500 uppercase">Utilisation</span>
//                                 <span className={`text-xl font-bold ${getUtilColor(pct)}`}>{pct}%</span>
//                             </div>
//                         )}
//                         {summary.pageFaults !== undefined && summary.pageFaults !== null && (
//                             <div className="stat-card">
//                                 <span className="text-[10px] text-zinc-500 uppercase">Page faults</span>
//                                 <span className="text-xl font-bold text-amber-400">
//                                     {typeof summary.pageFaults === 'number' ? summary.pageFaults.toLocaleString() : summary.pageFaults}
//                                 </span>
//                             </div>
//                         )}
//                     </div>

//                     {pct !== null && (
//                         <div>
//                             <div className="flex justify-between text-[10px] text-zinc-500 mb-1">
//                                 <span>Utilisé</span>
//                                 <span>{pct}%</span>
//                             </div>
//                             <div className="h-3 bg-zinc-800 rounded-full overflow-hidden">
//                                 <div className={`h-full rounded-full transition-all duration-500 ${getUtilBarColor(pct)}`}
//                                      style={{ width: `${pct}%` }} />
//                             </div>
//                         </div>
//                     )}
//                 </div>

//                 {/* Historique RAM */}
//                 {summary.freeHistory.length > 1 && (
//                     <div className="telemetry-panel">
//                         {(() => {
//                             const latestDate = summary.freeHistory[0]?.time?.split('T')[0] || '';
//                             const activeDate = historyDateFilter || latestDate;

//                             const filteredData = activeDate 
//                                 ? summary.freeHistory.filter(d => d.time && d.time.startsWith(activeDate))
//                                 : summary.freeHistory;
//                             const chartData = [...filteredData].reverse();

//                             return (
//                                 <>
//                                     <div className="flex items-center justify-between mb-4">
//                                         <div className="flex items-center gap-2">
//                                             <TrendingUp className="w-4 h-4 text-purple-400" />
//                                             <span className="text-sm font-semibold text-zinc-200">Historique mémoire libre</span>
//                                         </div>
//                                         <div className="flex items-center gap-2">
//                                             <span className="text-[10px] text-zinc-500">Date du relevé :</span>
//                                             <input 
//                                                 type="date" 
//                                                 value={activeDate}
//                                                 onChange={(e) => setHistoryDateFilter(e.target.value)}
//                                                 className="bg-zinc-900 border border-white/10 rounded-lg px-3 py-1.5 text-xs text-zinc-300 outline-none focus:border-purple-500/50"
//                                             />
//                                         </div>
//                                     </div>

//                                     {chartData.length === 0 ? (
//                                         <div className="text-xs text-zinc-500 italic text-center py-4">Aucune donnée pour cette date.</div>
//                                     ) : (
//                                         <div className="h-64 w-full">
//                                             <ResponsiveContainer width="100%" height="100%">
//                                                 <BarChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
//                                                     <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
//                                                     <XAxis 
//                                                         dataKey="time" 
//                                                         tickFormatter={(t) => {
//                                                             try { return new Date(t).toLocaleTimeString('fr-FR', {hour: '2-digit', minute:'2-digit'}); } 
//                                                             catch { return ''; }
//                                                         }}
//                                                         stroke="#71717a" fontSize={10} tickLine={false} axisLine={false}
//                                                     />
//                                                     <YAxis stroke="#71717a" fontSize={10} tickLine={false} axisLine={false} tickFormatter={(v) => formatBytes(v)} />
//                                                     <RechartsTooltip 
//                                                         contentStyle={{ backgroundColor: 'rgba(24, 24, 32, 0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
//                                                         itemStyle={{ color: '#c084fc' }}
//                                                         cursor={{ fill: 'rgba(255,255,255,0.05)' }}
//                                                         labelFormatter={(t) => formatDate(t)}
//                                                         formatter={(val) => [formatBytes(val), 'Libre']}
//                                                     />
//                                                     <Bar dataKey="free" fill="#a855f7" radius={[4, 4, 0, 0]} />
//                                                 </BarChart>
//                                             </ResponsiveContainer>
//                                         </div>
//                                     )}
//                                 </>
//                             );
//                         })()}
//                     </div>
//                 )}
//             </div>
//         );
//     };
// return renderRamTab
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

function RamTab({ reports, historyDateFilter, setHistoryDateFilter, deviceId }) {
    const [modal, setModal] = useState(false);

    const handleExport = async (format) => {
        try {
            const exportFn = format === 'pdf' ? exportPdf : exportExcel;
            await exportFn({ onglet: 'ram', id: deviceId });
        } catch (e) {
            console.error(e);
        }
    };
    const summary = extractRamSummary(reports);
    if (!summary) return <NoData title="RAM" />;

    const pct = summary.total ? usagePercent(summary.free, summary.total) : null;

    return (
        <div className="mt-4 space-y-5">
            <div className="telemetry-panel">
                <div className="flex items-center gap-2 mb-4">
                    <Activity className="w-4 h-4 text-purple-400" />
                    <span className="text-sm font-semibold text-zinc-200">État de la mémoire</span>
                    <span className="text-[10px] text-zinc-500 ml-auto">{formatDate(summary.time)}</span>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-4">
                    <div className="stat-card">
                        <span className="text-[10px] text-zinc-500 uppercase">Mémoire libre</span>
                        <span className="text-xl font-bold text-purple-400">{formatBytes(summary.free)}</span>
                    </div>
                    {summary.total && (
                        <div className="stat-card">
                            <span className="text-[10px] text-zinc-500 uppercase">Mémoire totale</span>
                            <span className="text-xl font-bold text-zinc-200">{formatBytes(summary.total)}</span>
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
            {summary.freeHistory.length > 1 && (
                <div className="telemetry-panel">
                    {(() => {
                        const latestDate = summary.freeHistory[0]?.time?.split('T')[0] || '';
                        const activeDate = historyDateFilter || latestDate;

                        const filteredData = activeDate
                            ? summary.freeHistory.filter(d => d.time && d.time.startsWith(activeDate))
                            : summary.freeHistory;
                        const chartData = [...filteredData].reverse();

                        return (
                            <>
                                <div className="flex items-center justify-between mb-4">
                                    <div className="flex items-center gap-2">
                                        <TrendingUp className="w-4 h-4 text-purple-400" />
                                        <span className="text-sm font-semibold text-zinc-200">Historique mémoire libre</span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <span className="text-[10px] text-zinc-500">Date du relevé :</span>
                                        <input
                                            type="date"
                                            value={activeDate}
                                            onChange={(e) => setHistoryDateFilter(e.target.value)}
                                            className="bg-zinc-900 border border-white/10 rounded-lg px-3 py-1.5 text-xs text-zinc-300 outline-none focus:border-purple-500/50"
                                        />
                                    </div>
                                </div>

                                {chartData.length === 0 ? (
                                    <div className="text-xs text-zinc-500 italic text-center py-4">Aucune donnée pour cette date.</div>
                                ) : (
                                    <div className="h-64 w-full">
                                        <ResponsiveContainer width="100%" height="100%">
                                            <BarChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
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
                                )}
                            </>
                        );
                    })()}
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