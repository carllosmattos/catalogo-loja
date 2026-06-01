"""Galeria de imagens e carrossel."""

from __future__ import annotations

import html
from typing import Any

import streamlit as st

CAROUSEL_SECONDS = 4


def normalize_image_urls(item: dict[str, Any]) -> list[str]:
    urls = item.get("image_urls") or []
    if urls:
        return [u for u in urls if u]
    single = item.get("image_url") or item.get("banner_url")
    return [single] if single else []


def build_image_carousel_html(urls: list[str], *, css_class: str = "item-photo-carousel") -> str:
    """Conteúdo interno da área de foto (dentro de .product-image-wrap)."""
    if not urls:
        return '<div class="product-photo product-photo-empty"></div>'
    if len(urls) == 1:
        u = html.escape(urls[0])
        return f'<img class="product-photo" src="{u}" alt="Foto">'

    n = len(urls)
    duration = CAROUSEL_SECONDS * n
    slides = "".join(
        f'<img class="product-photo product-banner-slide" src="{html.escape(u)}" '
        f'alt="Foto {i + 1}">'
        for i, u in enumerate(urls)
    )
    return (
        f'<div class="{css_class} product-photo-carousel-inner" '
        f'style="--banner-count:{n};--banner-duration:{duration}s">'
        f'<div class="product-banner-track">{slides}</div>'
        f"</div>"
    )


def render_admin_gallery(
    urls: list[str],
    key_prefix: str,
    on_update,
) -> None:
    """Exibe fotos com botão excluir (fora de form). on_update(new_urls) persiste."""
    if not urls:
        st.caption("Nenhuma foto cadastrada.")
        return

    for idx, url in enumerate(urls):
        col_img, col_btn = st.columns([4, 1])
        with col_img:
            st.image(url, use_container_width=True)
        with col_btn:
            if st.button("Excluir", key=f"del_{key_prefix}_{idx}", use_container_width=True):
                new_urls = [u for i, u in enumerate(urls) if i != idx]
                on_update(new_urls)
                st.rerun()
