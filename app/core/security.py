from passlib.context import CryptContext
import hashlib

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _prehash(password: str) -> bytes:
    return hashlib.sha256(password.encode('utf-8')).hexdigest().encode('utf-8')

def hash_password(password: str) -> str:
    prehashed = _prehash(password)
    return pwd_context.hash(prehashed)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    prehashed = _prehash(plain_password)
    return pwd_context.verify(prehashed, hashed_password)