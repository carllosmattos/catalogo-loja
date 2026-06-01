"""Registro e relatórios de vendas."""

from __future__ import annotations

from datetime import date, datetime, time
from typing import Any

from lib.catalog import fetch_active_promotions, fetch_product_gifts
from lib.customers import upsert_customer
from lib.profit import calculate_profit, extract_gift_from_link
from lib.supabase_client import get_authenticated_client
from lib.utils import is_valid_cpf, normalize_cpf


def gift_stock_ok_for_quantity(
    linked: list[dict[str, Any]],
    quantity: int,
) -> bool:
    for lg in linked:
        gift = extract_gift_from_link(lg)
        if not gift:
            continue
        needed = int(lg.get("quantity_per_sale", 1)) * quantity
        if int(gift.get("stock", 0)) < needed:
            return False
    return True


def register_sale(
    product: dict[str, Any],
    customer_name: str,
    customer_phone: str = "",
    customer_cpf: str = "",
    customer_address: str = "",
    notes: str = "",
    quantity: int = 1,
    *,
    selected_size: str | None = None,
) -> str:
    """Registra venda via RPC, decrementa estoque."""
    qty = max(int(quantity), 1)
    if not customer_name.strip():
        raise ValueError("Informe o nome do cliente.")
    if not is_valid_cpf(customer_cpf):
        raise ValueError("CPF inválido.")

    cpf_normalized = normalize_cpf(customer_cpf)
    customer = upsert_customer(
        customer_name, customer_phone, cpf_normalized, customer_address
    )

    client = get_authenticated_client()
    promotions = fetch_active_promotions()
    linked = fetch_product_gifts(product["id"])
    profit = calculate_profit(
        product, linked, promotions, selected_size=selected_size
    )

    if profit.stock < qty:
        raise ValueError(f"Estoque insuficiente (disponível: {profit.stock}).")
    if not gift_stock_ok_for_quantity(linked, qty):
        raise ValueError("Estoque de brinde insuficiente.")

    gifts_payload = []
    for lg in linked:
        gift = extract_gift_from_link(lg)
        if not gift:
            continue
        per_sale = int(lg.get("quantity_per_sale", 1))
        gifts_payload.append(
            {
                "gift_id": gift["id"],
                "gift_name": gift.get("name", "Brinde"),
                "quantity": per_sale * qty,
            }
        )

    promo_id = None
    if profit.promotion_name:
        for p in promotions:
            if p.get("name") == profit.promotion_name:
                promo_id = p.get("id")
                break

    unit_final = float(profit.preco_final_cliente)
    unit_lucro = float(profit.lucro_bruto)

    result = client.rpc(
        "register_sale",
        {
            "p_customer_name": customer_name.strip(),
            "p_customer_phone": customer_phone.strip(),
            "p_product_id": product["id"],
            "p_product_name": product["name"],
            "p_product_size": selected_size or product.get("size", "") or "M",
            "p_preco_catalogo": float(profit.preco_catalogo),
            "p_desconto": float(profit.desconto),
            "p_sale_freight": float(product.get("sale_freight", 0)),
            "p_preco_final": unit_final * qty,
            "p_promotion_id": promo_id,
            "p_promotion_name": profit.promotion_name,
            "p_lucro": unit_lucro * qty,
            "p_notes": notes.strip(),
            "p_gifts": gifts_payload,
            "p_quantity": qty,
            "p_customer_id": customer["id"],
            "p_customer_cpf": cpf_normalized,
        },
    ).execute()

    sale_id = result.data
    if isinstance(sale_id, list):
        sale_id = sale_id[0] if sale_id else None
    if not sale_id:
        raise ValueError("Erro ao registrar venda.")
    return str(sale_id)


def cancel_sale(sale_id: str) -> None:
    """Cancela venda via RPC e devolve estoque."""
    client = get_authenticated_client()
    client.rpc("cancel_sale", {"p_sale_id": sale_id}).execute()


def fetch_sales(
    start: date | None = None,
    end: date | None = None,
    limit: int = 200,
    include_cancelled: bool = False,
    cancelled_only: bool = False,
) -> list[dict[str, Any]]:
    client = get_authenticated_client()
    query = (
        client.table("sales")
        .select("*, sale_gifts(*)")
        .order("created_at", desc=True)
        .limit(limit)
    )
    if cancelled_only:
        query = query.not_.is_("cancelled_at", "null")
    elif not include_cancelled:
        query = query.is_("cancelled_at", "null")
    if start:
        query = query.gte("created_at", datetime.combine(start, time.min).isoformat())
    if end:
        query = query.lte("created_at", datetime.combine(end, time.max).isoformat())
    return query.execute().data or []


def sales_summary(sales: list[dict[str, Any]]) -> dict[str, float]:
    total_receita = sum(float(s.get("preco_final", 0)) for s in sales)
    total_lucro = sum(float(s.get("lucro", 0)) for s in sales)
    total_pecas = sum(int(s.get("quantity", 1)) for s in sales)
    return {
        "count": len(sales),
        "pecas": total_pecas,
        "receita": total_receita,
        "lucro": total_lucro,
    }


def sales_by_day(sales: list[dict[str, Any]]) -> dict[str, float]:
    """Agrega receita por dia (YYYY-MM-DD)."""
    by_day: dict[str, float] = {}
    for s in sales:
        created = s.get("created_at", "")[:10]
        if not created:
            continue
        by_day[created] = by_day.get(created, 0) + float(s.get("preco_final", 0))
    return dict(sorted(by_day.items()))


def sale_quantity(sale: dict[str, Any]) -> int:
    return max(int(sale.get("quantity") or 1), 1)
