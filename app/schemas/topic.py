from pydantic import BaseModel
from typing import Optional

# ── Entry ────────────────────────────────────────────────────

class EntryCreate(BaseModel):
    latin: str
    uzbek: str

class EntryUpdate(BaseModel):
    latin: Optional[str] = None
    uzbek: Optional[str] = None

class EntryResponse(BaseModel):
    uid: str
    latin: str
    uzbek: str
    topic_uid: Optional[str]
    section_uid: Optional[str]

    class Config:
        from_attributes = True


# ── Section ──────────────────────────────────────────────────

class SectionCreate(BaseModel):
    title: str
    image_url: Optional[str] = None
    entries: Optional[list[EntryCreate]] = []

class SectionUpdate(BaseModel):
    title: Optional[str] = None
    image_url: Optional[str] = None

class SectionResponse(BaseModel):
    uid: str
    topic_uid: str
    title: str
    image_url: Optional[str]
    entries: list[EntryResponse] = []

    class Config:
        from_attributes = True


# ── Topic ────────────────────────────────────────────────────

class TopicCreate(BaseModel):
    title: str
    sections: Optional[list[SectionCreate]] = []
    entries: Optional[list[EntryCreate]] = []   # direct entries (no section)

class TopicUpdate(BaseModel):
    title: Optional[str] = None

class TopicResponse(BaseModel):
    uid: str
    title: str
    sections: list[SectionResponse] = []
    entries: list[EntryResponse] = []

    class Config:
        from_attributes = True