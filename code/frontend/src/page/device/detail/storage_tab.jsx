// const renderStorageTab = () => {
//         const reports = tabData.stockage;
//         const summary = extractStorageSummary(reports);
//         if (!summary) return noData('Stockage');

//         return (
//             <div className="mt-4 space-y-5">
//                 <div className="telemetry-panel">
//                     <div className="flex items-center gap-2 mb-4">
//                         <HardDrive className="w-4 h-4 text-amber-400" />
//                         <span className="text-sm font-semibold text-zinc-200">Volumes de stockage</span>
//                         <span className="text-[10px] text-zinc-500 ml-auto">{formatDate(summary.time)}</span>
//                     </div>
//                     <div className="space-y-4">
//                         {summary.disks.map((disk, i) => {
//                             const pct = usagePercent(disk.storageFreeBytes, disk.storageTotalBytes);
//                             return (
//                                 <div key={i} className="p-4 rounded-xl bg-zinc-800/40 border border-white/5">
//                                     <div className="flex items-center justify-between mb-3">
//                                         <span className="text-sm font-mono text-zinc-200">
//                                             {disk.volumeId || `Volume ${i + 1}`}
//                                         </span>
//                                         {pct !== null && (
//                                             <span className={`text-sm font-bold ${getUtilColor(pct)}`}>{pct}% utilisé</span>
//                                         )}
//                                     </div>
//                                     <div className="grid grid-cols-2 gap-3 mb-3">
//                                         <div className="stat-card-sm">
//                                             <span className="text-[10px] text-zinc-500">Total</span>
//                                             <span className="text-sm font-bold text-zinc-200">
//                                                 {formatBytes(disk.storageTotalBytes)}
//                                             </span>
//                                         </div>
//                                         <div className="stat-card-sm">
//                                             <span className="text-[10px] text-zinc-500">Libre</span>
//                                             <span className="text-sm font-bold text-emerald-400">
//                                                 {formatBytes(disk.storageFreeBytes)}
//                                             </span>
//                                         </div>
//                                     </div>
//                                     {pct !== null && (
//                                         <div className="h-2.5 bg-zinc-800 rounded-full overflow-hidden">
//                                             <div className={`h-full rounded-full transition-all duration-500 ${getUtilBarColor(pct)}`}
//                                                  style={{ width: `${pct}%` }} />
//                                         </div>
//                                     )}
//                                 </div>
//                             );
//                         })}
//                     </div>
//                 </div>
//             </div>
//         );
//     };

// return renderStorageTab
import { useState } from 'react';
import { HardDrive } from 'lucide-react';
import { extractStorageSummary } from '../../../fonction/deviceFonction';
import { getUtilBarColor, getUtilColor, formatBytes, formatDate, usagePercent, exportPdf, exportExcel } from '../../../fonction/utils/util';
import ExportModal from '../../../components/ExportModal';
import NoData from './NoData';

function StorageTab({ reports, deviceId }) {
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
    if (!summary) return <NoData title="Stockage" />;

    return (
        <div className="mt-4 space-y-5">
            <div className="telemetry-panel">
                <div className="flex items-center gap-2 mb-4">
                    <HardDrive className="w-4 h-4 text-amber-400" />
                    <span className="text-sm font-semibold text-zinc-200">Volumes de stockage</span>
                    <span className="text-[10px] text-zinc-500 ml-auto">{formatDate(summary.time)}</span>
                </div>
                <div className="space-y-4">
                    {summary.disks.map((disk, i) => {
                        const pct = usagePercent(disk.storageFreeBytes, disk.storageTotalBytes);
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
                                <div className="grid grid-cols-2 gap-3 mb-3">
                                    <div className="stat-card-sm">
                                        <span className="text-[10px] text-zinc-500">Total</span>
                                        <span className="text-sm font-bold text-zinc-200">
                                            {formatBytes(disk.storageTotalBytes)}
                                        </span>
                                    </div>
                                    <div className="stat-card-sm">
                                        <span className="text-[10px] text-zinc-500">Libre</span>
                                        <span className="text-sm font-bold text-emerald-400">
                                            {formatBytes(disk.storageFreeBytes)}
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