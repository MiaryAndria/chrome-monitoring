import api_service from "../api/api_service";

export const getListeFiliale = async () => {
    try {
        const response = await api_service.get('/filiale/liste');
        return response.data;
    } catch (e) {
        console.log(e);
    }
};

export const getDevicesByFiliale = async (id_filiale) => {
    try {
        const response = await api_service.get(`/filiale/${id_filiale}/devices`);
        return response.data;
    } catch (e) {
        console.log(e);
    }
};