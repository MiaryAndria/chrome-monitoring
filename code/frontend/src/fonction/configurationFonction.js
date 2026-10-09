import api_service from "../api/api_service";

export const getListeConfiguration = async () => {
    try {
        const response = await api_service.get('configuration/liste');
        return response;
    } catch (e) {
        console.log(e)
    }
};

export const createConfiguration = async (t,v) => {
    try {
        await api_service.post('configuration/create', {
            type:t,
            valeur:v
        })
    } catch (e) {
        console.log(e)
    }
};

export const updateConfiguration = async (id,t,v) => {
    try {
        await api_service.put(`configuration/${id}/update`, {
            type: t,
            valeur :v
        })
    } catch (e) {
        console.log(e)
    }
};

export const deleteConfiguration = async(id)=>{
    try{
        await api_service.post(`configuration/${id}/delete`)
    }catch(e){
     console.log(e)   
    }
};

export const getListeArchiver = async()=>{
    try{
        return await api_service.get(`configuration/archive`)
    }catch(e){
        console.log(e)
    }
};
