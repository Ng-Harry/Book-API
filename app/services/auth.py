from datetime import timedelta
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user import UserRepository
from app.schemas.auth import UserLogin, UserRegister
from app.utils.security import verify_password, get_password_hash
from app.auth.jwt import create_access_token, create_refresh_token

class AuthService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)

    async def register(self, user_data: UserRegister):
        # Check if user already exists
        existing_user = await self.user_repo.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Hash password
        hashed_password = get_password_hash(user_data.password)
        
        # Create user
        user_dict = user_data.dict()
        user_dict["password_hash"] = hashed_password
        del user_dict["password"]
        
        user = await self.user_repo.create(user_dict)
        return user

    async def login(self, credentials: UserLogin):
        user = await self.user_repo.get_by_email(credentials.email)
        if not user or not verify_password(credentials.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        # Create tokens
        token_data = {
            "user_id": user.id,
            "email": user.email,
            "role": user.role
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "refresh_token": refresh_token
        }