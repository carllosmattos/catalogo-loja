"""Mensagens WhatsApp com pedido e pagamento PIX."""

from __future__ import annotations

from typing import Any

from lib.utils import format_currency
from lib.whatsapp import build_whatsapp_url


def _order_status_label(status: str) -> str:
    labels = {
        "pending_payment": "Aguardando pagamento PIX",
        "paid": "Pago",
        "cancelled": "Cancelado",
        "refund_requested": "Reembolso solicitado",
        "refunded": "Reembolsado",
    }
    return labels.get(status, status)


def build_order_payment_message(
    bundle: dict[str, Any],
    store_name: str,
    *,
    tracking_url: str = "",
) -> str:
    order = bundle.get("order") or {}
    items = bundle.get("items") or []
    payment = bundle.get("payment") or {}

    lines = ["Olá! Segue meu pedido:", ""]
    lines.append(f"Loja: {store_name}")
    lines.append(f"Pedido: {str(order.get('id', ''))[:8]}…")
    lines.append(f"Status: {_order_status_label(order.get('status', ''))}")
    lines.append("")

    for i, item in enumerate(items, start=1):
        qty = int(item.get("quantity", 1))
        name = item.get("product_name", "Peça")
        size = item.get("product_size", "")
        line_total = float(item.get("preco_final_line", 0))
        lines.append(f"{i}. {name}" + (f" (tam. {size})" if size else ""))
        lines.append(f"   Qtd: {qty} · {format_currency(line_total)}")

    lines.append("")
    lines.append(f"Total: {format_currency(float(order.get('total_amount', 0)))}")

    pix = payment.get("pix_copy_paste") or ""
    if pix and len(str(pix)) < 2000:
        lines.extend(["", "PIX copia e cola:", str(pix)])

    if tracking_url:
        lines.extend(["", f"Acompanhar: {tracking_url}"])

    return "\n".join(lines)


def build_whatsapp_payment_url(
    whatsapp_number: str,
    bundle: dict[str, Any],
    store_name: str,
    *,
    tracking_url: str = "",
) -> str:
    msg = build_order_payment_message(bundle, store_name, tracking_url=tracking_url)
    return build_whatsapp_url(whatsapp_number, msg)
