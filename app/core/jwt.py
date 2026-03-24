import base64
import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone

from app.core.config import settings

try:
    import jwt as pyjwt
    from jwt import InvalidTokenError
except ImportError:
    pyjwt = None
    InvalidTokenError = Exception


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode((data + padding).encode("ascii"))


def _encode_hs256(payload: dict, secret: str) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    sig = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    return f"{header_b64}.{payload_b64}.{_b64url_encode(sig)}"


def _decode_hs256(token: str, secret: str) -> dict:
    parts = token.split(".")
    if len(parts) != 3:
        return {}

    header_b64, payload_b64, sig_b64 = parts
    try:
        header = json.loads(_b64url_decode(header_b64))
        if header.get("alg") != "HS256":
            return {}

        signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
        expected_sig = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
        provided_sig = _b64url_decode(sig_b64)
        if not hmac.compare_digest(expected_sig, provided_sig):
            return {}

        payload = json.loads(_b64url_decode(payload_b64))
        exp = payload.get("exp")
        if exp is not None and datetime.now(timezone.utc).timestamp() > float(exp):
            return {}
        return payload
    except Exception:
        return {}


def create_token(payload: dict, expires_delta: timedelta) -> str:
    to_encode = payload.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": int(expire.timestamp())})

    if pyjwt is not None:
        return pyjwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return _encode_hs256(to_encode, settings.SECRET_KEY)


def decode_token(token: str) -> dict:
    if pyjwt is not None:
        try:
            return pyjwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        except InvalidTokenError:
            return {}
    return _decode_hs256(token, settings.SECRET_KEY)
