import base64
import hashlib
import hmac
import os

try:
    from passlib.context import CryptContext
except ImportError:
    CryptContext = None

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") if CryptContext else None
PBKDF2_PREFIX = "pbkdf2_sha256"
PBKDF2_ITERATIONS = 100_000

def _prehash(password: str) -> bytes:
    return hashlib.sha256(password.encode('utf-8')).hexdigest().encode('utf-8')


def _hash_with_pbkdf2(prehashed: bytes) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", prehashed, salt, PBKDF2_ITERATIONS)
    salt_b64 = base64.urlsafe_b64encode(salt).decode("ascii")
    digest_b64 = base64.urlsafe_b64encode(digest).decode("ascii")
    return f"{PBKDF2_PREFIX}${PBKDF2_ITERATIONS}${salt_b64}${digest_b64}"


def _verify_pbkdf2(prehashed: bytes, hashed_password: str) -> bool:
    try:
        prefix, iterations_str, salt_b64, digest_b64 = hashed_password.split("$", 3)
        if prefix != PBKDF2_PREFIX:
            return False

        iterations = int(iterations_str)
        salt = base64.urlsafe_b64decode(salt_b64.encode("ascii"))
        expected = base64.urlsafe_b64decode(digest_b64.encode("ascii"))
        actual = hashlib.pbkdf2_hmac("sha256", prehashed, salt, iterations)
        return hmac.compare_digest(actual, expected)
    except Exception:
        return False


def hash_password(password: str) -> str:
    prehashed = _prehash(password)
    if pwd_context:
        return pwd_context.hash(prehashed)
    return _hash_with_pbkdf2(prehashed)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    prehashed = _prehash(plain_password)
    if hashed_password.startswith(f"{PBKDF2_PREFIX}$"):
        return _verify_pbkdf2(prehashed, hashed_password)
    if pwd_context:
        return pwd_context.verify(prehashed, hashed_password)
    return False
