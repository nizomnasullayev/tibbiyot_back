import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, UploadFile
from app.config import CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET

cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
)

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

async def upload_image(file: UploadFile, folder: str = "tibbiyot") -> dict:
    # Validate type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG and WEBP images are allowed")

    # Read and validate size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size must be under 5MB")

    # Upload to Cloudinary
    try:
        result = cloudinary.uploader.upload(
            contents,
            folder=folder,
            resource_type="image",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")

    return {
        "image_url": result["secure_url"],   # https URL
        "public_id": result["public_id"],    # needed for deletion
    }


def delete_image(public_id: str):
    try:
        cloudinary.uploader.destroy(public_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {e}")