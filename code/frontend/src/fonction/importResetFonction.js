import api_service from "../api/api_service";
export const synchData = async () => {
    try {
        const response = await api_service.post('/synch');
        return response;
    } catch (e) {
        console.log(e)
    }
};

export const resetData = async () => {
    try {
        const response = await api_service.post('/reset');
        return response;
    } catch (e) {
        console.log(e)
    }
};