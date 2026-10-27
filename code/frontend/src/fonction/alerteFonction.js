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

