from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user import UserRepository
from app.schemas.user import UserUpdate
from app.utils.security import get_password_hash

class UserService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)

    async def update_user(self, user_id: int, user_update: UserUpdate):
        update_data = user_update.dict(exclude_unset=True)
        
        # Hash password if it's being updated
        if 'password' in update_data:
            update_data['password_hash'] = get_password_hash(update_data.pop('password'))
        
        return await self.user_repo.update(user_id, update_data)