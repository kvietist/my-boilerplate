from fastapi import APIRouter,  Depends, status, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import schemas, models, oauth2
from oauth2 import get_current_user
from oauth2 import get_current_miniapp_user


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
            detail=f"diary with id {id} not found !"
        )

    if diary.owner_id != current_user:
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail="you are not authorized to perform this action"
        )
    diary_query.delete(synchronize_session=False)
    db.commit()


miniapp_router = APIRouter(prefix="/miniapp/diaries", tags=["Telegram Mini App"])


@miniapp_router.get("/", response_model=list[schemas.Diaryresponse])
async def get_my_mini_app_diaries(
    db: Session = Depends(get_db),
    current_user: models.Usertable = Depends(get_current_miniapp_user),
):
    return db.query(models.Diary).filter(
        models.Diary.owner_id == current_user.id
    ).all()


@miniapp_router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Diaryresponse)
async def create_my_mini_app_diary(
    diary: schemas.Diarycreate,
    db: Session = Depends(get_db),
    current_user: models.Usertable = Depends(get_current_miniapp_user),
):
    new_entry = models.Diary(**diary.model_dump(), owner_id=current_user.id)
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return new_entry


@miniapp_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_mini_app_diary(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.Usertable = Depends(get_current_miniapp_user),
):
    diary = db.query(models.Diary).filter(
        models.Diary.id == id,
        models.Diary.owner_id == current_user.id,
    ).first()
    if not diary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"diary with id {id} not found",
        )

    db.delete(diary)
    db.commit()