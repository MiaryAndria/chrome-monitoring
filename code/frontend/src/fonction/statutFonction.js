export const getListeStatut = async()=>{
    try{
        const response = await api_service.get('statut/liste');
        return response.data
    }catch(e){
        console.log(e)
    }
};