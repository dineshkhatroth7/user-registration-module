
from app.models.user_models import UserRegister,LoginRequest,ChangeContactRequest,ChangePasswordRequest
from app.db.mongo import users_collection
from app.utils.logger import logger  
from app.utils.exceptions import UserAlreadyExistsException,InvalidCredentialsException,SamePasswordException,IncorrectOldPasswordException,PasswordExpiredException
from datetime import datetime,timezone
from passlib.context import CryptContext
from app.utils.jwt_handler import create_jwt_token
from bson import ObjectId
from app.utils.password import hash_password,verify_password,pwd_context,is_password_expired


async def register_user_service(request: UserRegister):
    request.email = request.email.lower().strip()
    request.mobile = request.mobile.strip()
    logger.info(f"Received registration request for {request.email},{request.mobile}")

    existing_user =await users_collection.find_one({
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
    await users_collection.insert_one(user_data)

    logger.info(f"User {request.email},{request.mobile} registered successfully.")
    return {"message": " User registered successfully"}


async def login_user_service(request:LoginRequest):

    username = request.username.strip().lower() if "@" in request.username else request.username.strip()
    key = "email" if "@" in request.username else "mobile"

    user =  await users_collection.find_one({key: username})

    if not user:
        logger.warning(f"Login failed: {username} not found.")
        raise InvalidCredentialsException()
    
    if not pwd_context.verify(request.password, user["password"]):
        logger.warning(f"Login failed: Incorrect password for {username}")
        raise InvalidCredentialsException()
    
    if is_password_expired(user.get("password_last_changed")):
        logger.warning(f"Password expired for {username}")
        raise PasswordExpiredException()
    
    payload = {
        "sub": str(user["_id"]),
        "email": user["email"],
        "mobile": user["mobile"]
    }
    token = create_jwt_token(payload)

    logger.info(f"User {username} logged in successfully.")
    return {"message": "Login successful",
            "access_token": token,
             "token_type": "bearer"
             }


async def change_user_contact_service(user_id: str, request: ChangeContactRequest):
    logger.info(f"User {user_id} requested contact update")

    updates = {}

    if request.email:
        email = request.email.strip().lower()
        logger.info(f"Checking for existing email: {email}")
        email_exists = await users_collection.find_one({
            "_id": {"$ne": ObjectId(user_id)},
            "email":email
        })

        if email_exists:
            logger.warning(f"Email {email} already in use by another user")
            raise UserAlreadyExistsException()
        updates["email"] = email

    if request.mobile:
        mobile = request.mobile.strip()
        logger.info(f"Checking for existing mobile: {mobile}")
        mobile_exists = await users_collection.find_one({
            "_id": {"$ne": ObjectId(user_id)},
            "mobile": mobile
        })

        if mobile_exists:
            logger.warning(f"Mobile {mobile} already in use by another user")
            raise UserAlreadyExistsException()
        updates["mobile"] = mobile

    await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": updates}
    )
    logger.info(f"User {user_id} updated contact: {updates}")
    return {"message": "Contact updated successfully"}



async def change_password_service(user_id:str,request:ChangePasswordRequest):
    logger.info(f"Password change request received for user_id: {user_id}")
    user=await users_collection.find_one({"_id":ObjectId(user_id)})

    if not user:
        logger.error(f"User with ID {user_id} not found.")
        raise InvalidCredentialsException()

    if not verify_password(request.old_password,user["password"]):
        logger.warning(f"Incorrect old password for user_id: {user_id}")
        raise IncorrectOldPasswordException()
    
    previous_hashes = user.get("password_history", []) + [user["password"]]

    for old_hash in previous_hashes:
        if verify_password(request.new_password, old_hash):
            logger.warning(f"Password reuse attempt for user_id: {user_id}")
            raise SamePasswordException()
   
    new_hashed = hash_password(request.new_password)

    updated_history = previous_hashes[-2:]  
    updated_history.append(user["password"])

    await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {
            "password": new_hashed,
            "password_history": updated_history,
            "password_last_changed": datetime.now(timezone.utc)
        }}
    )
    logger.info(f"Password changed successfully for user_id: {user_id}")
    return {"message": "Password changed successfully"}