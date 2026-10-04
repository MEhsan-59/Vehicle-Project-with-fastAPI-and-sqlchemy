# auth.py
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from config import Config


def create_access_token(user_id: str):
    payload = {
        "sub": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm=Config.ALGORITHM)


def decode_access_token(token: str):
    try:
        return jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.ALGORITHM])
    except JWTError:
        return None
