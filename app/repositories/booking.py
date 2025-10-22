from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_
from datetime import datetime
from app.models.booking import Booking
from app.models.service import Service
from app.schemas.booking import BookingCreate, BookingUpdate
from app.repositories.base import BaseRepository

class BookingRepository(BaseRepository[Booking, BookingCreate, BookingUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(Booking, db)

    async def get_user_bookings(self, user_id: int, skip: int = 0, limit: int = 100):
        result = await self.db.execute(
            select(Booking).where(Booking.user_id == user_id).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def get_bookings_with_filters(self, status: str = None, from_date: datetime = None, to_date: datetime = None):
        stmt = select(Booking)
        
        if status:
            stmt = stmt.where(Booking.status == status)
        
        if from_date:
            stmt = stmt.where(Booking.start_time >= from_date)
        
        if to_date:
            stmt = stmt.where(Booking.start_time <= to_date)
        
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_booking_with_service(self, booking_id: int):
        """Get booking with service details"""
        result = await self.db.execute(
            select(Booking, Service)
            .join(Service, Booking.service_id == Service.id)
            .where(Booking.id == booking_id)
        )
        return result.first()

    async def get_user_bookings_with_services(self, user_id: int, skip: int = 0, limit: int = 100):
        """Get user bookings with service details"""
        result = await self.db.execute(
            select(Booking, Service)
            .join(Service, Booking.service_id == Service.id)
            .where(Booking.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return result.all()

    async def get_all_bookings_with_services(self, status: str = None, from_date: datetime = None, to_date: datetime = None):
        """Get all bookings with service details (for admin)"""
        stmt = select(Booking, Service).join(Service, Booking.service_id == Service.id)
        
        if status:
            stmt = stmt.where(Booking.status == status)
        
        if from_date:
            stmt = stmt.where(Booking.start_time >= from_date)
        
        if to_date:
            stmt = stmt.where(Booking.start_time <= to_date)
        
        result = await self.db.execute(stmt)
        return result.all()

    async def check_booking_conflict(self, service_id: int, start_time: datetime, end_time: datetime, exclude_booking_id: int = None):
        stmt = select(Booking).where(
            and_(
                Booking.service_id == service_id,
                Booking.status.in_(["pending", "confirmed"]),
                or_(
                    and_(Booking.start_time <= start_time, Booking.end_time > start_time),
                    and_(Booking.start_time < end_time, Booking.end_time >= end_time),
                    and_(Booking.start_time >= start_time, Booking.end_time <= end_time)
                )
            )
        )
        
        if exclude_booking_id:
            stmt = stmt.where(Booking.id != exclude_booking_id)
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None