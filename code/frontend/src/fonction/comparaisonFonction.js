import api_service from "../api/api_service";

export const listeComparaison = async () => {
    try {
        const response = await api_service.get("comparaison/liste");
        return response.data;
    } catch (e) {
        console.log(e);
        return null;
    }
};

export const listeDeviceVersion = async (id_device) => {
    try {
        const response = await api_service.get(`comparaison/version/${id_device}`);
        return response.data;
    } catch (e) {
        console.log(e);
        return null;
    }
};

export const effectuerComparaisonSimple = async (id_device, version_a, version_b) => {
    const response = await api_service.post("comparaison/simple", {
        id_device,
        version_a,
        version_b,
    });
    return response.data;
};

export const effectuerDoubleComparaison = async (id_device_a, version_a, id_device_b, version_b) => {
    const response = await api_service.post("comparaison/double", {
        id_device_a,
        version_a,
        id_device_b,
        version_b,
    });
    return response.data;
};
