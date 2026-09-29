import api_service from "../api/api_service";
import { CheckCircle2, Activity, XOctagon, ShieldAlert } from 'lucide-react';

export const getDashboardStats = async () => {
    try {
        const response = await api_service.get('/dashboard/stats');
        return response.data;
    } catch (e) {
        console.log(e);
    }
};

export const getListeStatut = async () => {
    try {
        const response = await api_service.get('/statut/liste');
        return response.data;
    } catch (e) {
        console.log(e);
    }
};

const STATUS_STYLES = [
    { colorClass: "text-emerald-400", bgClass: "bg-emerald-500/10", borderClass: "border-emerald-500/30", hoverClass: "hover:bg-emerald-500/20 hover:border-emerald-500/50", icon: CheckCircle2 },
    { colorClass: "text-amber-400", bgClass: "bg-amber-500/10", borderClass: "border-amber-500/30", hoverClass: "hover:bg-amber-500/20 hover:border-amber-500/50", icon: Activity },
    { colorClass: "text-red-400", bgClass: "bg-red-500/10", borderClass: "border-red-500/30", hoverClass: "hover:bg-red-500/20 hover:border-red-500/50", icon: XOctagon },
    { colorClass: "text-purple-400", bgClass: "bg-purple-500/10", borderClass: "border-purple-500/30", hoverClass: "hover:bg-purple-500/20 hover:border-purple-500/50", icon: ShieldAlert }
];

export const getStatusStyle = (index) => STATUS_STYLES[index % STATUS_STYLES.length];

export const synchData = async () => {
    try {
        const response = await api_service.post('/device/synch');
        return response;
    } catch (e) {
        console.log(e)
    }
};

export const resetData = async () => {
    try {
        const response = await api_service.post('/device/reset');
        return response;
    } catch (e) {
        console.log(e)
    }
};

export const getListeDevice = async () => {
    try {
        const response = await api_service.get('/device/liste')
        return response.data;
    } catch (e) {
        console.log(e)
    }
}

export const getDeviceDetail = async (id) => {
    try {
        const response = await api_service.get(`/device/${id}`)
        return response.data;
    } catch (e) {
        console.log(e)
    }
}

export const getBadgeClass = (status) => {
    const s = (status || '').toUpperCase();

    if (s === 'ACTIVE' || s === 'ACTIFS') {
        return "badge-success bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
    }
    if (s === 'INACTIVE' || s === 'DEPROVISIONED' || s === 'INDISPONIBLES') {
        return "badge-error bg-red-500/10 text-red-400 border-red-500/20"; // Rouge
    }
    return "badge-warning bg-amber-500/10 text-amber-400 border-amber-500/20"; // Jaune / Orange
}


export const searchDevices = async (query) => {
    try {
        const response = await api_service.get(`/device/search?recherche=${encodeURIComponent(query)}`);
        return response.data;
    } catch (e) {
        console.log(e);
    }
};

export const getDetailCpu = async(id)=>{
    try{
        const response = await api_service.get(`/rapport/cpu/${id}`);
        return response.data;
    }catch(e){
        console.log(e)
    }
};

export const getDetailRam = async(id)=>{
    try{    
        const response = await api_service.get(`/rapport/ram/${id}`);
        return response.data;
    }catch(e){  
        console.log(e)
    }
};

export const getDetailStockage = async(id)=>{
    try{    
        const response = await api_service.get(`/rapport/stockage/${id}`);
        return response.data
    }catch(e){
        console.log(e)
    }
};

export const detailBatterie = async(id)=>{
    try{
        const response = await api_service.get(`/rapport/batterie/${id}`);
        return response.data
    }catch(e){
        console.log(e)
    }
};

export const detailReseau = async(id)=>{
    try{
        const response = await api_service.get(`/rapport/reseau/${id}`);
        return response.data
    }catch(e){
        console.log(e)
    }
};

export const detailPeripheriques = async(id)=>{  
    try{
        const response = await api_service.get(`/rapport/peripheriques/${id}`);
        return response.data
    }catch(e){
        console.log(e)
    }
};

export const getDetailGeneral = async(id)=>{
    try{
        const response = await api_service.get(`/rapport/general/${id}`);
        return response.data;
    }catch(e){
        console.log(e)
    }
};

export const extractCpuSummary = (reports) => {
    if (!reports || reports.length === 0) return null;
    let latestTemps = null, latestUtil = null;
    let utilHistory = [], latestTempTime = null, latestUtilTime = null;
    for (const r of reports) {
        const d = r.donnees;
        if (!d) continue;
        if (d.cpuTemperatureInfo?.length > 0 && !latestTemps) {
            latestTemps = d.cpuTemperatureInfo;
            latestTempTime = d.reportTime || r.report_time;
        }
        if (d.cpuUtilizationPct !== undefined && d.cpuUtilizationPct !== null) {
            if (latestUtil === null) {
                latestUtil = d.cpuUtilizationPct;
                latestUtilTime = d.reportTime || r.report_time;
            }
            utilHistory.push({ time: d.reportTime || r.report_time, value: d.cpuUtilizationPct });
        }
    }
    return { latestTemps, latestUtil, utilHistory, latestTempTime, latestUtilTime };
};

export const extractRamSummary = (reports) => {
    if (!reports || reports.length === 0) return null;
    let latest = null;
    let freeHistory = [];
    for (const r of reports) {
        const d = r.donnees;
        if (!d || d.systemRamFreeBytes === undefined) continue;
        if (!latest) {
            latest = { free: d.systemRamFreeBytes, total: d.totalRamBytes, pageFaults: d.pageFaults, time: d.reportTime || r.report_time };
        }
        freeHistory.push({ time: d.reportTime || r.report_time, free: d.systemRamFreeBytes, total: d.totalRamBytes });
    }
    return latest ? { ...latest, freeHistory } : null;
};

export const extractStorageSummary = (reports) => {
    if (!reports || reports.length === 0) return null;
    for (const r of reports) {
        const d = r.donnees;
        if (!d?.disk?.length) continue;
        return { disks: d.disk, time: d.reportTime || r.report_time };
    }
    return null;
};

export const extractBatterySummary = (reports) => {
    if (!reports || reports.length === 0) return null;
    for (const r of reports) {
        const d = r.donnees;
        if (!d) continue;
        if (d.batteryHealth || d.cycleCount !== undefined || d.fullChargeCapacity) {
            return {
                health: d.batteryHealth, cycleCount: d.cycleCount,
                fullChargeCapacity: d.fullChargeCapacity, designCapacity: d.designCapacity,
                serialNumber: d.serialNumber, manufacturer: d.manufacturer,
                status: d.status, voltage: d.batteryVoltage,
                time: d.reportTime || r.report_time
            };
        }
    }
    return null;
};

export const extractNetworkSummary = (reports) => {
    if (!reports || reports.length === 0) return null;
    const results = [];
    for (const r of reports) {
        const d = r.donnees;
        if (!d) continue;
        const entry = { time: d.reportTime || r.report_time };
        const keys = Object.keys(d).filter(k => k !== 'reportTime');
        if (keys.length > 0) {
            keys.forEach(k => entry[k] = d[k]);
            results.push(entry);
        }
    }
    return results.length > 0 ? results : null;
};

export const extractPeripheralsSummary = (reports) => {
    if (!reports || reports.length === 0) return null;
    const devices = [];
    for (const r of reports) {
        const d = r.donnees;
        if (!d) continue;
        if (d.usbPeripheralReport) {
            d.usbPeripheralReport.forEach(p => {
                if (!devices.find(x => x.vid === p.vid && x.pid === p.pid)) devices.push(p);
            });
        }
    }
    return devices.length > 0 ? devices : null;
};

export const filterByDeviceIdAndDate = async (id_device, id_type_rapport, date_debut, date_fin) => {
    try {
        const response = await api_service.get('/rapport/filter', {
            params: { id_device, id_type_rapport, date_debut, date_fin }
        });
        return response.data;
    } catch (e) {
        console.log(e);
    }
};

export const getIdByName = async (name) => {
    try {
        const response = await api_service.get('/rapport/idByName', {
            params: { name }
        });
        return response.data.id;
    } catch (e) {
        console.log(e);
    }
};

