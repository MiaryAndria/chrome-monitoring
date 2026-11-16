import api_service from "../api/api_service";

export const resetData = async () => {
    try {
        const response = await api_service.post('/reset');
        return response;
    } catch (e) {
        console.log(e)
    }
};