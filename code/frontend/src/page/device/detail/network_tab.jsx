// const renderNetworkTab = () => {
//         const reports = tabData.reseau;
//         const entries = extractNetworkSummary(reports);
//         if (!entries) return noData('Réseau');

//         return (
//             <div className="mt-4 space-y-5">
//                 <div className="telemetry-panel">
//                     <div className="flex items-center gap-2 mb-4">
//                         <Wifi className="w-4 h-4 text-blue-400" />
//                         <span className="text-sm font-semibold text-zinc-200">Rapports réseau</span>
//                     </div>
//                     <div className="space-y-3">
//                         {entries.slice(0, 15).map((entry, i) => {
//                             const { time, ...fields } = entry;
//                             return (
//                                 <div key={i} className="p-3 rounded-xl bg-zinc-800/40 border border-white/5">
//                                     <div className="text-[10px] text-zinc-500 mb-2 font-mono">
//                                         {formatDate(time) || '—'}
//                                     </div>
//                                     <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
//                                         {Object.entries(fields).map(([key, value]) => (
//                                             <div key={key} className="flex flex-col gap-0.5">
//                                                 <span className="text-[10px] text-zinc-500">{key}</span>
//                                                 <span className="text-xs text-zinc-200 font-mono break-all">
//                                                     {typeof value === 'object' ? JSON.stringify(value) : String(value)}
//                                                 </span>
//                                             </div>
//                                         ))}
//                                     </div>
//                                 </div>
//                             );
//                         })}
//                     </div>
//                 </div>
//             </div>
//         );
//     };
// return renderNetworkTab
import { useState } from 'react';
import { Wifi } from 'lucide-react';
import { extractNetworkSummary } from '../../../fonction/deviceFonction';
import { formatDate, exportPdf, exportExcel } from '../../../fonction/utils/util';
import ExportModal from '../../../components/ExportModal';
import NoData from './NoData';

function NetworkTab({ reports, deviceId }) {
    const [modal, setModal] = useState(false);
    const handleExport = async (format) => {
        try {
            const exportFn = format === 'pdf' ? exportPdf : exportExcel;
            await exportFn({ onglet: 'reseau', id: deviceId });
        } catch (e) {
            console.error(e);
        }
    };
    const entries = extractNetworkSummary(reports);
    if (!entries) return <NoData title="Réseau" />;

    return (
        <div className="mt-4 space-y-5">
            <div className="telemetry-panel">
                <div className="flex items-center gap-2 mb-4">
                    <Wifi className="w-4 h-4 text-blue-400" />
                    <span className="text-sm font-semibold text-zinc-200">Rapports réseau</span>
                </div>
                <div className="space-y-3">
                    {entries.slice(0, 15).map((entry, i) => {
                        const { time, ...fields } = entry;
                        return (
                            <div key={i} className="p-3 rounded-xl bg-zinc-800/40 border border-white/5">
                                <div className="text-[10px] text-zinc-500 mb-2 font-mono">
                                    {formatDate(time) || '—'}
                                </div>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                                    {Object.entries(fields).map(([key, value]) => (
                                        <div key={key} className="flex flex-col gap-0.5">
                                            <span className="text-[10px] text-zinc-500">{key}</span>
                                            <span className="text-xs text-zinc-200 font-mono break-all">
                                                {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        );
                    })}
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

export default NetworkTab;