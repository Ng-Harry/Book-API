from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.review import ReviewRepository
from app.repositories.booking import BookingRepository
from app.schemas.review import ReviewCreate, ReviewUpdate
from app.models.booking import BookingStatus

class ReviewService:
    def __init__(self, db: AsyncSession):
        self.review_repo = ReviewRepository(db)
        self.booking_repo = BookingRepository(db)

    async def create_review(self, user_id: int, review_data: ReviewCreate):
        # Get booking
        booking = await self.booking_repo.get_by_id(review_data.booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )

        # Check if user owns the booking
        if booking.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to review this booking"
            )

        # Check if booking is completed
        if booking.status != BookingStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only review completed bookings"
            )

        # Check if review already exists
        existing_review = await self.review_repo.get_by_booking_id(review_data.booking_id)
        if existing_review:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Review already exists for this booking"
            )

        return await self.review_repo.create(review_data)

    async def get_service_reviews(self, service_id: int, skip: int = 0, limit: int = 100):
        return await self.review_repo.get_service_reviews(service_id, skip, limit)

    async def update_review(self, review_id: int, user_id: int, review_update: ReviewUpdate):
        review = await self.review_repo.get_by_id(review_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )

        # Check if user owns the review
        booking = await self.booking_repo.get_by_id(review.booking_id)
        if booking.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this review"
            )

        return await self.review_repo.update(review_id, review_update)

    async def delete_review(self, review_id: int, user_id: int, is_admin: bool = False):
        review = await self.review_repo.get_by_id(review_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )

        # Check permissions
        booking = await self.booking_repo.get_by_id(review.booking_id)
        if not is_admin and booking.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this review"
            )

        await self.review_repo.delete(review_id)
        return True