// const renderCpuTab = () => {
//         const reports = tabData.cpu;
//         const summary = extractCpuSummary(reports);
//         if (!summary) return noData('CPU');

//         return (
//             <div className="mt-4 space-y-5">
//                 {/* Utilisation CPU */}
//                 {summary.latestUtil !== null && (
//                     <div className="telemetry-panel">
//                         <div className="flex items-center gap-2 mb-4">
//                             <Gauge className="w-4 h-4 text-cyan-400" />
//                             <span className="text-sm font-semibold text-zinc-200">Utilisation CPU</span>
//                             <span className="text-[10px] text-zinc-500 ml-auto">
//                                 {formatDate(summary.latestUtilTime)}
//                             </span>
//                         </div>
//                         <div className="flex items-end gap-4 mb-3">
//                             <span className={`text-4xl font-bold ${getUtilColor(summary.latestUtil)}`}>
//                                 {summary.latestUtil}%
//                             </span>
//                         </div>
//                         <div className="h-3 bg-zinc-800 rounded-full overflow-hidden">
//                             <div className={`h-full rounded-full transition-all duration-500 ${getUtilBarColor(summary.latestUtil)}`}
//                                  style={{ width: `${Math.max(summary.latestUtil, 2)}%` }} />
//                         </div>
//                     </div>
//                 )}

//                 {/* Températures */}
//                 {summary.latestTemps?.length > 0 && (
//                     <div className="telemetry-panel">
//                         <div className="flex items-center gap-2 mb-4">
//                             <Thermometer className="w-4 h-4 text-amber-400" />
//                             <span className="text-sm font-semibold text-zinc-200">Températures des capteurs</span>
//                             <span className="text-[10px] text-zinc-500 ml-auto">
//                                 {formatDate(summary.latestTempTime)}
//                             </span>
//                         </div>
//                         <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
//                             {summary.latestTemps.map((sensor, i) => {
//                                 const s = getTempStyle(sensor.temperatureCelsius);
//                                 return (
//                                     <div key={i} className={`temp-card ${s.bg} border ${s.border}`}>
//                                         <div className="text-[10px] text-zinc-400 truncate mb-1">
//                                             {cleanLabel(sensor.label)}
//                                         </div>
//                                         <div className={`text-xl font-bold ${s.text}`}>
//                                             {sensor.temperatureCelsius}°C
//                                         </div>
//                                         <div className="mt-2 h-1.5 bg-zinc-800/50 rounded-full overflow-hidden">
//                                             <div className={`h-full rounded-full ${s.bar}`}
//                                                  style={{ width: `${Math.min(sensor.temperatureCelsius, 100)}%` }} />
//                                         </div>
//                                     </div>
//                                 );
//                             })}
//                         </div>
//                     </div>
//                 )}

//                 {/* Historique utilisation */}
//                 {summary.utilHistory.length > 1 && (
//                     <div className="telemetry-panel">
//                         {(() => {
//                             const latestDate = summary.utilHistory[0]?.time?.split('T')[0] || '';
//                             const activeDate = historyDateFilter || latestDate;

//                             const filteredData = activeDate 
//                                 ? summary.utilHistory.filter(d => d.time && d.time.startsWith(activeDate))
//                                 : summary.utilHistory;
//                             const chartData = [...filteredData].reverse();

//                             return (
//                                 <>
//                                     <div className="flex items-center justify-between mb-4">
//                                         <div className="flex items-center gap-2">
//                                             <TrendingUp className="w-4 h-4 text-cyan-400" />
//                                             <span className="text-sm font-semibold text-zinc-200">Historique d'utilisation CPU</span>
//                                         </div>
//                                         <div className="flex items-center gap-2">
//                                             <span className="text-[10px] text-zinc-500">Date du relevé :</span>
//                                             <input 
//                                                 type="date" 
//                                                 value={activeDate}
//                                                 onChange={(e) => setHistoryDateFilter(e.target.value)}
//                                                 className="bg-zinc-900 border border-white/10 rounded-lg px-3 py-1.5 text-xs text-zinc-300 outline-none focus:border-cyan-500/50"
//                                             />
//                                         </div>
//                                     </div>

//                                     {chartData.length === 0 ? (
//                                         <div className="text-xs text-zinc-500 italic text-center py-4">Aucune donnée pour cette date.</div>
//                                     ) : (
//                                         <div className="h-64 w-full">
//                                             <ResponsiveContainer width="100%" height="100%">
//                                                 <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
//                                                     <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
//                                                     <XAxis 
//                                                         dataKey="time" 
//                                                         tickFormatter={(t) => {
//                                                             try { return new Date(t).toLocaleTimeString('fr-FR', {hour: '2-digit', minute:'2-digit'}); } 
//                                                             catch { return ''; }
//                                                         }}
//                                                         stroke="#71717a" fontSize={10} tickLine={false} axisLine={false}
//                                                     />
//                                                     <YAxis stroke="#71717a" fontSize={10} tickLine={false} axisLine={false} tickFormatter={(v) => `${v}%`} />
//                                                     <RechartsTooltip 
//                                                         contentStyle={{ backgroundColor: 'rgba(24, 24, 32, 0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
//                                                         itemStyle={{ color: '#22d3ee' }}
//                                                         cursor={{ fill: 'rgba(255,255,255,0.05)' }}
//                                                         labelFormatter={(t) => formatDate(t)}
//                                                         formatter={(val) => [`${val}%`, 'Utilisation']}
//                                                     />
//                                                     <Bar dataKey="value" fill="#06b6d4" radius={[4, 4, 0, 0]} />
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
// return renderCpuTab
import { useState } from 'react';
import { Gauge, Thermometer, TrendingUp } from 'lucide-react';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid,
    Tooltip as RechartsTooltip, ResponsiveContainer
} from 'recharts';
import { extractCpuSummary } from '../../../fonction/deviceFonction';
import { getTempStyle, getUtilBarColor, getUtilColor, cleanLabel, formatDate, exportPdf, exportExcel } from '../../../fonction/utils/util';
import ExportModal from '../../../components/ExportModal';
import NoData from './NoData';

function CpuTab({ reports, deviceId }) {
    const [modal, setModal] = useState(false);

    const summary = extractCpuSummary(reports);
    if (!summary) return <NoData title="CPU" />;

    const chartData = [...summary.utilHistory].reverse();
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
            {summary.latestUtil !== null && (
                <div className="telemetry-panel">
                    <div className="flex items-center gap-2 mb-4">
                        <Gauge className="w-4 h-4 text-cyan-400" />
                        <span className="text-sm font-semibold text-zinc-200">Utilisation CPU</span>
                        <span className="text-[10px] text-zinc-500 ml-auto">
                            {formatDate(summary.latestUtilTime)}
                        </span>
                    </div>
                    <div className="flex items-end gap-4 mb-3">
                        <span className={`text-4xl font-bold ${getUtilColor(summary.latestUtil)}`}>
                            {summary.latestUtil}%
                        </span>
                    </div>
                    <div className="h-3 bg-zinc-800 rounded-full overflow-hidden">
                        <div className={`h-full rounded-full transition-all duration-500 ${getUtilBarColor(summary.latestUtil)}`}
                            style={{ width: `${Math.max(summary.latestUtil, 2)}%` }} />
                    </div>
                </div>
            )}

            {/* Températures */}
            {summary.latestTemps?.length > 0 && (
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

            {/* Historique utilisation */}
            {summary.utilHistory.length > 1 && (
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

                    <div className="h-64 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                                <XAxis
                                    dataKey="time"
                                    tickFormatter={(t) => {
                                        try { return new Date(t).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }); }
                                        catch { return ''; }
                                    }}
                                    stroke="#71717a" fontSize={10} tickLine={false} axisLine={false}
                                />
                                <YAxis stroke="#71717a" fontSize={10} tickLine={false} axisLine={false} tickFormatter={(v) => `${v}%`} />
                                <RechartsTooltip
                                    contentStyle={{ backgroundColor: 'rgba(24, 24, 32, 0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                                    itemStyle={{ color: '#22d3ee' }}
                                    cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                                    labelFormatter={(t) => formatDate(t)}
                                    formatter={(val) => [`${val}%`, 'Utilisation']}
                                />
                                <Bar dataKey="value" fill="#06b6d4" radius={[4, 4, 0, 0]} />
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

export default CpuTab;