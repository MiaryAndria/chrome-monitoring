import api_service from "../api/api_service";

export const getListeSeuilPage = async (params = {}) => {
    try {
        const response = await api_service.get('seuil/liste/page', { params });
        return response.data;
    } catch (e) {
        console.log(e);
        return { items: [], total: 0, page: 1, page_size: params.page_size || 10, total_pages: 0 };
    }
};

export const supprimerSeuil = async(id)=>{
    try{
        return await api_service.post(`seuil/${id}/hard/delete`)
    }catch(e){
        console.log(e)
    }
};

export const getListeCategorieSeuil = async () => {
    try {
        const response = await api_service.get('seuil/categorie/type');
        return response.data;
    } catch (e) {
        console.log(e);
        return [];
    }
};

export const getListeTypeSeuil = async (idCategorie) => {
    try {
        const response = await api_service.get(`seuil/type/${idCategorie}`);
        return response.data;
    } catch (e) {
        console.log(e);
        return [];
    }
};

export const createSeuil = async (idType, valeur) => {
    return await api_service.post('seuil/create', {
        id_type: idType,
        valeur: valeur
    });
};

export const getDetailSeuil = async (id) => {
    try {
        const response = await api_service.get(`seuil/${id}`);
        return response.data;
    } catch (e) {
        console.log(e);
    }
};

export const updateSeuil = async (id, idType, valeur, sens) => {
    try {
        return await api_service.put(`seuil/${id}/update`, {
            id_type: idType,
            valeur: valeur,
            sens: sens
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
