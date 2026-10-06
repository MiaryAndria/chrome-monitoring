import api_service from "../api/api_service";

export const getListeImprimante = async () => {
    try {
        const response = await api_service.get('/imprimante/liste');
        return response.data;
    } catch (e) {
        console.log(e);
    }
};