from fastapi import APIRouter, HTTPException,Query
from fastapi.responses import StreamingResponse
from datetime import date
from typing import List,Optional
from backend.fonction.metier.service.rapport_service import (
    getCpuRaportById,
    getRamRaportById,
    getStockageRaportById,
    getBatterieRaportById,
    getReseauRaportById,
    getConnectedPerRaportById,
    getDeviceRaportGeneral,
    filterRapportDeviceByDate,
    idByName,getReportsForExport
)
from backend.fonction.metier.service.export_service import (
    build_sections, generate_excel, generate_pdf, TABLE_BUILDERS,
    build_export_filename, resolve_device_export_name, save_export_file,
)
from backend.fonction.metier.models.rapport import RapportDeviceResponse,TypeRapportIdResponse
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
def getRapportFiltrer(id_device: int, id_type_rapport: int, date_debut: date, date_fin: date):
    try:
        return filterRapportDeviceByDate(id_device, id_type_rapport, date_debut, date_fin)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/idByName", response_model=TypeRapportIdResponse)
def getIdByName(name: str):
    try:
        return {"id": idByName(name)}
    except Exception as e:
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
        device_name = resolve_device_export_name(id)
        titre = f"Rapport {onglet} - {device_name}"

        buffer = generate_excel(sections, titre)
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
        device_name = resolve_device_export_name(id)
        titre = f"Rapport {onglet} - {device_name}"
        periode = f"Période : {date_debut} au {date_fin}" if date_debut and date_fin else "Toute la période"

        buffer = generate_pdf(sections, titre, periode)
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
    
  
