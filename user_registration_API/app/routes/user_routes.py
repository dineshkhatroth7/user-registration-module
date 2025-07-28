
from fastapi import APIRouter,Depends
from app.models.user_models import UserRegister,LoginRequest,ChangeContactRequest,ChangePasswordRequest,ForgotPasswordRequest
from app.services.user_service import register_user_service,login_user_service,change_user_contact_service,change_password_service,forgot_password_service
from app.utils.jwt_handler import get_current_user
from app.utils.decorators import log_execution_time

router = APIRouter()
 
@router.post("/register")
@log_execution_time
async def register_user(request: UserRegister):
    return await register_user_service(request)

@router.post("/login")
@log_execution_time
async def login(request: LoginRequest):
    return await login_user_service(request)


@router.put("/change-contact")
@log_execution_time
async def change_contact(request: ChangeContactRequest,current_user: dict = Depends(get_current_user)):
    return await change_user_contact_service(current_user["user_id"], request)


@router.post("/change-password")
@log_execution_time
async def change_password(request: ChangePasswordRequest,current_user: dict = Depends(get_current_user)):
    return await change_password_service(current_user["user_id"], request)

@router.post("/forgot-password")
@log_execution_time
def forgot_password(request: ForgotPasswordRequest):
    return forgot_password_service(request)