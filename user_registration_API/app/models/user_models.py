from pydantic import BaseModel,Field,EmailStr,field_validator
import re



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


    @field_validator('mobile')
    def validate_mobile(cls,v):
      pattern=r'^[6-9]\d{9}$'
      if not re.fullmatch(pattern,v):
        raise ValueError("Mobile number must be a valid 10-digit number.")
      return v
    
    @field_validator('password')
    def validate_password_strength(cls, v):
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,20}$'
        if not re.fullmatch(pattern, v):
            raise ValueError("Password must include uppercase, lowercase, number, and special character.")
        return v
    
    @field_validator('email')
    def validate_email_domain(cls, v):
        v = v.lower()
        if not v.endswith(('gmail.com')):
            raise ValueError("Only gmail.com  domains are allowed.")
        return v
    


