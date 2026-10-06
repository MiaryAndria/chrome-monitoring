import { useEffect, useState } from "react";
import { useParams, useNavigate } from 'react-router-dom';
import {
    Laptop, Network, Copy, Check, ArrowLeft, Cpu, HardDrive,
    Monitor, Activity, Zap, Plug, Layers, RefreshCw
} from 'lucide-react';
import Sidebar from "../../components/Sidebar";
import Navbar from "../../components/Navbar";
import MouseSpotlight from "../../components/MouseSpotlight";
import {
    getDeviceDetail, getDetailCpu, getDetailRam, getDetailStockage,
    detailBatterie, detailReseau, detailPeripheriques, getDetailGeneral,
    filterByDeviceIdAndDate, getIdByName
} from "../../fonction/deviceFonction";
import '../../css/liste.css';
import '../../css/filiale.css';
import '../../css/detail.css';
import GeneralTab from "./detail/general_tab";

import CpuTab from './detail/cpu_tab';
import RamTab from './detail/ram_tab';
import StorageTab from './detail/storage_tab';
import BatteryTab from './detail/battery_tab';
import NetworkTab from './detail/network_tab';
import PeripheriquesTab from './detail/peripherique_tab';
import DateFilter from "./detail/dateFilter";

const TYPE_RAPPORT_NAME = {
    cpu: 'CPU_STATUS',
    ram: 'MEMORY_STATUS',
    stockage: 'STORAGE_STATUS',
    batterie: 'BATTERY_STATUS',
    reseau: 'NETWORK_STATUS',
    peripheriques: 'PERIPHERALS_REPORT',
};

const FETCHERS = {
    cpu: getDetailCpu,
    ram: getDetailRam,
    stockage: getDetailStockage,
    batterie: detailBatterie,
    reseau: detailReseau,
    peripheriques: detailPeripheriques,
};

const TABS = [
    { key: 'general', label: 'Vue d\'ensemble', icon: Layers },
    { key: 'cpu', label: 'CPU', icon: Cpu },
    { key: 'ram', label: 'Mémoire RAM', icon: Activity },
    { key: 'stockage', label: 'Stockage', icon: HardDrive },
    { key: 'batterie', label: 'Batterie', icon: Zap },
    { key: 'reseau', label: 'Réseau', icon: Network },
    { key: 'peripheriques', label: 'Périphériques', icon: Plug }
];

function DetailDevice() {
    const navigate = useNavigate();
    const { id } = useParams();

    const [copiedSN, setCopiedSN] = useState(null);
    const [device, setDevice] = useState(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('general');
    const [generalData, setGeneralData] = useState(null);
    const [tabData, setTabData] = useState({
        cpu: null, ram: null, stockage: null,
        batterie: null, reseau: null, peripheriques: null
    });
    const [tabLoading, setTabLoading] = useState(false);
    const [dateDebut, setDateDebut] = useState('');
    const [dateFin, setDateFin] = useState('');

    const fetchDeviceDetail = async () => {
        try {
            setLoading(true);
            setDevice(await getDeviceDetail(id));
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    const fetchGeneralData = async () => {
        setTabLoading(true);
        try {
            const data = await getDetailGeneral(id);
            if (data) {
                setGeneralData(data);
                setTabData({
                    cpu: data.cpu || [], ram: data.ram || [],
                    stockage: data.stockage || [], batterie: data.batterie || [],
                    reseau: data.reseau || [], peripheriques: data.peripheriques || []
                });
            }
        } catch (e) {
            console.error(e);
        } finally {
            setTabLoading(false);
        }
    };

    const handleTabChange = async (tabKey) => {
        setActiveTab(tabKey);
        setDateDebut('');
        setDateFin('');

        if (tabKey === 'general') {
            if (!generalData) fetchGeneralData();
            return;
        }

        setTabLoading(true);
        try {
            const res = await FETCHERS[tabKey]?.(id);
            setTabData(prev => ({ ...prev, [tabKey]: res }));
        } catch (e) {
            console.error(e);
        } finally {
            setTabLoading(false);
        }
    };

    const filtrerByDate = async () => {
        if (activeTab === 'general') return;
        if (!dateDebut || !dateFin) return;
        if (dateDebut > dateFin) {
            alert("La date de début doit être antérieure à la date de fin.");
            return;
        }

        try {
            setTabLoading(true);
            const idType = await getIdByName(TYPE_RAPPORT_NAME[activeTab]);
            if (!idType) return;

            const res = await filterByDeviceIdAndDate(id, idType, dateDebut, dateFin);
            setTabData(prev => ({ ...prev, [activeTab]: res || [] }));
        } catch (e) {
            console.error(e);
        } finally {
            setTabLoading(false);
        }
    };

    const resetFiltre = async () => {
        if (activeTab === 'general') return;
        setDateDebut('');
        setDateFin('');

        try {
            setTabLoading(true);
            const res = await FETCHERS[activeTab]?.(id);
            setTabData(prev => ({ ...prev, [activeTab]: res || [] }));
        } catch (e) {
            console.error(e);
        } finally {
            setTabLoading(false);
        }
    };

    const handleCopySN = (sn) => {
        if (!sn) return;
        navigator.clipboard.writeText(sn);
        setCopiedSN(sn);
        setTimeout(() => setCopiedSN(null), 2000);
    };

    const getStatusClass = (status) => {
        if (!status) return 'badge-ghost';
        const s = status.toLowerCase();
        if (s.includes('actif') || s.includes('active') || s.includes('provisioned')) return 'status-actif';
        if (s.includes('hors') || s.includes('offline') || s.includes('disabled')) return 'status-hors-ligne';
        if (s.includes('réparation') || s.includes('repair')) return 'status-reparation';
        if (s.includes('anomalie') || s.includes('deprovisioned')) return 'status-anomalie';
        return 'status-default';
    };

    useEffect(() => {
        if (id) {
            fetchDeviceDetail();
            fetchGeneralData();
        }
    }, [id]);

    const renderTabContent = () => {
        if (tabLoading) {
            return (
                <div className="flex justify-center p-12">
                    <RefreshCw className="w-6 h-6 text-cyan-400 animate-spin" />
                </div>
            );
        }
        switch (activeTab) {
            case 'general':
                return <GeneralTab generalData={generalData} device={device} onSelectTab={handleTabChange} deviceId={Number(id)} />;
            case 'cpu':
                return <CpuTab reports={tabData.cpu} device={device} deviceId={Number(id)} />;
            case 'ram':
                return <RamTab reports={tabData.ram} device={device} deviceId={Number(id)} />;
            case 'stockage':
                return <StorageTab reports={tabData.stockage} device={device} deviceId={Number(id)} />;
            case 'batterie':
                return <BatteryTab reports={tabData.batterie} deviceId={Number(id)} />;
            case 'reseau':
                return <NetworkTab reports={tabData.reseau} deviceId={Number(id)} />;
            case 'peripheriques':
                return <PeripheriquesTab reports={tabData.peripheriques} deviceId={Number(id)} />;
            default:
                return null;
        }
    };

    return (
        <div className="device-layout" data-theme="dark">
            <MouseSpotlight />
            <Sidebar />

            <div className="flex-1 flex flex-col h-screen overflow-hidden relative z-10">
                <div className="bg-glow-cyan"></div>
                <div className="bg-glow-purple"></div>
                <Navbar />

                <div className="flex-1 overflow-y-auto p-6 lg:p-8 space-y-6 z-10">
                    <div className="flex items-center justify-between">
                        <button onClick={() => navigate(-1)} className="back-btn">
                            <ArrowLeft className="w-4 h-4" />
                            Retour
                        </button>
                    </div>

                    {loading ? (
                        <div className="flex justify-center p-12">
                            <span className="loading loading-infinity loading-lg text-cyan-500"></span>
                        </div>
                    ) : !device ? (
                        <div className="telemetry-empty">Appareil introuvable.</div>
                    ) : (
                        <div className="detail-card space-y-6">
                            <div className="flex justify-between items-start border-b border-white/10 pb-5">
                                <div className="flex items-center gap-4">
                                    <div className="p-4 bg-cyan-500/10 border border-cyan-500/20 rounded-2xl text-cyan-400">
                                        {device.type_appareil === 'Chromebox' ? (
                                            <Monitor className="w-8 h-8" />
                                        ) : (
                                            <Laptop className="w-8 h-8" />
                                        )}
                                    </div>
                                    <div>
                                        <h1 className="text-2xl font-bold text-zinc-100">
                                            {device.modele || 'Modèle inconnu'}
                                        </h1>
                                        <p className="text-sm text-zinc-400 flex items-center gap-2 mt-1">
                                            S/N: <span className="font-mono text-zinc-200">
                                                {device.serial_number || 'N/A'}
                                            </span>
                                            <button
                                                onClick={() => handleCopySN(device.serial_number)}
                                                className="text-zinc-500 hover:text-cyan-400 transition-colors p-1"
                                                title="Copier N° Série"
                                            >
                                                {copiedSN === device.serial_number ? (
                                                    <Check className="w-4 h-4 text-emerald-400" />
                                                ) : (
                                                    <Copy className="w-4 h-4" />
                                                )}
                                            </button>
                                        </p>
                                    </div>
                                </div>
                                <span className={`status-badge ${getStatusClass(device.status)}`}>
                                    {device.status || 'N/A'}
                                </span>
                            </div>

                            <div className="flex border-b border-white/10 overflow-x-auto no-scrollbar space-x-1 pb-1">
                                {TABS.map((tab) => {
                                    const IconComp = tab.icon;
                                    const isActive = activeTab === tab.key;
                                    return (
                                        <button
                                            key={tab.key}
                                            onClick={() => handleTabChange(tab.key)}
                                            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-medium text-sm transition-all whitespace-nowrap ${isActive
                                                ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 shadow-lg shadow-cyan-500/10'
                                                : 'text-zinc-400 hover:text-zinc-200 hover:bg-white/5 border border-transparent'
                                                }`}
                                        >
                                            <IconComp className="w-4 h-4" />
                                            {tab.label}
                                        </button>
                                    );
                                })}
                            </div>

                            {activeTab !== 'general' && (
                                <DateFilter
                                    dateDebut={dateDebut}
                                    dateFin={dateFin}
                                    setDateDebut={setDateDebut}
                                    setDateFin={setDateFin}
                                    onFilter={filtrerByDate}
                                    onReset={resetFiltre}
                                />
                            )}

                            {renderTabContent()}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default DetailDevice;