from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request

from app.core.payments import InMemoryPaymentStore
from app.schemas.payment import PaymentCreate, PaymentDetails, PaymentSummary

router = APIRouter()


def payment_store(request: Request) -> InMemoryPaymentStore:
    return request.app.state.payment_store


Store = Annotated[InMemoryPaymentStore, Depends(payment_store)]


@router.post("/api/v1/payments", status_code=201, response_model=PaymentSummary)
def create_payment(data: PaymentCreate, store: Store) -> PaymentSummary:
    return PaymentSummary.model_validate(store.create(data.amount, data.currency))


@router.get("/api/v1/payments/{payment_id}", response_model=PaymentDetails)
def get_payment(payment_id: UUID, store: Store) -> PaymentDetails:
    payment = store.get(payment_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return PaymentDetails.model_validate(payment)
