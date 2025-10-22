from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.auth.dependencies import get_current_active_user, require_admin
from app.schemas.service import ServiceResponse, ServiceCreate, ServiceUpdate
from app.services.service import ServiceService

router = APIRouter(prefix="/services", tags=["services"])

@router.get("/", response_model=list[ServiceResponse])
async def get_services(
    q: Optional[str] = Query(None),
    price_min: Optional[float] = Query(None),
    price_max: Optional[float] = Query(None),
    active: bool = Query(True),
    db: AsyncSession = Depends(get_db)
):
    service_service = ServiceService(db)
    return await service_service.search_services(q, price_min, price_max, active)

@router.get("/{service_id}", response_model=ServiceResponse)
async def get_service(service_id: int, db: AsyncSession = Depends(get_db)):
    service_service = ServiceService(db)
    service = await service_service.get_service(service_id)
    return service

@router.post("/", response_model=ServiceResponse, status_code=201)
async def create_service(
    service_data: ServiceCreate,
    db: AsyncSession = Depends(get_db),
    admin_user = Depends(require_admin)
):
    service_service = ServiceService(db)
    return await service_service.create_service(service_data)

@router.patch("/{service_id}", response_model=ServiceResponse)
async def update_service(
    service_id: int,
    service_update: ServiceUpdate,
    db: AsyncSession = Depends(get_db),
    admin_user = Depends(require_admin)
):
    service_service = ServiceService(db)
    return await service_service.update_service(service_id, service_update)

@router.delete("/{service_id}")
async def delete_service(
    service_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user = Depends(require_admin)
):
    service_service = ServiceService(db)
    await service_service.delete_service(service_id)
    return {"message": "Service deleted successfully"}