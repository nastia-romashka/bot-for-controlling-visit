from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer
from db.models.base import Base

class Admin(Base):
    __tablename__ = 'admin'
    adminTelegram_id: Mapped[int] = mapped_column(Integer,primary_key=True,use_existing_column=False)
    adminPassword: Mapped[str] = mapped_column(String(64), use_existing_column=False)