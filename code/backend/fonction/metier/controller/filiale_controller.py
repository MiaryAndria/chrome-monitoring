from typing import List
from fastapi import APIRouter, HTTPException
from backend.fonction.metier.models.filiale import FilialeResponse
from backend.fonction.metier.models.device import DeviceResponses
from backend.fonction.metier.service.filiale_service import (
    get_all_filiales,
    get_devices_by_filiale,
)

router = APIRouter()


@router.get("/liste", response_model=List[FilialeResponse])
def getListeFiliale():
    filiales = get_all_filiales()
    if filiales is None:
        raise HTTPException(
            status_code=500,
            detail="Impossible de récupérer la liste des filiales"
        )
    return [
        {
            "id": f[0],
            "org_unit_path": f[1],
        }
        for f in filiales
    ]


@router.get("/{id_filiale}/devices", response_model=List[DeviceResponses])
def getDevicesByFiliale(id_filiale: int):
    devices = get_devices_by_filiale(id_filiale)
    if devices is None:
        raise HTTPException(
            status_code=500,
            detail="Impossible de récupérer les devices de cette filiale"
        )
    return [
        {
            "id": d[0],
            "id_device": d[1],
            "serial_number": d[2],
            "modele": d[3],
            "id_type_appareil": d[4],
            "id_utilisateur": d[5],
            "chromeos_version": d[6],
            "chrome_version": d[7],
            "date": str(d[8]) if d[8] else None,
            "ip_adress": d[9],
            "mac_adress": d[10],
            "status": d[11],
            "utilisateur_email": d[12],
            "utilisateurs_recents": d[13],
        }
        for d in devices
    ]

