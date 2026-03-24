from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests

from app.core.database import get_db
from app.models.user import User
from app.core.jwt import create_token, decode_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/google")
def google_login(data: dict, db: Session = Depends(get_db)):
    token = data.get("token")

    if not token:
        raise HTTPException(status_code=400, detail="Token missing")

    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )

        email = idinfo["email"]
        name = idinfo.get("name")
        picture = idinfo.get("picture")

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Google token")

    # Check if user exists
    user = db.query(User).filter(User.email == email).first()

    if not user:
        user = User(
            username=name.replace(" ", "").lower(),  # simple username
            email=email,
            hashed_password=None,
            roles=["teacher"],
            is_active=True,
            avatar=picture,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Activate user automatically if Google login
    if not user.is_active:
        user.is_active = True
        db.commit()

    access_token = create_token({
        "sub": str(user.id),
        "type": "access"
    })

    refresh_token = decode_token({
        "sub": str(user.id),
        "type": "refresh"
    })

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
