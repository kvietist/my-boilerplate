from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class Usercreate(BaseModel):
    username: str = Field(min_length=3, max_length=15)
    password: str = Field(min_length=6, max_length=15)
    email: EmailStr = Field(max_length=26)
    age: int = Field(ge=18, le=45)

class Userlogin(BaseModel):
    username: str
    email: str

    class Config:
        from_attributes = True

class Userout(BaseModel):
    id: int
    username: str
    email: str
    class Config:
        from_attributes = True

class DiaryBase(BaseModel):
    title: str
    content: str

class Diarycreate(DiaryBase):
    pass

class Diaryresponse(DiaryBase):
    id:int
    owner_id: int

    class Config:
        from_attributes = True