from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.roles import require_teacher_or_admin
from app.models.user import User
from app.schema.baamboozle_question_schema import (
    BaamboozleAIGenerateRequest,
    BaamboozleAIGenerateResponse,
    BaamboozleQuestionCreate,
    BaamboozleQuestionOut,
    BaamboozleQuestionUpdate,
)
from app.service import ai_baamboozle_service
from app.service import baamboozle_question_service

router = APIRouter(prefix="/baamboozle-questions", tags=["Baamboozle Questions"])


@router.post("/", response_model=BaamboozleQuestionOut, status_code=status.HTTP_201_CREATED)
def create_question(
    data: BaamboozleQuestionCreate,
    db: Session = Depends(get_db),
    teacher_or_admin: User = Depends(require_teacher_or_admin),
):
    return baamboozle_question_service.create_question(db, data, teacher_or_admin)


@router.post("/ai-generate", response_model=BaamboozleAIGenerateResponse, status_code=status.HTTP_201_CREATED)
def create_questions_with_ai(
    data: BaamboozleAIGenerateRequest,
    db: Session = Depends(get_db),
    teacher_or_admin: User = Depends(require_teacher_or_admin),
):
    generated = ai_baamboozle_service.generate_question_creates(data)
    created = baamboozle_question_service.create_questions_bulk(db, generated, teacher_or_admin)
    return {"created_questions": created}


@router.get("/", response_model=list[BaamboozleQuestionOut])
def list_questions(
    db: Session = Depends(get_db),
    teacher_or_admin: User = Depends(require_teacher_or_admin),
):
    return baamboozle_question_service.list_questions(db, teacher_or_admin)


@router.get("/{question_id}", response_model=BaamboozleQuestionOut)
def get_question_by_id(
    question_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return baamboozle_question_service.get_question_by_id(db, question_id, current_user)


@router.put("/{question_id}", response_model=BaamboozleQuestionOut)
def update_question(
    question_id: UUID,
    data: BaamboozleQuestionUpdate,
    db: Session = Depends(get_db),
    teacher_or_admin: User = Depends(require_teacher_or_admin),
):
    return baamboozle_question_service.update_question(db, question_id, data, teacher_or_admin)


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(
    question_id: UUID,
    db: Session = Depends(get_db),
    teacher_or_admin: User = Depends(require_teacher_or_admin),
):
    baamboozle_question_service.delete_question(db, question_id, teacher_or_admin)
    return
