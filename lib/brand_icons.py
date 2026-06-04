"""Ícones oficiais de marcas para botões do catálogo."""

from __future__ import annotations

import base64
import html
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
ICONS_DIR = ROOT / "resources" / "icons"

HELP_PIX = "Pagar com PIX"
HELP_PIX_OFF = "Complete seu cadastro para pagar com PIX"
HELP_WA = "Comprar pelo WhatsApp"

_ACTION_ROW = (
    '.catalog-product-grid div[data-testid="stHorizontalBlock"]:'
    'has(> div[data-testid="column"]:nth-child(3)):'
    'not(:has(> div[data-testid="column"]:nth-child(4)))'
)


def icon_data_uri(filename: str) -> str:
    """Retorna data URI do SVG para uso em HTML."""
    content = (ICONS_DIR / filename).read_bytes()
    b64 = base64.b64encode(content).decode("ascii")
    return f"data:image/svg+xml;base64,{b64}"


def inject_catalog_action_icon_css() -> None:
    """Estilos dos botões de ação com logos oficiais."""
    pix = icon_data_uri("pix.svg")
    pix_white = icon_data_uri("pix-white.svg")

    st.markdown(
        f"""
        <style>
        :root {{
            --catalog-action-icon: 1.05rem;
            --catalog-pix-icon: calc(var(--catalog-action-icon) * 0.82);
            --catalog-action-btn-height: 2.25rem;
        }}

        /* Altura uniforme: carrinho, Pix e WhatsApp */
        {_ACTION_ROW} {{
            align-items: stretch !important;
        }}

        {_ACTION_ROW} > [data-testid="column"] {{
            display: flex !important;
            align-items: stretch !important;
        }}

        {_ACTION_ROW} > [data-testid="column"] .stElementContainer,
        {_ACTION_ROW} > [data-testid="column"] div.stButton,
        {_ACTION_ROW} > [data-testid="column"] [data-testid="stMarkdownContainer"],
        {_ACTION_ROW} > [data-testid="column"] .catalog-action-cell {{
            width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
            height: var(--catalog-action-btn-height) !important;
            min-height: var(--catalog-action-btn-height) !important;
            max-height: var(--catalog-action-btn-height) !important;
            display: flex !important;
            align-items: stretch !important;
            box-sizing: border-box !important;
        }}

        {_ACTION_ROW} > [data-testid="column"] div.stButton {{
            flex: 1 1 auto !important;
        }}

        [class*="st-key-add_"] button,
        [class*="st-key-buy_pix_off_"] button,
        [class*="st-key-buy_pix_"]:not([class*="buy_pix_off"]) button,
        a.catalog-brand-wa {{
            width: 100% !important;
            height: var(--catalog-action-btn-height) !important;
            min-height: var(--catalog-action-btn-height) !important;
            max-height: var(--catalog-action-btn-height) !important;
            padding: 0 !important;
            margin: 0 !important;
            box-sizing: border-box !important;
            border-radius: 0.5rem !important;
            line-height: 1 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }}

        /* Pix: logo dentro do botão */
        [class*="st-key-buy_pix_off_"] button,
        [class*="st-key-buy_pix_"]:not([class*="buy_pix_off"]) button {{
            font-size: 0 !important;
            color: transparent !important;
            position: relative !important;
        }}

        [class*="st-key-buy_pix_off_"] button > div,
        [class*="st-key-buy_pix_"]:not([class*="buy_pix_off"]) button > div,
        [class*="st-key-buy_pix_off_"] button p,
        [class*="st-key-buy_pix_"]:not([class*="buy_pix_off"]) button p {{
            display: none !important;
            width: 0 !important;
            height: 0 !important;
            overflow: hidden !important;
            margin: 0 !important;
            padding: 0 !important;
        }}

        [class*="st-key-buy_pix_off_"] button::before,
        [class*="st-key-buy_pix_"]:not([class*="buy_pix_off"]) button::before {{
            content: "" !important;
            display: block !important;
            position: absolute !important;
            left: 50% !important;
            top: 50% !important;
            transform: translate(-50%, -50%) !important;
            width: var(--catalog-pix-icon) !important;
            height: var(--catalog-pix-icon) !important;
            background-repeat: no-repeat !important;
            background-position: center center !important;
            background-size: contain !important;
            margin: 0 !important;
        }}

        [class*="st-key-buy_pix_off_"] button::before {{
            background-image: url("{pix}") !important;
        }}

        [class*="st-key-buy_pix_"]:not([class*="buy_pix_off"]) button::before {{
            background-image: url("{pix_white}") !important;
        }}

        .catalog-action-cell {{
            width: 100% !important;
            height: var(--catalog-action-btn-height) !important;
            min-height: var(--catalog-action-btn-height) !important;
            max-height: var(--catalog-action-btn-height) !important;
            display: flex !important;
            align-items: stretch !important;
            margin: 0 !important;
            padding: 0 !important;
            box-sizing: border-box !important;
        }}

        a.catalog-brand-wa {{
            border: 1px solid rgba(49, 51, 63, 0.2) !important;
            background: #fff !important;
            text-decoration: none !important;
        }}

        a.catalog-brand-wa:hover {{
            border-color: #25D366 !important;
            background: #f6fff8 !important;
        }}

        a.catalog-brand-wa img {{
            display: block !important;
            width: var(--catalog-action-icon) !important;
            height: var(--catalog-action-icon) !important;
            max-width: var(--catalog-action-icon) !important;
            max-height: var(--catalog-action-icon) !important;
            object-fit: contain !important;
        }}

        @media (max-width: 480px) {{
            :root {{
                --catalog-action-icon: 0.95rem;
                --catalog-action-btn-height: 2rem;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_pix_button(
    *,
    key: str,
    disabled: bool = False,
    primary: bool = False,
) -> bool:
    """Botão Pix com logo oficial (::before no botão dentro de st-key-*)."""
    help_text = HELP_PIX_OFF if disabled else HELP_PIX
    return st.button(
        "\u200b",
        key=key,
        help=help_text,
        disabled=disabled,
        type="primary" if primary and not disabled else "secondary",
        use_container_width=True,
    )


def render_whatsapp_action(url: str) -> None:
    """Link WhatsApp com logo oficial."""
    icon = icon_data_uri("whatsapp.svg")
    safe_url = html.escape(url, quote=True)
    st.markdown(
        f'<div class="catalog-action-cell">'
        f'<a href="{safe_url}" target="_blank" rel="noopener noreferrer" '
        f'class="catalog-brand-wa" title="{HELP_WA}">'
        f'<img src="{icon}" alt="WhatsApp"></a>'
        f"</div>",
        unsafe_allow_html=True,
    )
