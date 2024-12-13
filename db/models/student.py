from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer
from db.models.base import Base

class Student(Base):
    __tablename__ = 'student'

    studentTelegram_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    studentGroup: Mapped[str] = mapped_column(String, use_existing_column=False)
    studentSurname: Mapped[str] = mapped_column(String(30), use_existing_column=False)
    studentName: Mapped[str] = mapped_column(String(30), use_existing_column=False)
    studentPatronymic: Mapped[str] = mapped_column(String(30), use_existing_column=False)