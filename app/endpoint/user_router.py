from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from uuid import uuid4
from pathlib import Path

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.roles import require_admin
from app.models.user import User
from app.schema.user_schema import UserCreate, UserOut, UserUpdate, UserRolesUpdate
from app.service import user_service

router = APIRouter(prefix="/users", tags=["Users"])

try:
    import multipart  # type: ignore # noqa: F401
    MULTIPART_INSTALLED = True
except ImportError:
    MULTIPART_INSTALLED = False

UPLOAD_DIR = Path("app/static/uploads/avatars")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

if MULTIPART_INSTALLED:
    @router.post("/me/avatar", response_model=UserOut)
    def upload_avatar(
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Only image files are allowed")

        ext = file.filename.split(".")[-1]
        filename = f"{uuid4()}.{ext}"
        file_path = UPLOAD_DIR / filename

        with open(file_path, "wb") as f:
            f.write(file.file.read())

        current_user.avatar = f"/static/uploads/avatars/{filename}"
        db.commit()
        db.refresh(current_user)

        return current_user
else:
    @router.post("/me/avatar", response_model=UserOut)
    def upload_avatar(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        raise HTTPException(
            status_code=503,
            detail="Avatar uploads require python-multipart to be installed",
        )

@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return user_service.create_user(db, user)


@router.get("/", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return user_service.get_users(db)


@router.get("/{user_id}", response_model=UserOut)
def get_user_by_id(
    user_id: UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    db_user = user_service.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return user_service.update_user(db, user_id, user_data)


@router.patch("/{user_id}/roles", response_model=UserOut)
def update_roles(
    user_id: UUID,
    role_data: UserRolesUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return user_service.update_user_roles(db, user_id, [role.value for role in role_data.roles])


@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    user_service.delete_user(db, user_id)
    return
