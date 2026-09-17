import hashlib
import hmac
import json
import secrets
import urllib.parse

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from database import get_db
import models
import utils
from utils import verify_access_token
from config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="could not validate credentials", headers= {"www-Authenticate": "Bearer"})

    return verify_access_token(token, credentials_exception)


def verify_telegram_webapp_signature(
    authorization: str = Header(...),
):
    if not authorization.startswith("TelegramMiniApp "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Telegram Mini App authorization.",
        )

    if not settings.telegram_bot_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Telegram Mini App authentication is not configured.",
        )

    init_data_raw = authorization.removeprefix("TelegramMiniApp ").strip()
    parsed_data = dict(urllib.parse.parse_qsl(init_data_raw, strict_parsing=False))
    received_hash = parsed_data.pop("hash", None)

    if not received_hash or "user" not in parsed_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed Telegram Mini App security data.",
        )

    data_check_string = "\n".join(
        f"{key}={value}" for key, value in sorted(parsed_data.items())
    )
    secret_key = hmac.new(
        b"WebAppData", settings.telegram_bot_token.encode(), hashlib.sha256
    ).digest()
    calculated_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Telegram Mini App signature.",
        )

    try:
        return json.loads(parsed_data["user"])
    except (json.JSONDecodeError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram Mini App user data.",
        )


def get_current_miniapp_user(
    tg_user: dict = Depends(verify_telegram_webapp_signature),
    db: Session = Depends(get_db),
):
    telegram_id = tg_user.get("id")
    if telegram_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Telegram user ID is missing.",
        )

    username = str(telegram_id)
    user = db.query(models.Usertable).filter(
        models.Usertable.username == username
    ).first()
    if user:
        return user

    new_user = models.Usertable(
        username=username,
        email=f"{username}@tma.com",
        password=utils.hash_password(secrets.token_urlsafe(32)),
        age=18,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user