from passlib.context import CryptContext
from cryptography.fernet import Fernet

import pyotp
import logging

from dotenv import load_dotenv
import os


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
FERNET_KEY = os.getenv("FERNET_KEY")
if not FERNET_KEY:
    raise ValueError("FERNET_KEY not found in .env")
fernet = Fernet(FERNET_KEY.encode()) 

def encrypt_secret(secret: str) -> str:
    return fernet.encrypt(secret.encode()).decode()

def decrypt_secret(encrypted_secret: str) -> str:
    return fernet.decrypt(encrypted_secret.encode()).decode()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')
    logging.info(f"Password: {password!r}, length in bytes: {len(password_bytes)}")
    return pwd_context.hash(password)

    #print(f"Password length in bytes: {len(password.encode('utf-8'))}")
    #return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

