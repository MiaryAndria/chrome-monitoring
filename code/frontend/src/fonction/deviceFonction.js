import api_service from "../api/api_service";

export const getDeviceStats = (device) => {
    try {
        const stats = {
            total: device.length,
            active: 0,
            inactive: 0,
            deprovisioned: 0,
            disabled: 0,
            unknown: 0
        };

        device.forEach(d => {
            const s = (d.status || '').toUpperCase();
            if (s === 'ACTIVE') stats.active++;
            else if (s === 'INACTIVE') stats.inactive++;
            else if (s === 'DEPROVISIONED') stats.deprovisioned++;
            else if (s === 'DISABLED') stats.disabled++;
            else stats.unknown++;
        });

        return stats;
    } catch (e) {
        console.log(e);
        return { total: 0, active: 0, inactive: 0, deprovisioned: 0, disabled: 0, unknown: 0 };
    }
};


export const synchData = async()=>{
    try{
        const response = await api_service.post('/device/synch');
        return response;
    }catch(e){
        console.log(e)
    }
};

export const resetData = async()=>{
    try{
        const response = await api_service.post('/device/reset');
        return response;
    }catch(e){
        console.log(e)
    }
};

export const getListeDevice = async() =>{
    try{
        const response = await api_service.get('/device/liste')
        return response.data;
    }catch(e){
        console.log(e)
    }
}

export const getDeviceDetail = async(id)=>{
    try{
        const response = await api_service.get(`/device/${id}`)
        return response.data;
    }catch(e){
        console.log(e)
    }
}