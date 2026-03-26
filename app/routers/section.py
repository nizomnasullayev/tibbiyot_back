from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.topic import SectionCreate, SectionUpdate, SectionResponse
from app.services import topic as service
from app.utils.dependencies import require_admin
from app.models.user import User

router = APIRouter(prefix="/sections", tags=["Sections"])

@router.get("/{uid}", response_model=SectionResponse)
def get_section(uid: str, db: Session = Depends(get_db)):
    return service.get_section(uid, db)

@router.post("/", response_model=SectionResponse)
def create_section(topic_uid: str, data: SectionCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return service.create_section(topic_uid, data, db)

@router.put("/{uid}", response_model=SectionResponse)
def update_section(uid: str, data: SectionUpdate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return service.update_section(uid, data, db)

@router.delete("/{uid}")
def delete_section(uid: str, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return service.delete_section(uid, db)