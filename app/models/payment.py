from uuid import UUID

from sqlalchemy import Float, String, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="pending")
