from typing import List
from datetime import datetime
from pydantic import BaseModel


class AlerteNombreResponse(BaseModel):
    nombre: int


class AlerteResume(BaseModel):
    id: int
    id_device: int
    serial_number: str | None = None
    type: str
    message: str | None = None
    date: datetime | None = None
    utilisateur_recent: str | None = None


class AlerteResumePageResponse(BaseModel):
    items: List[AlerteResume]
    total: int
    page: int
    page_size: int
    total_pages: int
