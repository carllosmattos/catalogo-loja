"""Tema visual mobile-first com cores da loja."""

from __future__ import annotations

import streamlit as st


DEFAULT_COLORS = {
    "primary_color": "#E1306C",
    "secondary_color": "#833AB4",
    "accent_color": "#FCAF45",
}


def inject_theme(settings: dict | None = None, hide_sidebar: bool = False):
    primary = (settings or {}).get("primary_color", DEFAULT_COLORS["primary_color"])
    secondary = (settings or {}).get(
        "secondary_color", DEFAULT_COLORS["secondary_color"]
    )
    accent = (settings or {}).get("accent_color", DEFAULT_COLORS["accent_color"])

    sidebar_css = ""
    if hide_sidebar:
        sidebar_css = """
        [data-testid="stSidebar"] { display: none; }
        [data-testid="collapsedControl"] { display: none; }
        """

    st.markdown(
        f"""
        <style>
        :root {{
            --primary: {primary};
            --secondary: {secondary};
            --accent: {accent};
        }}

        {sidebar_css}

        .block-container {{
            padding-top: 1rem;
            padding-bottom: 2rem;
            max-width: 480px;
        }}

        .store-header {{
            text-align: center;
            padding: 1rem 0 1.5rem;
        }}

        .store-header img {{
            max-height: 80px;
            border-radius: 50%;
            object-fit: cover;
        }}

        .store-name {{
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--primary);
            margin-top: 0.5rem;
        }}

        .product-card {{
            border: 1px solid #efefef;
            border-radius: 12px;
            overflow: hidden;
            margin-bottom: 1rem;
            background: #fff;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }}

        .product-card img {{
            width: 100%;
            aspect-ratio: 1;
            object-fit: cover;
        }}

        .product-info {{
            padding: 0.75rem 1rem 1rem;
        }}

        .product-name {{
            font-weight: 600;
            font-size: 1rem;
            color: #262626;
        }}

        .product-price {{
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--primary);
        }}

        .product-price-old {{
            text-decoration: line-through;
            color: #999;
            font-size: 0.85rem;
            margin-right: 0.5rem;
        }}

        .promo-badge {{
            display: inline-block;
            background: var(--accent);
            color: #fff;
            font-size: 0.75rem;
            font-weight: 600;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            margin-bottom: 0.25rem;
        }}

        .gift-tag {{
            font-size: 0.8rem;
            color: var(--secondary);
            margin-top: 0.25rem;
        }}

        div.stButton > button[kind="primary"] {{
            background-color: var(--primary);
            border-color: var(--primary);
            width: 100%;
            border-radius: 8px;
            font-weight: 600;
        }}

        div.stButton > button[kind="primary"]:hover {{
            background-color: var(--secondary);
            border-color: var(--secondary);
        }}

        .out-of-stock {{
            opacity: 0.6;
        }}

        .profit-positive {{ color: #28a745; font-weight: 600; }}
        .profit-negative {{ color: #dc3545; font-weight: 600; }}
        .profit-warning {{ color: #ffc107; font-weight: 600; }}
        </style>
        """,
        unsafe_allow_html=True,
    )
