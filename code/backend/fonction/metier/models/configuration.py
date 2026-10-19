from pydantic import BaseModel
from typing import Any
from datetime import datetime

class ConfigurationData(BaseModel):
    type: str
    valeur: Any

class ConfigurationResponse(BaseModel):
    id:int
    type: str
    valeur: Any
    date: datetime | None = None
