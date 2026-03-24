from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.endpoint.user_router import router as users_router
from app.endpoint.auth_router import router as auth_router
from app.endpoint.baamboozle_question_router import router as baamboozle_question_router
from app.endpoint.country_router import router as country_router
# from app.endpoint.google_router import router as google_router
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.service.google_oauth_service import set_google_client_id
from app.core.config import settings
from app.core.database import SessionLocal
from app.service.country_service import ensure_countries_seeded
from sqlalchemy.exc import OperationalError, ProgrammingError


# alembic upgrade head

# alembic revision --autogenerate -m "describe change"
# alembic upgrade head


app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

set_google_client_id(settings.GOOGLE_CLIENT_ID)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(baamboozle_question_router)
app.include_router(country_router)
# app.include_router(google_router)


@app.on_event("startup")
def _seed_countries() -> None:
    db = SessionLocal()
    try:
        ensure_countries_seeded(db)
    except (OperationalError, ProgrammingError):
        # Likely migrations not applied yet.
        pass
    finally:
        db.close()