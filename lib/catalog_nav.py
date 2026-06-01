"""Navegação compacta do catálogo público."""

from __future__ import annotations

import streamlit as st


def render_catalog_nav(
    options: list[str],
    *,
    cart_count: int = 0,
) -> str:
    """Barra de abas compacta (3 colunas). Retorna a view ativa."""
    if "catalog_view" not in st.session_state:
        st.session_state.catalog_view = options[0]

    labels = []
    for opt in options:
        if opt == "Carrinho" and cart_count > 0:
            labels.append(f"Carrinho ({cart_count})")
        else:
            labels.append(opt)

    st.markdown('<div class="catalog-nav-compact">', unsafe_allow_html=True)
    cols = st.columns(len(options))
    for col, opt, label in zip(cols, options, labels):
        with col:
            active = st.session_state.catalog_view == opt
            if st.button(
                label,
                key=f"catalog_nav_{opt}",
                use_container_width=True,
                type="primary" if active else "secondary",
            ):
                if st.session_state.catalog_view != opt:
                    st.session_state.catalog_view = opt
                    st.rerun()
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
        st.session_state.catalog_page = 1
        st.rerun()

    return st.session_state[session_key]
