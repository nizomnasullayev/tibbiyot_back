from sqlalchemy import Column, Float, String

from app.core.database import Base


class Country(Base):
    __tablename__ = "countries"

    # Stable ID (e.g. ISO 3166-1 numeric as string: "076", "124", ...)
    id = Column(String(length=10), primary_key=True, index=True)

    name = Column(String(length=120), nullable=False, unique=True, index=True)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    emoji = Column(String(length=16), nullable=False)
    continent = Column(String(length=32), nullable=False, index=True)
