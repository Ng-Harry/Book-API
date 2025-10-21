from pydantic import BaseModel
from datetime import datetime
from app.models.booking import BookingStatus

class BookingBase(BaseModel):
    service_id: int
    start_time: datetime

class BookingCreate(BookingBase):
    pass

class BookingUpdate(BaseModel):
    start_time: datetime | None = None
    status: BookingStatus | None = None

class BookingResponse(BaseModel):
    id: int
    user_id: int
    service_id: int
    start_time: datetime
    end_time: datetime
    status: BookingStatus
    created_at: datetime

    class Config:
        from_attributes = True

class BookingWithDetails(BookingResponse):
    user_name: str
    service_title: str