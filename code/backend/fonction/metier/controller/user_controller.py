from backend.fonction.metier.models.user import UserResponse,UserLogin
from backend.fonction.metier.service.user_service import login_user
from fastapi import APIRouter , HTTPException
router = APIRouter()
@router.post("/login",response_model = UserResponse)

def login(data: UserLogin):
    user = login_user(data.email,data.mdp)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Email ou mot de passe incorrect"
        )
        
    return {
            "id":user[0],
            "nom":user [1],
            "email":user[2]
        }