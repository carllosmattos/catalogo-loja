"""Ícones oficiais de marcas para botões do catálogo."""

from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
ICONS_DIR = ROOT / "resources" / "icons"

# Linha de 3 colunas (🛒 Pix WhatsApp) — distinta da linha de tamanhos (4 colunas)
_ACTION_ROW = (
    'div[data-testid="stHorizontalBlock"]:'
    'has(> div[data-testid="column"]:nth-child(3)):'
    'not(:has(> div[data-testid="column"]:nth-child(4)))'
)


def icon_data_uri(filename: str) -> str:
    """Retorna data URI do SVG para uso em HTML/CSS."""
    content = (ICONS_DIR / filename).read_bytes()
    b64 = base64.b64encode(content).decode("ascii")
    return f"data:image/svg+xml;base64,{b64}"


def _css_url(filename: str) -> str:
    return f'url("{icon_data_uri(filename)}")'


def inject_catalog_action_icon_css() -> None:
    """Aplica logos oficiais Pix e WhatsApp nos botões de ação do produto."""
    pix = _css_url("pix.svg")
    pix_white = _css_url("pix-white.svg")
    whatsapp = _css_url("whatsapp.svg")

    pix_btn = f"{_ACTION_ROW} > div[data-testid=\"column\"]:nth-child(2) div.stButton > button"
    wa_btn = (
        f"{_ACTION_ROW} > div[data-testid=\"column\"]:nth-child(3) "
        f'a[data-testid="stLinkButton"]'
    )

    st.markdown(
        f"""
        <style>
        {pix_btn} {{
            position: relative !important;
            color: transparent !important;
            font-size: 0 !important;
            line-height: 0 !important;
            overflow: hidden !important;
        }}

        {pix_btn}::before {{
            content: "" !important;
            display: block !important;
            width: 1.35rem !important;
            height: 1.35rem !important;
            margin: 0 auto !important;
            background-image: {pix} !important;
            background-repeat: no-repeat !important;
            background-position: center center !important;
            background-size: contain !important;
        }}

        {pix_btn}[kind="primary"]::before,
        {pix_btn}[data-testid="baseButton-primary"]::before {{
            background-image: {pix_white} !important;
        }}

        {wa_btn} {{
            position: relative !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            color: transparent !important;
            font-size: 0 !important;
            line-height: 0 !important;
            overflow: hidden !important;
            min-height: 2.15rem !important;
        }}

        {wa_btn} p {{
            display: none !important;
        }}

        {wa_btn}::before {{
            content: "" !important;
            display: block !important;
            width: 1.35rem !important;
            height: 1.35rem !important;
            margin: 0 auto !important;
            background-image: {whatsapp} !important;
            background-repeat: no-repeat !important;
            background-position: center center !important;
            background-size: contain !important;
        }}

        @media (max-width: 480px) {{
            {pix_btn}::before,
            {wa_btn}::before {{
                width: 1.15rem !important;
                height: 1.15rem !important;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
