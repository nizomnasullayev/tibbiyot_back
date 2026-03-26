from fastapi import Depends, HTTPException
from app.models.user import User
from app.utils.jwt import get_current_user

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if "admin" not in current_user.roles:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

def require_user(current_user: User = Depends(get_current_user)) -> User:
    if "user" not in current_user.roles:
        raise HTTPException(status_code=403, detail="User access required")
    return current_user