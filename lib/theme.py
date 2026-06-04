"""Tema visual mobile-first com cores da loja."""

from __future__ import annotations

import streamlit as st


from lib.branding import DEFAULT_SETTINGS as DEFAULT_COLORS, STREAMLIT_BRANDING_CSS


def inject_theme(
    settings: dict | None = None,
    hide_sidebar: bool = False,
    catalog_app: bool = False,
):
    primary = (settings or {}).get("primary_color", DEFAULT_COLORS["primary_color"])
    secondary = (settings or {}).get(
        "secondary_color", DEFAULT_COLORS["secondary_color"]
    )
    accent = (settings or {}).get("accent_color", DEFAULT_COLORS["accent_color"])

    sidebar_css = ""
    if catalog_app:
        sidebar_css = """
        [data-testid="collapsedControl"] { display: none !important; }
        [data-testid="stSidebarCollapsedControl"] { display: none !important; }
        [data-testid="stHeader"] { display: none !important; }
        [data-testid="stToolbar"] { display: none !important; }
        [data-testid="stDecoration"] { display: none !important; }
        #MainMenu { visibility: hidden !important; }
        footer { visibility: hidden !important; }
        """
    elif hide_sidebar:
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

        /* Oculta logo / "Made with Streamlit" (canto inferior) */
        {STREAMLIT_BRANDING_CSS}

        {sidebar_css}

        .block-container {{
            padding-top: 1rem;
            padding-bottom: 1.25rem;
            max-width: 720px;
        }}

        @media (min-width: 769px) {{
            .block-container {{
                max-width: 1080px;
            }}
        }}

        @media (min-width: 481px) and (max-width: 768px) {{
            .block-container {{
                max-width: 900px;
            }}
        }}

        .catalog-menu-drawer {{
            display: none !important;
        }}

        /* Grade de produtos: 3 colunas web/tablet, 2 colunas mobile */
        .catalog-product-grid [data-testid="stHorizontalBlock"] {{
            flex-wrap: wrap !important;
            gap: 0.45rem !important;
            margin-bottom: 0.35rem !important;
        }}

        .catalog-product-grid [data-testid="stHorizontalBlock"] > [data-testid="column"] {{
            min-width: 0 !important;
        }}

        @media (min-width: 481px) {{
            .catalog-product-grid [data-testid="stHorizontalBlock"] > [data-testid="column"] {{
                flex: 0 0 calc(33.333% - 0.35rem) !important;
                max-width: calc(33.333% - 0.35rem) !important;
            }}
        }}

        @media (max-width: 480px) {{
            .catalog-product-grid [data-testid="stHorizontalBlock"] > [data-testid="column"] {{
                flex: 0 0 calc(50% - 0.25rem) !important;
                max-width: calc(50% - 0.25rem) !important;
            }}

            .catalog-product-grid .product-card-compact .product-photo-empty {{
                min-height: 88px;
            }}

            .catalog-product-grid .product-card-compact .product-info {{
                padding: 0.45rem 0.5rem 0.55rem;
            }}

            .catalog-product-grid .product-card-compact .product-name {{
                font-size: 0.78rem;
                -webkit-line-clamp: 2;
            }}

            .catalog-product-grid .product-card-compact .price-current {{
                font-size: 0.88rem;
            }}

            .catalog-product-grid .product-card-compact .price-block {{
                margin-top: 0.35rem;
                padding: 0.3rem 0.4rem;
            }}

            .catalog-product-grid .product-card-compact .badge {{
                padding: 0.2rem 0.35rem;
                font-size: 0.58rem;
            }}

            .catalog-product-grid div[data-testid="column"] div.stButton > button,
            .catalog-product-grid div[data-testid="column"] a[data-testid="stLinkButton"] {{
                font-size: 0.58rem !important;
                min-height: 1.55rem !important;
                padding: 0.18rem 0.08rem !important;
            }}

            .catalog-product-grid div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(4)) button {{
                font-size: 0.55rem !important;
                min-height: 1.45rem !important;
                padding: 0.2rem 0.05rem !important;
            }}
        }}

        .catalog-greeting {{
            font-size: 0.78rem;
            color: #666;
            text-align: center;
            margin: 0 0 0.35rem;
        }}

        .catalog-topbar {{
            margin-bottom: 0.35rem;
        }}

        .catalog-topbar [data-testid="column"]:first-child button {{
            min-height: 2rem !important;
            font-size: 1.05rem !important;
            padding: 0.2rem 0.5rem !important;
            border-radius: 8px !important;
        }}

        .catalog-topbar-title-wrap {{
            display: flex;
            align-items: center;
            min-height: 2rem;
        }}

        .catalog-topbar-title {{
            font-size: 0.95rem;
            font-weight: 700;
            color: var(--primary);
        }}

        /* Tamanhos Único/P/M/G — linha com 4 colunas */
        div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(4)):not(:has(> div[data-testid="column"]:nth-child(5))) {{
            gap: 0.25rem !important;
            margin: 0.2rem 0 0.3rem !important;
        }}

        div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(4)):not(:has(> div[data-testid="column"]:nth-child(5))) > div[data-testid="column"] {{
            padding: 0 0.08rem !important;
            min-width: 0 !important;
        }}

        div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(4)):not(:has(> div[data-testid="column"]:nth-child(5))) button {{
            font-size: 0.68rem !important;
            font-weight: 700 !important;
            min-height: 1.85rem !important;
            padding: 0.32rem 0.08rem !important;
            line-height: 1 !important;
            white-space: nowrap !important;
        }}

        /* Ações do produto — 🛒 💠 💬 na mesma linha */
        .catalog-product-grid div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(3)):not(:has(> div[data-testid="column"]:nth-child(4))) {{
            gap: 0.28rem !important;
            margin: 0.28rem 0 0 !important;
        }}

        .catalog-product-grid div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(3)):not(:has(> div[data-testid="column"]:nth-child(4))) > div[data-testid="column"] {{
            flex: 1 1 0% !important;
            min-width: 0 !important;
            padding: 0 0.06rem !important;
        }}

        .catalog-product-grid div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(3)):not(:has(> div[data-testid="column"]:nth-child(4))) button,
        .catalog-product-grid div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(3)):not(:has(> div[data-testid="column"]:nth-child(4))) a {{
            min-height: 2.15rem !important;
            font-size: 1.05rem !important;
            padding: 0.28rem 0.15rem !important;
            line-height: 1 !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
        }}

        @media (max-width: 480px) {{
            .catalog-product-grid div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(3)):not(:has(> div[data-testid="column"]:nth-child(4))) button,
            .catalog-product-grid div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(3)):not(:has(> div[data-testid="column"]:nth-child(4))) a {{
                min-height: 1.85rem !important;
                font-size: 0.95rem !important;
                padding: 0.22rem 0.1rem !important;
            }}
        }}

        /* Adicionar + Comprar lado a lado no mobile (dentro do card) */
        @media (max-width: 768px) {{
            [data-testid="column"] div[data-testid="stHorizontalBlock"]:not(:has(> div[data-testid="column"]:nth-child(3))),
            [data-testid="stColumn"] div[data-testid="stHorizontalBlock"]:not(:has(> div[data-testid="column"]:nth-child(3))) {{
                flex-direction: row !important;
                flex-wrap: nowrap !important;
                gap: 0.25rem !important;
            }}

            [data-testid="column"] div[data-testid="stHorizontalBlock"]:not(:has(> div[data-testid="column"]:nth-child(3))) > div,
            [data-testid="stColumn"] div[data-testid="stHorizontalBlock"]:not(:has(> div[data-testid="column"]:nth-child(3))) > div {{
                flex: 1 1 0% !important;
                min-width: 0 !important;
                width: auto !important;
                max-width: none !important;
            }}

            [data-testid="column"] div[data-testid="stHorizontalBlock"]:not(:has(> div[data-testid="column"]:nth-child(3))) button,
            [data-testid="column"] div[data-testid="stHorizontalBlock"]:not(:has(> div[data-testid="column"]:nth-child(3))) a,
            [data-testid="stColumn"] div[data-testid="stHorizontalBlock"]:not(:has(> div[data-testid="column"]:nth-child(3))) button,
            [data-testid="stColumn"] div[data-testid="stHorizontalBlock"]:not(:has(> div[data-testid="column"]:nth-child(3))) a {{
                font-size: 0.65rem !important;
                min-height: 1.75rem !important;
                padding: 0.22rem 0.1rem !important;
                white-space: nowrap !important;
            }}
        }}

        .catalog-nav-compact {{
            margin-bottom: 0.45rem;
        }}

        .catalog-nav-compact [data-testid="column"] {{
            padding: 0 0.15rem !important;
        }}

        .catalog-nav-compact [data-testid="column"] button {{
            padding: 0.28rem 0.15rem !important;
            font-size: 0.72rem !important;
            min-height: 1.65rem !important;
            border-radius: 8px !important;
            line-height: 1.1 !important;
            white-space: nowrap;
        }}

        .catalog-filter-label {{
            display: block;
            font-size: 0.72rem;
            font-weight: 600;
            color: #888;
            margin-bottom: 0.1rem;
        }}

        .catalog-filter-wrap {{
            margin-bottom: 0.35rem;
        }}

        .catalog-filter-wrap div[data-baseweb="select"] {{
            font-size: 0.82rem;
        }}

        .catalog-filter-wrap div[data-baseweb="select"] > div {{
            min-height: 2rem !important;
            border-radius: 8px !important;
            border-color: #f0e0ea !important;
        }}

        .catalog-count {{
            font-size: 0.72rem;
            color: #888;
            text-align: right;
            margin: 0.15rem 0 0.35rem;
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

        .store-social-bar {{
            text-align: center;
            margin: 0 0 0.4rem;
        }}

        .store-social-link {{
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            font-size: 0.72rem;
            font-weight: 600;
            color: var(--primary);
            text-decoration: none;
            padding: 0.2rem 0.55rem;
            border-radius: 999px;
            background: #fff5f8;
            border: 1px solid #f0e0ea;
        }}

        .store-social-link:hover {{
            color: var(--secondary);
            border-color: var(--secondary);
        }}

        .social-icon-svg {{
            width: 1.05rem;
            height: 1.05rem;
            flex-shrink: 0;
            display: block;
        }}

        .social-icon-text {{
            line-height: 1;
        }}

        .social-icon-link {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 1.85rem;
            height: 1.85rem;
            border-radius: 50%;
            color: #aaa;
            background: #fafafa;
            border: 1px solid #eee;
            text-decoration: none;
            transition: color 0.15s, border-color 0.15s, background 0.15s;
        }}

        .social-icon-link .social-icon-svg {{
            width: 1rem;
            height: 1rem;
        }}

        .social-icon-link:hover {{
            color: var(--primary);
            border-color: #f0c0dd;
            background: #fff5f8;
        }}

        .dev-footer {{
            text-align: center;
            margin-top: 1.25rem;
            padding: 0.75rem 0 1rem;
            font-size: 0.68rem;
            color: #999;
            line-height: 1.5;
        }}

        .dev-footer-label {{
            display: block;
            margin-bottom: 0.4rem;
        }}

        .dev-footer-links {{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 0.5rem;
        }}

        .catalog-pagination {{
            text-align: center;
            color: #666;
            font-size: 0.88rem;
            margin: 0.5rem 0 0.75rem;
        }}

        .size-picker-anchor,
        .product-actions-anchor {{
            display: none;
        }}

        .catalog-back-top {{
            position: fixed;
            bottom: 4.5rem;
            right: 1rem;
            z-index: 99990;
            width: 2.5rem;
            height: 2.5rem;
            border: none;
            border-radius: 50%;
            background: var(--primary);
            color: #fff;
            font-size: 1.15rem;
            font-weight: 700;
            line-height: 1;
            cursor: pointer;
            box-shadow: 0 4px 14px rgba(199, 21, 133, 0.35);
        }}

        @media (max-width: 768px) {{
            .catalog-back-top {{
                bottom: 5.25rem;
                right: 0.85rem;
            }}
        }}

        .catalog-back-top:active {{
            transform: scale(0.96);
        }}

        div[data-testid="column"] div.stButton > button,
        div[data-testid="column"] a[data-testid="stLinkButton"] {{
            font-size: 0.78rem !important;
            padding: 0.35rem 0.5rem !important;
            min-height: 2rem;
        }}

        .store-header {{
            text-align: center;
            padding: 0 0 0.35rem;
            overflow: visible;
        }}

        .store-header-banner {{
            padding: 0 0 0.25rem;
        }}

        .store-banner-wrap {{
            width: 100%;
            margin: 0 auto;
            border-radius: 12px;
            overflow: hidden;
        }}

        .store-banner {{
            width: 100%;
            height: auto;
            max-height: 130px;
            object-fit: contain;
            display: block;
            margin: 0 auto;
            border-radius: 12px;
        }}

        .store-banner-carousel {{
            position: relative;
            width: 100%;
            min-height: 90px;
            max-height: 130px;
            aspect-ratio: 2.2 / 1;
        }}

        .store-banner-track {{
            position: relative;
            width: 100%;
            height: 100%;
            min-height: 120px;
        }}

        .store-banner-slide {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            max-height: 200px;
            object-fit: contain;
            opacity: 0;
            animation: bannerCrossfade var(--banner-duration, 15s) infinite;
        }}

        .store-banner-slide:nth-child(1) {{ animation-delay: 0s; }}
        .store-banner-slide:nth-child(2) {{
            animation-delay: calc(-1 * var(--banner-duration, 15s) / var(--banner-count, 2));
        }}
        .store-banner-slide:nth-child(3) {{
            animation-delay: calc(-2 * var(--banner-duration, 15s) / var(--banner-count, 3));
        }}
        .store-banner-slide:nth-child(4) {{
            animation-delay: calc(-3 * var(--banner-duration, 15s) / var(--banner-count, 4));
        }}
        .store-banner-slide:nth-child(5) {{
            animation-delay: calc(-4 * var(--banner-duration, 15s) / var(--banner-count, 5));
        }}

        @keyframes bannerCrossfade {{
            0%, 18% {{ opacity: 1; z-index: 1; }}
            22%, 100% {{ opacity: 0; z-index: 0; }}
        }}

        .store-banner-dots {{
            display: flex;
            justify-content: center;
            gap: 6px;
            margin-top: 0.4rem;
        }}

        .store-banner-dot {{
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: #e0c0d0;
            animation: bannerDot var(--banner-duration, 15s) infinite;
        }}

        .store-banner-dot.active {{
            background: var(--primary);
        }}

        @keyframes bannerDot {{
            0%, 18% {{ background: var(--primary); transform: scale(1.2); }}
            22%, 100% {{ background: #e0c0d0; transform: scale(1); }}
        }}

        .store-header:not(.store-header-banner) img,
        .store-header:not(.store-header-banner) [data-testid="stImage"] img {{
            max-height: 140px;
            width: auto !important;
            height: auto !important;
            object-fit: contain;
            display: block;
            margin: 0 auto;
            box-shadow: none;
            border-radius: 0;
        }}

        .store-header-banner img {{
            max-height: none;
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

        .product-photo-carousel-inner,
        .item-photo-carousel {{
            position: relative;
            width: 100%;
            aspect-ratio: 1;
            overflow: hidden;
        }}

        .product-photo-carousel-inner .product-banner-track {{
            position: relative;
            width: 100%;
            height: 100%;
            min-height: unset;
        }}

        .product-photo-carousel-inner .product-banner-slide {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            max-height: none;
            object-fit: cover;
            opacity: 0;
            animation: bannerCrossfade var(--banner-duration, 12s) infinite;
        }}

        .product-photo-carousel-inner .product-banner-slide:nth-child(1) {{ animation-delay: 0s; }}
        .product-photo-carousel-inner .product-banner-slide:nth-child(2) {{
            animation-delay: calc(-1 * var(--banner-duration, 12s) / var(--banner-count, 2));
        }}
        .product-photo-carousel-inner .product-banner-slide:nth-child(3) {{
            animation-delay: calc(-2 * var(--banner-duration, 12s) / var(--banner-count, 3));
        }}
        .product-photo-carousel-inner .product-banner-slide:nth-child(4) {{
            animation-delay: calc(-3 * var(--banner-duration, 12s) / var(--banner-count, 4));
        }}
        .product-photo-carousel-inner .product-banner-slide:nth-child(5) {{
            animation-delay: calc(-4 * var(--banner-duration, 12s) / var(--banner-count, 5));
        }}

        .size-picker {{
            margin: 0.25rem 0 0.35rem;
        }}

        .size-picker [data-testid="column"] {{
            padding: 0 0.12rem !important;
        }}

        .size-picker button {{
            font-size: 0.72rem !important;
            min-height: 1.75rem !important;
            padding: 0.2rem 0.1rem !important;
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
            gap: 0.35rem;
            margin-bottom: 0.5rem;
        }}

        div[role="radiogroup"] label {{
            background: #fff;
            border: 1px solid #f0e0ea;
            border-radius: 999px;
            padding: 0.25rem 0.65rem !important;
            font-weight: 600;
            font-size: 0.78rem !important;
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
