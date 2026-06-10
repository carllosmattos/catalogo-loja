"""Acesso a pedidos e pagamentos via Supabase RPC."""

from __future__ import annotations

import json
import uuid
from typing import Any

from lib.supabase_client import get_supabase


def _parse_rpc_payload(data: Any) -> Any:
    if data is None:
        return None
    if isinstance(data, str):
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return None
    return data


def _valid_tracking_token(token: str | None) -> str | None:
    if not token:
        return None
    cleaned = str(token).strip()
    if not cleaned:
        return None
    try:
        uuid.UUID(cleaned)
    except ValueError:
        return None
    return cleaned


def create_checkout_order(customer_id: str, items: list[dict[str, Any]]) -> dict[str, Any]:
    client = get_supabase()
    result = client.rpc(
        "create_checkout_order",
        {"p_customer_id": customer_id, "p_items": items},
    ).execute()
    data = _parse_rpc_payload(result.data)
    if isinstance(data, list):
        data = data[0] if data else None
    if not data:
        raise ValueError("Erro ao criar pedido.")
    return data


def attach_payment_to_order(
    *,
    order_id: str,
    provider_payment_id: str,
    status: str,
    amount: float,
    pix_copy_paste: str = "",
    raw: dict | None = None,
) -> str:
    client = get_supabase()
    result = client.rpc(
        "attach_order_payment_public",
        {
            "p_order_id": order_id,
            "p_provider_payment_id": provider_payment_id,
            "p_status": status,
            "p_amount": amount,
            "p_pix_copy_paste": pix_copy_paste,
            "p_raw": raw or {},
        },
    ).execute()
    pid = result.data
    if isinstance(pid, list):
        pid = pid[0] if pid else None
    return str(pid) if pid else ""


def get_order_bundle(tracking_token: str) -> dict[str, Any] | None:
    token = _valid_tracking_token(tracking_token)
    if not token:
        return None
    try:
        client = get_supabase()
        result = client.rpc(
            "get_order_by_tracking",
            {"p_token": token},
        ).execute()
        data = _parse_rpc_payload(result.data)
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def list_customer_orders(
    customer_id: str, limit: int = 30
) -> tuple[list[dict[str, Any]], str | None]:
    if not customer_id:
        return [], None
    try:
        uuid.UUID(str(customer_id))
    except ValueError:
        return [], "Cliente inválido."
    try:
        client = get_supabase()
        result = client.rpc(
            "list_orders_by_customer",
            {"p_customer_id": customer_id, "p_limit": limit},
        ).execute()
        data = _parse_rpc_payload(result.data)
        if isinstance(data, list):
            return [row for row in data if isinstance(row, dict)], None
        if data is None:
            return [], None
        return [], "Resposta inesperada ao listar pedidos."
    except Exception as exc:
        return [], str(exc)


def cancel_order(
    customer_id: str,
    order_id: str,
    *,
    provider_payment_id: str | None = None,
) -> None:
    if provider_payment_id:
        try:
            from lib.payments.factory import get_payment_gateway, payments_enabled

            if payments_enabled():
                get_payment_gateway().cancel_payment(str(provider_payment_id))
        except Exception:
            pass
    client = get_supabase()
    client.rpc(
        "cancel_unpaid_order",
        {"p_order_id": order_id, "p_customer_id": customer_id},
    ).execute()


def request_refund(customer_id: str, order_id: str, reason: str = "") -> None:
    client = get_supabase()
    client.rpc(
        "request_order_refund",
        {
            "p_order_id": order_id,
            "p_customer_id": customer_id,
            "p_reason": reason,
        },
    ).execute()
