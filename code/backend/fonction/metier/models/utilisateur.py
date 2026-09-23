from pydantic import BaseModel

class Utilisateur(BaseModel):
    email:str

class UtilisateurResponse(BaseModel):
    id:int
    email:int