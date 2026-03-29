from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.progress import FinalTestResult
from app.utils.dependencies import require_admin
from app.utils.jwt import get_current_user
from app.schemas.auth import UserResponse
from app.schemas.progress import AdminFinalTestResultResponse
from pydantic import BaseModel

router = APIRouter(prefix="/users", tags=["Users"])

class UpdateProfileRequest(BaseModel):
    first_name: str
    last_name: str
    father_name: str

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me/profile")
def update_profile(
    body: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    current_user.first_name = body.first_name
    current_user.last_name = body.last_name
    current_user.father_name = body.father_name
    db.commit()
    db.refresh(current_user)
    return {"message": "Profile updated successfully"}

@router.get("/final-results", response_model=list[AdminFinalTestResultResponse])
def get_final_results(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    rows = (
        db.query(FinalTestResult, User)
        .join(User, User.uid == FinalTestResult.user_uid)
        .order_by(FinalTestResult.completed_at.desc())
        .all()
    )

    return [
        {
            "uid": result.uid,
            "user_uid": user.uid,
            "full_name": user.name or user.email,
            "accuracy": result.accuracy,
            "score": result.score,
            "total": result.total,
            "passed": result.passed,
            "completed_at": result.completed_at,
        }
        for result, user in rows
    ]