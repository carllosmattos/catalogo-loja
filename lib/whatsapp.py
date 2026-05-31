"""Geração de links WhatsApp com mensagem pré-preenchida."""

from __future__ import annotations

from urllib.parse import quote

from lib.profit import ProfitResult
from lib.utils import format_currency, parse_whatsapp_number


def build_order_message(
    product: dict,
    profit: ProfitResult,
    store_name: str,
) -> str:
    lines = [
        "Olá! Quero comprar:",
        "",
        f"Peça: {product.get('name', '')}",
    ]

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


def build_whatsapp_url(whatsapp_number: str, message: str) -> str:
    number = parse_whatsapp_number(whatsapp_number)
    encoded = quote(message)
    return f"https://wa.me/{number}?text={encoded}"
