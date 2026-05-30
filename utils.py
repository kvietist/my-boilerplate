from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from datetime import datetime, timezone, timedelta
from config import settings
from jose import jwt, JWTError
ph = PasswordHasher()

SECRET_KEY= settings.secret_key
ALGORITHM= settings.algorithm

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(hashed_password: str, plain_password: str) ->bool:
    try:
        return ph.verify(hashed_password, plain_password)

    except VerifyMismatchError:
        return False

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=30)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token:str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        return user_id

    except JWTError:
        raise credentials_exception
    