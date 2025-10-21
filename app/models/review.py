from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False, unique=True)
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    booking = relationship("Booking")