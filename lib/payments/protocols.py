"""Contrato do gateway de pagamento."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from lib.payments.models import CheckoutRequest, CheckoutResult, PaymentStatus, WebhookEvent


class PaymentGateway(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Identificador do provedor (ex.: mercado_pago)."""

    @abstractmethod
    def create_pix_checkout(self, request: CheckoutRequest) -> CheckoutResult:
        """Cria pagamento PIX e retorna copia e cola / QR."""

    @abstractmethod
    def get_payment(self, provider_payment_id: str) -> dict[str, Any]:
        """Consulta pagamento no provedor."""

    @abstractmethod
    def refund_payment(self, provider_payment_id: str, amount: float | None = None) -> dict[str, Any]:
        """Solicita reembolso total (v1)."""

    @abstractmethod
    def parse_webhook(self, headers: dict[str, str], body: dict[str, Any]) -> WebhookEvent | None:
        """Interpreta notificação do webhook."""

    def map_status(self, raw_status: str) -> PaymentStatus:
        """Mapeia status do provedor; subclasses podem sobrescrever."""
        key = (raw_status or "").lower()
        mapping = {
            "approved": PaymentStatus.APPROVED,
            "pending": PaymentStatus.PENDING,
            "in_process": PaymentStatus.IN_PROCESS,
            "rejected": PaymentStatus.REJECTED,
            "cancelled": PaymentStatus.CANCELLED,
            "refunded": PaymentStatus.REFUNDED,
        }
        return mapping.get(key, PaymentStatus.PENDING)
