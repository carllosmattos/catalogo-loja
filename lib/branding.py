"""Identidade visual LM moda feminina."""

from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
LOGO_RAW = ROOT / "resources" / "lm.jpeg"
LOGO_PATH = ROOT / "resources" / "lm_logo.png"

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
