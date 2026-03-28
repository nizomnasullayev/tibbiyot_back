from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.jwt import get_current_user
from app.models.user import User
from app.models.progress import Certificate
from app.schemas.progress import CertificateResponse

router = APIRouter(prefix="/certificates", tags=["Certificates"])

@router.get("/me", response_model=CertificateResponse)
def get_my_certificate(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cert = db.query(Certificate).filter(Certificate.user_uid == current_user.uid).first()
    if not cert:
        raise HTTPException(status_code=404, detail="No certificate yet. Complete all tests first!")
    return cert

@router.get("/verify/{uid}")          # public — no auth needed
def verify_certificate(uid: str, db: Session = Depends(get_db)):
    cert = db.query(Certificate).filter(Certificate.uid == uid).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    user = db.query(User).filter(User.uid == cert.user_uid).first()
    return {
        "valid": True,
        "certificate_number": cert.certificate_number,
        "full_name": user.name,
        "accuracy": cert.accuracy,
        "issued_at": cert.issued_at,
    }