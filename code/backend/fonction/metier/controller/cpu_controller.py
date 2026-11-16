from datetime import datetime

from fastapi import APIRouter

from backend.exceptions import ValidationError
from backend.fonction.metier.service.cpu_service import (
    get_cpu_device_date,
    get_latest_cpu,
)

router = APIRouter()


@router.get("/{device_id}/latest")
def getCpuLatest(device_id: int):
    latest = get_latest_cpu(device_id)
    return {"device_id": device_id, "latest": latest}


@router.get("/{device_id}/somme")
def getCpuSomme(device_id: int, date_debut: datetime, date_fin: datetime):
    if date_fin < date_debut:
        raise ValidationError("date_fin doit être supérieure ou égale à date_debut")
    return get_cpu_device_date(device_id, date_debut, date_fin)
