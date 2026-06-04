"""Identidade visual LM moda feminina."""

from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
LOGO_RAW = ROOT / "resources" / "lm.jpeg"
LOGO_PATH = ROOT / "resources" / "lm_logo.png"
BANNER_DEFAULT = ROOT / "resources" / "banner.png"

STORE_NAME = "LM moda feminina"

PRIMARY = "#C71585"
SECONDARY = "#D4AF37"
ACCENT = "#F8C8DC"
BRAND_FONT = 'Georgia, "Times New Roman", serif'

DEFAULT_SETTINGS = {
    "store_name": STORE_NAME,
    "whatsapp_number": "",
    "primary_color": PRIMARY,
    "secondary_color": SECONDARY,
    "accent_color": ACCENT,
    "logo_url": None,
    "default_banner_url": None,
}

STREAMLIT_BRANDING_CSS = """
footer,
.stApp > footer,
[data-testid="stFooter"],
[class*="viewerBadge"],
[class*="stDeployButton"],
a[href*="streamlit.io/made-with-streamlit"],
a[href*="streamlit.io"][target="_blank"] {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    overflow: hidden !important;
    pointer-events: none !important;
}

[data-testid="stSidebarNav"],
[data-testid="stSidebarNavItems"],
[data-testid="stSidebarNavSeparator"] {
    display: none !important;
}
"""


def hide_streamlit_branding() -> None:
    """Remove logo / 'Made with Streamlit' e menu automático de páginas."""
    st.markdown(
        f"<style>{STREAMLIT_BRANDING_CSS}</style>",
        unsafe_allow_html=True,
    )


def get_logo_path() -> Path | None:
    if LOGO_PATH.is_file():
        return LOGO_PATH
    if LOGO_RAW.is_file():
        return LOGO_RAW
    return None


def configure_page(
    title: str,
    layout: str = "centered",
    sidebar_state: str = "auto",
):
    icon = str(get_logo_path() or LOGO_RAW)
    st.set_page_config(
        page_title=f"{title} — {STORE_NAME}",
        page_icon=icon,
        layout=layout,
        initial_sidebar_state=sidebar_state,
    )
    hide_streamlit_branding()


def logo_exists() -> bool:
    return get_logo_path() is not None


def logo_base64() -> str:
    path = get_logo_path()
    if not path:
        return ""
    data = path.read_bytes()
    return base64.b64encode(data).decode()


def resolve_logo_url(settings: dict | None) -> str | None:
    """URL remota do Supabase ou data URI da logo local."""
    if settings and settings.get("logo_url"):
        return settings["logo_url"]
    path = get_logo_path()
    if path:
        mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
        return f"data:{mime};base64,{logo_base64()}"
    return None


def merge_brand_settings(settings: dict | None) -> dict:
    merged = {**DEFAULT_SETTINGS, **(settings or {})}
    if not merged.get("store_name") or merged["store_name"] == "Minha Loja":
        merged["store_name"] = STORE_NAME
    for key, default in DEFAULT_SETTINGS.items():
        if key.endswith("_color") and not (settings or {}).get(key):
            merged[key] = default
    return merged


def brand_display_lines(store_name: str | None = None) -> tuple[str, str]:
    """Separa nome da loja em linha principal (LM) e tagline."""
    name = (store_name or STORE_NAME).strip()
    if name.upper().startswith("LM"):
        rest = name[2:].strip()
        return "LM", (rest or "moda feminina").lower()
    parts = name.split(None, 1)
    if len(parts) == 2:
        return parts[0], parts[1].lower()
    return name, ""


def banner_default_base64() -> str:
    if not BANNER_DEFAULT.is_file():
        return ""
    return base64.b64encode(BANNER_DEFAULT.read_bytes()).decode()


def resolve_default_banner_url(settings: dict | None) -> str | None:
    """URL remota do banner padrão ou data URI do banner local."""
    if settings and settings.get("default_banner_url"):
        return settings["default_banner_url"]
    if BANNER_DEFAULT.is_file():
        return f"data:image/png;base64,{banner_default_base64()}"
    return None


def resolve_promo_banners(promotions: list[dict] | None) -> list[str]:
    """URLs de banners de promoções ativas marcadas para exibição."""
    urls: list[str] = []
    for promo in promotions or []:
        if not promo.get("show_banner"):
            continue
        url = (promo.get("banner_url") or "").strip()
        if url:
            urls.append(url)
    return urls


def resolve_catalog_banner(
    settings: dict | None,
    promotions: list[dict] | None,
) -> dict:
    """
    Define qual banner exibir no catálogo.
    Prioridade: promoções > banner padrão > banner local > legacy (logo+nome).
    """
    promo_urls = resolve_promo_banners(promotions)
    if len(promo_urls) >= 2:
        return {"mode": "carousel", "urls": promo_urls}
    if len(promo_urls) == 1:
        return {"mode": "single", "urls": promo_urls}

    default_url = resolve_default_banner_url(settings)
    if default_url:
        mode = "default" if settings and settings.get("default_banner_url") else "local"
        return {"mode": mode, "urls": [default_url]}

    return {"mode": "legacy", "urls": []}
