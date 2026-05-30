from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import schemas, models, utils
from database import get_db
from oauth2 import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/get_info", status_code=status.HTTP_201_CREATED, response_model=schemas.Userlogin)
async def get_info(user: schemas.Usercreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.Usertable).filter(models.Usertable.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="username already exist !")
    
    hashed_password = utils.hash_password(user.password)
    user.password = hashed_password
    new_user = models.Usertable(**user.model_dump())

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

    


@router.get("/{id}", response_model=schemas.Userlogin)
async def get_user(id:int, db: Session = Depends(get_db)):
    user_id = db.query(models.Usertable).filter(models.Usertable.id == id).first()
    if not user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")

    return user_id

@router.put("/{id}", response_model=schemas.Userlogin)
async def update_user(id:int, updated_user: schemas.Usercreate, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    if current_user != id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="you are not authorized to perform this action !")
    user_query = db.query(models.Usercreate).filter(models.Usercreate.username == username)
    user = user_query.first()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUNT, detail=f"the user with id {id} not found")

    conflict_user = db.query(models.Usercreate).filter(models.Usercreate.username == updated_user.username, models.Usercreate.id != id).first()
    if conflict_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="username already taken !")
    
    user_query.update(updated_user.model_dump(), synchronize_session=False)
    db.commit()
    return updated_user

@router.delete("/{user_id}", response_model=schemas.Userlogin)
async def delete_user(user_id: int, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    if current_user != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="you are not authorized to perform this action !")

    user_query = db.query(models.Usercreate).filter(models.Usercreate.id == user_id)
    user = user_query.first()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id {user_id} not found")


    user_query.delete(synchronize_session=False)
    db.commit()
    return {"message": "user with id {user_id} deleted successfully !"}