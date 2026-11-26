import api_service from "../api/api_service";

export const getListeSynchronisation = async (params = {}) => {
    try {
        const response = await api_service.get("/synchronisation/liste/page", { params });
        return response.data;
    } catch (e) {
        console.log(e);
        return { items: [], total: 0, page: 1, page_size: params.page_size || 10, total_pages: 0 };
    }
};

export const getDetailSynchronisation = async (id) => {
    try {
        const response = await api_service.get(`/synchronisation/${id}`);
        return response.data;
    } catch (e) {
        console.log(e);
        return null;
    }
};

export const getSynchronisationEnCours = async () => {
    try {
        const response = await api_service.get("/synchronisation/en-cours");
        return response.data;
    } catch (e) {
        console.log(e);
        return null;
    }
};

export const getStatutsSynchronisation = async () => {
    try {
        const response = await api_service.get("/synchronisation/statuts");
        return response.data;
    } catch (e) {
        console.log(e);
        return [];
    }
};
