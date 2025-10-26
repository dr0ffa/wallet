from datetime import datetime, timedelta, timezone
from typing import Dict, Union
import jwt
from fastapi import HTTPException
#from logging import getLogger
#logger = getLogger(__name__)


SECRET_KEY = "secret-key"
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS   = 7

def create_access_token(data: Dict[str, Union[str,int,datetime]], expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    payload = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + expires_delta
    payload.update({
        "iat": now,    
        "exp": expire,     
        "type": "access"     
    })
    #logger.info(f"{payload}")
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    #logger.info(f"{encoded_jwt}")
    return encoded_jwt

def create_refresh_token(data: Dict[str, Union[str,int,datetime]], expires_delta: timedelta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)):
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + expires_delta
    to_encode.update({
        "iat": now,
        "exp": expire,
        "type": "refresh"
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Dict[str, Union[str,int]]:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload

def validation_token(request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Missing access token")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    return username
