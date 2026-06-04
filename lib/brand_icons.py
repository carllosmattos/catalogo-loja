"""Ícones oficiais de marcas para botões do catálogo."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import quote

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
ICONS_DIR = ROOT / "resources" / "icons"

_ACTION_ROW = (
    '.catalog-product-grid div[data-testid="stHorizontalBlock"]:'
    'has(> div[data-testid="column"]:nth-child(3)):'
    'not(:has(> div[data-testid="column"]:nth-child(4)))'
)


def _svg_data_url(filename: str) -> str:
    content = (ICONS_DIR / filename).read_text(encoding="utf-8")
    return f'url("data:image/svg+xml,{quote(content)}")'


def inject_catalog_action_icon_css() -> None:
    """Aplica logos oficiais Pix e WhatsApp nos botões de ação do produto."""
    pix = _svg_data_url("pix.svg")
    pix_white = _svg_data_url("pix-white.svg")
    whatsapp = _svg_data_url("whatsapp.svg")

    st.markdown(
        f"""
        <style>
        {_ACTION_ROW} > div[data-testid="column"]:nth-child(2) button {{
            color: transparent !important;
            font-size: 0 !important;
            background-image: {pix} !important;
            background-repeat: no-repeat !important;
            background-position: center center !important;
            background-size: 1.35rem auto !important;
        }}

        {_ACTION_ROW} > div[data-testid="column"]:nth-child(2) button[kind="primary"] {{
            background-image: {pix_white} !important;
        }}

        {_ACTION_ROW} > div[data-testid="column"]:nth-child(3) a {{
            color: transparent !important;
            font-size: 0 !important;
            background-image: {whatsapp} !important;
            background-repeat: no-repeat !important;
            background-position: center center !important;
            background-size: 1.35rem auto !important;
        }}

        @media (max-width: 480px) {{
            {_ACTION_ROW} > div[data-testid="column"]:nth-child(2) button,
            {_ACTION_ROW} > div[data-testid="column"]:nth-child(3) a {{
                background-size: 1.2rem auto !important;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
