
from fastapi import APIRouter
from app.models.user_models import UserRegister,LoginRequest
from app.services.user_service import register_user_service,login_user_service

router = APIRouter()
 
@router.post("/register")
def register_user(request: UserRegister):
    return register_user_service(request)

@router.post("/login")
def login(request: LoginRequest):
    return login_user_service(request)
