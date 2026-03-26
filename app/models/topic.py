import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class Topic(Base):
    __tablename__ = "topics"

    uid = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    sections = relationship("Section", back_populates="topic", cascade="all, delete-orphan")
    entries = relationship(
        "Entry",
        primaryjoin="and_(Entry.topic_uid == Topic.uid, Entry.section_uid == None)",
        back_populates="topic",
        cascade="all, delete-orphan",
        overlaps="entries"
    )


class Section(Base):
    __tablename__ = "sections"

    uid = Column(String, primary_key=True, default=generate_uuid)
    topic_uid = Column(String, ForeignKey("topics.uid", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    topic = relationship("Topic", back_populates="sections")
    entries = relationship("Entry", back_populates="section", cascade="all, delete-orphan")


class Entry(Base):
    __tablename__ = "entries"

    uid = Column(String, primary_key=True, default=generate_uuid)
    topic_uid = Column(String, ForeignKey("topics.uid", ondelete="CASCADE"), nullable=True)
    section_uid = Column(String, ForeignKey("sections.uid", ondelete="CASCADE"), nullable=True)
    latin = Column(String, nullable=False)
    uzbek = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    topic = relationship("Topic", foreign_keys=[topic_uid], overlaps="entries")
    section = relationship("Section", back_populates="entries")