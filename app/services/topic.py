from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from app.models.topic import Topic, Section, Entry
from app.schemas.topic import TopicCreate, TopicUpdate, SectionCreate, SectionUpdate, EntryCreate, EntryUpdate


# ── Topic ────────────────────────────────────────────────────

def get_all_topics(db: Session) -> list[Topic]:
    return db.query(Topic).options(
        joinedload(Topic.sections).joinedload(Section.entries)
    ).all()


def get_topic(uid: str, db: Session) -> Topic:
    topic = db.query(Topic).options(
        joinedload(Topic.sections).joinedload(Section.entries)
    ).filter(Topic.uid == uid).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic


def create_topic(data: TopicCreate, db: Session) -> Topic:
    topic = Topic(title=data.title)
    db.add(topic)
    db.flush()  # get uid before commit

    # create sections with their entries
    for section_data in data.sections:
        section = Section(topic_uid=topic.uid, title=section_data.title, image_url=section_data.image_url)
        db.add(section)
        db.flush()
        for entry_data in section_data.entries:
            db.add(Entry(section_uid=section.uid, topic_uid=topic.uid, latin=entry_data.latin, uzbek=entry_data.uzbek))

    # create direct entries (no section)
    for entry_data in data.entries:
        db.add(Entry(topic_uid=topic.uid, latin=entry_data.latin, uzbek=entry_data.uzbek))

    db.commit()
    db.refresh(topic)
    return get_topic(topic.uid, db)


def update_topic(uid: str, data: TopicUpdate, db: Session) -> Topic:
    topic = get_topic(uid, db)
    if data.title:
        topic.title = data.title
    db.commit()
    return get_topic(uid, db)


def delete_topic(uid: str, db: Session):
    topic = get_topic(uid, db)
    db.delete(topic)
    db.commit()
    return {"message": "Topic deleted"}


# ── Section ──────────────────────────────────────────────────

def get_section(uid: str, db: Session) -> Section:
    section = db.query(Section).options(
        joinedload(Section.entries)
    ).filter(Section.uid == uid).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    return section


def create_section(topic_uid: str, data: SectionCreate, db: Session) -> Section:
    get_topic(topic_uid, db)  # ensure topic exists
    section = Section(topic_uid=topic_uid, title=data.title, image_url=data.image_url)
    db.add(section)
    db.flush()
    for entry_data in data.entries:
        db.add(Entry(section_uid=section.uid, topic_uid=topic_uid, latin=entry_data.latin, uzbek=entry_data.uzbek))
    db.commit()
    return get_section(section.uid, db)


def update_section(uid: str, data: SectionUpdate, db: Session) -> Section:
    section = get_section(uid, db)
    if data.title:
        section.title = data.title
    if data.image_url is not None:
        section.image_url = data.image_url
    db.commit()
    return get_section(uid, db)


def delete_section(uid: str, db: Session):
    section = get_section(uid, db)
    db.delete(section)
    db.commit()
    return {"message": "Section deleted"}


# ── Entry ────────────────────────────────────────────────────

def get_entry(uid: str, db: Session) -> Entry:
    entry = db.query(Entry).filter(Entry.uid == uid).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry


def create_entry_in_section(section_uid: str, data: EntryCreate, db: Session) -> Entry:
    section = get_section(section_uid, db)
    entry = Entry(section_uid=section_uid, topic_uid=section.topic_uid, latin=data.latin, uzbek=data.uzbek)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def create_entry_in_topic(topic_uid: str, data: EntryCreate, db: Session) -> Entry:
    get_topic(topic_uid, db)
    entry = Entry(topic_uid=topic_uid, latin=data.latin, uzbek=data.uzbek)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def update_entry(uid: str, data: EntryUpdate, db: Session) -> Entry:
    entry = get_entry(uid, db)
    if data.latin:
        entry.latin = data.latin
    if data.uzbek:
        entry.uzbek = data.uzbek
    db.commit()
    db.refresh(entry)
    return entry


def delete_entry(uid: str, db: Session):
    entry = get_entry(uid, db)
    db.delete(entry)
    db.commit()
    return {"message": "Entry deleted"}