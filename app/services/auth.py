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
        """
        Register a new user with proper password validation and hashing.
        Supports both user and admin roles.
        """
        # Additional password length check (though schema should handle this)
        if len(user_data.password) > 72:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password cannot exceed 72 characters"
            )

        # Check if user already exists
        existing_user = await self.user_repo.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Hash password with error handling
        try:
            hashed_password = get_password_hash(user_data.password)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error processing password"
            )
        
        # Create user data as dictionary including role
        user_dict = {
            "name": user_data.name,
            "email": user_data.email,
            "password_hash": hashed_password,
            "role": user_data.role.value
        }
        
        try:
            user = await self.user_repo.create(user_dict)
            return user
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating user account"
            )

    async def login(self, credentials: UserLogin):
        """
        Authenticate user and return JWT tokens.
        """
        user = await self.user_repo.get_by_email(credentials.email)
        if not user:
            # Don't reveal whether user exists
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        # Verify password with error handling
        try:
            password_valid = verify_password(credentials.password, user.password_hash)
        except Exception as e:
            print(f"Password verification error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication error"
            )

        if not password_valid:
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