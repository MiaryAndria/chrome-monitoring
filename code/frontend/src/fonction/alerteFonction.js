import api_service from "../api/api_service";

export const getNombreAlerte = async () => {
    try {
        const response = await api_service.get('/alerte/nombre');
        return response.data;            
    } catch (e) {
        console.log(e);
        return { nombre: 0 };
    }
};

export const getNombreAlerteResolue= async () => {
    try {
        const response = await api_service.get('/alerte/nombre/resolue');
        return response.data;            
    } catch (e) {
        console.log(e);
        return { nombre: 0 };
    }
};

export const getNombreAlerteCpuActive= async (date_debut,date_fin) => {
    try {
        const response = await api_service.get('/alerte/cpu/active',{
            params: { date_debut, date_fin }
        });
        return response.data.nombre;            
    } catch (e) {
        console.log(e);
        return 0;
    }
};

export const getNombreAlerteRamActive= async (date_debut,date_fin) => {
    try {
        const response = await api_service.get('/alerte/ram/active',{
            params: { date_debut, date_fin }
        });
        return response.data.nombre;            
    } catch (e) {
        console.log(e);
        return 0;
    }
};

export const getNombreAlerteTemperatureActive= async (date_debut,date_fin) => {
    try {
        const response = await api_service.get('/alerte/temperature/active',{
            params: { date_debut, date_fin }
        });
        return response.data.nombre;            
    } catch (e) {
        console.log(e);
        return 0;
    }
};

export const getNombreAlerteCpuResolue= async (date_debut,date_fin) => {
    try {
        const response = await api_service.get('/alerte/cpu/resolue',{
            params: { date_debut, date_fin }
        });
        return response.data.nombre;            
    } catch (e) {
        console.log(e);
        return 0;
    }
};

export const getNombreAlerteRamResolue= async (date_debut,date_fin) => {
    try {
        const response = await api_service.get('/alerte/ram/resolue',{
            params: { date_debut, date_fin }
        });
        return response.data.nombre;            
    } catch (e) {
        console.log(e);
        return 0;
    }
};

export const getNombreAlerteTemperatureResolue= async (date_debut,date_fin) => {
    try {
        const response = await api_service.get('/alerte/temp/resolue',{
            params: { date_debut, date_fin }
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

export const getListeAlerte = async (date_debut, date_fin) => {
    try {
        const response = await api_service.get('/alerte/device', {
            params: { date_debut, date_fin }
        });
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

export const getListeAlerteResolue = async (date_debut, date_fin) => {
    try {
        const response = await api_service.get('/alerte/device/resolue', {
            params: { date_debut, date_fin }
        });
        return response.data;
    } catch (e) {
        console.log(e);
        return [];
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
