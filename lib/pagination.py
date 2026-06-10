"""Controles de paginação reutilizáveis no admin."""

from __future__ import annotations

import streamlit as st


def render_pagination(
    *,
    state_key: str,
    page: int,
    total_items: int,
    page_size: int = 25,
) -> int:
    """Renderiza Anterior / Próximo. Retorna página atual (pode ter mudado)."""
    if total_items <= 0:
        return 0
    total_pages = max(1, (total_items + page_size - 1) // page_size)
    page = max(0, min(page, total_pages - 1))

    start = page * page_size + 1
    end = min((page + 1) * page_size, total_items)

    col_prev, col_info, col_next = st.columns([1, 2, 1])
    with col_prev:
        if st.button("← Anterior", key=f"{state_key}_prev", disabled=page <= 0):
            st.session_state[state_key] = page - 1
            st.rerun()
    with col_info:
        st.caption(f"Página {page + 1} de {total_pages} · {start}–{end} de {total_items}")
    with col_next:
        if st.button(
            "Próximo →",
            key=f"{state_key}_next",
            disabled=page >= total_pages - 1,
        ):
            st.session_state[state_key] = page + 1
            st.rerun()

    return page
