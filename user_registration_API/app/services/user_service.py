
from app.models.user_models import UserRegister
from app.db.mongo import users_collection
from app.utils.logger import logger  
from app.utils.exceptions import UserAlreadyExistsException
from datetime import datetime

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
    user_data["dob"] = datetime.strptime(user_data["dob"], "%Y-%m-%d")
    user_data["doj"] = datetime.strptime(user_data["doj"], "%Y-%m-%d")
    users_collection.insert_one(user_data)

    logger.info(f"User {request.email},{request.mobile} registered successfully.")
    return {"message": " User registered successfully"}
