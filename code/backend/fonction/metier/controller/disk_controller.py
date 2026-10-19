import traceback

from fastapi import APIRouter, HTTPException

from backend.fonction.metier.service.disk_service import get_latest_disk

router = APIRouter()


@router.get("/{device_id}/latest")
def getDiskLatest(device_id: int):
    try:
        latest = get_latest_disk(device_id)
        return {"device_id": device_id, "latest": latest}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
