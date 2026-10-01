from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, Response

from app.core.payments import IdempotencyConflict, InMemoryPaymentStore, PaymentStatus
from app.schemas.payment import PaymentCreate, PaymentDetails, PaymentSummary

router = APIRouter()


def payment_store(request: Request) -> InMemoryPaymentStore:
    return request.app.state.payment_store


Store = Annotated[InMemoryPaymentStore, Depends(payment_store)]


@router.post(
    "/api/v1/payments", status_code=201, response_model=PaymentSummary,
    responses={200: {"model": PaymentSummary, "description": "Existing payment replay"}},
)
def create_payment(
    data: PaymentCreate,
    store: Store,
    response: Response,
    idempotency_key: Annotated[
        str | None, Header(min_length=1, max_length=128, pattern=r"\S")
    ] = None,
) -> PaymentSummary:
    try:
        payment, created = store.create(data.amount, data.currency, idempotency_key)
    except IdempotencyConflict as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    response.status_code = 201 if created else 200
    return PaymentSummary.model_validate(payment)


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


@router.post("/api/v1/payments/{payment_id}/cancel", response_model=PaymentDetails)
def cancel_payment(payment_id: UUID, store: Store) -> PaymentDetails:
    payment = store.cancel(payment_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return PaymentDetails.model_validate(payment)
