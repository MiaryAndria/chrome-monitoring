from pydantic import BaseModel

class UserLogin(BaseModel):
    email:str
    mdp:str
    
class UserResponse(BaseModel):
    email:str
    nom:str