"""Gateway de pagamento (abstração SOLID)."""

from lib.payments.factory import get_payment_gateway

__all__ = ["get_payment_gateway"]
