from fastapi import APIRouter

from backend.fonction.metier.service.disk_service import get_latest_disk

router = APIRouter()


@router.get("/{device_id}/latest")
def getDiskLatest(device_id: int):
    latest = get_latest_disk(device_id)
    return {"device_id": device_id, "latest": latest}
