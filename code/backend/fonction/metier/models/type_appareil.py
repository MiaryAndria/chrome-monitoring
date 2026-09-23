from pydantic import BaseModel

class typeAppreil(BaseModel):
    nom:str

class typeAppareilResponse(BaseModel):
    id:int
    nom:str