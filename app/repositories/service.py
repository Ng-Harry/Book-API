from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.service import Service
from app.schemas.service import ServiceCreate, ServiceUpdate
from app.repositories.base import BaseRepository

class ServiceRepository(BaseRepository[Service, ServiceCreate, ServiceUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(Service, db)

    async def get_active_services(self, skip: int = 0, limit: int = 100):
        result = await self.db.execute(
            select(Service).where(Service.is_active == True).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def search_services(self, query: str = None, min_price: float = None, max_price: float = None, active: bool = True):
        stmt = select(Service)
        
        if active:
            stmt = stmt.where(Service.is_active == True)
        
        if query:
            stmt = stmt.where(Service.title.ilike(f"%{query}%"))
        
        if min_price is not None:
            stmt = stmt.where(Service.price >= min_price)
        
        if max_price is not None:
            stmt = stmt.where(Service.price <= max_price)
        
        result = await self.db.execute(stmt)
        return result.scalars().all()