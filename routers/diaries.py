from fastapi import APIRouter,  Depends, status, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import schemas, models, oauth2
from oauth2 import get_current_user


router = APIRouter(prefix="/diaries", tags=["Diaries"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Diaryresponse)
async def create_diaries(diary: schemas.Diarycreate, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    new_entry = models.Diary(**diary.model_dump(), owner_id = current_user)
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return new_entry

@router.get("/", response_model=list[schemas.Diaryresponse])
async def get_diaries(db: Session = Depends(get_db), current_user: int = Depends(get_current_user), limit: int = 10, offset: int = 0):
    diaries = db.query(models.Diary).filter(models.Diary.owner_id == current_user).limit(limit).offset(offset).all()
    return diaries

@router.put("/{id}", response_model=schemas.Diaryresponse)
async def update_diaries(id:int,updated_diary: schemas.Diarycreate,  db:Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    diary_query = db.query(models.Diary).filter(models.Diary.id == id)
    diary = diary_query.first()

    if not diary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="content not found")


    if diary.owner_id != current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="you are not authorized to perform this action")


    
    diary_query.update(updated_diary.model_dump(), synchronize_session=False)
    db.commit()
    return diary

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_diaries(id: int, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    diary_query = db.query(models.Diary).filter(models.Diary.id == id)
    diary = diary_query.first()
    
    if not diary:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail=f"diary with id {user_id} not found !"
        )

    if diary.owner_id != current_user:
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail="you are not authorized to perform this action"
        )
    diary_query.delete(synchronize_session=False)
    db.commit()