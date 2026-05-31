"""HTML dos cards do catálogo público."""

from __future__ import annotations

from lib.profit import GiftCost, ProfitResult
from lib.utils import format_currency


def _promo_percent(profit: ProfitResult) -> int | None:
    if profit.preco_catalogo <= 0 or profit.desconto <= 0:
        return None
    pct = round(profit.desconto / profit.preco_catalogo * 100)
    return pct if pct >= 1 else None


def _gift_card_html(g: GiftCost) -> str:
    qty = f" x{g.quantity}" if g.quantity > 1 else ""
    if g.image_url:
        media = (
            f'<div class="gift-photo-wrap">'
            f'<img class="gift-photo" src="{g.image_url}" alt="{g.name}">'
            f'<span class="gift-photo-tag">GRÁTIS</span>'
            f"</div>"
        )
    else:
        media = (
            '<div class="gift-photo-wrap gift-photo-placeholder">'
            '<span class="gift-photo-emoji">🎁</span>'
            '<span class="gift-photo-tag">GRÁTIS</span>'
            "</div>"
        )

    return (
        f'<div class="gift-card">{media}'
        f'<div class="gift-card-body">'
        f'<div class="gift-card-label">Seu brinde</div>'
        f'<div class="gift-card-name">{g.name}{qty}</div>'
        f'<div class="gift-card-sub">Incluso na compra</div>'
        f"</div></div>"
    )


def build_product_card_html(
    product: dict,
    profit: ProfitResult,
    out_of_stock: bool,
) -> str:
    urls = product.get("image_urls") or []
    card_class = "product-card out-of-stock" if out_of_stock else "product-card"
    has_promo = bool(profit.promotion_name and profit.desconto > 0)
    has_gifts = bool(profit.gifts)
    promo_pct = _promo_percent(profit) if has_promo else None

    html = f'<div class="{card_class}">'

    # Foto + badges sobrepostos
    html += '<div class="product-image-wrap">'
    if urls:
        html += f'<img class="product-photo" src="{urls[0]}" alt="{product["name"]}">'
    else:
        html += '<div class="product-photo product-photo-empty"></div>'

    html += '<div class="product-badges">'
    if has_promo and promo_pct:
        html += f'<span class="badge badge-promo">−{promo_pct}%</span>'
    elif has_promo:
        html += '<span class="badge badge-promo">PROMO</span>'
    if has_gifts:
        html += '<span class="badge badge-gift">🎁 BRINDE</span>'
    html += "</div></div>"

    # Faixa combo
    if has_promo and has_gifts:
        html += (
            '<div class="combo-strip">'
            f"<span>{profit.promotion_name}</span>"
            '<span class="combo-dot">•</span>'
            "<span>Brinde incluso</span>"
            "</div>"
        )
    elif has_promo:
        html += f'<div class="promo-strip">{profit.promotion_name}</div>'
    elif has_gifts:
        html += '<div class="gift-strip">🎁 Ganhe brinde exclusivo</div>'

    html += '<div class="product-info">'
    html += f'<div class="product-name">{product["name"]}</div>'

    if product.get("size"):
        html += f'<div class="product-size">Tam. {product["size"]}</div>'

    if product.get("description"):
        html += f'<div class="product-desc">{product["description"]}</div>'

    # Preço
    html += '<div class="price-block">'
    if has_promo:
        html += f'<div class="price-old">{format_currency(profit.preco_catalogo)}</div>'
        html += (
            f'<div class="price-current">{format_currency(profit.preco_final_cliente)}</div>'
        )
        html += (
            f'<div class="price-save">Economize {format_currency(profit.desconto)}</div>'
        )
    else:
        html += (
            f'<div class="price-current solo">'
            f"{format_currency(profit.preco_final_cliente)}</div>"
        )
    html += "</div>"

    # Brindes em destaque
    if has_gifts:
        html += '<div class="gifts-section">'
        for g in profit.gifts:
            html += _gift_card_html(g)
        html += "</div>"

    if out_of_stock:
        html += '<div class="stock-out">Esgotado</div>'

    html += "</div></div>"
    return html
