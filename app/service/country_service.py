from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.country import Country

_SEED_PATH = Path(__file__).resolve().parents[1] / "data" / "countries_seed.json"


def _load_seed_data() -> list[dict]:
    if not _SEED_PATH.exists():
        return []
    with _SEED_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("countries_seed.json must be a JSON array")
    return data


def ensure_countries_seeded(db: Session) -> int:
    """
    Inserts missing seed countries into the DB (idempotent).
    Never updates existing rows (keeps DB data stable).
    Returns: number of inserted rows.
    """
    seed = _load_seed_data()
    if not seed:
        return 0

    seed_ids: list[str] = [str(item["id"]) for item in seed if "id" in item]
    existing_ids = {
        row[0]
        for row in db.query(Country.id).filter(Country.id.in_(seed_ids)).all()
    }

    to_add: list[Country] = []
    for item in seed:
        country_id = str(item["id"])
        if country_id in existing_ids:
            continue
        to_add.append(
            Country(
                id=country_id,
                name=item["name"],
                lat=float(item["lat"]),
                lng=float(item["lng"]),
                emoji=item["emoji"],
                continent=item["continent"],
            )
        )

    if not to_add:
        return 0

    db.add_all(to_add)
    db.commit()
    return len(to_add)


def list_countries(db: Session, continent: str | None = None) -> list[Country]:
    query = db.query(Country)
    if continent:
        query = query.filter(Country.continent == continent)
    return query.order_by(Country.name.asc()).all()


def list_continents(db: Session) -> list[str]:
    rows = db.query(Country.continent).distinct().order_by(Country.continent.asc()).all()
    return [row[0] for row in rows]
