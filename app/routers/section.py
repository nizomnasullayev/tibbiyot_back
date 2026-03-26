from fastapi import APIRouter, Depends, UploadFile, File, Form
from typing import Optional
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.topic import SectionUpdate, SectionResponse
from app.services import topic as service
from app.utils.dependencies import require_admin
from app.utils.cloudinary import upload_image
from app.models.user import User

router = APIRouter(prefix="/sections", tags=["Sections"])

@router.get("/{uid}", response_model=SectionResponse)
def get_section(uid: str, db: Session = Depends(get_db)):
    return service.get_section(uid, db)

@router.post("/", response_model=SectionResponse)
async def create_section(
    topic_uid: str = Form(...),
    title: str = Form(...),
    image: Optional[UploadFile] = File(None),  # optional image
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    image_url = None
    if image and image.filename:
        result = await upload_image(image, folder="tibbiyot")
        image_url = result["image_url"]

    from app.schemas.topic import SectionCreate
    data = SectionCreate(title=title, image_url=image_url)
    return service.create_section(topic_uid, data, db)

@router.put("/{uid}", response_model=SectionResponse)
async def update_section(
    uid: str,
    title: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),  # optional new image
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    image_url = None
    if image and image.filename:
        result = await upload_image(image, folder="tibbiyot")
        image_url = result["image_url"]

    from app.schemas.topic import SectionUpdate
    data = SectionUpdate(title=title, image_url=image_url)
    return service.update_section(uid, data, db)

@router.delete("/{uid}")
def delete_section(uid: str, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return service.delete_section(uid, db)