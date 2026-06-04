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
    """Estilos dos botões de ação com logos oficiais."""
    st.markdown(
        """
        <style>
        :root {
            --catalog-action-icon: 1.05rem;
        }

        /* Pix: ícone HTML sobre o botão (mesma coluna) */
        [data-testid="column"]:has(.catalog-pix-icon-wrap) {
            position: relative !important;
        }

        [data-testid="column"]:has(.catalog-pix-icon-wrap) [data-testid="stMarkdownContainer"] {
            height: 0 !important;
            min-height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: visible !important;
        }

        .catalog-pix-icon-wrap {
            position: absolute !important;
            inset: 0 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            pointer-events: none !important;
            z-index: 2 !important;
        }

        .catalog-pix-icon-wrap img {
            display: block !important;
            width: var(--catalog-action-icon) !important;
            height: var(--catalog-action-icon) !important;
            max-width: var(--catalog-action-icon) !important;
            max-height: var(--catalog-action-icon) !important;
            object-fit: contain !important;
            transform: scale(0.82) !important;
        }

        [data-testid="column"]:has(.catalog-pix-icon-wrap) div[data-testid="stButton"] {
            position: relative !important;
            z-index: 1 !important;
        }

        [data-testid="column"]:has(.catalog-pix-icon-wrap) div[data-testid="stButton"] > button {
            min-height: 2.15rem !important;
            font-size: 0 !important;
            color: transparent !important;
            line-height: 0 !important;
        }

        a.catalog-brand-wa {
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
        }

        a.catalog-brand-wa:hover {
            border-color: #25D366 !important;
            background: #f6fff8 !important;
        }

        a.catalog-brand-wa img {
            display: block !important;
            width: var(--catalog-action-icon) !important;
            height: var(--catalog-action-icon) !important;
            max-width: var(--catalog-action-icon) !important;
            max-height: var(--catalog-action-icon) !important;
            object-fit: contain !important;
        }

        @media (max-width: 480px) {
            :root {
                --catalog-action-icon: 0.95rem;
            }
            [data-testid="column"]:has(.catalog-pix-icon-wrap) div[data-testid="stButton"] > button,
            a.catalog-brand-wa {
                min-height: 1.85rem !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _pix_icon_html(*, primary: bool, disabled: bool) -> str:
    icon_file = "pix.svg" if disabled or not primary else "pix-white.svg"
    icon = icon_data_uri(icon_file)
    return (
        f'<div class="catalog-pix-icon-wrap">'
        f'<img src="{icon}" alt="Pix">'
        f"</div>"
    )


def render_pix_button(
    *,
    key: str,
    disabled: bool = False,
    primary: bool = False,
) -> bool:
    """Botão Pix com logo oficial centralizado no botão."""
    help_text = HELP_PIX_OFF if disabled else HELP_PIX
    st.markdown(_pix_icon_html(primary=primary, disabled=disabled), unsafe_allow_html=True)
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
        f'<a href="{safe_url}" target="_blank" rel="noopener noreferrer" '
        f'class="catalog-brand-wa" title="{HELP_WA}">'
        f'<img src="{icon}" alt="WhatsApp"></a>',
        unsafe_allow_html=True,
    )
