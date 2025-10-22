from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewUpdate
from app.repositories.base import BaseRepository

class ReviewRepository(BaseRepository[Review, ReviewCreate, ReviewUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(Review, db)

    async def get_by_booking_id(self, booking_id: int):
        result = await self.db.execute(select(Review).where(Review.booking_id == booking_id))
        return result.scalar_one_or_none()

    async def get_service_reviews(self, service_id: int, skip: int = 0, limit: int = 100):
        from app.models.booking import Booking
        result = await self.db.execute(
            select(Review)
            .join(Booking, Review.booking_id == Booking.id)
            .where(Booking.service_id == service_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()