import traceback

from fastapi import APIRouter, HTTPException,Query
from fastapi.responses import StreamingResponse
from datetime import date, datetime
from typing import List,Optional
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
    idByName,getReportsForExport,
    getListeReport
)

from backend.fonction.metier.service.imprimante_service import get_imprimante_detail

from backend.fonction.metier.service.export_service import (
    build_sections, generate_excel, generate_pdf, TABLE_BUILDERS,
    build_export_filename, resolve_device_export_name, save_export_file,
)
from backend.fonction.metier.models.rapport import RapportDeviceResponse,TypeRapportIdResponse
from backend.utils.validation import is_valid_datetime_range
router = APIRouter()

ONGLETS_VALIDES = {"general", *TABLE_BUILDERS.keys()}

@router.get("/general/{id}")
def getReportGeneral(id: int):
    try:
        report = getDeviceRaportGeneral(id)
        if report is None:
            raise HTTPException(status_code=404, detail="Rapport non trouvé pour ce device")
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cpu/{id}")
def getCpuReport(id: int):
    try:
        return getCpuRaportById(id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ram/{id}")
def getRamReport(id: int):
    try:
        return getRamRaportById(id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stockage/{id}")
def getStockageReport(id: int):
    try:
        return getStockageRaportById(id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/batterie/{id}")
def getBatterieReport(id: int):
    try:
        return getBatterieRaportById(id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reseau/{id}")
def getReseauReport(id: int):
    try:
        return getReseauRaportById(id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/peripheriques/{id}")
def getPeripheriquesReport(id: int):
    try:
        return getConnectedPerRaportById(id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

        
@router.get("/filter", response_model=List[RapportDeviceResponse])
def getRapportFiltrer(
    id_device: int,
    id_type_rapport: int,
    datetime_from: datetime,
    datetime_to: datetime,
):
    if not is_valid_datetime_range(datetime_from, datetime_to):
        raise HTTPException(
            status_code=400,
            detail="datetime_to doit être supérieur ou égal à datetime_from",
        )
    try:
        return filterRapportDeviceByDatetime(
            id_device, id_type_rapport, datetime_from, datetime_to
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/idByName", response_model=TypeRapportIdResponse)
def getIdByName(name: str):
    try:
        return {"id": idByName(name)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/excel/imprimante/{id}")
def exportImprimanteExcel(id: int):
    try:
        detail = get_imprimante_detail(id)
        if detail is None:
            raise HTTPException(status_code=404, detail="Imprimante introuvable")

        nom = detail.get("nom") or f"imprimante_{id}"
        sections = build_imprimante_sections(detail)
        titre = f"Rapport imprimante - {nom}"

        buffer = generate_excel(sections, titre, device_info=None)
        media = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ext = "xlsx"

        filename = build_export_filename("imprimante", id, ext, nom)
        save_export_file(buffer, ext, filename)
        return StreamingResponse(
            buffer, media_type=media,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/pdf/imprimante/{id}")
def exportImprimantePdf(id: int):
    try:
        detail = get_imprimante_detail(id)
        if detail is None:
            
            raise HTTPException(status_code=404, detail="Imprimante introuvable")

        nom = detail.get("nom") or f"imprimante_{id}"
        sections = build_imprimante_sections(detail)
        titre = f"Rapport imprimante - {nom}"
        periode = "Toute la période"

        buffer = generate_pdf(sections, titre, periode, device_info=None)
        media = "application/pdf"
        ext = "pdf"

        filename = build_export_filename("imprimante", id, ext, nom)
        save_export_file(buffer, ext, filename)
        return StreamingResponse(
            buffer, media_type=media,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/export/excel/{onglet}/{id}")
def exportRapportExcel(
    onglet: str,
    id: int,
    date_debut: Optional[date] = None,
    date_fin: Optional[date] = None,
):
    if onglet not in ONGLETS_VALIDES:
        raise HTTPException(status_code=404, detail="Onglet inconnu")
    try:
        reports = getReportsForExport(onglet, id, date_debut, date_fin)
        sections = build_sections(onglet, reports)
        from backend.fonction.metier.service.device_service import getDeviceDetail
        device_info = getDeviceDetail(id)
        device_name = resolve_device_export_name(id)
        titre = f"Rapport {onglet} - {device_name}"

        buffer = generate_excel(sections, titre, device_info=device_info)
        media = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ext = "xlsx"

        filename = build_export_filename(onglet, id, ext, device_name)
        save_export_file(buffer, ext, filename)
        return StreamingResponse(
            buffer, media_type=media,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except HTTPException:
        raise
    except Exception as e:
        
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/export/pdf/{onglet}/{id}")
def exportPdf(
    onglet: str,
    id: int,
    date_debut: Optional[date] = None,
    date_fin: Optional[date] = None,
):
    if onglet not in ONGLETS_VALIDES:
        raise HTTPException(status_code=404, detail="Onglet inconnu")
    try:
        reports = getReportsForExport(onglet, id, date_debut, date_fin)
        sections = build_sections(onglet, reports)
        from backend.fonction.metier.service.device_service import getDeviceDetail
        device_info = getDeviceDetail(id)
        device_name = resolve_device_export_name(id)
        titre = f"Rapport {onglet} - {device_name}"
        periode = f"Période : {date_debut} au {date_fin}" if date_debut and date_fin else "Toute la période"

        buffer = generate_pdf(sections, titre, periode, device_info=device_info)
        media = "application/pdf"
        ext = "pdf"

        filename = build_export_filename(onglet, id, ext, device_name)
        save_export_file(buffer, ext, filename)
        return StreamingResponse(
            buffer, media_type=media,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

  
@router.get("/liste")
def getReport():
    try:
        report = getListeReport()
        if report is None:
            raise HTTPException(status_code=404, detail="Rapport non trouvé pour ce device")
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
