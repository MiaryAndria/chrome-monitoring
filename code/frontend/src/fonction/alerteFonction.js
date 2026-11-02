import api_service from "../api/api_service";
import { Cpu, MemoryStick, Thermometer, HardDrive, BatteryFull, BatteryWarning, Printer, Bell } from 'lucide-react';

export const ALERTE_META = {
    ALERTE_CPU:            { label: 'CPU',            color: '#22d3ee', text: 'text-cyan-400',    Icon: Cpu },
    ALERTE_RAM:            { label: 'RAM',            color: '#a78bfa', text: 'text-violet-400',  Icon: MemoryStick },
    ALERTE_TEMPERATURE:    { label: 'Température',    color: '#f59e0b', text: 'text-amber-400',   Icon: Thermometer },
    ALERTE_STOCKAGE:       { label: 'Stockage',       color: '#34d399', text: 'text-emerald-400', Icon: HardDrive },
    ALERTE_SANTE_BATTERIE: { label: 'Santé batterie', color: '#f472b6', text: 'text-pink-400',    Icon: BatteryWarning },
    ALERTE_BATTERIE:       { label: 'Batterie',       color: '#facc15', text: 'text-yellow-400',  Icon: BatteryFull },
    ALERTE_TACHE_PRINT:    { label: 'Impression',     color: '#60a5fa', text: 'text-blue-400',    Icon: Printer },
    ALERTE_EVENEMENTS:     { label: 'Événements',     color: '#fb7185', text: 'text-rose-400',    Icon: Bell },
};

export const getNombreAlerte = async () => {
    try {
        const response = await api_service.get('/alerte/nombre');
        return response.data;            
    } catch (e) {
        console.log(e);
        return { nombre: 0 };
    }
};

export const getNombreAlerteType = async (type, statut = 'active', date_debut, date_fin) => {
    try {
        const response = await api_service.get(`/alerte/stats/${type}`, {
            params: { statut, date_debut, date_fin }
        });
        return response.data.nombre;
    } catch (e) {
        console.log(e);
        return 0;
    }
};

export const getDixPremierAlerte = async () => {
    try {
        const response = await api_service.get('/alerte/tenAlerte');
        return response.data;
    } catch (e) {
        console.log(e);
        return [];
    }
};

export const getListeAlertePage = async (params = {}) => {
    try {
        const response = await api_service.get('/alerte/device/page', { params });
        return response.data;
    } catch (e) {
        console.log(e);
        return { items: [], total: 0, page: 1, page_size: params.page_size || 10, total_pages: 0 };
    }
};

export const getListeAlerteResoluePage = async (params = {}) => {
    try {
        const response = await api_service.get('/alerte/device/resolue/page', { params });
        return response.data;
    } catch (e) {
        console.log(e);
        return { items: [], total: 0, page: 1, page_size: params.page_size || 10, total_pages: 0 };
    }
};

export const getListeType = async()=>{
    try{
        const response = await api_service.get('/alerte/liste/type')
        return response.data
    }catch(e){
        console.log(e)
        return []
    }
};
