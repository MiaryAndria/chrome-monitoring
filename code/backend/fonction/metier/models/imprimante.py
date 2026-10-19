from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class ImprimanteResponse(BaseModel):
    id: int
    vid: Optional[int] = None
    pid: Optional[int] = None
    vendor: Optional[str] = None
    nom: Optional[str] = None


class DeviceImprimanteResponse(BaseModel):
    device_id: Optional[str] = None
    serial_number: Optional[str] = None
    modele: Optional[str] = None
    ip_adress: Optional[str] = None
    mac_adress: Optional[str] = None
    chromeos_version: Optional[str] = None
    derniere_detection: Optional[datetime] = None


class UserImprimanteResponse(BaseModel):
    email: str
    derniere_utilisation: Optional[datetime] = None


class ImprimanteDetailResponse(ImprimanteResponse):
    device: List[DeviceImprimanteResponse] = []
    user: List[UserImprimanteResponse] = []


class ImprimantePageResponse(BaseModel):
    items: List[ImprimanteResponse]
    total: int
    page: int
    page_size: int
    total_pages: int