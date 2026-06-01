"""Navegação do catálogo público — menu ☰ sempre visível."""

from __future__ import annotations

import html

import streamlit as st

NAV_ICONS = {
    "Catálogo": "🏷️",
    "Carrinho": "🛒",
    "Minha conta": "👤",
}


def _nav_label(option: str, cart_count: int) -> str:
    if option == "Carrinho" and cart_count > 0:
        return f"Carrinho ({cart_count})"
    return option


def render_catalog_nav(
    options: list[str],
    *,
    cart_count: int = 0,
    store_name: str = "",
) -> str:
    """Barra superior com ☰ (popover) + título da seção ativa."""
    if "catalog_view" not in st.session_state:
        st.session_state.catalog_view = options[0]

    current = st.session_state.catalog_view
    current_label = _nav_label(current, cart_count)

    st.markdown('<div class="catalog-topbar">', unsafe_allow_html=True)
    bar_menu, bar_title = st.columns([1, 5], gap="small")
    with bar_menu:
        with st.popover("☰", help="Abrir menu"):
            if store_name:
                st.caption(store_name)
            st.markdown("**Menu**")
            for opt in options:
                label = _nav_label(opt, cart_count)
                icon = NAV_ICONS.get(opt, "•")
                active = current == opt
                if st.button(
                    f"{icon}  {label}",
                    key=f"catalog_nav_{opt}",
                    use_container_width=True,
                    type="primary" if active else "secondary",
                ):
                    if st.session_state.catalog_view != opt:
                        st.session_state.catalog_view = opt
                        if opt == "Catálogo":
                            st.session_state.catalog_limit = 20
                        st.rerun()
    with bar_title:
        st.markdown(
            f'<div class="catalog-topbar-title-wrap">'
            f'<span class="catalog-topbar-title">{html.escape(current_label)}</span>'
            f"</div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    return st.session_state.catalog_view


def render_category_filter(
    filter_options: list[str],
    session_key: str = "catalog_category",
) -> str:
    """Dropdown compacto de categorias (uma linha)."""
    if session_key not in st.session_state:
        st.session_state[session_key] = filter_options[0]

    current = st.session_state[session_key]
    if current not in filter_options:
        current = filter_options[0]
        st.session_state[session_key] = current

    st.markdown(
        '<span class="catalog-filter-label">Categoria</span>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="catalog-filter-wrap">', unsafe_allow_html=True)
    selected = st.selectbox(
        "Categoria",
        options=filter_options,
        index=filter_options.index(current),
        label_visibility="collapsed",
        key="catalog_category_select",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if selected != st.session_state[session_key]:
        st.session_state[session_key] = selected
        st.session_state.catalog_limit = 20
        st.rerun()

    return st.session_state[session_key]
