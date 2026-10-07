import api_service from "../api/api_service";

export const getListeEvenement = async () => {
    try {
        const response = await api_service.get('/evenement/liste');
        return response.data?.evenements ?? [];
    } catch (e) {
        console.log(e);
        return [];
    }
};

export const getListeTypeEvenement = async()=>{
    try{
        const response = await api_service.get('evenement/liste/type');
        return response.data
    }catch(e){
        console.log(e)
    }
};