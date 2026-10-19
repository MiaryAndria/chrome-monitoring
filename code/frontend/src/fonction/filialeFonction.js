import api_service from "../api/api_service";

export const getListeFiliale = async () => {
    try {
        const response = await api_service.get('/filiale/liste');
        return response.data;
    } catch (e) {
        console.log(e);
    }
};

export const getDevicesByFiliale = async (id_filiale, params = {}) => {
    try {
        const response = await api_service.get(`/filiale/${id_filiale}/devices`, { params });
        return response.data;
    } catch (e) {
        console.log(e);
        return { items: [], total: 0, page: 1, page_size: params.page_size || 10, total_pages: 0 };
    }
};