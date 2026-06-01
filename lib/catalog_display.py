"""HTML dos cards do catálogo público."""

from __future__ import annotations

import html

import streamlit as st

from lib.branding import get_logo_path, resolve_catalog_banner, resolve_logo_url
from lib.profit import GiftCost, ProfitResult
from lib.utils import format_currency

CAROUSEL_SECONDS = 5


def build_banner_header_html(mode: str, urls: list[str]) -> str:
    """HTML do header com banner único ou carrossel."""
    if not urls:
        return ""

    if mode == "carousel" and len(urls) >= 2:
        n = len(urls)
        duration = CAROUSEL_SECONDS * n
        slides = "".join(
            f'<img class="store-banner store-banner-slide" src="{html.escape(u)}" '
            f'alt="Promoção {i + 1}">'
            for i, u in enumerate(urls)
        )
        dots = "".join(
            f'<span class="store-banner-dot" style="animation-delay:{i * CAROUSEL_SECONDS}s"></span>'
            for i in range(n)
        )
        return (
            f'<div class="store-header store-header-banner">'
            f'<div class="store-banner-wrap store-banner-carousel" '
            f'style="--banner-count:{n};--banner-duration:{duration}s">'
            f'<div class="store-banner-track">{slides}</div>'
            f'<div class="store-banner-dots">{dots}</div>'
            f"</div></div>"
        )

    url = urls[0]
    return (
        f'<div class="store-header store-header-banner">'
        f'<div class="store-banner-wrap">'
        f'<img class="store-banner" src="{html.escape(url)}" alt="Banner da loja">'
        f"</div></div>"
    )


def render_catalog_header(settings: dict, promotions: list[dict] | None) -> None:
    """Renderiza banner ou fallback logo + nome no topo do catálogo."""
    banner = resolve_catalog_banner(settings, promotions)

    if banner["mode"] != "legacy":
        st.markdown(build_banner_header_html(banner["mode"], banner["urls"]), unsafe_allow_html=True)
        return

    store_name = settings.get("store_name", "")
    st.markdown('<div class="store-header">', unsafe_allow_html=True)
    logo_url = resolve_logo_url(settings)
    if logo_url:
        st.image(logo_url, width=140)
    else:
        logo_path = get_logo_path()
        if logo_path:
            st.image(str(logo_path), width=140)
    st.markdown(
        f'<div class="store-name">{html.escape(store_name)}</div></div>',
        unsafe_allow_html=True,
    )


def build_banner_preview_html(settings: dict, promotions: list[dict] | None) -> str:
    """Preview HTML para admin."""
    banner = resolve_catalog_banner(settings, promotions)
    if banner["mode"] == "legacy":
        return ""
    return build_banner_header_html(banner["mode"], banner["urls"])


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
    *,
    compact: bool = False,
) -> str:
    urls = product.get("image_urls") or []
    card_class = "product-card out-of-stock" if out_of_stock else "product-card"
    if compact:
        card_class += " product-card-compact"
    has_promo = bool(profit.promotion_name and profit.desconto > 0)
    has_gifts = bool(profit.gifts)
    promo_pct = _promo_percent(profit) if has_promo else None
    category = (product.get("category") or "").strip()

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
        html += '<span class="badge badge-gift">🎁</span>' if compact else '<span class="badge badge-gift">🎁 BRINDE</span>'
    html += "</div></div>"

    # Faixa combo (omitida no modo compacto — badges já indicam)
    if not compact:
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
    if category:
        html += f'<div class="product-category">{category}</div>'
    html += f'<div class="product-name">{product["name"]}</div>'

    if product.get("size"):
        html += f'<div class="product-size">Tam. {product["size"]}</div>'

    if product.get("description"):
        desc_class = "product-desc product-desc-clamp" if compact else "product-desc"
        html += f'<div class="{desc_class}">{product["description"]}</div>'

    # Preço
    html += '<div class="price-block">'
    if has_promo:
        if not compact:
            html += f'<div class="price-old">{format_currency(profit.preco_catalogo)}</div>'
        html += (
            f'<div class="price-current">{format_currency(profit.preco_final_cliente)}</div>'
        )
        if not compact:
            html += (
                f'<div class="price-save">Economize {format_currency(profit.desconto)}</div>'
            )
    else:
        html += (
            f'<div class="price-current solo">'
            f"{format_currency(profit.preco_final_cliente)}</div>"
        )
    html += "</div>"

    # Brindes em destaque (somente no card grande)
    if has_gifts and not compact:
        html += '<div class="gifts-section">'
        for g in profit.gifts:
            html += _gift_card_html(g)
        html += "</div>"
    elif has_gifts and compact:
        gift_names = ", ".join(g.name for g in profit.gifts[:2])
        if len(profit.gifts) > 2:
            gift_names += "…"
        html += f'<div class="gift-compact">🎁 {gift_names}</div>'

    if out_of_stock:
        html += '<div class="stock-out">Esgotado</div>'

    html += "</div></div>"
    return html
