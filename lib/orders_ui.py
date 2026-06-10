"""UI de pedidos no catálogo público."""

from __future__ import annotations

from typing import Any

import streamlit as st

from lib.feedback import catalog_toast, flash_toast
from lib.payments.factory import app_base_url, payments_enabled
from lib.payments.orders_db import cancel_order, get_order_bundle, list_customer_orders, request_refund
from lib.payments.whatsapp_payment import build_whatsapp_payment_url
from lib.utils import format_currency


def _status_badge(status: str) -> str:
    labels = {
        "pending_payment": "⏳ Aguardando PIX",
        "paid": "✅ Pago",
        "cancelled": "❌ Cancelado",
        "refund_requested": "↩️ Reembolso solicitado",
        "refunded": "↩️ Reembolsado",
    }
    return labels.get(status, status)


def render_order_detail(
    bundle: dict[str, Any],
    *,
    customer_id: str | None,
    whatsapp_number: str,
    store_name: str,
) -> None:
    order = bundle.get("order") or {}
    items = bundle.get("items") or []
    payment = bundle.get("payment") or {}
    oid = str(order.get("id", ""))
    status = order.get("status", "")
    token = str(order.get("tracking_token", ""))

    st.markdown(f"**Status:** {_status_badge(status)}")
    st.markdown(f"**Total:** {format_currency(float(order.get('total_amount', 0)))}")

    for item in items:
        qty = int(item.get("quantity", 1))
        st.markdown(
            f"- **{item.get('product_name')}** "
            f"({item.get('product_size', '')}) × {qty} — "
            f"{format_currency(float(item.get('preco_final_line', 0)))}"
        )

    pix = payment.get("pix_copy_paste") or ""
    if status == "pending_payment" and pix:
        st.subheader("PIX copia e cola")
        st.code(pix, language=None)

    base = app_base_url()
    track_url = f"{base}?order={token}&view=Minhas%20compras" if base and token else ""

    if whatsapp_number:
        wa_url = build_whatsapp_payment_url(
            whatsapp_number,
            bundle,
            store_name,
            tracking_url=track_url,
        )
        st.link_button(
            "Enviar pedido e PIX no WhatsApp",
            wa_url,
            use_container_width=True,
            type="primary",
        )

    if customer_id and str(order.get("customer_id")) == str(customer_id):
        if status == "pending_payment":
            col_cancel, col_refresh = st.columns(2)
            with col_refresh:
                if st.button("Atualizar status", key=f"refresh_{oid}", use_container_width=True):
                    mp_id = payment.get("provider_payment_id")
                    if mp_id:
                        try:
                            from lib.payments.factory import get_payment_gateway, payments_enabled
                            from lib.payments.mercado_pago.mapper import map_mp_status

                            if payments_enabled():
                                mp = get_payment_gateway().get_payment(str(mp_id))
                                mp_status = map_mp_status(mp.get("status", ""))
                                catalog_toast(
                                    "info",
                                    f"Status no Mercado Pago: {mp_status}. "
                                    "Se já pagou, aguarde a confirmação.",
                                )
                        except Exception as e:
                            catalog_toast("error", str(e))
                    st.rerun()
            with col_cancel:
                if st.button("Cancelar pedido", key=f"cancel_{oid}", use_container_width=True):
                    try:
                        cancel_order(
                            customer_id,
                            oid,
                            provider_payment_id=payment.get("provider_payment_id"),
                        )
                        flash_toast("success", "Pedido cancelado.")
                        st.rerun()
                    except Exception as e:
                        flash_toast("error", str(e))
                        st.rerun()
        elif status == "paid":
            with st.form(f"refund_{oid}"):
                reason = st.text_area("Motivo do reembolso", height=80)
                if st.form_submit_button("Solicitar reembolso", use_container_width=True):
                    try:
                        request_refund(customer_id, oid, reason)
                        flash_toast("success", "Solicitação enviada. A loja irá analisar.")
                        st.rerun()
                    except Exception as e:
                        flash_toast("error", str(e))
                        st.rerun()


def render_my_orders(
    customer: dict[str, Any],
    *,
    whatsapp_number: str,
    store_name: str,
    highlight_token: str | None = None,
) -> None:
    if not payments_enabled():
        catalog_toast("info", "Pagamentos online em breve.")
        return

    customer_id = str(customer.get("id", ""))
    if highlight_token:
        bundle = get_order_bundle(highlight_token)
        if bundle:
            st.subheader("Acompanhar minha compra")
            render_order_detail(
                bundle,
                customer_id=customer_id,
                whatsapp_number=whatsapp_number,
                store_name=store_name,
            )
            st.markdown("---")
        else:
            catalog_toast("warning", "Pedido não encontrado ou link inválido.")

    rows, list_error = list_customer_orders(customer_id)
    if list_error:
        catalog_toast(
            "error",
            "Não foi possível carregar seus pedidos. "
            "Verifique se a migração 021 foi aplicada no Supabase.",
        )
        return
    if not rows:
        catalog_toast("info", "Você ainda não tem pedidos.")
        return

    st.subheader("Minhas compras")
    for row in rows:
        if not isinstance(row, dict):
            continue
        order = row.get("order") or {}
        token = str(order.get("tracking_token", ""))
        with st.expander(
            f"{_status_badge(order.get('status', ''))} — "
            f"{format_currency(float(order.get('total_amount', 0)))} — "
            f"{(order.get('created_at') or '')[:10]}",
            expanded=bool(highlight_token and token == str(highlight_token).strip()),
        ):
            full = get_order_bundle(token) if token else None
            if full:
                render_order_detail(
                    full,
                    customer_id=customer_id,
                    whatsapp_number=whatsapp_number,
                    store_name=store_name,
                )
            else:
                st.caption("Detalhes indisponíveis.")
