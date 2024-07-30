from models.base import Base
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import mapped_column
import bcrypt


class User(Base):
    __tablename__ = "users"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    email = mapped_column(String(100), nullable=False, unique=True)
    username = mapped_column(String(100), nullable=False, unique=True)
    password_hash = mapped_column(String(255), nullable=False)
    role = mapped_column(String(50), nullable=False)
    created_at = mapped_column(DateTime, nullable=False, server_default=func.now())
    update_at = mapped_column(DateTime(timezone=True), onupdate=func.now())

    def set_password(self, password_hash):
        self.password_hash = bcrypt.hashpw(
            password_hash.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

    def check_password(self, password_hash):
        return bcrypt.checkpw(
            password_hash.encode("utf-8"), self.password_hash.encode("utf-8")
        )
