from fastapi import Depends, HTTPException, status
from app.dependencies.auth import get_current_user
from app.models.user import User


def require_roles(*allowed_roles: str):
    """Dependency to check if user has one of the allowed roles."""
    def checker(user: User = Depends(get_current_user)):
        user_roles = set(user.roles or [])
        if not user_roles.intersection(set(allowed_roles)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied"
            )
        return user
    return checker


# Role-specific dependencies
require_admin = require_roles("admin")
require_teacher = require_roles("teacher", "admin")  # Teachers and admins
require_student = require_roles("student", "teacher", "admin")  # Students, teachers, and admins
require_authenticated = Depends(get_current_user)  # Any authenticated user

# Combined role checkers
require_teacher_or_admin = require_roles("teacher", "admin")
require_instructor = require_roles("teacher", "admin")  # Alias for require_teacher_or_admin