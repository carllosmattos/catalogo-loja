"""Admin — transações, reembolsos e configuração de pagamentos."""

import streamlit as st

from lib.auth import require_auth, render_sidebar
from lib.branding import configure_page
from lib.payments.admin import (
    approve_refund_request,
    fetch_order_bundle_by_id,
    fetch_orders,
    fetch_payments,
    fetch_refund_requests,
    reject_refund_request,
)
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
    orders = fetch_orders(80)
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
                    st.code(pay["pix_copy_paste"], language=None)
                bundle = fetch_order_bundle_by_id(str(o["id"]))
                if bundle:
                    st.caption(f"Pedido `{o['id']}` · tracking `{o.get('tracking_token', '')}`")

with tab_tx:
    payments = fetch_payments(80)
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
                    st.code(p["pix_copy_paste"], language=None)
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
