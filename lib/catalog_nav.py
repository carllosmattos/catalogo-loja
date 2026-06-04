"""Navegação do catálogo público — sidebar colapsável."""

from __future__ import annotations

import html

import streamlit as st

from lib.branding import resolve_logo_url

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
        /* Barra fixa — título e logo em HTML (grid estável); botão ☰ sobrepõe via .st-key-catalog_menu_toggle */
        .catalog-header-bar {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            width: 100% !important;
            max-width: 100% !important;
            height: var(--catalog-header-height, 3.25rem) !important;
            min-height: var(--catalog-header-height, 3.25rem) !important;
            max-height: var(--catalog-header-height, 3.25rem) !important;
            display: grid !important;
            grid-template-columns: 2.55rem minmax(0, 1fr) auto !important;
            align-items: center !important;
            gap: 0.35rem !important;
            padding: 0 0.5rem !important;
            box-sizing: border-box !important;
            z-index: 10010 !important;
            background: var(--catalog-header-bg, var(--accent)) !important;
            border-bottom: 1px solid color-mix(in srgb, var(--primary) 22%, transparent) !important;
            margin: 0 !important;
            pointer-events: none !important;
        }

        .catalog-header-bar__menu {
            width: 2.55rem !important;
            height: 2.4rem !important;
            flex-shrink: 0 !important;
        }

        .catalog-header-bar__title {
            font-family: Georgia, "Times New Roman", serif;
            font-size: 0.95rem;
            font-weight: 700;
            color: var(--primary);
            line-height: 1 !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            white-space: nowrap !important;
            min-width: 0 !important;
            pointer-events: auto !important;
        }

        .catalog-header-bar__logo {
            display: flex !important;
            align-items: center !important;
            justify-content: flex-end !important;
            line-height: 0 !important;
            pointer-events: auto !important;
        }

        .catalog-header-bar__logo img {
            display: block !important;
            max-height: 2.1rem !important;
            max-width: 2.75rem !important;
            width: auto !important;
            height: auto !important;
            object-fit: contain !important;
        }

        div.stElementContainer.st-key-catalog_menu_toggle,
        [class*="st-key-catalog_menu_toggle"].stElementContainer,
        div[class*="st-key-catalog_menu_toggle"] {
            position: fixed !important;
            top: calc((var(--catalog-header-height, 3.25rem) - 2.4rem) / 2) !important;
            left: max(0.5rem, env(safe-area-inset-left)) !important;
            width: 2.4rem !important;
            height: 2.4rem !important;
            min-width: 2.4rem !important;
            min-height: 2.4rem !important;
            max-width: 2.4rem !important;
            max-height: 2.4rem !important;
            z-index: 10012 !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        div.stElementContainer.st-key-catalog_menu_toggle div.stButton,
        [class*="st-key-catalog_menu_toggle"] div.stButton {
            width: 2.4rem !important;
            height: 2.4rem !important;
            min-width: 2.4rem !important;
            min-height: 2.4rem !important;
            margin: 0 !important;
        }

        div.stElementContainer.st-key-catalog_menu_toggle button,
        [class*="st-key-catalog_menu_toggle"] button {
            width: 2.4rem !important;
            height: 2.4rem !important;
            min-width: 2.4rem !important;
            min-height: 2.4rem !important;
            max-width: 2.4rem !important;
            max-height: 2.4rem !important;
            padding: 0 !important;
            margin: 0 !important;
            font-size: 1.05rem !important;
            line-height: 1 !important;
            border-radius: 8px !important;
            background: #fff !important;
            color: var(--primary) !important;
            border: 1px solid color-mix(in srgb, var(--primary) 28%, transparent) !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            box-sizing: border-box !important;
        }

        @media (max-width: 768px) {
            section[data-testid="stSidebar"] {
                display: none !important;
            }

            .catalog-header-bar {
                grid-template-columns: 2.45rem minmax(0, 1fr) auto !important;
                padding: 0 0.4rem !important;
                padding-left: max(0.4rem, env(safe-area-inset-left)) !important;
                padding-right: max(0.4rem, env(safe-area-inset-right)) !important;
                gap: 0.3rem !important;
            }

            .catalog-header-bar__menu {
                width: 2.45rem !important;
                height: 2.2rem !important;
            }

            .catalog-header-bar__title {
                font-size: 0.82rem !important;
            }

            .catalog-header-bar__logo img {
                max-height: 1.85rem !important;
                max-width: 2.35rem !important;
            }

            div.stElementContainer.st-key-catalog_menu_toggle,
            [class*="st-key-catalog_menu_toggle"].stElementContainer,
            div[class*="st-key-catalog_menu_toggle"] {
                top: calc((var(--catalog-header-height, 3.25rem) - 2.2rem) / 2) !important;
                left: max(0.4rem, env(safe-area-inset-left)) !important;
                width: 2.2rem !important;
                height: 2.2rem !important;
                min-width: 2.2rem !important;
                min-height: 2.2rem !important;
                max-width: 2.2rem !important;
                max-height: 2.2rem !important;
            }

            div.stElementContainer.st-key-catalog_menu_toggle div.stButton,
            div.stElementContainer.st-key-catalog_menu_toggle button,
            [class*="st-key-catalog_menu_toggle"] div.stButton,
            [class*="st-key-catalog_menu_toggle"] button {
                width: 2.2rem !important;
                height: 2.2rem !important;
                min-width: 2.2rem !important;
                min-height: 2.2rem !important;
                max-width: 2.2rem !important;
                max-height: 2.2rem !important;
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

    with st.sidebar:
        _render_nav_buttons(
            options,
            cart_count=cart_count,
            current=current,
            key_prefix="catalog_nav",
        )

    logo_url = resolve_logo_url(None)
    logo_html = ""
    if logo_url:
        safe_logo = html.escape(logo_url, quote=True)
        logo_html = (
            f'<div class="catalog-header-bar__logo">'
            f'<img src="{safe_logo}" alt="LM moda feminina" />'
            f"</div>"
        )

    st.markdown(
        f'<div class="catalog-header-bar">'
        f'<div class="catalog-header-bar__menu" aria-hidden="true"></div>'
        f'<div class="catalog-header-bar__title">{html.escape(current_label)}</div>'
        f"{logo_html}"
        f"</div>",
        unsafe_allow_html=True,
    )

    if st.button(
        "☰",
        key="catalog_menu_toggle",
        help="Abrir menu",
        use_container_width=False,
    ):
        _catalog_mobile_menu(
            options,
            cart_count=cart_count,
            current=current,
        )

    _inject_catalog_nav_css()

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
