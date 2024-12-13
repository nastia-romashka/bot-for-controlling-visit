from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, String, Integer
from db.models.base import Base

class Lesson(Base):
    __tablename__ = 'lesson'

    lessonId: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    teacherTelegram_id: Mapped[int] = mapped_column(Integer, ForeignKey('teacher.teacherTelegram_id'))
    lessonName: Mapped[str] = mapped_column(String(30), use_existing_column=False)
    lessonType: Mapped[str] = mapped_column(String(3), use_existing_column=False)
    group: Mapped[str] = mapped_column(String, use_existing_column=False)
