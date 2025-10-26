from passlib.context import CryptContext

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')
    logging.info(f"Password: {password!r}, length in bytes: {len(password_bytes)}")
    return pwd_context.hash(password)

    #print(f"Password length in bytes: {len(password.encode('utf-8'))}")
    #return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
