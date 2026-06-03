"""Modelos de domínio para pagamentos."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class PaymentStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    IN_PROCESS = "in_process"


@dataclass
class CheckoutPayer:
    email: str
    name: str
    cpf: str
    phone: str = ""


@dataclass
class CheckoutRequest:
    order_id: str
    amount: float
    description: str
    payer: CheckoutPayer
    notification_url: str = ""
    back_url_success: str = ""
    back_url_failure: str = ""


@dataclass
class CheckoutResult:
    provider_payment_id: str
    status: PaymentStatus
    pix_copy_paste: str = ""
    ticket_url: str = ""
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class WebhookEvent:
    provider_payment_id: str
    external_reference: str
    status: PaymentStatus
    amount: float
    pix_copy_paste: str = ""
    raw: dict[str, Any] = field(default_factory=dict)
