from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.topic import (
    TopicCreate, TopicUpdate, TopicResponse,
    SectionCreate, SectionUpdate, SectionResponse,
    EntryCreate, EntryUpdate, EntryResponse,
)
from app.services import topic as service

router = APIRouter(prefix="/topics", tags=["Topics"])


# ── Topics ───────────────────────────────────────────────────
@router.get("/", response_model=list[TopicResponse])
def list_topics(db: Session = Depends(get_db)):
    return service.get_all_topics(db)

@router.get("/{uid}", response_model=TopicResponse)
def get_topic(uid: str, db: Session = Depends(get_db)):
    return service.get_topic(uid, db)

@router.post("/", response_model=TopicResponse)
def create_topic(data: TopicCreate, db: Session = Depends(get_db)):
    return service.create_topic(data, db)

@router.put("/{uid}", response_model=TopicResponse)
def update_topic(uid: str, data: TopicUpdate, db: Session = Depends(get_db)):
    return service.update_topic(uid, data, db)

@router.delete("/{uid}")
def delete_topic(uid: str, db: Session = Depends(get_db)):
    return service.delete_topic(uid, db)


# ── Sections ─────────────────────────────────────────────────
@router.post("/{topic_uid}/sections", response_model=SectionResponse)
def create_section(topic_uid: str, data: SectionCreate, db: Session = Depends(get_db)):
    return service.create_section(topic_uid, data, db)

@router.put("/sections/{uid}", response_model=SectionResponse)
def update_section(uid: str, data: SectionUpdate, db: Session = Depends(get_db)):
    return service.update_section(uid, data, db)

@router.delete("/sections/{uid}")
def delete_section(uid: str, db: Session = Depends(get_db)):
    return service.delete_section(uid, db)


# ── Entries ──────────────────────────────────────────────────
@router.post("/{topic_uid}/entries", response_model=EntryResponse)
def create_entry_in_topic(topic_uid: str, data: EntryCreate, db: Session = Depends(get_db)):
    return service.create_entry_in_topic(topic_uid, data, db)

@router.post("/sections/{section_uid}/entries", response_model=EntryResponse)
def create_entry_in_section(section_uid: str, data: EntryCreate, db: Session = Depends(get_db)):
    return service.create_entry_in_section(section_uid, data, db)

@router.put("/entries/{uid}", response_model=EntryResponse)
def update_entry(uid: str, data: EntryUpdate, db: Session = Depends(get_db)):
    return service.update_entry(uid, data, db)

@router.delete("/entries/{uid}")
def delete_entry(uid: str, db: Session = Depends(get_db)):
    return service.delete_entry(uid, db)