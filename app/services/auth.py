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

