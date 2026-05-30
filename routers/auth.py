from fastapi import Depends, HTTPException, APIRouter, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import database, utils, schemas, models
from database import get_db

router = APIRouter(tags=["Authentication"])

@router.post("/login")
async def loggin_user(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db) ):
    user = db.query(models.Usertable).filter(models.Usertable.username == user_credentials.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="invalid credentials")

    if not utils.verify_password(user.password, user_credentials.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="invalid credentials")

    access_token = utils.create_access_token(data={"user_id": user.id})
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }