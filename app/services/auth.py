from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import uuid4
from app.models.user import User
from app.utils.firebase import verify_firebase_token
from app.utils.jwt import create_access_token
from app.utils.password import hash_password, verify_password


# ── Google login/register — users only ──────────────────────
def google_auth_service(token: str, db: Session) -> dict:
    try:
        firebase_user = verify_firebase_token(token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    uid = firebase_user["uid"]
    email = firebase_user.get("email")
    name = firebase_user.get("name")
    avatar = firebase_user.get("picture")

    user = db.query(User).filter(User.uid == uid).first()

    if not user:
        user = User(
            uid=uid,
            email=email,
            name=name,
            avatar=avatar,
            roles=["user"]       # default role
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user.name = name
        user.avatar = avatar
        db.commit()
        db.refresh(user)

    access_token = create_access_token({
        "sub": user.uid,
        "email": user.email,
        "roles": user.roles,     # e.g. ["user"] or ["user", "admin"]
    })

    return {"access_token": access_token, "token_type": "bearer", "user": user}


# ── Admin register ───────────────────────────────────────────
def admin_register_service(email: str, password: str, name: str, db: Session) -> dict:
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        uid=str(uuid4()),
        email=email,
        name=name,
        hashed_password=hash_password(password),
        roles=["user"]           # starts as user — you add "admin" in pgAdmin
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "Account created. Ask admin to upgrade your role in database."}


# ── Admin login ──────────────────────────────────────────────
def admin_login_service(email: str, password: str, db: Session) -> dict:
    user = db.query(User).filter(User.email == email).first()

    if not user or not user.hashed_password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if "admin" not in user.roles:
        raise HTTPException(status_code=403, detail="You don't have admin access yet")

    access_token = create_access_token({
        "sub": user.uid,
        "email": user.email,
        "roles": user.roles,
    })

    return {"access_token": access_token, "token_type": "bearer", "user": user}