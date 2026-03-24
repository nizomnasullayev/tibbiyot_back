from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.baamboozle_question import BaamboozleQuestion
from app.models.user import User
from app.schema.baamboozle_question_schema import BaamboozleQuestionCreate, BaamboozleQuestionUpdate


def _is_admin(user: User) -> bool:
    return "admin" in (user.roles or [])


def _can_manage(user: User, question: BaamboozleQuestion) -> bool:
    if _is_admin(user):
        return True
    return question.created_by == user.id


def create_question(db: Session, data: BaamboozleQuestionCreate, current_user: User) -> BaamboozleQuestion:
    payload = data.model_dump(mode="json")
    question = BaamboozleQuestion(
        category=payload["category"],
        question=payload["question"],
        answer=payload["answer"],
        created_by=current_user.id,
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


def create_questions_bulk(
    db: Session,
    data_list: list[BaamboozleQuestionCreate],
    current_user: User,
) -> list[BaamboozleQuestion]:
    questions: list[BaamboozleQuestion] = []
    for data in data_list:
        payload = data.model_dump(mode="json")
        questions.append(
            BaamboozleQuestion(
                category=payload["category"],
                question=payload["question"],
                answer=payload["answer"],
                created_by=current_user.id,
            )
        )

    db.add_all(questions)
    db.commit()
    for question in questions:
        db.refresh(question)
    return questions


def list_questions(db: Session, current_user: User) -> list[BaamboozleQuestion]:
    query = db.query(BaamboozleQuestion)
    if not _is_admin(current_user):
        query = query.filter(BaamboozleQuestion.created_by == current_user.id)
    return query.order_by(BaamboozleQuestion.created_at.desc()).all()


def get_question_by_id(db: Session, question_id: UUID, current_user: User) -> BaamboozleQuestion:
    question = db.query(BaamboozleQuestion).filter(BaamboozleQuestion.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Baamboozle question not found")
    if not _can_manage(current_user, question):
        raise HTTPException(status_code=403, detail="Permission denied")
    return question


def update_question(
    db: Session,
    question_id: UUID,
    data: BaamboozleQuestionUpdate,
    current_user: User,
) -> BaamboozleQuestion:
    question = get_question_by_id(db, question_id, current_user)
    update_data = data.model_dump(exclude_unset=True, mode="json")

    for key, value in update_data.items():
        setattr(question, key, value)

    db.commit()
    db.refresh(question)
    return question


def delete_question(db: Session, question_id: UUID, current_user: User) -> None:
    question = get_question_by_id(db, question_id, current_user)
    db.delete(question)
    db.commit()
