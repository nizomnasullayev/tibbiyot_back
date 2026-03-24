from pydantic import BaseModel

class GoogleLoginSchema(BaseModel):
    """Schema for Google OAuth login"""
    id_token: str  # Token from Google (from frontend)


class GoogleLoginResponse(BaseModel):
    """Response with JWT tokens"""
    access_token: str
    refresh_token: str
    token_type: str
    user: dict