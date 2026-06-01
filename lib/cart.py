"""Carrinho de compras do catálogo público (session_state)."""

from __future__ import annotations

from typing import Any

import streamlit as st

from lib.profit import ProfitResult

CART_KEY = "cart"


def _ensure_cart() -> list[dict[str, Any]]:
    if CART_KEY not in st.session_state:
        st.session_state[CART_KEY] = []
    return st.session_state[CART_KEY]


def get_cart() -> list[dict[str, Any]]:
    return list(_ensure_cart())


def cart_piece_count() -> int:
    return sum(int(item.get("quantity", 1)) for item in get_cart())


def cart_line_id(product_id: str, size: str) -> str:
    return f"{product_id}:{size}"


def cart_item_from_product(
    product: dict[str, Any],
    profit: ProfitResult,
    size: str,
) -> dict[str, Any]:
    return {
        "product_id": str(product["id"]),
        "cart_line_id": cart_line_id(str(product["id"]), size),
        "name": product.get("name", ""),
        "size": size,
        "quantity": 1,
        "preco_catalogo": float(profit.preco_catalogo),
        "desconto": float(profit.desconto),
        "preco_final": float(profit.preco_final_cliente),
        "promotion_name": profit.promotion_name,
        "gifts": [{"name": g.name, "qty": g.quantity} for g in profit.gifts],
        "max_stock": int(profit.stock),
    }


def add_to_cart(item: dict[str, Any]) -> bool:
    """Adiciona ou incrementa item. Retorna False se estoque insuficiente."""
    cart = _ensure_cart()
    line_id = item.get("cart_line_id") or cart_line_id(
        item["product_id"], item.get("size", "M")
    )
    add_qty = int(item.get("quantity", 1))
    max_stock = int(item.get("max_stock", 0))

    for existing in cart:
        if existing.get("cart_line_id", existing["product_id"]) == line_id:
            new_qty = int(existing["quantity"]) + add_qty
            if new_qty > max_stock:
                return False
            existing["quantity"] = new_qty
            existing["max_stock"] = max_stock
            return True

    if add_qty > max_stock:
        return False
    cart.append({**item, "cart_line_id": line_id, "quantity": add_qty})
    return True


def update_qty(cart_line_id: str, qty: int) -> bool:
    cart = _ensure_cart()
    qty = max(int(qty), 1)
    for item in cart:
        cid = item.get("cart_line_id", item["product_id"])
        if cid == cart_line_id:
            if qty > int(item.get("max_stock", 0)):
                return False
            item["quantity"] = qty
            return True
    return False


def remove_from_cart(cart_line_id: str) -> None:
    cart = _ensure_cart()
    st.session_state[CART_KEY] = [
        i
        for i in cart
        if i.get("cart_line_id", i["product_id"]) != cart_line_id
    ]


def clear_cart() -> None:
    st.session_state[CART_KEY] = []


def cart_totals() -> dict[str, float | int]:
    cart = get_cart()
    total_pieces = 0
    total_value = 0.0
    for item in cart:
        qty = int(item.get("quantity", 1))
        total_pieces += qty
        total_value += float(item.get("preco_final", 0)) * qty
    return {
        "pieces": total_pieces,
        "items": len(cart),
        "total": total_value,
    }
