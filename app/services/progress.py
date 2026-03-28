from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.progress import UserProgress, TopicTestResult, FinalTestResult, Certificate
from app.models.topic import Topic, Entry
from app.models.user import User
from app.services.test_generator import build_topic_test_questions, build_final_test_questions
from app.services.certificate import generate_certificate, upload_certificate


# ── Progress ─────────────────────────────────────────────────

def get_all_progress(user: User, db: Session) -> list[UserProgress]:
    return db.query(UserProgress).filter(UserProgress.user_uid == user.uid).all()


def get_topic_progress(user: User, topic_uid: str, db: Session) -> UserProgress:
    progress = db.query(UserProgress).filter(
        UserProgress.user_uid == user.uid,
        UserProgress.topic_uid == topic_uid
    ).first()
    if not progress:
        # create fresh progress record
        progress = UserProgress(user_uid=user.uid, topic_uid=topic_uid, learned_entries=[])
        db.add(progress)
        db.commit()
        db.refresh(progress)
    return progress


def learn_entry(user: User, topic_uid: str, entry_uid: str, db: Session) -> UserProgress:
    # Validate entry belongs to topic
    entry = db.query(Entry).filter(Entry.uid == entry_uid, Entry.topic_uid == topic_uid).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found in this topic")

    progress = get_topic_progress(user, topic_uid, db)

    if entry_uid not in (progress.learned_entries or []):
        # Count total entries in topic
        total_entries = db.query(Entry).filter(Entry.topic_uid == topic_uid).count()

        new_learned = list(progress.learned_entries or []) + [entry_uid]
        new_progress = (len(new_learned) / total_entries) * 100 if total_entries > 0 else 0

        progress.learned_entries = new_learned
        progress.progress = round(new_progress, 2)
        db.commit()
        db.refresh(progress)

    return progress


# ── Topic Tests ───────────────────────────────────────────────

def get_topic_test(user: User, topic_uid: str, db: Session) -> list[dict]:
    progress = get_topic_progress(user, topic_uid, db)

    if progress.progress < 100.0:
        raise HTTPException(
            status_code=403,
            detail=f"You need to learn all entries first. Current progress: {progress.progress}%"
        )

    topic = db.query(Topic).filter(Topic.uid == topic_uid).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    entries = db.query(Entry).filter(Entry.topic_uid == topic_uid).all()
    return build_topic_test_questions(entries)


def submit_topic_test(user: User, topic_uid: str, answers: list, db: Session) -> dict:
    progress = get_topic_progress(user, topic_uid, db)

    if progress.progress < 100.0:
        raise HTTPException(status_code=403, detail="Topic not fully learned yet")

    # Generate correct answers to compare
    entries = db.query(Entry).filter(Entry.topic_uid == topic_uid).all()
    questions = build_topic_test_questions(entries)
    correct_map = {q["id"]: q["correct_answer"] for q in questions}

    score = sum(1 for a in answers if correct_map.get(a.question_id) == a.answer)
    total = len(questions)
    passed = score >= 1  # any score passes topic test

    # Save result
    result = TopicTestResult(
        user_uid=user.uid,
        topic_uid=topic_uid,
        score=score,
        total=total,
        passed=passed,
    )
    db.add(result)

    # Mark topic test as passed
    progress.topic_test_passed = True
    db.commit()

    accuracy = round((score / total) * 100, 1) if total > 0 else 0

    return {
        "score": score,
        "total": total,
        "passed": passed,
        "accuracy": accuracy,
        "message": f"Test completed! {score}/{total} correct."
    }


# ── Final Tests ───────────────────────────────────────────────

def check_all_topics_passed(user: User, db: Session) -> bool:
    all_topics = db.query(Topic).all()
    for topic in all_topics:
        progress = db.query(UserProgress).filter(
            UserProgress.user_uid == user.uid,
            UserProgress.topic_uid == topic.uid
        ).first()
        if not progress or not progress.topic_test_passed:
            return False
    return True


def get_final_test(user: User, db: Session) -> list[dict]:
    if not check_all_topics_passed(user, db):
        raise HTTPException(
            status_code=403,
            detail="You must complete all topic tests first"
        )

    all_entries = db.query(Entry).all()
    return build_final_test_questions(all_entries, total=50)


def submit_final_test(user: User, answers: list, db: Session) -> dict:
    if not check_all_topics_passed(user, db):
        raise HTTPException(status_code=403, detail="You must complete all topic tests first")

    all_entries = db.query(Entry).all()
    questions = build_final_test_questions(all_entries, total=50)
    correct_map = {q["id"]: q["correct_answer"] for q in questions}

    score = sum(1 for a in answers if correct_map.get(a.question_id) == a.answer)
    total = len(questions)
    accuracy = round((score / total) * 100, 1) if total > 0 else 0
    passed = score >= 35

    # Save result
    result = FinalTestResult(
        user_uid=user.uid,
        score=score,
        total=total,
        accuracy=accuracy,
        passed=passed,
    )
    db.add(result)
    db.commit()

    # Generate certificate if passed
    if passed:
        existing_cert = db.query(Certificate).filter(Certificate.user_uid == user.uid).first()
        if not existing_cert:
            cert_number = db.query(Certificate).count() + 1
            cert = Certificate(
                user_uid=user.uid,
                certificate_number=cert_number,
                accuracy=accuracy,
            )
            db.add(cert)
            db.commit()
            db.refresh(cert)

            # Generate and upload certificate image
            full_name = f"{user.name}" if user.name else "Foydalanuvchi"
            img_bytes = generate_certificate(full_name, accuracy, cert.uid, cert_number)
            cert_url = upload_certificate(img_bytes, cert.uid)

            cert.certificate_url = cert_url
            db.commit()

    return {
        "score": score,
        "total": total,
        "passed": passed,
        "accuracy": accuracy,
        "message": "Sertifikat olindi! 🎉" if passed else f"Kamida 35 ta to'g'ri javob kerak. Siz {score} ta topdingiz.",
    }