// const renderPeripheriquesTab = () => {
//         const reports = tabData.peripheriques;
//         const devices = extractPeripheralsSummary(reports);
//         if (!devices) return noData('Périphériques');

//         return (
//             <div className="mt-4 space-y-5">
//                 <div className="telemetry-panel">
//                     <div className="flex items-center gap-2 mb-4">
//                         <Plug className="w-4 h-4 text-pink-400" />
//                         <span className="text-sm font-semibold text-zinc-200">
//                             Périphériques connectés ({devices.length})
//                         </span>
//                     </div>
//                     <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
//                         {devices.map((p, i) => (
//                             <div key={i} className="p-4 rounded-xl bg-zinc-800/40 border border-white/5 hover:border-pink-500/20 transition-all">
//                                 <div className="flex items-center gap-3 mb-2">
//                                     <div className="p-2 bg-pink-500/10 rounded-lg">
//                                         <Plug className="w-4 h-4 text-pink-400" />
//                                     </div>
//                                     <div className="min-w-0">
//                                         <div className="text-sm font-semibold text-zinc-200 truncate">
//                                             {p.name || p.vendor || 'Périphérique inconnu'}
//                                         </div>
//                                         {p.vendor && p.name && (
//                                             <div className="text-[10px] text-zinc-500">{p.vendor}</div>
//                                         )}
//                                     </div>
//                                 </div>
//                                 <div className="flex flex-wrap gap-2 mt-2">
//                                     {p.vid && (
//                                         <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-zinc-700/50 text-zinc-400">
//                                             VID: {p.vid}
//                                         </span>
//                                     )}
//                                     {p.pid && (
//                                         <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-zinc-700/50 text-zinc-400">
//                                             PID: {p.pid}
//                                         </span>
//                                     )}
//                                     {p.categories?.map((cat, ci) => (
//                                         <span key={ci} className="text-[10px] px-2 py-0.5 rounded bg-pink-500/10 text-pink-400">
//                                             {cat}
//                                         </span>
//                                     ))}
//                                 </div>
//                             </div>
//                         ))}
//                     </div>
//                 </div>
//             </div>
//         );
//     };

// return renderPeripheriquesTab
import { useState } from 'react';
import { Plug } from 'lucide-react';
import { extractPeripheralsSummary } from '../../../fonction/deviceFonction';
import { exportExcel, exportPdf } from '../../../fonction/utils/util';
import ExportModal from '../../../components/ExportModal';
import NoData from './NoData';

function PeripheriquesTab({ reports, deviceId }) {
    const [modal, setModal] = useState(false);
    const handleExport = async (format) => {
        try {
            const exportFn = format === 'pdf' ? exportPdf : exportExcel;
            await exportFn({ onglet: 'peripheriques', id: deviceId });
        } catch (e) {
            console.error(e);
        }
    };

    const devices = extractPeripheralsSummary(reports);
    if (!devices) return <NoData title="Périphériques" />;

    return (
        <div className="mt-4 space-y-5">
            <div className="telemetry-panel">
                <div className="flex items-center gap-2 mb-4">
                    <Plug className="w-4 h-4 text-pink-400" />
                    <span className="text-sm font-semibold text-zinc-200">
                        Périphériques connectés ({devices.length})
                    </span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {devices.map((p, i) => (
                        <div key={i} className="p-4 rounded-xl bg-zinc-800/40 border border-white/5 hover:border-pink-500/20 transition-all">
                            <div className="flex items-center gap-3 mb-2">
                                <div className="p-2 bg-pink-500/10 rounded-lg">
                                    <Plug className="w-4 h-4 text-pink-400" />
                                </div>
                                <div className="min-w-0">
                                    <div className="text-sm font-semibold text-zinc-200 truncate">
                                        {p.name || p.vendor || 'Périphérique inconnu'}
                                    </div>
                                    {p.vendor && p.name && (
                                        <div className="text-[10px] text-zinc-500">{p.vendor}</div>
                                    )}
                                </div>
                            </div>
                            <div className="flex flex-wrap gap-2 mt-2">
                                {p.vid && (
                                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-zinc-700/50 text-zinc-400">
                                        VID: {p.vid}
                                    </span>
                                )}
                                {p.pid && (
                                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-zinc-700/50 text-zinc-400">
                                        PID: {p.pid}
                                    </span>
                                )}
                                {p.categories?.map((cat, ci) => (
                                    <span key={ci} className="text-[10px] px-2 py-0.5 rounded bg-pink-500/10 text-pink-400">
                                        {cat}
                                    </span>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>
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

export default PeripheriquesTab;