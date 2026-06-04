"""Grade responsiva de produtos no catálogo."""

from __future__ import annotations

from typing import Any, Callable

import streamlit as st

CATALOG_COLS = 3


def render_product_grid(
    products: list[dict[str, Any]],
    render_cell: Callable[[dict[str, Any], Any], None],
) -> None:
    """Renderiza produtos em linhas de 3 colunas (CSS adapta para 2 no mobile)."""
    st.markdown('<div class="catalog-product-grid">', unsafe_allow_html=True)
    for row_start in range(0, len(products), CATALOG_COLS):
        cols = st.columns(CATALOG_COLS, gap="small")
        for i, col in enumerate(cols):
            idx = row_start + i
            if idx < len(products):
                render_cell(products[idx], col)
    st.markdown("</div>", unsafe_allow_html=True)
