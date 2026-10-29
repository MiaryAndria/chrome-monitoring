import api_service from "../api/api_service";

export const effectuerComparaisonSimple = async(id1,id2)=>{
    try{
        return await api_service.post('comparaison/simple',{
            deviceId1 : id1,
            deviceId2 : id2
        })
    }catch(e){
        console.log(e)
        return null;
    }
};

export const effectuerDoubleComparaison = async(id1,id2)=>{
    try{
        return await api_service.post('comparaison/double',{
            deviceId : id1,
            deviceId2 : id2
        })
    }catch(e){
        console.log(e)
        return null;
    }
};

