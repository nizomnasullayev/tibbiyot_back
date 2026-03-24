from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Annotated
from uuid import UUID
from enum import Enum

EmailField = Annotated[str, Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")]


class UserRole(str, Enum):
    teacher = "teacher"
    admin = "admin"


class UserCreate(BaseModel):
    email: EmailField
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=100)


class UserOut(BaseModel):
    id: UUID
    username: str
    email: EmailField
    roles: List[UserRole]
    is_active: bool
    avatar: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    email: Optional[EmailField] = None
    username: Optional[str] = None
    password: Optional[str] = Field(default=None, min_length=6, max_length=100)
    roles: Optional[List[UserRole]] = None


class UserRolesUpdate(BaseModel):
    roles: List[UserRole] = Field(min_length=1)
