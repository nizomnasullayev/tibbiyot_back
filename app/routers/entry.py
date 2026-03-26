from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.topic import EntryCreate, EntryUpdate, EntryResponse
from app.services import topic as service
from app.utils.dependencies import require_admin
from app.models.user import User

router = APIRouter(prefix="/entries", tags=["Entries"])

@router.get("/{uid}", response_model=EntryResponse)
def get_entry(uid: str, db: Session = Depends(get_db)):
    return service.get_entry(uid, db)

@router.post("/topic/{topic_uid}", response_model=EntryResponse)
def create_entry_in_topic(topic_uid: str, data: EntryCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return service.create_entry_in_topic(topic_uid, data, db)

@router.post("/section/{section_uid}", response_model=EntryResponse)
def create_entry_in_section(section_uid: str, data: EntryCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return service.create_entry_in_section(section_uid, data, db)

@router.put("/{uid}", response_model=EntryResponse)
def update_entry(uid: str, data: EntryUpdate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return service.update_entry(uid, data, db)

@router.delete("/{uid}")
def delete_entry(uid: str, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return service.delete_entry(uid, db)