"""Navegação do catálogo público — sidebar colapsável."""

from __future__ import annotations

import html

import streamlit as st

from lib.branding import BRAND_FONT, brand_display_lines

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


def _brand_header_html(line1: str, line2: str) -> str:
    return (
        f'<div class="catalog-fixed-brand">'
        f'<div class="catalog-brand-lm">{html.escape(line1)}</div>'
        f'<div class="catalog-brand-tagline">{html.escape(line2)}</div>'
        f"</div>"
    )


def _inject_catalog_nav_css() -> None:
    st.markdown(
        f"""
        <style>
        .catalog-fixed-header-anchor + div[data-testid="stHorizontalBlock"] {{
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            width: 100% !important;
            max-width: 100% !important;
            z-index: 10005 !important;
            background: #fff !important;
            border-bottom: 1px solid #f0e0ea !important;
            box-shadow: 0 2px 12px rgba(199, 21, 133, 0.08) !important;
            padding: 0.42rem 0.65rem 0.48rem !important;
            margin: 0 !important;
            align-items: center !important;
        }}

        .catalog-fixed-header-anchor + div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {{
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }}

        .catalog-fixed-header-anchor + div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child {{
            justify-content: flex-start !important;
        }}

        .catalog-fixed-header-anchor + div[data-testid="stHorizontalBlock"] button {{
            font-family: {BRAND_FONT} !important;
            font-weight: 700 !important;
            font-size: 1.35rem !important;
            color: var(--primary) !important;
            background: transparent !important;
            border: 1px solid transparent !important;
            box-shadow: none !important;
            min-height: 2.45rem !important;
            min-width: 2.45rem !important;
            padding: 0 0.35rem !important;
            line-height: 1 !important;
        }}

        .catalog-fixed-header-anchor + div[data-testid="stHorizontalBlock"] button:hover {{
            color: var(--primary) !important;
            background: #fff5f8 !important;
            border-color: #f0e0ea !important;
        }}

        .catalog-fixed-brand {{
            text-align: center;
            font-family: {BRAND_FONT};
            line-height: 1.05;
            width: 100%;
        }}

        .catalog-brand-lm {{
            font-size: 1.22rem;
            font-weight: 700;
            color: var(--primary);
            letter-spacing: 0.05em;
        }}

        .catalog-brand-tagline {{
            font-size: 0.68rem;
            font-weight: 600;
            color: var(--secondary);
            letter-spacing: 0.12em;
            text-transform: lowercase;
            margin-top: 0.06rem;
        }}

        .catalog-fixed-spacer {{
            width: 2.45rem;
            min-height: 1px;
        }}

        @media (min-width: 769px) {{
            .catalog-fixed-header-anchor + div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child,
            .catalog-fixed-header-anchor + div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:last-child {{
                display: none !important;
            }}
        }}

        @media (max-width: 768px) {{
            [data-testid="collapsedControl"],
            [data-testid="stSidebarCollapsedControl"] {{
                display: none !important;
            }}

            section[data-testid="stSidebar"] {{
                display: none !important;
            }}
        }}

        @media (min-width: 769px) {{
            [data-testid="collapsedControl"],
            [data-testid="stSidebarCollapsedControl"] {{
                top: 3.65rem !important;
            }}
        }}

        div[data-testid="stDialogBackdrop"] {{
            background: transparent !important;
        }}

        div[data-testid="stDialog"] {{
            padding: 0 !important;
            background: transparent !important;
            align-items: flex-start !important;
            justify-content: flex-start !important;
        }}

        div[data-testid="stDialog"] > div,
        div[data-testid="stDialog"] [data-testid="stModalContainer"],
        div[data-testid="stDialog"] [role="dialog"] {{
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
        }}

        div[data-testid="stDialog"] button[aria-label="Close"],
        div[data-testid="stDialog"] [data-testid="stModalCloseButton"] {{
            color: #666 !important;
        }}
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
    """Header fixo LM + menu lateral."""
    if "catalog_view" not in st.session_state:
        st.session_state.catalog_view = options[0]

    current = st.session_state.catalog_view
    line1, line2 = brand_display_lines(store_name)

    _inject_catalog_nav_css()

    with st.sidebar:
        _render_nav_buttons(
            options,
            cart_count=cart_count,
            current=current,
            key_prefix="catalog_nav",
        )

    st.markdown('<div class="catalog-fixed-header-anchor"></div>', unsafe_allow_html=True)
    menu_col, brand_col, spacer_col = st.columns([1, 4, 1], gap="small")
    with menu_col:
        if st.button("M", key="catalog_menu_toggle", help="Menu"):
            _catalog_mobile_menu(
                options,
                cart_count=cart_count,
                current=current,
            )
    with brand_col:
        st.markdown(_brand_header_html(line1, line2), unsafe_allow_html=True)
    with spacer_col:
        st.markdown('<div class="catalog-fixed-spacer"></div>', unsafe_allow_html=True)

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
