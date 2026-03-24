from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import BaseModel

from app.core.database import get_db
from app.core.config import settings
from app.core.jwt import create_token, decode_token
from app.core.security import hash_password, verify_password
from app.service.user_service import authenticate_user, save_refresh_token_hash
from app.models.user import User
from app.dependencies.auth import get_current_user

import os

router = APIRouter(prefix="/auth", tags=["Auth"])

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

try:
    from google.oauth2 import id_token
    from google.auth.transport import requests
    GOOGLE_AUTH_INSTALLED = True
except ImportError:
    id_token = None
    requests = None
    GOOGLE_AUTH_INSTALLED = False


class LoginSchema(BaseModel):
    email: str
    password: str


class RefreshSchema(BaseModel):
    refresh_token: str


class GoogleLoginSchema(BaseModel):
    id_token: str


class GoogleLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: dict


@router.post("/login")
def login(data: LoginSchema, db: Session = Depends(get_db)):
    user = authenticate_user(db, data.email, data.password)

    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token = create_token(
        payload={"sub": str(user.id), "type": "access", "roles": user.roles},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    refresh_token = create_token(
        payload={"sub": str(user.id), "type": "refresh"},
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )

    save_refresh_token_hash(db, user, hash_password(refresh_token))

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh")
def refresh_token(data: RefreshSchema, db: Session = Depends(get_db)):
    payload = decode_token(data.refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Not a refresh token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    if not user.refresh_token_hash or not verify_password(data.refresh_token, user.refresh_token_hash):
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    access_token = create_token(
        payload={"sub": str(user.id), "type": "access"},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    save_refresh_token_hash(db, current_user, "")
    return {"msg": "Successfully logged out"}


# ==================== Google OAuth ====================

@router.post("/google-login", response_model=GoogleLoginResponse)
def google_login(data: GoogleLoginSchema, db: Session = Depends(get_db)):
    """
    Google OAuth login endpoint.

    Frontend sends: {"id_token": "..."}
    Backend returns: JWT tokens + user info
    """
    try:
        if not GOOGLE_AUTH_INSTALLED:
            raise HTTPException(
                status_code=503,
                detail="Google login requires google-auth to be installed",
            )

        # Verify Google token
        if not GOOGLE_CLIENT_ID:
            raise HTTPException(
                status_code=500,
                detail="Google Client ID not configured"
            )

        print(f"🔐 Verifying Google token...")
        idinfo = id_token.verify_oauth2_token(
            data.id_token,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )

        email = idinfo.get("email")
        name = idinfo.get("name", "User")
        picture = idinfo.get("picture")

        if not email:
            raise HTTPException(
                status_code=400,
                detail="Google token missing email"
            )

        print(f"✅ Token verified. Email: {email}")

        # Check if user exists
        user = db.query(User).filter(User.email == email).first()

        if not user:
            # Create new user from Google info
            username = email.split("@")[0]

            # Make username unique if it already exists
            base_username = username
            counter = 1
            while db.query(User).filter(User.username == username).first():
                username = f"{base_username}{counter}"
                counter += 1

            print(f"👤 Creating new user: {email} with username: {username}")

            user = User(
                email=email,
                username=username,
                hashed_password=hash_password("oauth_user"),  # OAuth users don't have passwords
                roles=["teacher"],
                avatar=picture,
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            print(f"✅ New user created")
        else:
            print(f"👤 Existing user found: {email}")

        # Generate JWT tokens
        access_token = create_token(
            payload={"sub": str(user.id), "type": "access", "roles": user.roles},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        refresh_token = create_token(
            payload={"sub": str(user.id), "type": "refresh"},
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )

        # Save refresh token hash
        save_refresh_token_hash(db, user, hash_password(refresh_token))

        print(f"✅ JWT tokens created")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "avatar": user.avatar,
                "roles": user.roles,
            }
        }

    except ValueError as e:
        print(f"❌ Invalid Google token: {e}")
        raise HTTPException(
            status_code=401,
            detail="Invalid Google token"
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in Google OAuth: {e}")
        raise HTTPException(
            status_code=500,
            detail="Google login failed"
        )
