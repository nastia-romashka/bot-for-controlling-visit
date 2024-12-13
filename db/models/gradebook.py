from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, Integer
from db.models.base import Base

class Gradebook(Base):
    __tablename__ = 'gradebook'

    gradebookId: Mapped[int] = mapped_column(Integer, primary_key=True,autoincrement=True)
    lessonId: Mapped[int] = mapped_column(Integer, ForeignKey('lesson.lessonId'))
    studentTelegram_id: Mapped[int] = mapped_column(Integer, ForeignKey('student.studentTelegram_id'))
    gradebook5: Mapped[int] = mapped_column(Integer, use_existing_column=False)
    gradebook4: Mapped[int] = mapped_column(Integer, use_existing_column=False)
    gradebook3: Mapped[int] = mapped_column(Integer, use_existing_column=False)
    gradebook2: Mapped[int] = mapped_column(Integer, use_existing_column=False)
    gradebookVisits: Mapped[int] = mapped_column(Integer, use_existing_column=False)