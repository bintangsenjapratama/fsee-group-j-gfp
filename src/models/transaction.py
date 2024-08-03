from models.base import Base
from sqlalchemy import Integer, DateTime, String, DECIMAL, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import mapped_column, relationship


class Transaction(Base):
    __tablename__ = "transactions"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    from_user_id = mapped_column(Integer, ForeignKey("users.id"))
    to_user_id = mapped_column(Integer, ForeignKey("users.id"))
    product_id = mapped_column(Integer, ForeignKey("products.id"))
    product_quantity = mapped_column(Integer, nullable=False)
    total_price = mapped_column(DECIMAL(10, 2), nullable=False)
    status = mapped_column(String(50))
    created_at = mapped_column(DateTime, default=func.now(), nullable=False)
    update_at = mapped_column(DateTime(timezone=True), onupdate=func.now())

    from_user = relationship(
        "User", foreign_keys=[from_user_id], back_populates="sent_transactions"
    )
    to_user = relationship(
        "User", foreign_keys=[to_user_id], back_populates="received_transactions"
    )
