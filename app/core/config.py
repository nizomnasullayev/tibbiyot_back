import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Settings(BaseModel):
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "openai")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    AI_ALLOW_FALLBACK: bool = _env_bool("AI_ALLOW_FALLBACK", False)

    class Config:
        env_file = ".env"


settings = Settings()

# Debug output
print("=" * 50)
print("Settings Loaded:")
print(f"SECRET_KEY: {'***' if settings.SECRET_KEY else 'NOT SET'}")
print(f"ALGORITHM: {settings.ALGORITHM}")
print(f"ACCESS_TOKEN_EXPIRE_MINUTES: {settings.ACCESS_TOKEN_EXPIRE_MINUTES}")
print(f"REFRESH_TOKEN_EXPIRE_DAYS: {settings.REFRESH_TOKEN_EXPIRE_DAYS}")
print(
    f"GOOGLE_CLIENT_ID: {settings.GOOGLE_CLIENT_ID[:20]}..." if settings.GOOGLE_CLIENT_ID else "GOOGLE_CLIENT_ID: NOT SET ❌")
print("=" * 50)
