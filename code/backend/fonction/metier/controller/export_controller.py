from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from backend.exceptions import NotFoundError
from backend.fonction.metier.service.export_service import generate_excel, EXPORT_BUILDERS

router = APIRouter()

MEDIA_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@router.get("/excel/{entite}")
def export_excel(entite: str):
    if entite not in EXPORT_BUILDERS:
        raise NotFoundError("Entité inconnue")

    titre, builder = EXPORT_BUILDERS[entite]
    sections = builder()
    buffer = generate_excel(sections, titre, device_info=None)

    return StreamingResponse(
        buffer,
        media_type=MEDIA_XLSX,
        headers={"Content-Disposition": f'attachment; filename="{entite}.xlsx"'},
    )
