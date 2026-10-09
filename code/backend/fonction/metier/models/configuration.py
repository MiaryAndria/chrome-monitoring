from pydantic import BaseModel
from datetime import datetime

class ConfigurationData(BaseModel):
    type: str
    valeur: int

class ConfigurationResponse(BaseModel):
    id: int
    type: str
    valeur: int
    date: datetime