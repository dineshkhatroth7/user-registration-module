import os
from datetime import datetime,timedelta,timezone
from jose import jwt


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_jwt_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc)  + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)