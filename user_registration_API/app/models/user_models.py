from pydantic import BaseModel,Field,EmailStr
from datetime import date



class UserRegister(BaseModel):
    email: EmailStr
    mobile: str
    first_name: str
    last_name: str
    dob: str
    doj: str
    address: str
    password: str = Field(min_length=8, max_length=20)
    active: bool


