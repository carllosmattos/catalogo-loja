"""Identidade visual LM moda feminina."""

from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st

from lib.theme import hide_streamlit_branding

ROOT = Path(__file__).resolve().parent.parent
LOGO_RAW = ROOT / "resources" / "lm.jpeg"
LOGO_PATH = ROOT / "resources" / "lm_logo.png"
BANNER_DEFAULT = ROOT / "resources" / "banner.png"

STORE_NAME = "LM moda feminina"

PRIMARY = "#C71585"
SECONDARY = "#D4AF37"
ACCENT = "#F8C8DC"

DEFAULT_SETTINGS = {
    "store_name": STORE_NAME,
    "whatsapp_number": "",
    "primary_color": PRIMARY,
    "secondary_color": SECONDARY,
    "accent_color": ACCENT,
    "logo_url": None,
    "default_banner_url": None,
}


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
