"""HTML dos cards do catálogo público."""

from __future__ import annotations

import html

import streamlit as st

from lib.branding import get_logo_path, resolve_catalog_banner, resolve_logo_url
from lib.carousel_css import build_crossfade_carousel_css
from lib.images import build_image_carousel_html, normalize_image_urls
from lib.profit import GiftCost, ProfitResult
from lib.utils import format_currency

CAROUSEL_SECONDS = 5


def build_banner_header_html(mode: str, urls: list[str]) -> tuple[str, str]:
    """HTML do header com banner único ou carrossel. Retorna (css, html)."""
    if not urls:
        return "", ""

    if mode == "carousel" and len(urls) >= 2:
        n = len(urls)
        duration = float(CAROUSEL_SECONDS * n)
        carousel_id = f"store{n}"
        css = build_crossfade_carousel_css(n, duration, carousel_id=carousel_id)
        slides = "".join(
            f'<img class="store-banner store-banner-slide" src="{html.escape(u)}" '
            f'alt="Promoção {i + 1}">'
            for i, u in enumerate(urls)
        )
        dots = "".join('<span class="store-banner-dot"></span>' for _ in range(n))
        body = (
            f'<div class="store-header store-header-banner">'
            f'<div class="store-banner-wrap store-banner-carousel" '
            f'data-slides="{n}" data-carousel-id="{carousel_id}">'
            f'<div class="store-banner-track">{slides}</div>'
            f'<div class="store-banner-dots">{dots}</div>'
            f"</div></div>"
        )
        return css, body

    url = urls[0]
    body = (
        f'<div class="store-header store-header-banner">'
        f'<div class="store-banner-wrap">'
        f'<img class="store-banner" src="{html.escape(url)}" alt="Banner da loja">'
        f"</div></div>"
    )
    return "", body


def build_banner_header_markup(mode: str, urls: list[str]) -> str:
    """CSS + HTML em uma string (admin preview)."""
    css, body = build_banner_header_html(mode, urls)
    return css + body


def render_catalog_header(
    settings: dict,
    promotions: list[dict] | None,
    store_banners: list[dict] | None = None,
) -> None:
    """Renderiza banner ou fallback logo + nome no topo do catálogo."""
    banner = resolve_catalog_banner(settings, promotions, store_banners)

    if banner["mode"] != "legacy":
        css, body = build_banner_header_html(banner["mode"], banner["urls"])
        if css:
            st.markdown(css, unsafe_allow_html=True)
        if body:
            st.markdown(body, unsafe_allow_html=True)
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


def build_banner_preview_html(
    settings: dict,
    promotions: list[dict] | None,
    store_banners: list[dict] | None = None,
) -> str:
    """Preview HTML para admin."""
    banner = resolve_catalog_banner(settings, promotions, store_banners)
    if banner["mode"] == "legacy":
        return ""
    return build_banner_header_markup(banner["mode"], banner["urls"])


def _promo_percent(profit: ProfitResult) -> int | None:
    if profit.preco_catalogo <= 0 or profit.desconto <= 0:
        return None
    pct = round(profit.desconto / profit.preco_catalogo * 100)
    return pct if pct >= 1 else None


def _gift_card_html(g: GiftCost) -> str:
    qty = f" x{g.quantity}" if g.quantity > 1 else ""
    urls = normalize_image_urls(
        {"image_urls": g.image_urls or [], "image_url": g.image_url}
    )
    if urls:
        if len(urls) == 1:
            media = (
                f'<div class="gift-photo-wrap">'
                f'<img class="gift-photo" src="{html.escape(urls[0])}" alt="{html.escape(g.name)}">'
                f'<span class="gift-photo-tag">GRÁTIS</span>'
                f"</div>"
            )
        else:
            inner = build_image_carousel_html(
                urls, css_class="gift-photo-carousel"
            )
            media = (
                f'<div class="gift-photo-wrap">'
                f"{inner}"
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
        f'<div class="gift-card-name">{html.escape(g.name)}{qty}</div>'
        f'<div class="gift-card-sub">Incluso na compra</div>'
        f"</div></div>"
    )


def build_product_card_html(
    product: dict,
    profit: ProfitResult,
    out_of_stock: bool,
    *,
    compact: bool = False,
    size_hint: str | None = None,
) -> str:
    urls = normalize_image_urls(product)
    card_class = "product-card out-of-stock" if out_of_stock else "product-card"
    if compact:
        card_class += " product-card-compact"
    has_promo = bool(profit.promotion_name and profit.desconto > 0)
    has_gifts = bool(profit.gifts)
    promo_pct = _promo_percent(profit) if has_promo else None
    category = (product.get("category") or "").strip()

    markup = f'<div class="{card_class}">'

    markup += '<div class="product-image-wrap">'
    markup += build_image_carousel_html(urls)

    markup += '<div class="product-badges">'
    if has_promo and promo_pct:
        markup += f'<span class="badge badge-promo">−{promo_pct}%</span>'
    elif has_promo:
        markup += '<span class="badge badge-promo">PROMO</span>'
    if has_gifts:
        markup += '<span class="badge badge-gift">🎁</span>' if compact else '<span class="badge badge-gift">🎁 BRINDE</span>'
    markup += "</div></div>"

    # Faixa combo (omitida no modo compacto — badges já indicam)
    if not compact:
        if has_promo and has_gifts:
            markup += (
                '<div class="combo-strip">'
                f"<span>{html.escape(profit.promotion_name or '')}</span>"
                '<span class="combo-dot">•</span>'
                "<span>Brinde incluso</span>"
                "</div>"
            )
        elif has_promo:
            markup += f'<div class="promo-strip">{html.escape(profit.promotion_name or "")}</div>'
        elif has_gifts:
            markup += '<div class="gift-strip">🎁 Ganhe brinde exclusivo</div>'

    markup += '<div class="product-info">'
    if category:
        markup += f'<div class="product-category">{html.escape(category)}</div>'
    markup += f'<div class="product-name">{html.escape(product["name"])}</div>'

    if size_hint:
        markup += f'<div class="product-size">Tam. {html.escape(size_hint)}</div>'

    if product.get("description"):
        desc_class = "product-desc product-desc-clamp" if compact else "product-desc"
        markup += f'<div class="{desc_class}">{html.escape(product["description"])}</div>'

    # Preço
    markup += '<div class="price-block">'
    if has_promo:
        if not compact:
            markup += f'<div class="price-old">{format_currency(profit.preco_catalogo)}</div>'
        markup += (
            f'<div class="price-current">{format_currency(profit.preco_final_cliente)}</div>'
        )
        if not compact:
            markup += (
                f'<div class="price-save">Economize {format_currency(profit.desconto)}</div>'
            )
    else:
        markup += (
            f'<div class="price-current solo">'
            f"{format_currency(profit.preco_final_cliente)}</div>"
        )
    markup += "</div>"

    # Brindes em destaque (somente no card grande)
    if has_gifts and not compact:
        markup += '<div class="gifts-section">'
        for g in profit.gifts:
            markup += _gift_card_html(g)
        markup += "</div>"
    elif has_gifts and compact:
        gift_names = ", ".join(g.name for g in profit.gifts[:2])
        if len(profit.gifts) > 2:
            gift_names += "…"
        markup += f'<div class="gift-compact">🎁 {html.escape(gift_names)}</div>'

    if out_of_stock:
        markup += '<div class="stock-out">Esgotado</div>'

    markup += "</div></div>"
    return markup
