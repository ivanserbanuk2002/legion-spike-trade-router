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


class IdempotencyConflict(ValueError):
    pass


def _snapshot(payment: Payment) -> PaymentSnapshot:
    return PaymentSnapshot(payment.id, payment.amount, payment.currency, payment.status)


class InMemoryPaymentStore:
    """Process-local payment examples; snapshots never expose mutable records."""

    def __init__(self) -> None:
        self._payments: dict[UUID, Payment] = {}
        self._keys: dict[str, UUID] = {}
        self._lock = Lock()

    def create(
        self, amount: float, currency: str, key: str | None = None
    ) -> tuple[PaymentSnapshot, bool]:
        with self._lock:
            if key is not None and key in self._keys:
                existing = self._payments[self._keys[key]]
                if (existing.amount, existing.currency) != (amount, currency):
                    raise IdempotencyConflict("Key already used for a different payment")
                return _snapshot(existing), False
            payment = Payment(
                id=generate_id(), amount=amount, currency=currency, status="pending"
            )
            self._payments[payment.id] = payment
            if key is not None:
                self._keys[key] = payment.id
            return _snapshot(payment), True

    def get(self, payment_id: UUID) -> PaymentSnapshot | None:
        with self._lock:
            payment = self._payments.get(payment_id)
            return _snapshot(payment) if payment is not None else None

    def list(
        self, status: PaymentStatus | None, limit: int, offset: int,
        currency: str | None = None
    ) -> list[PaymentSnapshot]:
        with self._lock:
            matches = (
                payment for payment in self._payments.values()
                if (status is None or payment.status == status)
                and (currency is None or payment.currency == currency)
            )
            return [_snapshot(payment) for payment in islice(matches, offset, offset + limit)]

    def cancel(self, payment_id: UUID) -> PaymentSnapshot | None:
        with self._lock:
            payment = self._payments.get(payment_id)
            if payment is None:
                return None
            if payment.status == "pending":
                payment.status = "cancelled"
            return _snapshot(payment)


    def counts(self) -> dict[str, dict[str, int]]:
        with self._lock:
            counts: dict[str, dict[str, int]] = {}
            for payment in self._payments.values():
                group = counts.setdefault(payment.currency, {"pending": 0, "cancelled": 0})
                group[payment.status] += 1
            return counts


    def purge_cancelled(self) -> int:
        with self._lock:
            removed = {key for key, value in self._payments.items()
                       if value.status == "cancelled"}
            self._keys = {key: value for key, value in self._keys.items()
                          if value not in removed}
            for payment_id in removed:
                del self._payments[payment_id]
            return len(removed)
