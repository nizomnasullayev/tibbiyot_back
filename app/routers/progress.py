from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.jwt import get_current_user
from app.models.user import User
from app.schemas.progress import UserProgressResponse, LearnEntryRequest
from app.services import progress as service

router = APIRouter(prefix="/progress", tags=["Progress"])

@router.get("/", response_model=list[UserProgressResponse])
def get_all_progress(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return service.get_all_progress(current_user, db)

@router.get("/{topic_uid}", response_model=UserProgressResponse)
def get_topic_progress(topic_uid: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return service.get_topic_progress(current_user, topic_uid, db)

@router.post("/{topic_uid}/learn", response_model=UserProgressResponse)
def learn_entry(topic_uid: str, body: LearnEntryRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return service.learn_entry(current_user, topic_uid, body.entry_uid, db)