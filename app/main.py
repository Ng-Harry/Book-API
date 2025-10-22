from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.config import settings
from app.routers import auth, users, services, bookings, reviews

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_PREFIX}/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(users.router, prefix=settings.API_PREFIX)
app.include_router(services.router, prefix=settings.API_PREFIX)
app.include_router(bookings.router, prefix=settings.API_PREFIX)
app.include_router(reviews.router, prefix=settings.API_PREFIX)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up BookIt API...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down BookIt API...")

@app.get("/")
async def root():
    return {"message": "Welcome to BookIt API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}