import { useState } from 'react';

import { Cpu, Activity, HardDrive, Zap, Network, Plug, ChevronRight, Monitor, Users, Shield, Server, FileText } from 'lucide-react';
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

    const storageDisk = storage?.disks?.[0] || null;
    const storageTotal = device?.disk_total ?? null;
    const freeFromDisk = storageDisk?.storageFreeBytes ?? null;
    const usedFromDisk = storageDisk?.storageUsedBytes ?? null;
    const storageFree = freeFromDisk ?? (storageTotal !== null && usedFromDisk !== null ? Math.max(storageTotal - usedFromDisk, 0) : device?.disk_free ?? null);
    const storagePercent = storageTotal !== null && storageFree !== null ? usagePercent(storageFree, storageTotal) : null;
    const cpuMaxTemp = cpu?.maxTemperature ?? (cpu?.latestTemps ? Math.max(...cpu.latestTemps.map(t => Number(t.temperatureCelsius) || 0)) : null);

    const summaryCards = [
        {
            key: 'cpu', icon: Cpu, label: 'Processeur', color: 'cyan',
            value: cpu?.latestUtil !== null && cpu?.latestUtil !== undefined ? `${cpu.latestUtil}%` : null,
            sub: cpuMaxTemp !== null ? `Max ${cpuMaxTemp}°C` : null,
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
            value: storagePercent !== null ? `${storagePercent}% utilisé` : null,
            sub: storageTotal !== null ? `${formatBytes(storageTotal)} total` : null,
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

    const recentUsersList = device?.utilisateurs_recents || [];

    return (
        <div className="mt-4 space-y-6">
            {/* Fiche d'information matériel */}
            <div className="bg-zinc-900/90 border border-zinc-800 rounded-xl p-6 shadow-xl backdrop-blur-sm">
                <div className="flex items-center justify-between pb-4 mb-4 border-b border-zinc-800/80">
                    <div className="flex items-center gap-3">
                        <div className="p-2.5 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                            <Monitor className="w-5 h-5" />
                        </div>
                        <div>
                            <h3 className="text-base font-bold text-zinc-100">Fiche d'Information Matériel</h3>
                            <p className="text-xs text-zinc-400">Caractéristiques système et composants physiques</p>
                        </div>
                    </div>
                    <span className="px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        {device?.status || 'Actif'}
                    </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-xs">
                    {/* Bloc Identité */}
                    <div className="space-y-3 bg-zinc-950/50 p-4 rounded-lg border border-zinc-800/50">
                        <div className="flex items-center gap-2 font-semibold text-zinc-200 text-sm mb-1">
                            <Server className="w-4 h-4 text-cyan-400" /> Appareil
                        </div>
                        <div className="flex justify-between border-b border-zinc-800/40 pb-1.5">
                            <span className="text-zinc-400">Modèle :</span>
                            <span className="font-semibold text-zinc-200">{device?.modele || 'Inconnu'}</span>
                        </div>
                        <div className="flex justify-between border-b border-zinc-800/40 pb-1.5">
                            <span className="text-zinc-400">N° de Série :</span>
                            <span className="font-mono text-zinc-300">{device?.serial_number || 'N/A'}</span>
                        </div>
                        <div className="flex justify-between border-b border-zinc-800/40 pb-1.5">
                            <span className="text-zinc-400">Filiale :</span>
                            <span className="text-zinc-300">{device?.filiale || 'Non attribuée'}</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-zinc-400">Version OS :</span>
                            <span className="text-zinc-300">{device?.chromeos_version || 'N/A'}</span>
                        </div>
                    </div>

                    {/* Bloc Matériel / Specs */}
                    <div className="space-y-3 bg-zinc-950/50 p-4 rounded-lg border border-zinc-800/50">
                        <div className="flex items-center gap-2 font-semibold text-zinc-200 text-sm mb-1">
                            <Cpu className="w-4 h-4 text-purple-400" /> Composants
                        </div>
                        <div className="flex justify-between border-b border-zinc-800/40 pb-1.5">
                            <span className="text-zinc-400">Processeur :</span>
                            <span className="text-zinc-300 truncate max-w-[150px]" title={device?.cpu_model}>{device?.cpu_model || 'N/A'}</span>
                        </div>
                        <div className="flex justify-between border-b border-zinc-800/40 pb-1.5">
                            <span className="text-zinc-400">Architecture :</span>
                            <span className="text-zinc-300">{device?.cpu_architecture || 'N/A'}</span>
                        </div>
                        <div className="flex justify-between border-b border-zinc-800/40 pb-1.5">
                            <span className="text-zinc-400">Fréquence Max :</span>
                            <span className="text-zinc-300">{device?.cpu_freq_max_label || 'N/A'}</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-zinc-400">RAM Totale :</span>
                            <span className="font-semibold text-purple-300">{device?.ram_total_label || (device?.ram_total ? formatBytes(device.ram_total) : 'N/A')}</span>
                        </div>
                    </div>

                    {/* Bloc Stockage & Utilisateurs */}
                    <div className="space-y-3 bg-zinc-950/50 p-4 rounded-lg border border-zinc-800/50">
                        <div className="flex items-center gap-2 font-semibold text-zinc-200 text-sm mb-1">
                            <HardDrive className="w-4 h-4 text-amber-400" /> Stockage & Accès
                        </div>
                        <div className="flex justify-between border-b border-zinc-800/40 pb-1.5">
                            <span className="text-zinc-400">Modèle Disque :</span>
                            <span className="text-zinc-300 truncate max-w-[140px]" title={device?.disk_model}>{device?.disk_model || 'N/A'}</span>
                        </div>
                        <div className="flex justify-between border-b border-zinc-800/40 pb-1.5">
                            <span className="text-zinc-400">Capacité Disque :</span>
                            <span className="font-semibold text-amber-300">{device?.disk_total_label || (storageTotal ? formatBytes(storageTotal) : 'N/A')}</span>
                        </div>
                        <div className="space-y-1">
                            <span className="text-zinc-400 flex items-center gap-1">
                                <Users className="w-3.5 h-3.5 text-blue-400" /> Utilisateurs Récents :
                            </span>
                            {recentUsersList.length > 0 ? (
                                <div className="flex flex-wrap gap-1 mt-1 max-h-16 overflow-y-auto pr-1">
                                    {recentUsersList.map((email, i) => (
                                        <span key={i} className="px-2 py-0.5 rounded text-[11px] bg-zinc-800/80 text-blue-300 border border-zinc-700/50">
                                            {email}
                                        </span>
                                    ))}
                                </div>
                            ) : (
                                <span className="text-zinc-500 italic block">Aucun utilisateur enregistré</span>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* Cartes de synthèse (CPU, RAM, Stockage, etc.) */}
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