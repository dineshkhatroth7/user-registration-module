from fastapi import HTTPException, status

class UserAlreadyExistsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or mobile already exists."
        )