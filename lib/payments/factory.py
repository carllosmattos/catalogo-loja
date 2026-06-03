"""Factory do gateway de pagamento."""

from __future__ import annotations

import os

from lib.payments.protocols import PaymentGateway
from lib.supabase_client import _clean, _from_streamlit_secrets


def _secret(key: str, default: str = "") -> str:
    value = _from_streamlit_secrets((key,))
    if value:
        return value
    return _clean(os.environ.get(key)) or default


def _secret_bool(key: str, default: bool = True) -> bool:
    raw = _secret(key, "")
    if not raw:
        return default
    if isinstance(raw, bool):
        return raw
    return str(raw).lower() in ("1", "true", "yes", "on")


def get_payment_gateway() -> PaymentGateway:
    provider = (_secret("PAYMENT_PROVIDER", "mercado_pago") or "mercado_pago").lower()
    if provider == "mercado_pago":
        from lib.payments.mercado_pago.gateway import MercadoPagoGateway

        token = _secret("MERCADOPAGO_ACCESS_TOKEN", "")
        if not token:
            raise ValueError("MERCADOPAGO_ACCESS_TOKEN não configurado.")
        return MercadoPagoGateway(access_token=token)
    raise ValueError(f"Provedor de pagamento não suportado: {provider}")


def payments_enabled() -> bool:
    return _secret_bool("PAYMENTS_ENABLED", True)


def app_base_url() -> str:
    return (_secret("APP_BASE_URL", "") or "").rstrip("/")


def webhook_notification_url() -> str:
    return (_secret("MERCADOPAGO_WEBHOOK_URL", "") or "").strip()
