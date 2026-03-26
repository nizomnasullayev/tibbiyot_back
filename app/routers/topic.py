from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.topic import TopicCreate, TopicUpdate, TopicResponse
from app.services import topic as service
from app.utils.jwt import get_current_user
from app.utils.dependencies import require_admin
from app.models.user import User

router = APIRouter(prefix="/topics", tags=["Topics"])

@router.get("/", response_model=list[TopicResponse])
def list_topics(db: Session = Depends(get_db)):
    return service.get_all_topics(db)

@router.get("/{uid}", response_model=TopicResponse)
def get_topic(uid: str, db: Session = Depends(get_db)):
    return service.get_topic(uid, db)

@router.post("/", response_model=TopicResponse)
def create_topic(data: TopicCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return service.create_topic(data, db)

@router.put("/{uid}", response_model=TopicResponse)
def update_topic(uid: str, data: TopicUpdate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return service.update_topic(uid, data, db)

@router.delete("/{uid}")
def delete_topic(uid: str, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return service.delete_topic(uid, db)