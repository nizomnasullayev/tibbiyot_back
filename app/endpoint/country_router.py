from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schema.country_schema import CountryOut
from app.service import country_service

router = APIRouter(prefix="/countries", tags=["Countries"])


@router.get("/", response_model=list[CountryOut])
def get_countries(
    continent: str | None = None,
    db: Session = Depends(get_db),
):
    return country_service.list_countries(db, continent=continent)


@router.get("/continents", response_model=list[str])
def get_continents(db: Session = Depends(get_db)):
    return country_service.list_continents(db)
