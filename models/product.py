from .base import Base
from sqlalchemy import Integer, DateTime, String, DECIMAL, ForeignKey, VARCHAR
from sqlalchemy.sql import func
from sqlalchemy.orm import mapped_column, relationship


class Product(Base):
    __tablename__ = "products"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id = mapped_column(Integer, ForeignKey("users.id"))
    product_name = mapped_column(String(100), nullable=True)
    price = mapped_column(DECIMAL(10, 2), nullable=True)
    description = mapped_column(String(255), nullable=True)
    stock = mapped_column(Integer, nullable=True)
    category = mapped_column(String(100))
    type = mapped_column(String(100))
    discount = mapped_column(DECIMAL(10, 2))
    created_at = mapped_column(DateTime, nullable=False, server_default=func.now())
    update_at = mapped_column(DateTime(timezone=True), onupdate=func.now())
    image_url = mapped_column(VARCHAR(255), nullable=True)

    user = relationship("User", back_populates="products")
