"""Navegação do catálogo público — sidebar colapsável."""

from __future__ import annotations

import html

import streamlit as st

NAV_ICONS = {
    "Catálogo": "🏷️",
    "Carrinho": "🛒",
    "Minhas compras": "📦",
    "Minha conta": "👤",
}


def _nav_label(option: str, cart_count: int) -> str:
    if option == "Carrinho" and cart_count > 0:
        return f"Carrinho ({cart_count})"
    return option


def _select_view(opt: str) -> None:
    if st.session_state.catalog_view != opt:
        st.session_state.catalog_view = opt
        if opt == "Catálogo":
            st.session_state.catalog_limit = 20
    st.rerun()


def _inject_catalog_nav_css() -> None:
    st.markdown(
        """
        <style>
        [data-testid="collapsedControl"],
        [data-testid="stSidebarCollapsedControl"] {
            display: flex !important;
            visibility: visible !important;
            z-index: 10002 !important;
        }

        .catalog-topbar {
            position: relative;
            z-index: 10001;
            margin-bottom: 0.35rem;
        }

        .catalog-topbar [data-testid="column"]:first-child button {
            min-height: 2rem !important;
            font-size: 1.05rem !important;
            padding: 0.2rem 0.5rem !important;
            border-radius: 8px !important;
        }

        @media (min-width: 769px) {
            .catalog-topbar [data-testid="column"]:first-child {
                display: none !important;
            }
        }

        @media (max-width: 768px) {
            section[data-testid="stSidebar"] {
                display: none !important;
            }
        }

        /* Menu mobile — drawer branco full-height, sem fundo cinza */
        div[data-testid="stDialogBackdrop"] {
            background: transparent !important;
        }

        div[data-testid="stDialog"] {
            padding: 0 !important;
            background: transparent !important;
            align-items: flex-start !important;
            justify-content: flex-start !important;
        }

        div[data-testid="stDialog"] > div,
        div[data-testid="stDialog"] [data-testid="stModalContainer"],
        div[data-testid="stDialog"] [role="dialog"] {
            position: fixed !important;
            left: 0 !important;
            top: 0 !important;
            margin: 0 !important;
            height: 100dvh !important;
            min-height: 100vh !important;
            max-height: 100vh !important;
            width: min(280px, 88vw) !important;
            max-width: min(280px, 88vw) !important;
            border-radius: 0 !important;
            background: #fff !important;
            box-shadow: 4px 0 20px rgba(0, 0, 0, 0.1) !important;
            padding: 1rem 0.85rem !important;
            box-sizing: border-box !important;
        }

        div[data-testid="stDialog"] button[aria-label="Close"],
        div[data-testid="stDialog"] [data-testid="stModalCloseButton"] {
            color: #666 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_nav_buttons(
    options: list[str],
    *,
    cart_count: int,
    current: str,
    key_prefix: str,
) -> None:
    for opt in options:
        label = _nav_label(opt, cart_count)
        icon = NAV_ICONS.get(opt, "•")
        active = current == opt
        if st.button(
            f"{icon}  {label}",
            key=f"{key_prefix}_{opt}",
            use_container_width=True,
            type="primary" if active else "secondary",
        ):
            _select_view(opt)


@st.dialog("Menu")
def _catalog_mobile_menu(
    options: list[str],
    *,
    cart_count: int,
    current: str,
) -> None:
    _render_nav_buttons(
        options,
        cart_count=cart_count,
        current=current,
        key_prefix="catalog_mobile_nav",
    )


def render_catalog_nav(
    options: list[str],
    *,
    cart_count: int = 0,
    store_name: str = "",
) -> str:
    """Sidebar no desktop; dialog lateral no mobile via botão ☰."""
    if "catalog_view" not in st.session_state:
        st.session_state.catalog_view = options[0]

    current = st.session_state.catalog_view
    current_label = _nav_label(current, cart_count)

    _inject_catalog_nav_css()

    with st.sidebar:
        _render_nav_buttons(
            options,
            cart_count=cart_count,
            current=current,
            key_prefix="catalog_nav",
        )

    st.markdown('<div class="catalog-topbar">', unsafe_allow_html=True)
    bar_menu, bar_title = st.columns([1, 5], gap="small")
    with bar_menu:
        if st.button("☰", key="catalog_menu_toggle", help="Abrir menu"):
            _catalog_mobile_menu(
                options,
                cart_count=cart_count,
                current=current,
            )
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
