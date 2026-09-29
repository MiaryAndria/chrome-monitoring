// const renderBatteryTab = () => {
//         const reports = tabData.batterie;
//         const summary = extractBatterySummary(reports);
//         if (!summary) return noData('Batterie');

//         const healthLabel = summary.health
//             ? summary.health.replace('BATTERY_HEALTH_', '').replace(/_/g, ' ')
//             : null;
//         const healthIsGood = summary.health?.includes('NORMAL') || summary.health?.includes('GOOD');
//         const wearPct = (summary.fullChargeCapacity && summary.designCapacity)
//             ? Math.round((parseInt(summary.fullChargeCapacity) / parseInt(summary.designCapacity)) * 100)
//             : null;

//         return (
//             <div className="mt-4 space-y-5">
//                 <div className="telemetry-panel">
//                     <div className="flex items-center gap-2 mb-4">
//                         <Battery className="w-4 h-4 text-emerald-400" />
//                         <span className="text-sm font-semibold text-zinc-200">État de la batterie</span>
//                         <span className="text-[10px] text-zinc-500 ml-auto">{formatDate(summary.time)}</span>
//                     </div>

//                     {/* Health badge */}
//                     {healthLabel && (
//                         <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-semibold mb-4 ${
//                             healthIsGood 
//                                 ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
//                                 : 'bg-amber-500/15 text-amber-400 border border-amber-500/30'
//                         }`}>
//                             {healthIsGood ? <ShieldCheck className="w-4 h-4" /> : <AlertTriangle className="w-4 h-4" />}
//                             {healthLabel}
//                         </div>
//                     )}

//                     <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
//                         {summary.cycleCount !== undefined && (
//                             <div className="stat-card">
//                                 <span className="text-[10px] text-zinc-500 uppercase">Cycles de charge</span>
//                                 <span className="text-xl font-bold text-emerald-400">{summary.cycleCount}</span>
//                             </div>
//                         )}
//                         {summary.fullChargeCapacity && (
//                             <div className="stat-card">
//                                 <span className="text-[10px] text-zinc-500 uppercase">Capacité actuelle</span>
//                                 <span className="text-xl font-bold text-zinc-200">
//                                     {(parseInt(summary.fullChargeCapacity) / 1000).toFixed(1)} Wh
//                                 </span>
//                             </div>
//                         )}
//                         {summary.designCapacity && (
//                             <div className="stat-card">
//                                 <span className="text-[10px] text-zinc-500 uppercase">Capacité d'origine</span>
//                                 <span className="text-xl font-bold text-zinc-400">
//                                     {(parseInt(summary.designCapacity) / 1000).toFixed(1)} Wh
//                                 </span>
//                             </div>
//                         )}
//                         {summary.voltage && (
//                             <div className="stat-card">
//                                 <span className="text-[10px] text-zinc-500 uppercase">Tension</span>
//                                 <span className="text-xl font-bold text-cyan-400">
//                                     {(parseInt(summary.voltage) / 1000).toFixed(2)} V
//                                 </span>
//                             </div>
//                         )}
//                         {summary.manufacturer && (
//                             <div className="stat-card">
//                                 <span className="text-[10px] text-zinc-500 uppercase">Fabricant</span>
//                                 <span className="text-sm font-semibold text-zinc-200">{summary.manufacturer}</span>
//                             </div>
//                         )}
//                         {summary.serialNumber && (
//                             <div className="stat-card">
//                                 <span className="text-[10px] text-zinc-500 uppercase">N° série batterie</span>
//                                 <span className="text-sm font-mono text-zinc-300">{summary.serialNumber}</span>
//                             </div>
//                         )}
//                     </div>

//                     {/* Usure batterie */}
//                     {wearPct !== null && (
//                         <div className="mt-4">
//                             <div className="flex justify-between text-[10px] text-zinc-500 mb-1">
//                                 <span>Santé de la batterie</span>
//                                 <span>{wearPct}%</span>
//                             </div>
//                             <div className="h-3 bg-zinc-800 rounded-full overflow-hidden">
//                                 <div className={`h-full rounded-full transition-all duration-500 ${
//                                     wearPct > 80 ? 'bg-emerald-500' : wearPct > 50 ? 'bg-amber-500' : 'bg-red-500'
//                                 }`} style={{ width: `${Math.min(wearPct, 100)}%` }} />
//                             </div>
//                         </div>
//                     )}
//                 </div>
//             </div>
//         );
//     };
// return renderBatteryTab
import { useState } from 'react';
import { Battery, ShieldCheck, AlertTriangle } from 'lucide-react';
import { extractBatterySummary } from '../../../fonction/deviceFonction';
import { formatDate, exportPdf, exportExcel } from '../../../fonction/utils/util';
import ExportModal from '../../../components/ExportModal';
import NoData from './NoData';

function BatteryTab({ reports, deviceId }) {
    const [modal, setModal] = useState(false);
    const summary = extractBatterySummary(reports);
    if (!summary) return <NoData title="Batterie" />;

    const healthLabel = summary.health
        ? summary.health.replace('BATTERY_HEALTH_', '').replace(/_/g, ' ')
        : null;
    const healthIsGood = summary.health?.includes('NORMAL') || summary.health?.includes('GOOD');
    const wearPct = (summary.fullChargeCapacity && summary.designCapacity)
        ? Math.round((parseInt(summary.fullChargeCapacity) / parseInt(summary.designCapacity)) * 100)
        : null;

    const handleExport = async (format) => {
        try {
            const exportFn = format === 'pdf' ? exportPdf : exportExcel;
            await exportFn({ onglet: 'batterie', id: deviceId });
        } catch (e) {
            console.error(e);
        }
    };

    return (
        <div className="mt-4 space-y-5">
            <div className="telemetry-panel">
                <div className="flex items-center gap-2 mb-4">
                    <Battery className="w-4 h-4 text-emerald-400" />
                    <span className="text-sm font-semibold text-zinc-200">État de la batterie</span>
                    <span className="text-[10px] text-zinc-500 ml-auto">{formatDate(summary.time)}</span>
                </div>

                {healthLabel && (
                    <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-semibold mb-4 ${
                        healthIsGood
                            ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                            : 'bg-amber-500/15 text-amber-400 border border-amber-500/30'
                    }`}>
                        {healthIsGood ? <ShieldCheck className="w-4 h-4" /> : <AlertTriangle className="w-4 h-4" />}
                        {healthLabel}
                    </div>
                )}

                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {summary.cycleCount !== undefined && (
                        <div className="stat-card">
                            <span className="text-[10px] text-zinc-500 uppercase">Cycles de charge</span>
                            <span className="text-xl font-bold text-emerald-400">{summary.cycleCount}</span>
                        </div>
                    )}
                    {summary.fullChargeCapacity && (
                        <div className="stat-card">
                            <span className="text-[10px] text-zinc-500 uppercase">Capacité actuelle</span>
                            <span className="text-xl font-bold text-zinc-200">
                                {(parseInt(summary.fullChargeCapacity) / 1000).toFixed(1)} Wh
                            </span>
                        </div>
                    )}
                    {summary.designCapacity && (
                        <div className="stat-card">
                            <span className="text-[10px] text-zinc-500 uppercase">Capacité d'origine</span>
                            <span className="text-xl font-bold text-zinc-400">
                                {(parseInt(summary.designCapacity) / 1000).toFixed(1)} Wh
                            </span>
                        </div>
                    )}
                    {summary.voltage && (
                        <div className="stat-card">
                            <span className="text-[10px] text-zinc-500 uppercase">Tension</span>
                            <span className="text-xl font-bold text-cyan-400">
                                {(parseInt(summary.voltage) / 1000).toFixed(2)} V
                            </span>
                        </div>
                    )}
                    {summary.manufacturer && (
                        <div className="stat-card">
                            <span className="text-[10px] text-zinc-500 uppercase">Fabricant</span>
                            <span className="text-sm font-semibold text-zinc-200">{summary.manufacturer}</span>
                        </div>
                    )}
                    {summary.serialNumber && (
                        <div className="stat-card">
                            <span className="text-[10px] text-zinc-500 uppercase">N° série batterie</span>
                            <span className="text-sm font-mono text-zinc-300">{summary.serialNumber}</span>
                        </div>
                    )}
                </div>

                {wearPct !== null && (
                    <div className="mt-4">
                        <div className="flex justify-between text-[10px] text-zinc-500 mb-1">
                            <span>Santé de la batterie</span>
                            <span>{wearPct}%</span>
                        </div>
                        <div className="h-3 bg-zinc-800 rounded-full overflow-hidden">
                            <div className={`h-full rounded-full transition-all duration-500 ${
                                wearPct > 80 ? 'bg-emerald-500' : wearPct > 50 ? 'bg-amber-500' : 'bg-red-500'
                            }`} style={{ width: `${Math.min(wearPct, 100)}%` }} />
                        </div>
                    </div>
                )}
            </div>

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

export default BatteryTab;