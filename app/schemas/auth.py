from pydantic import BaseModel, EmailStr

# ── Google (users) ──────────────────────
class GoogleTokenRequest(BaseModel):
    token: str

# ── Admin ────────────────────────────────
class AdminRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str

class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str

# ── Shared response ──────────────────────
class UserResponse(BaseModel):
    uid: str
    email: str
    name: str | None
    avatar: str | None
    roles: list[str]         # ["user"] or ["user", "admin"]

    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse