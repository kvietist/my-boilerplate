from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

class Usertable(Base):
    __tablename__ = "users_info"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    email: Mapped[str] = mapped_column()
    password: Mapped[str] =  mapped_column()
    age: Mapped[int] = mapped_column()

    diaries: Mapped[list["Diary"]] = relationship("Diary", back_populates="owner", cascade="all, delete-orphan")



class Diary(Base):
    __tablename__=  "diaries"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column()
    content: Mapped[str] = mapped_column()

    owner_id:  Mapped[int] = mapped_column(ForeignKey("users_info.id", ondelete="CASCADE")) 

    owner: Mapped["Usertable"] = relationship(back_populates="diaries")