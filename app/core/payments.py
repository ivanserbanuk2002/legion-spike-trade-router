from dataclasses import dataclass
from itertools import islice
from threading import Lock
from typing import Literal
from uuid import UUID

from app.core.utils import generate_id
from app.models.payment import Payment

PaymentStatus = Literal["pending", "cancelled"]


@dataclass(frozen=True)
class PaymentSnapshot:
    id: UUID
    amount: float
    currency: str
    status: PaymentStatus


def _snapshot(payment: Payment) -> PaymentSnapshot:
    return PaymentSnapshot(payment.id, payment.amount, payment.currency, payment.status)


class InMemoryPaymentStore:
    """Process-local payment examples; snapshots never expose mutable records."""

    def __init__(self) -> None:
        self._payments: dict[UUID, Payment] = {}
        self._lock = Lock()

    def create(self, amount: float, currency: str) -> PaymentSnapshot:
        with self._lock:
            payment = Payment(
                id=generate_id(), amount=amount, currency=currency, status="pending"
            )
            self._payments[payment.id] = payment
            return _snapshot(payment)

    def get(self, payment_id: UUID) -> PaymentSnapshot | None:
        with self._lock:
            payment = self._payments.get(payment_id)
            return _snapshot(payment) if payment is not None else None

    def list(
        self, status: PaymentStatus | None, limit: int, offset: int
    ) -> list[PaymentSnapshot]:
        with self._lock:
            matches = (
                payment for payment in self._payments.values()
                if status is None or payment.status == status
            )
            return [_snapshot(payment) for payment in islice(matches, offset, offset + limit)]
