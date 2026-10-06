import api_service from "../api/api_service";

export const getListeEvenement = async () => {
    try {
        const response = await api_service.get('/evenement/liste');
        // La réponse a la forme { total: N, evenements: [...] }
        return response.data?.evenements ?? [];
    } catch (e) {
        console.log(e);
        return [];
    }
};