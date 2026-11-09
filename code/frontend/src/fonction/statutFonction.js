import api_service from "../api/api_service";

export const getListeStatut = async()=>{
    try{
        const response = await api_service.get('statut/liste');
        return response.data
    }catch(e){
        console.log(e)
    }
};

export const getListeStatutAll = async()=>{
    try{
        const response = await api_service.get('statut/liste/all');
        return response.data
    }catch(e){
        console.log(e)
        return []
    }
};

export const getListeStatutPage = async (params = {}) => {
    try {
        const response = await api_service.get('statut/liste/page', { params });
        return response.data;
    } catch (e) {
        console.log(e);
        return { items: [], total: 0, page: 1, page_size: params.page_size || 10, total_pages: 0 };
    }
};

export const getDetailStatut = async(id)=>{
    try{
        const response = await api_service.get(`statut/${id}`);
        return response.data
    }catch(e){
        console.log(e)
    }
};

export const updateStatut = async(id, nom)=>{
    return await api_service.put(`statut/${id}/update`, { nom });
};
