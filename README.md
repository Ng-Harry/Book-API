# 📘 BookIt API

**BookIt API** is a production-ready REST API for a simple bookings platform.  
It allows users to browse services, make bookings, and leave reviews — while admins manage users, services, and bookings.

---

## Live Demo

- **Base URL:** https://book-i6m3zit5i-ngharrys-projects.vercel.app/
- **Host:** vercel.com
- **Docs:** https://book-i6m3zit5i-ngharrys-projects.vercel.app/docs
 *(Auto-generated via FastAPI Swagger UI)*

---

## Core Features

- **User Authentication & Authorization** using JWT (access & refresh tokens)
- **Role-based access control** (`user` & `admin`)
- **Bookings management** with conflict validation
- **Service management** (CRUD for admins)
- **User reviews** linked to completed bookings
- **Structured logging** and production-ready configuration
- **Deployed on Render** with environment-based configuration

---

## Core Entities

| Entity  | Fields |
|----------|--------|
| **User** | id, name, email, password_hash, role (`user` \| `admin`), created_at |
| **Service** | id, title, description, price, duration_minutes, is_active, created_at |
| **Booking** | id, user_id, service_id, start_time, end_time, status (`pending` \| `confirmed` \| `cancelled` \| `completed`), created_at |
| **Review** | id, booking_id, rating (1–5), comment, created_at |

---

## Architectural Decisions

**Chosen Database:** **PostgreSQL**
- Structured Data: Bookings data has clear relationships perfect for relational models
- ACID Compliance: Essential for preventing double-booking conflicts
- Complex Queries: Advanced filtering and date range operations
- Data Consistency: Strong schema enforcement
- SQLAlchemy Integration: Excellent async support

---

## Running Locally

### Clone the repository
```bash
git https://github.com/Ng-Harry/Book-API.git

cd bookit-api
```

## Create and activate virtual environment

```bash 
python -m venv venv

source venv/bin/activate  # activate env for macOS/Linux

venv\Scripts\activate     # activate env for Windows
```


## Environment Variables

| Variable | Description | Example |
|-----------|--------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://user:pass@host:port/dbname` |
| `JWT_SECRET_KEY` | Secret key for signing JWT tokens | `supersecretkey` |
| `JWT_REFRESH_SECRET_KEY` | Secret key for refresh tokens | `anothersecretkey` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT expiry time in minutes | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifespan | `7` |
| `ENV` | Environment (dev/prod) | `production` |
| `LOG_LEVEL` | Logging verbosity | `info` |

*(Use `.env` locally and Render Environment Variables in production)*

---

## Install dependencies

```bash 
pip install -r requirements.txt
```

## Start the server

```bash 
uvicorn app.main:app --reload
```