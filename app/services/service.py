from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.service import ServiceRepository
from app.schemas.service import ServiceCreate, ServiceUpdate

class ServiceService:
    def __init__(self, db: AsyncSession):
        self.service_repo = ServiceRepository(db)

    async def get_service(self, service_id: int):
        service = await self.service_repo.get_by_id(service_id)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found"
            )
        return service

    async def search_services(self, query: str = None, min_price: float = None, max_price: float = None, active: bool = True):
        return await self.service_repo.search_services(query, min_price, max_price, active)

    async def create_service(self, service_data: ServiceCreate):
        return await self.service_repo.create(service_data)

    async def update_service(self, service_id: int, service_update: ServiceUpdate):
        service = await self.get_service(service_id)
        return await self.service_repo.update(service_id, service_update)

    async def delete_service(self, service_id: int):
        service = await self.get_service(service_id)
        await self.service_repo.delete(service_id)
        return True