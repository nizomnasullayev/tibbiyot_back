from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.jwt import get_current_user
from app.models.user import User
from app.schemas.progress import TestQuestion, TopicTestSubmit, FinalTestSubmit, TestResultResponse
from app.services import progress as service

router = APIRouter(prefix="/tests", tags=["Tests"])

@router.get("/topic/{topic_uid}", response_model=list[TestQuestion])
def get_topic_test(topic_uid: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return service.get_topic_test(current_user, topic_uid, db)

@router.post("/topic/submit", response_model=TestResultResponse)
def submit_topic_test(body: TopicTestSubmit, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return service.submit_topic_test(current_user, body.topic_uid, body.answers, db)

@router.get("/final", response_model=list[TestQuestion])
def get_final_test(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return service.get_final_test(current_user, db)

@router.post("/final/submit", response_model=TestResultResponse)
def submit_final_test(body: FinalTestSubmit, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return service.submit_final_test(current_user, body.answers, db)