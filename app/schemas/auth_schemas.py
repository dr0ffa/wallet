from pydantic import BaseModel, EmailStr, Field, ValidationInfo, field_validator, model_validator
from typing_extensions import Self
import re


class RegisterUserRequest(BaseModel):
    email: EmailStr
    username: str = Field(max_length=50)
    password: str = Field(min_length=5, exclude=True)
    repeat_password: str

    @field_validator("password")
    def validate_password(cls, v):
        if not re.search(r"\d", v):
            raise ValueError("Password must contain a digit")
        return v

    @model_validator(mode='after')
    def check_passwords_match(self) -> Self:
        if self.password != self.repeat_password: 
            raise ValueError('Passwords do not match')
        return self

class LoginUserRequest(BaseModel):
    email: EmailStr
    username: str = Field(max_length=50)
    password: str = Field(min_length=5, exclude=True)
    
class ConfirmMFARequest(BaseModel):
    otp: str