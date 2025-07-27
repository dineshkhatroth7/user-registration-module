
from app.models.user_models import UserRegister,LoginRequest,ChangeContactRequest,ChangePasswordRequest
from app.db.mongo import users_collection
from app.utils.logger import logger  
from app.utils.exceptions import UserAlreadyExistsException,InvalidCredentialsException,SamePasswordException,IncorrectOldPasswordException
from datetime import datetime,timezone
from passlib.context import CryptContext
from app.utils.jwt_handler import create_jwt_token
from bson import ObjectId
from app.utils.password import hash_password,verify_password,pwd_context


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
    hashed_password = pwd_context.hash(user_data.pop("password"))
    user_data["password"] = hashed_password
    user_data["dob"] = datetime.strptime(user_data["dob"], "%Y-%m-%d")
    user_data["doj"] = datetime.strptime(user_data["doj"], "%Y-%m-%d")
    user_data["password_history"] = []  
    user_data["password_last_changed"] = datetime.now(timezone.utc)
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


def change_user_contact_service(user_id: str, request: ChangeContactRequest):

    logger.info(f"User {user_id} requested contact update")

    updates = {}

    if request.email:
        logger.info(f"Checking for existing email: {request.email}")
        email_exists = users_collection.find_one({
            "_id": {"$ne": ObjectId(user_id)},
            "email": request.email
        })

    if email_exists:
        logger.warning(f"Email {request.email} already in use by another user")
        raise UserAlreadyExistsException()
        
    updates["email"] = request.email

    if request.mobile:
        logger.info(f"Checking for existing mobile: {request.mobile}")
        mobile_exists = users_collection.find_one({
            "_id": {"$ne": ObjectId(user_id)},
            "mobile": request.mobile
        })
    if mobile_exists:
        logger.warning(f"Mobile {request.mobile} already in use by another user")
        raise UserAlreadyExistsException()
    
    updates["mobile"] = request.mobile

    users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": updates}
    )

    logger.info(f"User {user_id} updated contact: {updates}")
    
    return {"message": "Contact updated successfully"}



def change_password_service(user_id:str,request:ChangePasswordRequest):
    user=users_collection.find_one({"_id":ObjectId(user_id)})

    if not verify_password(request.old_password,user["password"]):
        raise IncorrectOldPasswordException()
    
    previous_hashes = user.get("password_history", []) + [user["password"]]

    for old_hash in previous_hashes:
        if verify_password(request.new_password, old_hash):
            raise SamePasswordException()
   
    
    new_hashed = hash_password(request.new_password)

    updated_history = previous_hashes[-2:]  
    updated_history.append(user["password"])


    users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {
            "password": new_hashed,
            "password_history": updated_history,
            "password_last_changed": datetime.now(timezone.utc)
        }}
    )
    return {"message": "Password changed successfully"}