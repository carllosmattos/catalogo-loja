"""Sincroniza status de pagamento com o Mercado Pago."""

from __future__ import annotations

from typing import Any

from lib.payments.factory import get_payment_gateway, payments_enabled
from lib.payments.mercado_pago.mapper import extract_pix_copy_paste, map_mp_status
from lib.supabase_client import get_authenticated_client, get_supabase


def _parse_rpc(data: Any) -> Any:
    if isinstance(data, list):
        return data[0] if data else None
    return data


def sync_order_payment(
    order_id: str,
    *,
    customer_id: str | None = None,
    provider_payment_id: str | None = None,
) -> dict[str, Any]:
    """
    Consulta Mercado Pago e aplica status no Supabase.
    Catálogo: informe customer_id. Admin: omita customer_id.
    """
    if not payments_enabled():
        raise ValueError("Pagamentos desativados.")

    mp_id = provider_payment_id
    if not mp_id:
        client = get_supabase()
        pay = (
            client.table("payments")
            .select("provider_payment_id")
            .eq("order_id", order_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        rows = pay.data or []
        if not rows or not rows[0].get("provider_payment_id"):
            raise ValueError("Pagamento não encontrado.")
        mp_id = str(rows[0]["provider_payment_id"])

    mp = get_payment_gateway().get_payment(str(mp_id))
    status = map_mp_status(mp.get("status", ""))
    amount = float(mp.get("transaction_amount") or 0)
    poi = mp.get("point_of_interaction") or {}
    tx = poi.get("transaction_data") or {}
    pix = str(tx.get("qr_code") or extract_pix_copy_paste(mp) or "")
    if len(pix) > 500:
        pix = ""

    rpc_name = (
        "apply_payment_status_public"
        if customer_id
        else "apply_payment_status_admin"
    )
    rpc_args: dict[str, Any] = {
        "p_order_id": order_id,
        "p_provider_payment_id": str(mp_id),
        "p_status": status.value,
        "p_amount": amount,
        "p_pix_copy_paste": pix,
        "p_raw": mp,
    }
    if customer_id:
        rpc_args["p_customer_id"] = customer_id

    db = get_authenticated_client() if not customer_id else get_supabase()
    result = db.rpc(rpc_name, rpc_args).execute()
    data = _parse_rpc(result.data)
    return data if isinstance(data, dict) else {"status": status.value}
