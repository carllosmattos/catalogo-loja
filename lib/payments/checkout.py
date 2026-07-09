"""Orquestração de checkout: pedido + PIX Mercado Pago."""

from __future__ import annotations

from typing import Any

from lib.catalog import fetch_active_promotions, fetch_product_gifts
from lib.payments.factory import app_base_url, get_payment_gateway, payments_enabled, webhook_notification_url
from lib.payments.models import CheckoutPayer, CheckoutRequest
from lib.payments.orders_db import (
    attach_payment_to_order,
    create_checkout_order,
    get_order_bundle,
)
from lib.shipping import calculate_shipping

PIX_EXPIRY_MINUTES = 15
from lib.profit import calculate_profit, extract_gift_from_link


def _gifts_snapshot(linked: list[dict[str, Any]], quantity: int) -> list[dict[str, Any]]:
    out = []
    for lg in linked:
        gift = extract_gift_from_link(lg)
        if not gift:
            continue
        per_sale = int(lg.get("quantity_per_sale", 1))
        out.append(
            {
                "gift_id": str(gift["id"]),
                "gift_name": gift.get("name", "Brinde"),
                "quantity": per_sale * quantity,
            }
        )
    return out


def _line_from_product(
    product: dict[str, Any],
    size: str,
    quantity: int,
    promotions: list[dict[str, Any]],
) -> dict[str, Any]:
    from lib.product_sizes import attach_sizes_to_products

    product = attach_sizes_to_products([product])[0]
    linked = fetch_product_gifts(product["id"])
    profit = calculate_profit(product, linked, promotions, selected_size=size)
    qty = max(int(quantity), 1)
    if profit.stock < qty:
        raise ValueError(f"Estoque insuficiente para {product.get('name', 'produto')}.")

    promo_id = None
    if profit.promotion_name:
        for p in promotions:
            if p.get("name") == profit.promotion_name:
                promo_id = p.get("id")
                break

    unit_final = float(profit.preco_final_cliente)
    unit_lucro = float(profit.lucro_bruto)

    return {
        "product_id": str(product["id"]),
        "product_name": product.get("name", ""),
        "product_size": size,
        "quantity": qty,
        "preco_catalogo": float(profit.preco_catalogo),
        "desconto": float(profit.desconto),
        "sale_freight": float(product.get("sale_freight", 0)),
        "preco_final_line": unit_final * qty,
        "lucro_line": unit_lucro * qty,
        "promotion_id": str(promo_id) if promo_id else "",
        "promotion_name": profit.promotion_name or "",
        "gifts_snapshot": _gifts_snapshot(linked, qty),
    }


def build_lines_from_cart(cart: list[dict[str, Any]], products_by_id: dict[str, dict]) -> list[dict[str, Any]]:
    promotions = fetch_active_promotions()
    lines = []
    for item in cart:
        pid = str(item.get("product_id", ""))
        product = products_by_id.get(pid)
        if not product:
            raise ValueError(f"Produto não encontrado: {item.get('name', pid)}")
        lines.append(
            _line_from_product(
                product,
                item.get("size", "M"),
                int(item.get("quantity", 1)),
                promotions,
            )
        )
    return lines


def start_checkout(
    customer: dict[str, Any],
    lines: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Cria pedido no Supabase e pagamento PIX no MP.
    Retorna dict com order, payment, pix_copy_paste, tracking_token.
    """
    if not payments_enabled():
        raise ValueError("Pagamentos online desativados.")

    customer_id = customer.get("id")
    if not customer_id:
        raise ValueError("Complete seu cadastro em Minha conta.")

    shipping = calculate_shipping(customer, lines)
    if shipping.blocked:
        raise ValueError(
            shipping.label or "Não entregamos neste endereço. Atualize em Minha conta."
        )

    created = create_checkout_order(
        str(customer_id), lines, shipping_amount=shipping.amount
    )
    order_id = str(created["order_id"])
    tracking_token = str(created["tracking_token"])
    total = float(created["total_amount"])
    expires_at = str(created.get("expires_at") or "")

    base = app_base_url()
    payer = CheckoutPayer(
        email=customer.get("email", ""),
        name=customer.get("name", ""),
        cpf=customer.get("cpf", ""),
        phone=customer.get("phone", ""),
    )
    desc = f"Pedido {order_id[:8]}"
    if len(lines) == 1:
        desc = lines[0].get("product_name", desc)

    from datetime import datetime, timedelta, timezone

    br_tz = timezone(timedelta(hours=-3))
    exp_dt = datetime.now(br_tz) + timedelta(minutes=PIX_EXPIRY_MINUTES)
    expires_iso = exp_dt.strftime("%Y-%m-%dT%H:%M:%S.000-03:00")

    gateway = get_payment_gateway()
    result = gateway.create_pix_checkout(
        CheckoutRequest(
            order_id=order_id,
            amount=total,
            description=desc,
            payer=payer,
            notification_url=webhook_notification_url(),
            back_url_success=f"{base}?order={tracking_token}&view=Minhas%20compras" if base else "",
            expires_at_iso=expires_iso,
        )
    )

    payment_id = attach_payment_to_order(
        order_id=order_id,
        provider_payment_id=result.provider_payment_id,
        status=result.status.value,
        amount=total,
        pix_copy_paste=result.pix_copy_paste,
        raw=result.raw,
        expires_at=expires_at or expires_iso,
    )

    return {
        "order_id": order_id,
        "tracking_token": tracking_token,
        "payment_id": payment_id,
        "pix_copy_paste": result.pix_copy_paste,
        "ticket_url": result.ticket_url,
        "provider_payment_id": result.provider_payment_id,
        "total": total,
        "shipping_amount": shipping.amount,
        "shipping_label": shipping.label,
        "expires_at": expires_at or expires_iso,
    }


def get_tracking_bundle(tracking_token: str) -> dict[str, Any] | None:
    return get_order_bundle(tracking_token)
