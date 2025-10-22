from datetime import timedelta
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.booking import BookingRepository
from app.repositories.service import ServiceRepository
from app.schemas.booking import BookingCreate, BookingUpdate
from app.models.booking import BookingStatus

class BookingService:
    def __init__(self, db: AsyncSession):
        self.booking_repo = BookingRepository(db)
        self.service_repo = ServiceRepository(db)

    async def create_booking(self, user_id: int, booking_data: BookingCreate):
        # Get service
        service = await self.service_repo.get_by_id(booking_data.service_id)
        if not service or not service.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found or inactive"
            )

        # Calculate end time
        end_time = booking_data.start_time + timedelta(minutes=service.duration_minutes)

        # Check for conflicts
        has_conflict = await self.booking_repo.check_booking_conflict(
            booking_data.service_id, booking_data.start_time, end_time
        )
        
        if has_conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Booking time conflicts with existing booking"
            )

        # Create booking
        booking_dict = booking_data.dict()
        booking_dict["user_id"] = user_id
        booking_dict["end_time"] = end_time
        
        booking = await self.booking_repo.create(booking_dict)
        return booking

    async def get_booking(self, booking_id: int):
        booking = await self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        return booking

    async def get_user_bookings(self, user_id: int):
        return await self.booking_repo.get_user_bookings(user_id)

    async def get_all_bookings_with_filters(self, status: str = None, from_date: str = None, to_date: str = None):
        return await self.booking_repo.get_bookings_with_filters(status, from_date, to_date)

    async def update_booking(self, booking_id: int, booking_update: BookingUpdate, current_user):
        booking = await self.get_booking(booking_id)
        
        # Check permissions
        if current_user.role != "admin" and booking.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this booking"
            )

        # If updating start_time, check for conflicts
        if booking_update.start_time:
            service = await self.service_repo.get_by_id(booking.service_id)
            new_end_time = booking_update.start_time + timedelta(minutes=service.duration_minutes)
            
            has_conflict = await self.booking_repo.check_booking_conflict(
                booking.service_id, booking_update.start_time, new_end_time, booking_id
            )
            
            if has_conflict:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="New booking time conflicts with existing booking"
                )
            
            booking_update_dict = booking_update.dict(exclude_unset=True)
            booking_update_dict["end_time"] = new_end_time
            booking_update = BookingUpdate(**booking_update_dict)

        return await self.booking_repo.update(booking_id, booking_update)

    async def cancel_booking(self, booking_id: int, user_id: int, is_admin: bool = False):
        booking = await self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )

        # Check permissions
        if not is_admin and booking.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to cancel this booking"
            )

        # Check if booking can be cancelled
        if booking.status not in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Booking cannot be cancelled in its current status"
            )

        # Update status
        updated_booking = await self.booking_repo.update(
            booking_id, {"status": BookingStatus.CANCELLED}
        )
        
        return updated_booking