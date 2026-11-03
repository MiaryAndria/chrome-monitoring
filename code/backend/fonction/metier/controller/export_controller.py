import traceback

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from backend.fonction.metier.service.export_service import generate_excel, EXPORT_BUILDERS

router = APIRouter()

MEDIA_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@router.get("/excel/{entite}")
def export_excel(entite: str):
    try:
        if entite not in EXPORT_BUILDERS:
            raise HTTPException(status_code=404, detail="Entité inconnue")

        titre, builder = EXPORT_BUILDERS[entite]
        sections = builder()
        buffer = generate_excel(sections, titre, device_info=None)

        return StreamingResponse(
            buffer,
            media_type=MEDIA_XLSX,
            headers={"Content-Disposition": f'attachment; filename="{entite}.xlsx"'},
        )
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
