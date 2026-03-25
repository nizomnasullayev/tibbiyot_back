from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.auth import (
    GoogleTokenRequest,
    AdminRegisterRequest,
    AdminLoginRequest,
    LoginResponse
)
from app.services.auth import (
    google_auth_service,
    admin_register_service,
    admin_login_service
)
from app.database import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])


# ── Users ────────────────────────────────
@router.post("/google", response_model=LoginResponse)
async def google_login(body: GoogleTokenRequest, db: Session = Depends(get_db)):
    return google_auth_service(body.token, db)


# ── Admins ───────────────────────────────
@router.post("/admin/register")
async def admin_register(body: AdminRegisterRequest, db: Session = Depends(get_db)):
    return admin_register_service(body.email, body.password, body.name, db)

@router.post("/admin/login", response_model=LoginResponse)
async def admin_login(body: AdminLoginRequest, db: Session = Depends(get_db)):
    return admin_login_service(body.email, body.password, db)