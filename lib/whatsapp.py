"""Geração de links WhatsApp com mensagem pré-preenchida."""

from __future__ import annotations

from urllib.parse import quote

from lib.profit import ProfitResult
from lib.utils import format_currency, parse_whatsapp_number


def build_order_message(
    product: dict,
    profit: ProfitResult,
    store_name: str,
    customer: dict | None = None,
) -> str:
    from lib.customer_session import customer_for_whatsapp

    lines = ["Olá! Quero comprar:", ""]
    lines.extend(customer_for_whatsapp(customer))
    lines.append(f"Peça: {product.get('name', '')}")

    if product.get("size"):
        lines.append(f"Tamanho: {product['size']}")
    if product.get("category"):
        lines.append(f"Categoria: {product['category']}")

    lines.append(f"Preço: {format_currency(profit.preco_catalogo)}")

    if profit.promotion_name and profit.desconto > 0:
        lines.append(f"Promoção: {profit.promotion_name}")
        lines.append(f"Desconto: -{format_currency(profit.desconto)}")

    if profit.gifts:
        lines.append("")
        lines.append("Brinde(s):")
        for g in profit.gifts:
            lines.append(f"  • {g.name} (x{g.quantity})")

    if float(product.get("sale_freight", 0)) > 0:
        lines.append(f"Frete: {format_currency(float(product['sale_freight']))}")

    lines.extend(
        [
            "",
            f"Valor final: {format_currency(profit.preco_final_cliente)}",
            "",
            f"Vi no catálogo da {store_name}",
        ]
    )

    return "\n".join(lines)


def build_cart_message(
    items: list[dict],
    store_name: str,
    customer: dict | None = None,
) -> str:
    """Mensagem WhatsApp para pedido com vários itens."""
    from lib.customer_session import customer_for_whatsapp

    lines = ["Olá! Quero comprar:", ""]
    lines.extend(customer_for_whatsapp(customer))
    grand_total = 0.0

    for i, item in enumerate(items, start=1):
        qty = int(item.get("quantity", 1))
        unit_final = float(item.get("preco_final", 0))
        subtotal = unit_final * qty
        grand_total += subtotal

        lines.append(f"{i}. {item.get('name', 'Peça')}")
        if item.get("size"):
            lines.append(f"   Tam.: {item['size']}")
        lines.append(f"   Qtd: {qty}")
        lines.append(f"   Preço unit.: {format_currency(unit_final)}")

        promo = item.get("promotion_name")
        desconto = float(item.get("desconto", 0))
        if promo and desconto > 0:
            lines.append(f"   Promo: {promo} (−{format_currency(desconto)}/un.)")

        gifts = item.get("gifts") or []
        if gifts:
            parts = []
            for g in gifts:
                if isinstance(g, dict):
                    per = int(g.get("qty", 1))
                    parts.append(f"{g.get('name', 'Brinde')} x{per * qty}")
            if parts:
                lines.append(f"   Brinde(s): {', '.join(parts)}")

        lines.append(f"   Subtotal: {format_currency(subtotal)}")
        lines.append("")

    lines.extend(
        [
            f"TOTAL: {format_currency(grand_total)}",
            "",
            f"Vi no catálogo da {store_name}",
        ]
    )
    return "\n".join(lines)


def build_whatsapp_url(whatsapp_number: str, message: str) -> str:
    number = parse_whatsapp_number(whatsapp_number)
    encoded = quote(message)
    return f"https://wa.me/{number}?text={encoded}"
