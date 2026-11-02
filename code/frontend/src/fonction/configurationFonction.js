import api_service from "../api/api_service";

export const getListeConfigurationPage = async (params = {}) => {
    try {
        const response = await api_service.get('configuration/liste/page', { params });
        return response.data;
    } catch (e) {
        console.log(e);
        return { items: [], total: 0, page: 1, page_size: params.page_size || 10, total_pages: 0 };
    }
};

export const getListeCategorieConfiguration = async () => {
    try {
        const response = await api_service.get('configuration/categorie/type');
        return response.data;
    } catch (e) {
        console.log(e);
        return [];
    }
};

export const getListeTypeConfiguration = async (idCategorie) => {
    try {
        const response = await api_service.get(`configuration/type/${idCategorie}`);
        return response.data;
    } catch (e) {
        console.log(e);
        return [];
    }
};

export const createConfiguration = async (idType, valeur) => {
    return await api_service.post('configuration/create', {
        id_type: idType,
        valeur: valeur
    });
};

export const getDetailConfiguration = async (id) => {
    try {
        const response = await api_service.get(`configuration/${id}`)
        return response.data
    } catch (e) {
        console.log(e)
    }
};

export const updateConfiguration = async (id, idType, valeur) => {
    try {
        return await api_service.put(`configuration/${id}/update`, {
            id_type: idType,
            valeur: valeur
        });
    } catch (e) {
        console.log(e);
        return null;
    }
};

export const deleteConfiguration = async (id) => {
    try {
        return await api_service.post(`configuration/${id}/delete`);
    } catch (e) {
        console.log(e);
        return null;
    }
};

export const supprimerConfiguration = async (id) => {
    try {
        return await api_service.post(`configuration/${id}/hard/delete`);
    } catch (e) {
        console.log(e);
        return null;
    }
};

export const getListeArchiverPage = async (params = {}) => {
    try {
        const response = await api_service.get('configuration/liste/archiver/page', { params });
        return response.data;
    } catch (e) {
        console.log(e);
        return { items: [], total: 0, page: 1, page_size: params.page_size || 10, total_pages: 0 };
    }
};

export const restaurerConfiguration = async (id) => {
    try {
        return await api_service.post(`configuration/${id}/restaurer`);
    } catch (e) {
        console.log(e);
        return null;
    }
};
