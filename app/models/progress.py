import uuid
from sqlalchemy import Column, String, Float, Boolean, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func
from app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class UserProgress(Base):
    __tablename__ = "user_progress"
    __table_args__ = (UniqueConstraint("user_uid", "topic_uid"),)

    uid = Column(String, primary_key=True, default=generate_uuid)
    user_uid = Column(String, ForeignKey("users.uid", ondelete="CASCADE"), nullable=False)
    topic_uid = Column(String, ForeignKey("topics.uid", ondelete="CASCADE"), nullable=False)
    learned_entries = Column(ARRAY(String), default=[])   # list of learned entry uids
    progress = Column(Float, default=0.0)                 # 0.0 to 100.0
    topic_test_passed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TopicTestResult(Base):
    __tablename__ = "topic_test_results"

    uid = Column(String, primary_key=True, default=generate_uuid)
    user_uid = Column(String, ForeignKey("users.uid", ondelete="CASCADE"), nullable=False)
    topic_uid = Column(String, ForeignKey("topics.uid", ondelete="CASCADE"), nullable=False)
    score = Column(Integer, nullable=False)     # correct answers
    total = Column(Integer, default=8)
    passed = Column(Boolean, nullable=False)
    completed_at = Column(DateTime(timezone=True), server_default=func.now())


class FinalTestResult(Base):
    __tablename__ = "final_test_results"

    uid = Column(String, primary_key=True, default=generate_uuid)
    user_uid = Column(String, ForeignKey("users.uid", ondelete="CASCADE"), nullable=False)
    score = Column(Integer, nullable=False)     # correct answers out of 50
    total = Column(Integer, default=50)
    accuracy = Column(Float, nullable=False)    # percentage
    passed = Column(Boolean, nullable=False)    # score >= 35
    completed_at = Column(DateTime(timezone=True), server_default=func.now())


class Certificate(Base):
    __tablename__ = "certificates"

    uid = Column(String, primary_key=True, default=generate_uuid)
    user_uid = Column(String, ForeignKey("users.uid", ondelete="CASCADE"), nullable=False)
    certificate_number = Column(Integer, nullable=False)
    accuracy = Column(Float, nullable=False)
    certificate_url = Column(String, nullable=True)
    issued_at = Column(DateTime(timezone=True), server_default=func.now())