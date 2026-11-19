import api_service from "../api/api_service";

export const getEvenements = async (params = {}) => {
    try {
        const response = await api_service.get('/evenement/liste', { params });
        return response.data;
    } catch (e) {
        console.log(e);
        return { items: [], total: 0, page: 1, page_size: params.page_size || 10, total_pages: 0 };
    }
};

export const getEvenementsResolues = async (params = {}) => {
    try {
        const response = await api_service.get('/evenement/liste/resolue', { params });
        return response.data;
    } catch (e) {
        console.log(e);
        return { items: [], total: 0, page: 1, page_size: params.page_size || 10, total_pages: 0 };
    }
};

export const getDureeVieEvenement = async (eventId) => {
    try {
        const response = await api_service.get(`/evenement/${eventId}/duree-vie`);
        return response.data;
    } catch (e) {
        console.log(e);
        return null;
    }
};

export const getDetailEvenement = async (eventId) => {
    try {
        const response = await api_service.get(`/evenement/${eventId}`);
        return response.data;
    } catch (e) {
        console.log(e);
        return null;
    }
};

export const marquerEvenementResolu = async (eventId) => {
    try {
        const response = await api_service.post(`/evenement/${eventId}/marquer-resolu`);
        return response.data;
    } catch (e) {
        console.log(e);
        throw e;
    }
};

export const repasserEvenementActif = async (eventId) => {
    try {
        const response = await api_service.post(`/evenement/${eventId}/repasser-active`);
        return response.data;
    } catch (e) {
        console.log(e);
        throw e;
    }
};

export const getListeTypeEvenement = async () => {
    try {
        const response = await api_service.get('evenement/liste/type');
        return response.data;
    } catch (e) {
        console.log(e);
    }
};
