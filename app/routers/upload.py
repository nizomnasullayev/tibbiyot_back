from fastapi import APIRouter, UploadFile, File, Depends
from app.utils.cloudinary import upload_image, delete_image
from app.utils.dependencies import require_admin
from app.models.user import User
from pydantic import BaseModel

router = APIRouter(prefix="/upload", tags=["Upload"])

class DeleteRequest(BaseModel):
    public_id: str  # Cloudinary public_id returned on upload

@router.post("/image")
async def upload(
    file: UploadFile = File(...),
    _: User = Depends(require_admin)
):
    result = await upload_image(file, folder="tibbiyot")
    return result  # returns image_url and public_id

@router.delete("/image")
def delete(
    body: DeleteRequest,
    _: User = Depends(require_admin)
):
    delete_image(body.public_id)
    return {"message": "Image deleted"}