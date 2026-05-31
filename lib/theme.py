"""Tema visual mobile-first com cores da loja."""

from __future__ import annotations

import streamlit as st


from lib.branding import DEFAULT_SETTINGS as DEFAULT_COLORS


def inject_theme(settings: dict | None = None, hide_sidebar: bool = False):
    primary = (settings or {}).get("primary_color", DEFAULT_COLORS["primary_color"])
    secondary = (settings or {}).get(
        "secondary_color", DEFAULT_COLORS["secondary_color"]
    )
    accent = (settings or {}).get("accent_color", DEFAULT_COLORS["accent_color"])

    sidebar_css = ""
    if hide_sidebar:
        sidebar_css = """
        [data-testid="stSidebar"] { display: none !important; }
        [data-testid="collapsedControl"] { display: none !important; }
        [data-testid="stSidebarCollapsedControl"] { display: none !important; }
        [data-testid="stHeader"] { display: none !important; }
        [data-testid="stToolbar"] { display: none !important; }
        [data-testid="stDecoration"] { display: none !important; }
        #MainMenu { visibility: hidden !important; }
        footer { visibility: hidden !important; }
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
            padding-top: 2.5rem;
            padding-bottom: 2rem;
            max-width: 720px;
        }}

        .catalog-grid-row {{
            margin-bottom: 0.5rem;
        }}

        div[data-testid="column"] .product-card {{
            margin-bottom: 0.65rem;
            height: 100%;
        }}

        .product-card-compact {{
            box-shadow: 0 2px 12px rgba(199, 21, 133, 0.1);
        }}

        .product-card-compact .product-photo-empty {{
            min-height: 120px;
        }}

        .product-card-compact .product-badges {{
            top: 6px;
            left: 6px;
            right: 6px;
            gap: 4px;
        }}

        .product-card-compact .badge {{
            padding: 0.3rem 0.5rem;
            font-size: 0.72rem;
        }}

        .product-card-compact .product-info {{
            padding: 0.65rem 0.7rem 0.75rem;
        }}

        .product-category {{
            font-size: 0.68rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: var(--secondary);
            margin-bottom: 0.2rem;
            overflow-wrap: anywhere;
            word-break: break-word;
        }}

        .product-card-compact .product-name {{
            font-size: 0.92rem;
            line-height: 1.25;
            overflow-wrap: anywhere;
            word-break: break-word;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}

        .product-card-compact .product-size {{
            font-size: 0.78rem;
        }}

        .product-desc-clamp {{
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            font-size: 0.8rem;
            margin-top: 0.35rem;
            padding-top: 0.35rem;
            overflow-wrap: anywhere;
            word-break: break-word;
        }}

        .product-card-compact .price-block {{
            margin-top: 0.5rem;
            padding: 0.45rem 0.55rem;
        }}

        .product-card-compact .price-current {{
            font-size: 1.05rem;
        }}

        .gift-compact {{
            margin-top: 0.4rem;
            font-size: 0.72rem;
            color: var(--primary);
            font-weight: 600;
            overflow-wrap: anywhere;
            word-break: break-word;
            line-height: 1.3;
        }}

        .product-card-compact .stock-out {{
            margin-top: 0.45rem;
            font-size: 0.78rem;
            padding: 0.35rem;
        }}

        .catalog-filter-wrap {{
            margin-bottom: 0.75rem;
        }}

        div[role="radiogroup"].catalog-categories {{
            flex-wrap: nowrap !important;
            overflow-x: auto;
            justify-content: flex-start !important;
            -webkit-overflow-scrolling: touch;
            padding-bottom: 0.25rem;
        }}

        div[role="radiogroup"].catalog-categories label {{
            flex-shrink: 0;
            white-space: nowrap;
            font-size: 0.82rem !important;
            padding: 0.3rem 0.75rem !important;
        }}

        .catalog-filter-wrap div[role="radiogroup"] {{
            flex-wrap: nowrap !important;
            overflow-x: auto;
            justify-content: flex-start !important;
            -webkit-overflow-scrolling: touch;
            padding-bottom: 0.25rem;
        }}

        .catalog-filter-wrap div[role="radiogroup"] label {{
            flex-shrink: 0;
            white-space: nowrap;
            font-size: 0.82rem !important;
            padding: 0.3rem 0.75rem !important;
        }}

        .catalog-pagination {{
            text-align: center;
            color: #666;
            font-size: 0.88rem;
            margin: 0.5rem 0 0.75rem;
        }}

        div[data-testid="column"] div.stButton > button,
        div[data-testid="column"] a[data-testid="stLinkButton"] {{
            font-size: 0.78rem !important;
            padding: 0.35rem 0.5rem !important;
            min-height: 2rem;
        }}

        .store-header {{
            text-align: center;
            padding: 0.5rem 0 1.25rem;
            overflow: visible;
        }}

        .store-header img,
        [data-testid="stImage"] img {{
            max-height: 140px;
            width: auto !important;
            height: auto !important;
            object-fit: contain;
            display: block;
            margin: 0 auto;
            box-shadow: none;
            border-radius: 0;
        }}

        .store-name {{
            font-size: 1.4rem;
            font-weight: 700;
            color: var(--primary);
            margin-top: 0.75rem;
            font-family: Georgia, "Times New Roman", serif;
            letter-spacing: 0.02em;
        }}

        .product-card {{
            border: none;
            border-radius: 16px;
            overflow: hidden;
            margin-bottom: 1.25rem;
            background: #fff;
            box-shadow: 0 4px 20px rgba(199, 21, 133, 0.12);
        }}

        .product-image-wrap {{
            position: relative;
            width: 100%;
        }}

        .product-photo {{
            width: 100%;
            aspect-ratio: 1;
            object-fit: cover;
            display: block;
        }}

        .product-photo-empty {{
            background: linear-gradient(135deg, #fff5f8, #fafafa);
            min-height: 280px;
        }}

        .product-badges {{
            position: absolute;
            top: 12px;
            left: 12px;
            right: 12px;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            z-index: 2;
        }}

        .badge {{
            display: inline-block;
            padding: 0.45rem 0.75rem;
            border-radius: 999px;
            font-weight: 800;
            font-size: 0.95rem;
            line-height: 1;
            box-shadow: 0 2px 10px rgba(0,0,0,0.18);
            letter-spacing: 0.02em;
        }}

        .badge-promo {{
            background: var(--secondary);
            color: #3d2e00;
        }}

        .badge-gift {{
            background: var(--primary);
            color: #fff;
        }}

        .combo-strip {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            flex-wrap: wrap;
            background: linear-gradient(90deg, var(--primary), #a0126b);
            color: #fff;
            font-weight: 700;
            font-size: 0.9rem;
            padding: 0.65rem 1rem;
            text-align: center;
        }}

        .combo-dot {{
            opacity: 0.85;
        }}

        .promo-strip {{
            background: var(--secondary);
            color: #3d2e00;
            text-align: center;
            font-weight: 800;
            font-size: 0.95rem;
            padding: 0.65rem 1rem;
            letter-spacing: 0.02em;
        }}

        .gift-strip {{
            background: linear-gradient(90deg, var(--accent), #ffe8f0);
            color: var(--primary);
            text-align: center;
            font-weight: 800;
            font-size: 0.95rem;
            padding: 0.65rem 1rem;
        }}

        .product-info {{
            padding: 1rem 1.1rem 1.15rem;
        }}

        .product-name {{
            font-weight: 700;
            font-size: 1.15rem;
            color: #262626;
            line-height: 1.3;
            overflow-wrap: anywhere;
            word-break: break-word;
        }}

        .product-size {{
            color: #666;
            font-size: 0.9rem;
            margin-top: 0.25rem;
        }}

        .product-desc {{
            color: #444;
            font-size: 0.92rem;
            line-height: 1.45;
            margin-top: 0.5rem;
            padding-top: 0.5rem;
            border-top: 1px solid #f0f0f0;
            overflow-wrap: anywhere;
            word-break: break-word;
        }}

        .price-block {{
            margin-top: 0.75rem;
            padding: 0.75rem 0.85rem;
            background: #fafafa;
            border-radius: 12px;
            border-left: 4px solid var(--primary);
        }}

        .price-old {{
            text-decoration: line-through;
            color: #999;
            font-size: 0.95rem;
        }}

        .price-current {{
            font-size: 1.55rem;
            font-weight: 800;
            color: var(--primary);
            line-height: 1.2;
            margin-top: 0.15rem;
        }}

        .price-current.solo {{
            margin-top: 0;
        }}

        .price-save {{
            margin-top: 0.35rem;
            font-size: 0.88rem;
            font-weight: 700;
            color: #2e7d32;
            background: #e8f5e9;
            display: inline-block;
            padding: 0.2rem 0.55rem;
            border-radius: 6px;
        }}

        .gifts-section {{
            margin-top: 1rem;
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }}

        .gift-card {{
            display: flex;
            align-items: stretch;
            gap: 0.85rem;
            padding: 0.75rem;
            background: linear-gradient(135deg, #fff9fc 0%, #fffbf0 100%);
            border: 2px solid var(--secondary);
            border-radius: 14px;
            box-shadow: 0 2px 12px rgba(212, 175, 55, 0.2);
        }}

        .gift-photo-wrap {{
            position: relative;
            flex-shrink: 0;
            width: 100px;
            height: 100px;
            border-radius: 12px;
            overflow: hidden;
            border: 2px solid var(--secondary);
            background: #fff;
        }}

        .gift-photo {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
        }}

        .gift-photo-placeholder {{
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(145deg, var(--accent), #fff);
        }}

        .gift-photo-emoji {{
            font-size: 2.5rem;
        }}

        .gift-photo-tag {{
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            background: var(--primary);
            color: #fff;
            font-size: 0.7rem;
            font-weight: 800;
            text-align: center;
            padding: 0.25rem 0;
            letter-spacing: 0.06em;
        }}

        .gift-card-body {{
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            min-width: 0;
        }}

        .gift-card-label {{
            font-size: 0.72rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--secondary);
        }}

        .gift-card-name {{
            font-size: 1.05rem;
            font-weight: 700;
            color: var(--primary);
            margin-top: 0.2rem;
            line-height: 1.25;
        }}

        .gift-card-sub {{
            font-size: 0.82rem;
            color: #666;
            margin-top: 0.25rem;
        }}

        .stock-out {{
            color: #dc3545;
            font-size: 0.9rem;
            font-weight: 700;
            margin-top: 0.75rem;
            text-align: center;
            padding: 0.5rem;
            background: #fff5f5;
            border-radius: 8px;
        }}

        a[data-testid="stLinkButton"] {{
            background-color: var(--primary) !important;
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

        div[data-testid="column"] div.stButton > button {{
            border-radius: 8px;
            font-weight: 600;
        }}

        .cart-item {{
            background: #fff;
            border-radius: 12px;
            padding: 0.85rem 1rem;
            margin-bottom: 0.5rem;
            box-shadow: 0 2px 12px rgba(199, 21, 133, 0.1);
            border-left: 4px solid var(--primary);
        }}

        .cart-summary {{
            background: linear-gradient(135deg, #fff5f8, #fffbf0);
            border: 2px solid var(--secondary);
            border-radius: 14px;
            padding: 1rem 1.1rem;
            margin: 1rem 0;
            font-size: 1.15rem;
            text-align: center;
        }}

        .account-box {{
            background: #fff;
            border-radius: 14px;
            padding: 1rem;
            box-shadow: 0 2px 12px rgba(199, 21, 133, 0.1);
            margin-bottom: 1rem;
        }}

        div[role="radiogroup"] {{
            justify-content: center;
            gap: 0.5rem;
            margin-bottom: 1rem;
        }}

        div[role="radiogroup"] label {{
            background: #fff;
            border: 2px solid #f0e0ea;
            border-radius: 999px;
            padding: 0.35rem 1rem !important;
            font-weight: 600;
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
