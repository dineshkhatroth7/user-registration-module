
from fastapi import APIRouter
from app.models.user_models import UserRegister
from app.services.user_service import register_user_service

router = APIRouter()
 
@router.post("/register")
def register_user(request: UserRegister):
    return register_user_service(request)
