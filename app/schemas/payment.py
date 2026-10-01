from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from app.core.payments import PaymentStatus


class PaymentCreate(BaseModel):
    amount: float = Field(gt=0, allow_inf_nan=False)
    currency: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class PaymentSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: PaymentStatus


class PaymentDetails(PaymentSummary):
    amount: float
    currency: str
