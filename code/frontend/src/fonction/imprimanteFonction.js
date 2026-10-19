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

export const getListeImprimante = async () => {
    const data = await getImprimantes({ page: 1, page_size: 10000 });
    return data?.items ?? [];
};

export const getImprimanteDetail = async(id)=>{
    try{
        const response = await api_service.get(`/imprimante/${id}`)
        return response.data;
    }catch(e){
        console.log(e);
    }
}