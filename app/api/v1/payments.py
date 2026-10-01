from fastapi import APIRouter
from pydantic import BaseModel

from app.core.utils import generate_id
from app.models.payment import Payment

router = APIRouter()


class PaymentCreate(BaseModel):
    amount: float
    currency: str


@router.post("/api/v1/payments", status_code=201)
def create_payment(data: PaymentCreate) -> dict[str, str]:
    payment = Payment(
        id=generate_id(), amount=data.amount, currency=data.currency, status="pending"
    )
    return {"id": str(payment.id), "status": payment.status}
