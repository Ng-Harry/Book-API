from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional

from app.database import get_db
from app.auth.dependencies import get_current_active_user, require_admin
from app.schemas.booking import BookingResponse, BookingWithServiceResponse, BookingCreate, BookingUpdate
from app.services.booking import BookingService

router = APIRouter(prefix="/bookings", tags=["bookings"])

@router.post("/", response_model=BookingWithServiceResponse, status_code=201)
async def create_booking(
    booking_data: BookingCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    booking_service = BookingService(db)
    booking = await booking_service.create_booking(current_user.id, booking_data)
    # Return booking with service details
    return await booking_service.get_booking_with_service(booking.id)

@router.get("/", response_model=list[BookingWithServiceResponse])
async def get_bookings(
    status: Optional[str] = Query(None),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    booking_service = BookingService(db)
    
    if current_user.role == "admin":
        return await booking_service.get_all_bookings_with_filters(status, from_date, to_date)
    else:
        return await booking_service.get_user_bookings(current_user.id)

@router.get("/{booking_id}", response_model=BookingWithServiceResponse)
async def get_booking(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    booking_service = BookingService(db)
    booking_with_service = await booking_service.get_booking_with_service(booking_id)
    
    # Check permissions
    if current_user.role != "admin" and booking_with_service.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this booking"
        )
    
    return booking_with_service

@router.patch("/{booking_id}", response_model=BookingWithServiceResponse)
async def update_booking(
    booking_id: int,
    booking_update: BookingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    booking_service = BookingService(db)
    updated_booking = await booking_service.update_booking(booking_id, booking_update, current_user)
    return await booking_service.get_booking_with_service(booking_id)

@router.delete("/{booking_id}")
async def delete_booking(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    booking_service = BookingService(db)
    await booking_service.cancel_booking(booking_id, current_user.id, current_user.role == "admin")
    return {"message": "Booking cancelled successfully"}