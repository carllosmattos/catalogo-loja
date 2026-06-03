"""Acesso a pedidos e pagamentos via Supabase RPC."""

from __future__ import annotations

from typing import Any

from lib.supabase_client import get_supabase


def create_checkout_order(customer_id: str, items: list[dict[str, Any]]) -> dict[str, Any]:
    client = get_supabase()
    result = client.rpc(
        "create_checkout_order",
        {"p_customer_id": customer_id, "p_items": items},
    ).execute()
    data = result.data
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
    """Grava pagamento via upsert (usa anon — precisa RPC pública ou tabela).

    Para v1 o pagamento inicial é gravado pelo Streamlit com RPC dedicada.
    """
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
    client = get_supabase()
    result = client.rpc(
        "get_order_by_tracking",
        {"p_token": tracking_token},
    ).execute()
    return result.data


def list_customer_orders(customer_id: str, limit: int = 30) -> list[dict[str, Any]]:
    client = get_supabase()
    result = client.rpc(
        "list_orders_by_customer",
        {"p_customer_id": customer_id, "p_limit": limit},
    ).execute()
    data = result.data
    if isinstance(data, list):
        return data
    return data if isinstance(data, list) else []


def cancel_order(customer_id: str, order_id: str) -> None:
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
