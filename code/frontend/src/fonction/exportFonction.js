import api_service from "../api/api_service";

export const telechargerFichier = async (url, nomDefaut) => {
    const response = await api_service.get(url, { responseType: "blob" });
    const blob = new Blob([response.data]);
    const objectUrl = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = objectUrl;
    a.download = nomDefaut;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(objectUrl);
};

export const exporterEntite = (entite) =>
    telechargerFichier(`/export/excel/${entite}`, `${entite}.xlsx`);

export const exporterAppareilsExcel = () =>
    telechargerFichier("/export/excel/devices", "liste_appareils.xlsx");

export const exporterFilialesExcel = () =>
    telechargerFichier("/export/excel/filiales", "appareils_par_filiale.xlsx");

export const exporterImprimantesExcel = () =>
    telechargerFichier("/export/excel/imprimantes", "liste_imprimantes.xlsx");
