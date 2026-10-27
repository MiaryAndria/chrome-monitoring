import api_service from "../api/api_service";

export const getListeSeuil = async () => {
    try {
        return await api_service.get('seuil/liste');
    } catch (e) {
        console.log(e);
        return { data: [] };
    }
};

export const getListeSeuilPage = async (params = {}) => {
    try {
        const response = await api_service.get('seuil/liste/page', { params });
        return response.data;
    } catch (e) {
        console.log(e);
        return { items: [], total: 0, page: 1, page_size: params.page_size || 10, total_pages: 0 };
    }
};

export const createSeuil = async (cle, valeur) => {
    try {
        return await api_service.post('seuil/create', {
            cle: cle,
            valeur: valeur
        });
    } catch (e) {
        console.log(e);
        return null;
    }
};

export const getDetailSeuil = async (id) => {
    try {
        const response = await api_service.get(`seuil/${id}`);
        return response.data;
    } catch (e) {
        console.log(e);
    }
};

export const updateSeuil = async (id, cle, valeur) => {
    try {
        return await api_service.put(`seuil/${id}/update`, {
            cle: cle,
            valeur: valeur
        });
    } catch (e) {
        console.log(e);
        return null;
    }
};

export const deleteSeuil = async (id) => {
    try {
        return await api_service.post(`seuil/${id}/delete`);
    } catch (e) {
        console.log(e);
        return null;
    }
};

export const getListeArchiver = async () => {
    try {
        return await api_service.get('seuil/liste/archiver');
    } catch (e) {
        console.log(e);
        return { data: [] };
    }
};

export const getListeArchiverPage = async (params = {}) => {
    try {
        const response = await api_service.get('seuil/liste/archiver/page', { params });
        return response.data;
    } catch (e) {
        console.log(e);
        return { items: [], total: 0, page: 1, page_size: params.page_size || 10, total_pages: 0 };
    }
};

export const restaurerSeuil = async (id) => {
    try {
        return await api_service.post(`seuil/${id}/restaurer`);
    } catch (e) {
        console.log(e);
        return null;
    }
};
