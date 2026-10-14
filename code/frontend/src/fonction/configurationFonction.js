import api_service from "../api/api_service";

export const getListeConfiguration = async () => {
    try {
        return await api_service.get('configuration/liste');
    } catch (e) {
        console.log(e);
        return { data: [] };
    }
};

export const createConfiguration = async (t, v) => {
    try {
        return await api_service.post('configuration/create', {
            type: t,
            valeur: v
        });
    } catch (e) {
        console.log(e);
        return null;
    }
};

export const updateConfiguration = async (id, t, v) => {
    try {
        return await api_service.put(`configuration/${id}/update`, {
            type: t,
            valeur: v
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

export const getListeArchiver = async () => {
    try {
        return await api_service.get('configuration/liste/archiver');
    } catch (e) {
        console.log(e);
        return { data: [] };
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
