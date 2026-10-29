import api_service from "../api/api_service";

export const getImprimantes = async (params = {}) => {
    try {
        const response = await api_service.get('/imprimante/liste', { params });
        return response.data;
    } catch (e) {
        console.log(e);
        return { items: [], total: 0, page: 1, page_size: params.page_size || 10, total_pages: 0 };
    }
};

export const getVendors = async () => {
    try {
        const response = await api_service.get('/imprimante/vendors');
        return response.data || [];
    } catch (e) {
        console.log(e);
        return [];
    }
};

export const getImprimanteDetail = async(id)=>{
    try{
        const response = await api_service.get(`/imprimante/${id}`)
        return response.data;
    }catch(e){
        console.log(e);
    }
}