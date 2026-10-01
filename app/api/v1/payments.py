from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.core.payments import InMemoryPaymentStore, PaymentStatus
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


@router.get("/api/v1/payments", response_model=list[PaymentDetails])
def list_payments(
    store: Store,
    status: PaymentStatus | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0, le=1_000_000)] = 0,
) -> list[PaymentDetails]:
    return [PaymentDetails.model_validate(item) for item in store.list(status, limit, offset)]
