"""Catálogo público de roupas — mobile-first para iPhone."""

import streamlit as st

from lib.catalog import (
    fetch_active_promotions,
    fetch_product_gifts,
    fetch_products,
    fetch_store_settings,
)
from lib.profit import calculate_profit
from lib.theme import inject_theme
from lib.utils import format_currency
from lib.whatsapp import build_order_message, build_whatsapp_url

st.set_page_config(
    page_title="Catálogo",
    page_icon="👗",
    layout="centered",
    initial_sidebar_state="collapsed",
)

settings = fetch_store_settings()
inject_theme(settings, hide_sidebar=True)

store_name = settings.get("store_name", "Minha Loja")
whatsapp_number = settings.get("whatsapp_number", "")

# Header
header_html = '<div class="store-header">'
if settings.get("logo_url"):
    header_html += f'<img src="{settings["logo_url"]}" alt="Logo">'
header_html += f'<div class="store-name">{store_name}</div></div>'
st.markdown(header_html, unsafe_allow_html=True)

if not whatsapp_number:
    st.warning("Catálogo em configuração. WhatsApp ainda não definido.")

products = fetch_products(active_only=True)
promotions = fetch_active_promotions()

if not products:
    st.info("Em breve novidades por aqui! ✨")
    st.stop()

for product in products:
    linked_gifts = fetch_product_gifts(product["id"])
    profit = calculate_profit(product, linked_gifts, promotions)

    urls = product.get("image_urls") or []
    out_of_stock = profit.stock <= 0
    card_class = "product-card out-of-stock" if out_of_stock else "product-card"

    card_html = f'<div class="{card_class}">'
    if urls:
        card_html += f'<img src="{urls[0]}" alt="{product["name"]}">'
    card_html += '<div class="product-info">'
    card_html += f'<div class="product-name">{product["name"]}</div>'

    if product.get("size"):
        card_html += f'<div style="color:#666;font-size:0.85rem;">Tam: {product["size"]}</div>'

    if profit.promotion_name and profit.desconto > 0:
        card_html += f'<div class="promo-badge">{profit.promotion_name}</div>'
        card_html += (
            f'<div><span class="product-price-old">'
            f'{format_currency(profit.preco_catalogo)}</span>'
            f'<span class="product-price">{format_currency(profit.preco_final_cliente)}</span></div>'
        )
    else:
        card_html += f'<div class="product-price">{format_currency(profit.preco_final_cliente)}</div>'

    if profit.gifts:
        gift_names = ", ".join(f"{g.name}" for g in profit.gifts)
        card_html += f'<div class="gift-tag">🎁 Brinde: {gift_names}</div>'

    if out_of_stock:
        card_html += '<div style="color:#dc3545;font-size:0.85rem;margin-top:4px;">Esgotado</div>'

    card_html += "</div></div>"
    st.markdown(card_html, unsafe_allow_html=True)

    if product.get("description"):
        st.caption(product["description"])

    if whatsapp_number and not out_of_stock:
        message = build_order_message(product, profit, store_name)
        wa_url = build_whatsapp_url(whatsapp_number, message)
        st.link_button(
            "Comprar no WhatsApp",
            wa_url,
            use_container_width=True,
            type="primary",
        )
    elif out_of_stock:
        st.button("Indisponível", disabled=True, use_container_width=True)

    st.markdown("")

st.markdown("---")
st.caption(f"Catálogo {store_name} · Compre pelo WhatsApp")
