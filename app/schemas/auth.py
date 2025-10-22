from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserRole

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str

class TokenData(BaseModel):
    user_id: int
    email: str
    role: str

class RefreshToken(BaseModel):
    refresh_token: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password cannot be empty")

class UserRegister(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Name must be between 1-100 characters")
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=72, description="Password must be 6-72 characters")
    role: UserRole = UserRole.USER