"""Factory do gateway de pagamento."""

from __future__ import annotations

import os

import streamlit as st

from lib.payments.protocols import PaymentGateway


def _secret(key: str, default: str = "") -> str:
    try:
        return st.secrets.get(key, os.environ.get(key, default))
    except Exception:
        return os.environ.get(key, default)


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
    try:
        flag = st.secrets.get("PAYMENTS_ENABLED", True)
        if isinstance(flag, str):
            return flag.lower() in ("1", "true", "yes", "on")
        return bool(flag)
    except Exception:
        return bool(os.environ.get("PAYMENTS_ENABLED", "1") not in ("0", "false", "no"))


def app_base_url() -> str:
    return (_secret("APP_BASE_URL", "") or "").rstrip("/")


def webhook_notification_url() -> str:
    return (_secret("MERCADOPAGO_WEBHOOK_URL", "") or "").strip()
