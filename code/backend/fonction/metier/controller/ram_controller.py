from datetime import datetime
from typing import Optional

from fastapi import APIRouter

from backend.exceptions import ValidationError
from backend.fonction.metier.service.ram_service import (
    get_latest_ram,
    get_max_total_ram,
    get_ram_device_date,
)

router = APIRouter()


@router.get("/{device_id}/max-total")
def getRamMaxTotal(
    device_id: int,
    datetime_from: Optional[datetime] = None,
    datetime_to: Optional[datetime] = None,
):
    valeur = get_max_total_ram(device_id, datetime_from, datetime_to)
    return {"device_id": device_id, "max_total": valeur}


@router.get("/{device_id}/latest")
def getRamLatest(device_id: int):
    latest = get_latest_ram(device_id)
    return {"device_id": device_id, "latest": latest}


@router.get("/{device_id}/somme")
def getRamSomme(device_id: int, date_debut: datetime, date_fin: datetime):
    if date_fin < date_debut:
        raise ValidationError("date_fin doit être supérieure ou égale à date_debut")
    return get_ram_device_date(device_id, date_debut, date_fin)
