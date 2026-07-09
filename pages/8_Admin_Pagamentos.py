"""Admin — transações, reembolsos e configuração de pagamentos."""

import streamlit as st

from lib.auth import require_auth, render_sidebar
from lib.branding import configure_page
from lib.payments.admin import (
    approve_refund_request,
    count_orders,
    count_payments,
    fetch_order_bundle_by_id,
    fetch_orders,
    fetch_payments,
    fetch_refund_requests,
    reject_refund_request,
)
from lib.pagination import render_pagination
from lib.pix_display import render_pix_payment
from lib.payments.factory import app_base_url, payments_enabled, webhook_notification_url
from lib.utils import format_currency

configure_page("Admin — Pagamentos", layout="wide", sidebar_state="expanded")
render_sidebar()

if not require_auth():
    st.stop()

st.title("💳 Pagamentos")

tab_orders, tab_tx, tab_refund, tab_cfg = st.tabs(
    ["Pedidos", "Transações", "Reembolsos", "Configuração"]
)

with tab_orders:
    if "orders_page" not in st.session_state:
        st.session_state.orders_page = 0
    page_size = 25
    total_orders = count_orders()
    page = render_pagination(
        state_key="orders_page",
        page=st.session_state.orders_page,
        total_items=total_orders,
        page_size=page_size,
    )
    st.session_state.orders_page = page
    orders = fetch_orders(page_size, page * page_size)
    if not orders:
        st.info("Nenhum pedido online registrado.")
    else:
        for o in orders:
            items = o.get("order_items") or []
            payments = o.get("payments") or []
            pay = payments[0] if isinstance(payments, list) and payments else {}
            item_lines = ", ".join(
                f"{it.get('product_name')} ×{it.get('quantity', 1)}"
                for it in items[:3]
            )
            label = (
                f"{(o.get('created_at') or '')[:16]} — {o.get('status')} — "
                f"{format_currency(float(o.get('total_amount', 0)))} — "
                f"{o.get('customer_name', '')}"
            )
            with st.expander(label):
                st.markdown(f"**Cliente:** {o.get('customer_name')} — {o.get('customer_email')}")
                st.markdown(f"**Itens:** {item_lines or '—'}")
                st.markdown(f"**Pagamento:** {pay.get('status', '—')} — MP `{pay.get('provider_payment_id') or '—'}`")
                if pay.get("pix_copy_paste"):
                    render_pix_payment(
                        pay["pix_copy_paste"],
                        key=f"order_pix_{o['id']}",
                    )
                if o.get("status") == "pending_payment" and pay.get("provider_payment_id"):
                    if st.button("Sincronizar com MP", key=f"sync_order_{o['id']}"):
                        try:
                            from lib.payments.sync import sync_order_payment

                            sync_order_payment(str(o["id"]))
                            st.success("Status sincronizado.")
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
                bundle = fetch_order_bundle_by_id(str(o["id"]))
                if bundle:
                    st.caption(f"Pedido `{o['id']}` · tracking `{o.get('tracking_token', '')}`")

with tab_tx:
    if "payments_page" not in st.session_state:
        st.session_state.payments_page = 0
    page_size = 25
    total_payments = count_payments()
    page = render_pagination(
        state_key="payments_page",
        page=st.session_state.payments_page,
        total_items=total_payments,
        page_size=page_size,
    )
    st.session_state.payments_page = page
    payments = fetch_payments(page_size, page * page_size)
    if not payments:
        st.info("Nenhuma transação registrada.")
    else:
        for p in payments:
            order = p.get("orders") or {}
            label = (
                f"{(p.get('created_at') or '')[:16]} — "
                f"{p.get('status')} — {format_currency(float(p.get('amount', 0)))} — "
                f"{order.get('customer_name', '')}"
            )
            with st.expander(label):
                st.markdown(f"**ID pagamento:** `{p.get('id')}`")
                st.markdown(f"**MP:** `{p.get('provider_payment_id') or '—'}`")
                st.markdown(f"**Pedido:** `{p.get('order_id')}`")
                st.markdown(f"**Cliente:** {order.get('customer_name')} — {order.get('customer_email')}")
                if p.get("pix_copy_paste"):
                    render_pix_payment(
                        p["pix_copy_paste"],
                        key=f"pay_pix_{p['id']}",
                    )
                if order.get("id"):
                    from lib.catalog import fetch_store_settings
                    from lib.payments.whatsapp_payment import build_whatsapp_payment_url

                    settings = fetch_store_settings()
                    wa = settings.get("whatsapp_number", "")
                    if wa and st.button(
                        "Enviar detalhes + PIX no WhatsApp",
                        key=f"wa_pay_{p['id']}",
                    ):
                        bundle = fetch_order_bundle_by_id(str(order["id"]))
                        if bundle:
                            base = app_base_url()
                            token = order.get("tracking_token", "")
                            url = (
                                f"{base}?order={token}&view=Minhas%20compras" if base else ""
                            )
                            st.link_button(
                                "Abrir WhatsApp",
                                build_whatsapp_payment_url(
                                    wa,
                                    bundle,
                                    settings.get("store_name", "Loja"),
                                    tracking_url=url,
                                ),
                            )

with tab_refund:
    pending = fetch_refund_requests("pending")
    if not pending:
        st.success("Nenhum reembolso pendente.")
    else:
        for r in pending:
            order = r.get("orders") or {}
            with st.expander(
                f"{order.get('customer_name', '')} — "
                f"{format_currency(float(order.get('total_amount', 0)))}"
            ):
                st.markdown(f"**Motivo:** {r.get('reason') or '—'}")
                st.markdown(f"**Pedido:** `{r.get('order_id')}`")
                notes = st.text_input("Observações admin", key=f"adm_notes_{r['id']}")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Aprovar e reembolsar", key=f"appr_{r['id']}", type="primary"):
                        try:
                            approve_refund_request(str(r["id"]), notes)
                            st.success("Reembolso processado no MP e estoque estornado.")
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
                with c2:
                    if st.button("Rejeitar", key=f"rej_{r['id']}"):
                        try:
                            reject_refund_request(str(r["id"]), notes)
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))

with tab_cfg:
    st.markdown(f"**Pagamentos ativos (app):** {'Sim' if payments_enabled() else 'Não'}")
    st.markdown(f"**URL base:** `{app_base_url() or '—'}`")
    st.markdown(f"**Webhook MP:** `{webhook_notification_url() or '—'}`")
    st.info(
        "Configure em `.streamlit/secrets.toml` ou Streamlit Cloud: "
        "`MERCADOPAGO_ACCESS_TOKEN`, `MERCADOPAGO_WEBHOOK_URL`, "
        "`APP_BASE_URL`, `PAYMENTS_ENABLED`."
    )
    st.markdown(
        "Deploy da Edge Function `supabase/functions/mercadopago-webhook` "
        "e registre a URL nas notificações do Mercado Pago."
    )
