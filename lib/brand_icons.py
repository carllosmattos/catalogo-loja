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

        [data-testid="column"]:has(.catalog-brand-hit) .catalog-brand-hit {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: 100% !important;
            min-height: 2.15rem !important;
            margin-bottom: -2.15rem !important;
            position: relative !important;
            z-index: 2 !important;
            pointer-events: none !important;
            box-sizing: border-box !important;
        }

        .catalog-brand-hit img,
        a.catalog-brand-wa img {
            display: block !important;
            width: var(--catalog-action-icon) !important;
            height: var(--catalog-action-icon) !important;
            max-width: var(--catalog-action-icon) !important;
            max-height: var(--catalog-action-icon) !important;
            object-fit: contain !important;
        }

        .catalog-brand-hit--pix img {
            transform: scale(0.78) !important;
        }

        [data-testid="column"]:has(.catalog-brand-hit) div[data-testid="stButton"] > button,
        [data-testid="column"]:has(.catalog-brand-hit) div[data-testid="stButton"] > button:hover {
            min-height: 2.15rem !important;
            opacity: 0 !important;
            position: relative !important;
            z-index: 3 !important;
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
        }

        @media (max-width: 480px) {
            :root {
                --catalog-action-icon: 0.95rem;
            }
            [data-testid="column"]:has(.catalog-brand-hit) .catalog-brand-hit {
                min-height: 1.85rem !important;
                margin-bottom: -1.85rem !important;
            }
            [data-testid="column"]:has(.catalog-brand-hit) div[data-testid="stButton"] > button {
                min-height: 1.85rem !important;
            }
            a.catalog-brand-wa {
                min-height: 1.85rem !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _brand_hit(icon_file: str, alt: str) -> None:
    icon = icon_data_uri(icon_file)
    pix_class = " catalog-brand-hit--pix" if alt == "Pix" else ""
    st.markdown(
        f'<div class="catalog-brand-hit{pix_class}">'
        f'<img src="{icon}" alt="{html.escape(alt)}">'
        f"</div>",
        unsafe_allow_html=True,
    )


def render_pix_button(
    *,
    key: str,
    disabled: bool = False,
    primary: bool = False,
) -> bool:
    """Botão Pix com logo oficial (clique invisível sobre o ícone)."""
    icon_file = "pix.svg" if disabled or not primary else "pix-white.svg"
    help_text = HELP_PIX_OFF if disabled else HELP_PIX
    _brand_hit(icon_file, "Pix")
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
