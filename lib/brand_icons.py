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


def icon_data_uri(filename: str) -> str:
    """Retorna data URI do SVG para uso em HTML."""
    content = (ICONS_DIR / filename).read_bytes()
    b64 = base64.b64encode(content).decode("ascii")
    return f"data:image/svg+xml;base64,{b64}"


def inject_catalog_action_icon_css() -> None:
    """Estilos Pix (aria-label) e link WhatsApp."""
    pix = icon_data_uri("pix.svg")
    pix_white = icon_data_uri("pix-white.svg")

    st.markdown(
        f"""
        <style>
        button[title="{HELP_PIX}"],
        button[aria-label="{HELP_PIX}"] {{
            font-size: 0 !important;
            color: transparent !important;
            line-height: 0 !important;
            min-height: 2.15rem !important;
        }}

        button[title="{HELP_PIX}"]::before,
        button[aria-label="{HELP_PIX}"]::before {{
            content: "" !important;
            display: block !important;
            width: 1.35rem !important;
            height: 1.35rem !important;
            margin: 0 auto !important;
            background: url("{pix_white}") center/contain no-repeat !important;
        }}

        button[title="{HELP_PIX_OFF}"],
        button[aria-label="{HELP_PIX_OFF}"] {{
            font-size: 0 !important;
            color: transparent !important;
            line-height: 0 !important;
            min-height: 2.15rem !important;
        }}

        button[title="{HELP_PIX_OFF}"]::before,
        button[aria-label="{HELP_PIX_OFF}"]::before {{
            content: "" !important;
            display: block !important;
            width: 1.35rem !important;
            height: 1.35rem !important;
            margin: 0 auto !important;
            background: url("{pix}") center/contain no-repeat !important;
        }}

        a.catalog-brand-wa {{
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: 100% !important;
            min-height: 2.15rem !important;
            padding: 0.28rem 0.15rem !important;
            border: 1px solid rgba(49, 51, 63, 0.2) !important;
            border-radius: 0.5rem !important;
            background: #fff !important;
            text-decoration: none !important;
            box-sizing: border-box !important;
        }}

        a.catalog-brand-wa:hover {{
            border-color: #25D366 !important;
            background: #f6fff8 !important;
        }}

        a.catalog-brand-wa img {{
            display: block !important;
            width: 1.35rem !important;
            height: 1.35rem !important;
        }}

        @media (max-width: 480px) {{
            button[title="{HELP_PIX}"]::before,
            button[title="{HELP_PIX_OFF}"]::before,
            button[aria-label="{HELP_PIX}"]::before,
            button[aria-label="{HELP_PIX_OFF}"]::before,
            a.catalog-brand-wa img {{
                width: 1.15rem !important;
                height: 1.15rem !important;
            }}
            a.catalog-brand-wa {{
                min-height: 1.85rem !important;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_whatsapp_action(url: str) -> None:
    """Link WhatsApp com logo oficial."""
    icon = icon_data_uri("whatsapp.svg")
    safe_url = html.escape(url, quote=True)
    st.markdown(
        f'<a href="{safe_url}" target="_blank" rel="noopener noreferrer" '
        f'class="catalog-brand-wa" title="{HELP_WA}">'
        f'<img src="{icon}" alt="WhatsApp"></a>',
        unsafe_allow_html=True,
    )
