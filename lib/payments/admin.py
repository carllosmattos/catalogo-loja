"""Consultas admin de pagamentos e reembolsos."""

from __future__ import annotations

from typing import Any

from lib.supabase_client import get_authenticated_client


def fetch_payments(limit: int = 100) -> list[dict[str, Any]]:
    client = get_authenticated_client()
    result = (
        client.table("payments")
        .select("*, orders(*)")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return result.data or []


def fetch_order_bundle_by_id(order_id: str) -> dict[str, Any] | None:
    client = get_authenticated_client()
    order = (
        client.table("orders").select("*").eq("id", order_id).limit(1).execute()
    )
    if not order.data:
        return None
    o = order.data[0]
    items = (
        client.table("order_items").select("*").eq("order_id", order_id).execute().data
        or []
    )
    pay = (
        client.table("payments")
        .select("*")
        .eq("order_id", order_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    return {
        "order": o,
        "items": items,
        "payment": pay.data[0] if pay.data else None,
    }


def fetch_payment(payment_id: str) -> dict[str, Any] | None:
    client = get_authenticated_client()
    result = (
        client.table("payments")
        .select("*")
        .eq("id", payment_id)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def fetch_refund_requests(status: str | None = "pending", limit: int = 50) -> list[dict[str, Any]]:
    client = get_authenticated_client()
    query = (
        client.table("refund_requests")
        .select("*, orders(*), payments(*)")
        .order("created_at", desc=True)
        .limit(limit)
    )
    if status:
        query = query.eq("status", status)
    return query.execute().data or []


def approve_refund_request(refund_id: str, admin_notes: str = "") -> None:
    client = get_authenticated_client()
    row = (
        client.table("refund_requests")
        .select("*, orders(*), payments(*)")
        .eq("id", refund_id)
        .limit(1)
        .execute()
    )
    if not row.data:
        raise ValueError("Solicitação não encontrada.")
    req = row.data[0]
    payment = req.get("payments") or {}
    mp_id = payment.get("provider_payment_id")
    if not mp_id:
        raise ValueError("Pagamento sem ID do Mercado Pago.")

    from lib.payments.factory import get_payment_gateway

    gateway = get_payment_gateway()
    gateway.refund_payment(str(mp_id))

    client.table("refund_requests").update(
        {"status": "approved", "admin_notes": admin_notes.strip()}
    ).eq("id", refund_id).execute()

    order_id = req.get("order_id")
    if order_id:
        client.rpc("mark_order_refunded", {"p_order_id": order_id}).execute()


def reject_refund_request(refund_id: str, admin_notes: str = "") -> None:
    client = get_authenticated_client()
    req = (
        client.table("refund_requests")
        .select("order_id")
        .eq("id", refund_id)
        .limit(1)
        .execute()
    )
    client.table("refund_requests").update(
        {"status": "rejected", "admin_notes": admin_notes.strip()}
    ).eq("id", refund_id).execute()
    if req.data and req.data[0].get("order_id"):
        client.table("orders").update({"status": "paid"}).eq(
            "id", req.data[0]["order_id"]
        ).execute()
