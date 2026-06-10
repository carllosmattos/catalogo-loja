"""Toasts do catálogo (mensagens fora dos componentes)."""

from __future__ import annotations

import streamlit as st

_ICONS = {
    "error": "⚠️",
    "success": "✅",
    "info": "ℹ️",
    "warning": "⚠️",
}


def flash_toast(kind: str, message: str) -> None:
    """Enfileira toast para exibir após rerun."""
    st.session_state.setdefault("_flash_toasts", []).append((kind, message))


def catalog_toast(kind: str, message: str) -> None:
    """Toast imediato (sem rerun)."""
    if message:
        st.toast(message, icon=_ICONS.get(kind, "ℹ️"))


def show_flash_toasts() -> None:
    """Exibe toasts enfileirados no início da página."""
    pending = st.session_state.pop("_flash_toasts", [])
    for kind, message in pending:
        if message:
            st.toast(message, icon=_ICONS.get(kind, "ℹ️"))
