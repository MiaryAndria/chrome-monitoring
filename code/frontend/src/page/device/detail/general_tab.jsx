// import { getDeviceDetail,getDetailCpu,getDetailRam,getDetailStockage,detailBatterie,detailReseau,detailPeripheriques,getDetailGeneral,extractRamSummary,extractCpuSummary,extractStorageSummary,extractBatterySummary
// } from "../../fonction/deviceFonction";

// const [generalData, setGeneralData] = useState(null);

// const renderGeneralTab = () => {
//         if (!generalData) return null;
//         const cpu = extractCpuSummary(generalData.cpu);
//         const ram = extractRamSummary(generalData.ram);
//         const storage = extractStorageSummary(generalData.stockage);
//         const battery = extractBatterySummary(generalData.batterie);

//         const summaryCards = [
//             {
//                 key: 'cpu', icon: Cpu, label: 'Processeur', color: 'cyan',
//                 value: cpu?.latestUtil !== null && cpu?.latestUtil !== undefined ? `${cpu.latestUtil}%` : null,
//                 sub: cpu?.latestTemps ? `Max ${Math.max(...cpu.latestTemps.map(t => t.temperatureCelsius))}°C` : null,
//                 count: generalData.cpu?.length || 0
//             },
//             {
//                 key: 'ram', icon: Activity, label: 'Mémoire RAM', color: 'purple',
//                 value: ram ? formatBytes(ram.free) : null,
//                 sub: ram ? 'Libre' : null,
//                 count: generalData.ram?.length || 0
//             },
//             {
//                 key: 'stockage', icon: HardDrive, label: 'Stockage', color: 'amber',
//                 value: storage?.disks?.[0] ? `${usagePercent(storage.disks[0].storageFreeBytes, storage.disks[0].storageTotalBytes) ?? '?'}% utilisé` : null,
//                 sub: storage?.disks?.[0] ? `${formatBytes(storage.disks[0].storageTotalBytes)} total` : null,
//                 count: generalData.stockage?.length || 0
//             },
//             {
//                 key: 'batterie', icon: Zap, label: 'Batterie', color: 'emerald',
//                 value: battery?.health ? battery.health.replace('BATTERY_HEALTH_', '').replace(/_/g, ' ') : null,
//                 sub: battery?.cycleCount !== undefined ? `${battery.cycleCount} cycles` : null,
//                 count: generalData.batterie?.length || 0
//             },
//             {
//                 key: 'reseau', icon: Network, label: 'Réseau', color: 'blue',
//                 value: device?.ip_adress || null,
//                 sub: device?.mac_adress || null,
//                 count: generalData.reseau?.length || 0
//             },
//             {
//                 key: 'peripheriques', icon: Plug, label: 'Périphériques', color: 'pink',
//                 value: extractPeripheralsSummary(generalData.peripheriques)?.length 
//                     ? `${extractPeripheralsSummary(generalData.peripheriques).length} appareil(s)` : null,
//                 sub: null,
//                 count: generalData.peripheriques?.length || 0
//             }
//         ];

//         const colorMap = {
//             cyan:    { icon: 'bg-cyan-500/10 text-cyan-400',    border: 'hover:border-cyan-500/30',    val: 'text-cyan-400' },
//             purple:  { icon: 'bg-purple-500/10 text-purple-400',  border: 'hover:border-purple-500/30',  val: 'text-purple-400' },
//             amber:   { icon: 'bg-amber-500/10 text-amber-400',   border: 'hover:border-amber-500/30',   val: 'text-amber-400' },
//             emerald: { icon: 'bg-emerald-500/10 text-emerald-400',border: 'hover:border-emerald-500/30', val: 'text-emerald-400' },
//             blue:    { icon: 'bg-blue-500/10 text-blue-400',      border: 'hover:border-blue-500/30',    val: 'text-blue-400' },
//             pink:    { icon: 'bg-pink-500/10 text-pink-400',      border: 'hover:border-pink-500/30',    val: 'text-pink-400' },
//         };

//         return (
//             <div className="mt-4 space-y-6">
//                 {/* Summary cards */}
//                 <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
//                     {summaryCards.map(card => {
//                         const c = colorMap[card.color];
//                         const Icon = card.icon;
//                         return (
//                             <div key={card.key} onClick={() => handleTabChange(card.key)}
//                                 className={`summary-card ${c.border}`}>
//                                 <div className="flex items-center justify-between mb-3">
//                                     <div className="flex items-center gap-3">
//                                         <div className={`p-2 rounded-lg ${c.icon}`}>
//                                             <Icon className="w-5 h-5" />
//                                         </div>
//                                         <span className="text-sm font-semibold text-zinc-200">{card.label}</span>
//                                     </div>
//                                     <ChevronRight className="w-4 h-4 text-zinc-600 group-hover:text-zinc-400 transition-colors" />
//                                 </div>
//                                 {card.value ? (
//                                     <div className="space-y-1">
//                                         <div className={`text-xl font-bold ${c.val}`}>{card.value}</div>
//                                         {card.sub && <div className="text-xs text-zinc-400">{card.sub}</div>}
//                                         <div className="text-[10px] text-zinc-600 mt-1">{card.count} relevé(s)</div>
//                                     </div>
//                                 ) : (
//                                     <div className="text-xs text-zinc-600 italic">Aucune donnée</div>
//                                 )}
//                             </div>
//                         );
//                     })}
//                 </div>
//             </div>
//         );
//     };

// return renderGeneralTab
import { useState } from 'react';
import { Cpu, Activity, HardDrive, Zap, Network, Plug, ChevronRight } from 'lucide-react';
import {
    extractCpuSummary, extractRamSummary, extractStorageSummary,
    extractBatterySummary, extractPeripheralsSummary
} from '../../../fonction/deviceFonction';
import { formatBytes, usagePercent, exportPdf, exportExcel } from '../../../fonction/utils/util';
import ExportModal from '../../../components/ExportModal';

const colorMap = {
    cyan: { icon: 'bg-cyan-500/10 text-cyan-400', border: 'hover:border-cyan-500/30', val: 'text-cyan-400' },
    purple: { icon: 'bg-purple-500/10 text-purple-400', border: 'hover:border-purple-500/30', val: 'text-purple-400' },
    amber: { icon: 'bg-amber-500/10 text-amber-400', border: 'hover:border-amber-500/30', val: 'text-amber-400' },
    emerald: { icon: 'bg-emerald-500/10 text-emerald-400', border: 'hover:border-emerald-500/30', val: 'text-emerald-400' },
    blue: { icon: 'bg-blue-500/10 text-blue-400', border: 'hover:border-blue-500/30', val: 'text-blue-400' },
    pink: { icon: 'bg-pink-500/10 text-pink-400', border: 'hover:border-pink-500/30', val: 'text-pink-400' },
};

function GeneralTab({ generalData, device, onSelectTab, deviceId }) {
    const [modal, setModal] = useState(false);

    const handleExport = async (format) => {
        try {
            const exportFn = format === 'pdf' ? exportPdf : exportExcel;
            await exportFn({ onglet: 'general', id: deviceId });
        } catch (e) {
            console.error(e);
        }
    };

    if (!generalData) return null;

    const cpu = extractCpuSummary(generalData.cpu);
    const ram = extractRamSummary(generalData.ram);
    const storage = extractStorageSummary(generalData.stockage);
    const battery = extractBatterySummary(generalData.batterie);
    const peripherals = extractPeripheralsSummary(generalData.peripheriques);

    const summaryCards = [
        {
            key: 'cpu', icon: Cpu, label: 'Processeur', color: 'cyan',
            value: cpu?.latestUtil !== null && cpu?.latestUtil !== undefined ? `${cpu.latestUtil}%` : null,
            sub: cpu?.latestTemps ? `Max ${Math.max(...cpu.latestTemps.map(t => t.temperatureCelsius))}°C` : null,
            count: generalData.cpu?.length || 0
        },
        {
            key: 'ram', icon: Activity, label: 'Mémoire RAM', color: 'purple',
            value: ram ? formatBytes(ram.free) : null,
            sub: ram ? 'Libre' : null,
            count: generalData.ram?.length || 0
        },
        {
            key: 'stockage', icon: HardDrive, label: 'Stockage', color: 'amber',
            value: storage?.disks?.[0]
                ? `${usagePercent(storage.disks[0].storageFreeBytes, storage.disks[0].storageTotalBytes) ?? '?'}% utilisé`
                : null,
            sub: storage?.disks?.[0] ? `${formatBytes(storage.disks[0].storageTotalBytes)} total` : null,
            count: generalData.stockage?.length || 0
        },
        {
            key: 'batterie', icon: Zap, label: 'Batterie', color: 'emerald',
            value: battery?.health ? battery.health.replace('BATTERY_HEALTH_', '').replace(/_/g, ' ') : null,
            sub: battery?.cycleCount !== undefined ? `${battery.cycleCount} cycles` : null,
            count: generalData.batterie?.length || 0
        },
        {
            key: 'reseau', icon: Network, label: 'Réseau', color: 'blue',
            value: device?.ip_adress || null,
            sub: device?.mac_adress || null,
            count: generalData.reseau?.length || 0
        },
        {
            key: 'peripheriques', icon: Plug, label: 'Périphériques', color: 'pink',
            value: peripherals?.length ? `${peripherals.length} appareil(s)` : null,
            sub: null,
            count: generalData.peripheriques?.length || 0
        }
    ];

    return (
        <div className="mt-4 space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {summaryCards.map(card => {
                    const c = colorMap[card.color];
                    const Icon = card.icon;
                    return (
                        <div key={card.key} onClick={() => onSelectTab(card.key)}
                            className={`summary-card group ${c.border}`}>
                            <div className="flex items-center justify-between mb-3">
                                <div className="flex items-center gap-3">
                                    <div className={`p-2 rounded-lg ${c.icon}`}>
                                        <Icon className="w-5 h-5" />
                                    </div>
                                    <span className="text-sm font-semibold text-zinc-200">{card.label}</span>
                                </div>
                                <ChevronRight className="w-4 h-4 text-zinc-600 group-hover:text-zinc-400 transition-colors" />
                            </div>
                            {card.value ? (
                                <div className="space-y-1">
                                    <div className={`text-xl font-bold ${c.val}`}>{card.value}</div>
                                    {card.sub && <div className="text-xs text-zinc-400">{card.sub}</div>}
                                    <div className="text-[10px] text-zinc-600 mt-1">{card.count} relevé(s)</div>
                                </div>
                            ) : (
                                <div className="text-xs text-zinc-600 italic">Aucune donnée</div>
                            )}
                        </div>
                    );
                })}
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

export default GeneralTab;