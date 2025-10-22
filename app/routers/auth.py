from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.auth import UserLogin, UserRegister, Token, RefreshToken
from app.services.auth import AuthService
from app.auth.jwt import verify_token, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):

    auth_service = AuthService(db)
    try:
        user = await auth_service.register(user_data)
        # Auto-login after registration
        return await auth_service.login(UserLogin(
            email=user_data.email, 
            password=user_data.password
        ))
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed due to server error"
        )

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Authenticate user and return JWT tokens.
    """
    auth_service = AuthService(db)
    return await auth_service.login(credentials)

@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_data: RefreshToken, db: AsyncSession = Depends(get_db)):
    """
    Refresh access token using refresh token.
    """
    token_data = verify_token(refresh_data.refresh_token)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Create new access token
    new_access_token = create_access_token({
        "user_id": token_data.user_id,
        "email": token_data.email,
        "role": token_data.role
    })
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "refresh_token": refresh_data.refresh_token
    }

@router.post("/logout")
async def logout(response: Response):
    """
    Logout user (client should discard tokens).
    """
    response.delete_cookie("access_token")
    return {"message": "Successfully logged out"}