
from app.models.user_models import UserRegister,LoginRequest
from app.db.mongo import users_collection
from app.utils.logger import logger  
from app.utils.exceptions import UserAlreadyExistsException,InvalidCredentialsException
from datetime import datetime
from passlib.context import CryptContext
from app.utils.jwt_handler import create_jwt_token



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def register_user_service(request: UserRegister):
    logger.info(f"Received registration request for {request.email},{request.mobile}")

    existing_user = users_collection.find_one({
        "$or": [
            {"email": request.email},
            {"mobile": request.mobile}
        ]
    })

    if existing_user:
        logger.warning(f"Duplicate registration attempt: {request.email} or {request.mobile}")
        raise UserAlreadyExistsException()

    user_data = request.model_dump()
    user_data["password"] = pwd_context.hash(user_data["password"])
    user_data["dob"] = datetime.strptime(user_data["dob"], "%Y-%m-%d")
    user_data["doj"] = datetime.strptime(user_data["doj"], "%Y-%m-%d")
    users_collection.insert_one(user_data)

    logger.info(f"User {request.email},{request.mobile} registered successfully.")
    return {"message": " User registered successfully"}


def login_user_service(request:LoginRequest):

    key = "email" if "@" in request.username else "mobile"

    user = users_collection.find_one({key: request.username})

    if not user:
        logger.warning(f"Login failed: {request.username} not found.")
        raise InvalidCredentialsException()
    
    if not pwd_context.verify(request.password, user["password"]):
        logger.warning(f"Login failed: Incorrect password for {request.username}")
        raise InvalidCredentialsException()
    
    payload = {
        "sub": str(user["_id"]),
        "email": user["email"],
        "mobile": user["mobile"]
    }
    token = create_jwt_token(payload)


    
    return {"message": "Login successful",
            "access_token": token,
             "token_type": "bearer"
             }
