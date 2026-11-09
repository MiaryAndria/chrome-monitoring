import api_service from "../api/api_service";

export const getUtilisateursRecentPage = async (params = {}) => {
    try {
        const response = await api_service.get("/utilisateur/recent/page", { params });
        return response.data;
    } catch (e) {
        console.log(e);
        return { items: [], total: 0, page: 1, page_size: params.page_size || 10, total_pages: 0 };
    }
};

export const getUtilisateurRecentDevices = async (id, params = {}) => {
    try {
        const response = await api_service.get(`/utilisateur/recent/${id}/devices`, { params });
        return response.data;
    } catch (e) {
        console.log(e);
        return [];
    }
};
