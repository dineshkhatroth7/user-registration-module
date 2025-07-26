
from fastapi import APIRouter,Depends
from app.models.user_models import UserRegister,LoginRequest,ChangeContactRequest
from app.services.user_service import register_user_service,login_user_service,change_user_contact_service
from app.utils.jwt_handler import get_current_user

router = APIRouter()
 
@router.post("/register")
def register_user(request: UserRegister):
    return register_user_service(request)

@router.post("/login")
def login(request: LoginRequest):
    return login_user_service(request)


@router.put("/change-contact")
def change_contact(request: ChangeContactRequest,current_user: dict = Depends(get_current_user)):
    return change_user_contact_service(current_user["user_id"], request)
