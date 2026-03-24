from pydantic import BaseModel, Field


class CountryOut(BaseModel):
    id: str = Field(min_length=1, max_length=10)
    name: str = Field(min_length=1, max_length=120)
    lat: float
    lng: float
    emoji: str = Field(min_length=1, max_length=16)
    continent: str = Field(min_length=1, max_length=32)

    class Config:
        from_attributes = True
