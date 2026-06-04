"""Navegação do catálogo público — menu lateral (sidebar)."""

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


def _select_view(opt: str, cart_count: int) -> None:
    st.session_state.catalog_menu_open = False
    if st.session_state.catalog_view != opt:
        st.session_state.catalog_view = opt
        if opt == "Catálogo":
            st.session_state.catalog_limit = 20
    st.rerun()


def _inject_sidebar_nav_css(menu_open: bool) -> None:
    if menu_open:
        mobile_transform = "transform: translateX(0) !important; pointer-events: auto !important;"
        mobile_backdrop = """
            [data-testid="stAppViewContainer"]::before {
                content: "";
                position: fixed;
                inset: 0;
                background: rgba(0, 0, 0, 0.42);
                z-index: 9998;
                pointer-events: none;
            }
        """
    else:
        mobile_transform = (
            "transform: translateX(-100%) !important; pointer-events: none !important;"
        )
        mobile_backdrop = ""

    st.markdown(
        f"""
        <style>
        section[data-testid="stSidebar"] {{
            background: #fff;
            border-right: 1px solid #f0e0ea;
        }}

        section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {{
            padding-top: 0.75rem;
        }}

        section[data-testid="stSidebar"] div.stButton > button {{
            justify-content: flex-start !important;
            text-align: left !important;
            font-size: 0.88rem !important;
            min-height: 2.35rem !important;
            border-radius: 8px !important;
            margin-bottom: 0.2rem !important;
        }}

        section[data-testid="stSidebar"] .catalog-sidebar-close div.stButton > button {{
            font-size: 0.82rem !important;
            min-height: 2rem !important;
            color: #666 !important;
            border-color: #e8e8e8 !important;
        }}

        [data-testid="collapsedControl"],
        [data-testid="stSidebarCollapsedControl"] {{
            display: none !important;
        }}

        .catalog-topbar {{
            position: relative;
            z-index: 10001;
        }}

        @media (min-width: 769px) {{
            section[data-testid="stSidebar"] {{
                display: block !important;
                visibility: visible !important;
                transform: none !important;
                position: relative !important;
                pointer-events: auto !important;
            }}
            .catalog-topbar [data-testid="column"]:first-child {{
                display: none !important;
            }}
        }}

        @media (max-width: 768px) {{
            [data-testid="stAppViewContainer"] > [data-testid="stMain"],
            [data-testid="stAppViewContainer"] > .main {{
                margin-left: 0 !important;
                width: 100% !important;
                max-width: 100% !important;
            }}

            section[data-testid="stSidebar"] {{
                display: block !important;
                visibility: visible !important;
                position: fixed !important;
                left: 0 !important;
                top: 0 !important;
                height: 100vh !important;
                width: min(280px, 85vw) !important;
                min-width: unset !important;
                z-index: 9999 !important;
                box-shadow: 4px 0 24px rgba(0, 0, 0, 0.18);
                transition: transform 0.28s ease;
                {mobile_transform}
            }}
            {mobile_backdrop}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_catalog_nav(
    options: list[str],
    *,
    cart_count: int = 0,
    store_name: str = "",
) -> str:
    """Barra superior com ☰ (mobile) + navegação na sidebar lateral."""
    if "catalog_view" not in st.session_state:
        st.session_state.catalog_view = options[0]
    if "catalog_menu_open" not in st.session_state:
        st.session_state.catalog_menu_open = False

    current = st.session_state.catalog_view
    menu_open = st.session_state.catalog_menu_open
    current_label = _nav_label(current, cart_count)

    _inject_sidebar_nav_css(menu_open)

    with st.sidebar:
        if menu_open:
            st.markdown('<div class="catalog-sidebar-close">', unsafe_allow_html=True)
            if st.button("✕  Fechar", key="catalog_menu_close", use_container_width=True):
                st.session_state.catalog_menu_open = False
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("---")

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
                _select_view(opt, cart_count)

    st.markdown('<div class="catalog-topbar">', unsafe_allow_html=True)
    bar_menu, bar_title = st.columns([1, 5], gap="small")
    with bar_menu:
        if st.button("☰", key="catalog_menu_toggle", help="Menu"):
            st.session_state.catalog_menu_open = not st.session_state.catalog_menu_open
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
