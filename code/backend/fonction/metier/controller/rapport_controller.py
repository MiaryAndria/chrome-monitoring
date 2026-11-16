from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from datetime import datetime
from typing import List, Optional

from backend.exceptions import NotFoundError
from backend.fonction.metier.service.rapport_service import (
    build_imprimante_sections,
    getCpuRaportById,
    getRamRaportById,
    getStockageRaportById,
    getBatterieRaportById,
    getReseauRaportById,
    getConnectedPerRaportById,
    getDeviceRaportGeneral,
    filterRapportDeviceByDatetime,
    idByName,
    getReportsForExport,
    getListeReport,
)
from backend.fonction.metier.service.imprimante_service import get_imprimante_detail
from backend.fonction.metier.service.export_service import (
    build_sections,
    generate_excel,
    generate_pdf,
    TABLE_BUILDERS,
    build_export_filename,
    resolve_device_export_name,
)
from backend.fonction.metier.models.rapport import RapportDeviceResponse, TypeRapportIdResponse
from backend.utils.validation import valider_plage_datetime

router = APIRouter()

ONGLETS_VALIDES = {"general", *TABLE_BUILDERS.keys()}


@router.get("/general/{id}")
def getReportGeneral(id: int):
    report = getDeviceRaportGeneral(id)
    if report is None:
        raise NotFoundError("Rapport non trouvé pour ce device")
    return report


@router.get("/cpu/{id}")
def getCpuReport(id: int):
    return getCpuRaportById(id)


@router.get("/ram/{id}")
def getRamReport(id: int):
    return getRamRaportById(id)


@router.get("/stockage/{id}")
def getStockageReport(id: int):
    return getStockageRaportById(id)


@router.get("/batterie/{id}")
def getBatterieReport(id: int):
    return getBatterieRaportById(id)


@router.get("/reseau/{id}")
def getReseauReport(id: int):
    return getReseauRaportById(id)


@router.get("/peripheriques/{id}")
def getPeripheriquesReport(id: int):
    return getConnectedPerRaportById(id)


@router.get("/filter", response_model=List[RapportDeviceResponse])
def getRapportFiltrer(
    id_device: int,
    id_type_rapport: int,
    datetime_from: Optional[datetime] = None,
    datetime_to: Optional[datetime] = None,
):
    valider_plage_datetime(datetime_from, datetime_to)
    return filterRapportDeviceByDatetime(
        id_device, id_type_rapport, datetime_from, datetime_to
    )


@router.get("/idByName", response_model=TypeRapportIdResponse)
def getIdByName(name: str):
    return {"id": idByName(name)}


@router.get("/export/excel/imprimante/{id}")
def exportImprimanteExcel(id: int):
    detail = get_imprimante_detail(id)
    if detail is None:
        raise NotFoundError("Imprimante introuvable")

    nom = detail.get("nom") or f"imprimante_{id}"
    sections = build_imprimante_sections(detail)
    titre = f"Rapport imprimante - {nom}"

    buffer = generate_excel(sections, titre, device_info=None)
    media = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    filename = build_export_filename("imprimante", id, "xlsx", nom)
    return StreamingResponse(
        buffer, media_type=media,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/export/pdf/imprimante/{id}")
def exportImprimantePdf(id: int):
    detail = get_imprimante_detail(id)
    if detail is None:
        raise NotFoundError("Imprimante introuvable")

    nom = detail.get("nom") or f"imprimante_{id}"
    sections = build_imprimante_sections(detail)
    titre = f"Rapport imprimante - {nom}"

    buffer = generate_pdf(sections, titre, "Toute la période", device_info=None)
    media = "application/pdf"
    filename = build_export_filename("imprimante", id, "pdf", nom)
    return StreamingResponse(
        buffer, media_type=media,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/export/excel/{onglet}/{id}")
def exportRapportExcel(
    onglet: str,
    id: int,
    date_debut: Optional[datetime] = None,
    date_fin: Optional[datetime] = None,
):
    if onglet not in ONGLETS_VALIDES:
        raise NotFoundError("Onglet inconnu")
    reports = getReportsForExport(onglet, id, date_debut, date_fin)
    sections = build_sections(onglet, reports)
    from backend.fonction.metier.service.device_service import getDeviceDetail
    device_info = getDeviceDetail(id)
    device_name = resolve_device_export_name(id)
    titre = f"Rapport {onglet} - {device_name}"

    buffer = generate_excel(sections, titre, device_info=device_info)
    media = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    filename = build_export_filename(onglet, id, "xlsx", device_name)
    return StreamingResponse(
        buffer, media_type=media,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/export/pdf/{onglet}/{id}")
def exportPdf(
    onglet: str,
    id: int,
    date_debut: Optional[datetime] = None,
    date_fin: Optional[datetime] = None,
):
    if onglet not in ONGLETS_VALIDES:
        raise NotFoundError("Onglet inconnu")
    reports = getReportsForExport(onglet, id, date_debut, date_fin)
    sections = build_sections(onglet, reports)
    from backend.fonction.metier.service.device_service import getDeviceDetail
    device_info = getDeviceDetail(id)
    device_name = resolve_device_export_name(id)
    titre = f"Rapport {onglet} - {device_name}"
    periode = f"Période : {date_debut} au {date_fin}" if date_debut and date_fin else "Toute la période"

    buffer = generate_pdf(sections, titre, periode, device_info=device_info)
    media = "application/pdf"
    filename = build_export_filename(onglet, id, "pdf", device_name)
    return StreamingResponse(
        buffer, media_type=media,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/liste")
def getReport():
    report = getListeReport()
    if report is None:
        raise NotFoundError("Rapport non trouvé pour ce device")
    return report
