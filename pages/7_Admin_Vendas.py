"""Admin — registrar vendas, histórico e relatórios."""

from datetime import date, timedelta

import pandas as pd
import streamlit as st

from lib.auth import require_auth, render_sidebar
from lib.branding import configure_page
from lib.customers import search_customers
from lib.catalog import fetch_active_promotions, fetch_all_products, fetch_product_gifts
from lib.product_sizes import SIZES, stock_for_size, total_stock
from lib.profit import calculate_profit
from lib.sales import (
    cancel_sale,
    fetch_sales,
    gift_stock_ok_for_quantity,
    register_sale,
    sale_quantity,
    sales_by_day,
    sales_summary,
)
from lib.utils import format_cpf, format_currency, is_valid_cpf

configure_page("Admin — Vendas", layout="wide", sidebar_state="expanded")
render_sidebar()

if not require_auth():
    st.stop()

st.title("🛒 Vendas")

tab_nova, tab_historico, tab_relatorio, tab_canceladas = st.tabs(
    ["Nova venda", "Histórico", "Relatórios", "Canceladas"]
)

products = fetch_all_products()
promotions = fetch_active_promotions()
active_products = [
    p
    for p in products
    if p.get("active") and total_stock(p.get("sizes") or []) > 0
]

# ── Nova venda ──────────────────────────────────────────────
with tab_nova:
    if not active_products:
        st.warning("Nenhum produto ativo com estoque. Cadastre em Produtos.")
    else:
        for key in ("sale_cust_name", "sale_cust_phone", "sale_cust_cpf", "sale_cust_address"):
            if key not in st.session_state:
                st.session_state[key] = ""

        st.subheader("Cliente")
        col_sq, col_sb = st.columns([4, 1])
        with col_sq:
            search_q = st.text_input(
                "Buscar cliente (CPF, nome ou telefone)",
                key="customer_search_q",
                placeholder="Mínimo 3 caracteres",
            )
        with col_sb:
            st.markdown("<br>", unsafe_allow_html=True)
            search_btn = st.button("Buscar", key="customer_search_btn", use_container_width=True)

        if search_btn:
            if len(search_q.strip()) < 3:
                st.warning("Digite pelo menos 3 caracteres para buscar.")
            else:
                st.session_state.customer_search_results = search_customers(search_q)

        results = st.session_state.get("customer_search_results") or []
        if results:
            pick_map = {
                f"{c['name']} — {format_cpf(c['cpf'])}"
                + (f" — {c.get('phone')}" if c.get("phone") else ""): c
                for c in results
            }
            picked_label = st.selectbox(
                "Selecionar cliente",
                options=list(pick_map.keys()),
                key="customer_pick_label",
            )
            if st.button("Usar este cliente", key="use_customer_btn"):
                picked = pick_map[picked_label]
                st.session_state.sale_cust_name = picked["name"]
                st.session_state.sale_cust_phone = picked.get("phone", "")
                st.session_state.sale_cust_cpf = format_cpf(picked["cpf"])
                st.session_state.sale_cust_address = picked.get("address", "")
                st.rerun()

        c1, c2, c3 = st.columns(3)
        with c1:
            st.text_input("Nome do cliente *", key="sale_cust_name")
        with c2:
            st.text_input(
                "WhatsApp / telefone",
                key="sale_cust_phone",
                placeholder="5511999999999",
            )
        with c3:
            st.text_input(
                "CPF *",
                key="sale_cust_cpf",
                placeholder="000.000.000-00",
            )
        st.text_area(
            "Endereço de entrega",
            key="sale_cust_address",
            placeholder="Rua, número, bairro, cidade…",
        )

        st.markdown("---")
        st.subheader("Produto")

        product_map = {
            f"{p['name']} — estoque {total_stock(p.get('sizes') or [])}": p
            for p in active_products
        }

        product_options = list(product_map.keys())
        selected = st.selectbox(
            "Produto *",
            options=product_options,
            key="sale_product",
        )
        product = product_map[selected]
        sizes = product.get("sizes") or []
        in_stock = [s for s in SIZES if stock_for_size(sizes, s) > 0]
        size_key = "sale_size"
        if "sale_product_prev" not in st.session_state:
            st.session_state.sale_product_prev = selected
        if st.session_state.sale_product_prev != selected:
            st.session_state[size_key] = in_stock[0] if in_stock else "M"
            st.session_state.sale_product_prev = selected
        if size_key not in st.session_state or st.session_state[size_key] not in SIZES:
            st.session_state[size_key] = in_stock[0] if in_stock else "M"

        st.markdown("**Tamanho**")
        sz_cols = st.columns(3)
        for sz, scol in zip(SIZES, sz_cols):
            qty_sz = stock_for_size(sizes, sz)
            with scol:
                label = f"{sz} ({qty_sz})" if qty_sz > 0 else f"{sz} ✗"
                if st.button(
                    label,
                    key=f"sale_sz_{sz}",
                    disabled=qty_sz <= 0,
                    use_container_width=True,
                    type="primary"
                    if st.session_state[size_key] == sz and qty_sz > 0
                    else "secondary",
                ):
                    st.session_state[size_key] = sz
                    st.rerun()

        selected_size = st.session_state[size_key]
        if stock_for_size(sizes, selected_size) <= 0:
            st.warning(f"Tamanho {selected_size} esgotado — escolha outro.")

        linked = fetch_product_gifts(product["id"])
        profit = calculate_profit(
            product, linked, promotions, selected_size=selected_size
        )
        max_qty = max(int(profit.stock), 1)

        quantity = st.number_input(
            "Quantidade",
            min_value=1,
            max_value=max_qty,
            value=1,
            step=1,
            key="sale_qty",
        )
        gifts_ok = gift_stock_ok_for_quantity(linked, quantity)
        total_catalog = profit.preco_catalogo * quantity
        total_final = profit.preco_final_cliente * quantity
        total_lucro = profit.lucro_bruto * quantity

        st.markdown("---")
        st.subheader("Resumo da venda")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Quantidade", quantity)
        c2.metric("Preço catálogo", format_currency(total_catalog))
        c3.metric("Valor final", format_currency(total_final))
        c4.metric("Lucro estimado", format_currency(total_lucro))

        if quantity > 1:
            st.caption(
                f"Unitário: catálogo {format_currency(profit.preco_catalogo)} · "
                f"final {format_currency(profit.preco_final_cliente)} · "
                f"lucro {format_currency(profit.lucro_bruto)}"
            )

        if profit.promotion_name:
            st.success(
                f"Promoção: **{profit.promotion_name}** "
                f"(−{format_currency(profit.desconto * quantity)} total)"
            )
        if profit.gifts:
            gift_parts = []
            for g in profit.gifts:
                total_g = g.quantity * quantity
                gift_parts.append(f"{g.name} x{total_g}")
            st.info(f"Brindes: {', '.join(gift_parts)}")

        if profit.stock < quantity:
            st.error(f"Estoque insuficiente (disponível: {profit.stock}).")
        elif not gifts_ok:
            st.error("Estoque de brinde insuficiente para esta quantidade.")

        st.markdown("---")
        with st.form("new_sale"):
            notes = st.text_area("Observações", height=100)

            submitted = st.form_submit_button(
                "Confirmar venda",
                type="primary",
                use_container_width=True,
            )

            if submitted:
                customer_name = st.session_state.get("sale_cust_name", "").strip()
                customer_phone = st.session_state.get("sale_cust_phone", "")
                customer_cpf = st.session_state.get("sale_cust_cpf", "")
                customer_address = st.session_state.get("sale_cust_address", "")

                if not customer_name:
                    st.error("Informe o nome do cliente.")
                elif not is_valid_cpf(customer_cpf):
                    st.error("Informe um CPF válido.")
                elif profit.stock < quantity or not gifts_ok:
                    st.error("Estoque insuficiente.")
                else:
                    try:
                        sale_id = register_sale(
                            product,
                            customer_name=customer_name,
                            customer_phone=customer_phone,
                            customer_cpf=customer_cpf,
                            customer_address=customer_address,
                            notes=notes,
                            quantity=quantity,
                            selected_size=selected_size,
                        )
                        for key in (
                            "sale_cust_name",
                            "sale_cust_phone",
                            "sale_cust_cpf",
                            "sale_cust_address",
                            "customer_search_results",
                            "customer_search_q",
                        ):
                            st.session_state.pop(key, None)
                        st.success(f"Venda registrada! ID: {sale_id[:8]}…")
                        st.balloons()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")

# ── Histórico ───────────────────────────────────────────────
with tab_historico:
    col_a, col_b = st.columns(2)
    with col_a:
        hist_start = st.date_input(
            "De",
            value=date.today() - timedelta(days=30),
            key="hist_start",
        )
    with col_b:
        hist_end = st.date_input("Até", value=date.today(), key="hist_end")

    sales = fetch_sales(hist_start, hist_end)
    if not sales:
        st.info("Nenhuma venda no período.")
    else:
        for s in sales:
            gifts = s.get("sale_gifts") or []
            gift_label = ", ".join(
                f"{g.get('gift_name')} x{g.get('quantity', 1)}" for g in gifts
            )
            promo = s.get("promotion_name") or "—"
            qty = sale_quantity(s)
            qty_label = f" x{qty}" if qty > 1 else ""
            with st.expander(
                f"{s.get('created_at', '')[:10]} — {s.get('customer_name')} — "
                f"{s.get('product_name')}{qty_label} — "
                f"{format_currency(float(s.get('preco_final', 0)))}"
            ):
                st.markdown(f"**Cliente:** {s.get('customer_name')}")
                if s.get("customer_cpf"):
                    st.markdown(f"**CPF:** {format_cpf(s['customer_cpf'])}")
                if s.get("customer_phone"):
                    st.markdown(f"**Contato:** {s['customer_phone']}")
                st.markdown(
                    f"**Produto:** {s.get('product_name')} {s.get('product_size', '')}"
                )
                st.markdown(f"**Quantidade:** {qty}")
                st.markdown(f"**Promoção:** {promo}")
                st.markdown(f"**Brindes:** {gift_label or '—'}")
                st.markdown(f"**Valor final:** {format_currency(float(s.get('preco_final', 0)))}")
                st.markdown(f"**Lucro:** {format_currency(float(s.get('lucro', 0)))}")
                if s.get("notes"):
                    st.caption(s["notes"])

                confirm_key = f"confirm_cancel_{s['id']}"
                if confirm_key not in st.session_state:
                    st.session_state[confirm_key] = False

                if not st.session_state[confirm_key]:
                    if st.button(
                        "Cancelar venda",
                        key=f"cancel_btn_{s['id']}",
                        type="secondary",
                    ):
                        st.session_state[confirm_key] = True
                        st.rerun()
                else:
                    st.warning(
                        "Devolve o estoque desta venda (produto e brindes). "
                        "A venda sai dos relatórios."
                    )
                    c_yes, c_no = st.columns(2)
                    with c_yes:
                        if st.button(
                            "Confirmar cancelamento",
                            key=f"cancel_yes_{s['id']}",
                            type="primary",
                        ):
                            try:
                                cancel_sale(s["id"])
                                st.session_state[confirm_key] = False
                                st.success("Venda cancelada. Estoque devolvido.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro: {e}")
                    with c_no:
                        if st.button("Voltar", key=f"cancel_no_{s['id']}"):
                            st.session_state[confirm_key] = False
                            st.rerun()

# ── Relatórios ──────────────────────────────────────────────
with tab_relatorio:
    col1, col2 = st.columns(2)
    with col1:
        rep_start = st.date_input(
            "Período — início",
            value=date.today().replace(day=1),
            key="rep_start",
        )
    with col2:
        rep_end = st.date_input(
            "Período — fim",
            value=date.today(),
            key="rep_end",
        )

    rep_sales = fetch_sales(rep_start, rep_end)
    summary = sales_summary(rep_sales)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Vendas", summary["count"])
    m2.metric("Peças vendidas", int(summary["pecas"]))
    m3.metric("Receita", format_currency(summary["receita"]))
    m4.metric("Lucro", format_currency(summary["lucro"]))

    if rep_sales:
        by_day = sales_by_day(rep_sales)
        df = pd.DataFrame(
            {"Data": list(by_day.keys()), "Receita (R$)": list(by_day.values())}
        )
        st.subheader("Receita por dia")
        st.bar_chart(df.set_index("Data"))

        df_lucro = pd.DataFrame(
            [
                {
                    "Data": s.get("created_at", "")[:10],
                    "Lucro": float(s.get("lucro", 0)),
                }
                for s in rep_sales
            ]
        )
        if not df_lucro.empty:
            lucro_dia = df_lucro.groupby("Data")["Lucro"].sum().reset_index()
            st.subheader("Lucro por dia")
            st.line_chart(lucro_dia.set_index("Data"))

        st.subheader("Detalhamento")
        table = pd.DataFrame(
            [
                {
                    "Data": s.get("created_at", "")[:16].replace("T", " "),
                    "Cliente": s.get("customer_name"),
                    "CPF": format_cpf(s["customer_cpf"]) if s.get("customer_cpf") else "—",
                    "Produto": s.get("product_name"),
                    "Qtd": sale_quantity(s),
                    "Promoção": s.get("promotion_name") or "—",
                    "Final": float(s.get("preco_final", 0)),
                    "Lucro": float(s.get("lucro", 0)),
                }
                for s in rep_sales
            ]
        )
        st.dataframe(
            table,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Sem vendas no período selecionado.")

# ── Canceladas (auditoria) ───────────────────────────────────
with tab_canceladas:
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        cancel_start = st.date_input(
            "De",
            value=date.today() - timedelta(days=30),
            key="cancel_start",
        )
    with col_c2:
        cancel_end = st.date_input("Até", value=date.today(), key="cancel_end")

    cancelled = fetch_sales(cancel_start, cancel_end, cancelled_only=True)
    st.caption("Vendas canceladas não entram nos relatórios. Estoque foi devolvido.")
    if not cancelled:
        st.info("Nenhuma venda cancelada no período.")
    else:
        for s in cancelled:
            gifts = s.get("sale_gifts") or []
            gift_label = ", ".join(
                f"{g.get('gift_name')} x{g.get('quantity', 1)}" for g in gifts
            )
            cancelled_at = (s.get("cancelled_at") or "")[:16].replace("T", " ")
            created_at = (s.get("created_at") or "")[:10]
            qty = sale_quantity(s)
            qty_label = f" x{qty}" if qty > 1 else ""
            with st.expander(
                f"{created_at} — {s.get('customer_name')} — "
                f"{s.get('product_name')}{qty_label} — "
                f"Cancelada em {cancelled_at or '—'}"
            ):
                st.markdown(f"**Cliente:** {s.get('customer_name')}")
                if s.get("customer_cpf"):
                    st.markdown(f"**CPF:** {format_cpf(s['customer_cpf'])}")
                if s.get("customer_phone"):
                    st.markdown(f"**Contato:** {s['customer_phone']}")
                st.markdown(
                    f"**Produto:** {s.get('product_name')} {s.get('product_size', '')}"
                )
                st.markdown(f"**Quantidade:** {qty}")
                st.markdown(f"**Promoção:** {s.get('promotion_name') or '—'}")
                st.markdown(f"**Brindes:** {gift_label or '—'}")
                st.markdown(
                    f"**Valor final:** {format_currency(float(s.get('preco_final', 0)))}"
                )
                st.markdown(
                    f"**Lucro:** {format_currency(float(s.get('lucro', 0)))}"
                )
                st.markdown(f"**Cancelada em:** {cancelled_at or '—'}")
                if s.get("notes"):
                    st.caption(s["notes"])
