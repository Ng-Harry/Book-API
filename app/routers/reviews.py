from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth.dependencies import get_current_active_user, require_admin
from app.schemas.review import ReviewResponse, ReviewCreate, ReviewUpdate
from app.services.review import ReviewService

router = APIRouter(prefix="/reviews", tags=["reviews"])

@router.post("/", response_model=ReviewResponse, status_code=201)
async def create_review(
    review_data: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    review_service = ReviewService(db)
    return await review_service.create_review(current_user.id, review_data)

@router.get("/services/{service_id}/reviews", response_model=list[ReviewResponse])
async def get_service_reviews(
    service_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    review_service = ReviewService(db)
    return await review_service.get_service_reviews(service_id, skip, limit)

@router.patch("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: int,
    review_update: ReviewUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    review_service = ReviewService(db)
    return await review_service.update_review(review_id, current_user.id, review_update)

@router.delete("/{review_id}")
async def delete_review(
    review_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    review_service = ReviewService(db)
    await review_service.delete_review(review_id, current_user.id, current_user.role == "admin")
    return {"message": "Review deleted successfully"}