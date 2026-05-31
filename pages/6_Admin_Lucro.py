"""Dashboard de lucro e margem por produto."""

import streamlit as st

from lib.auth import require_auth, render_admin_nav
from lib.catalog import fetch_all_products, fetch_product_gifts, fetch_active_promotions
from lib.profit import calculate_profit
from lib.utils import format_currency

st.set_page_config(page_title="Admin — Lucro", page_icon="📊", layout="wide")

if not require_auth():
    st.stop()

render_admin_nav()
st.title("📊 Lucro & Margem")

products = fetch_all_products()
promotions = fetch_active_promotions()

if not products:
    st.info("Cadastre produtos para ver a análise de lucro.")
    st.stop()

total_lucro = 0.0
total_receita = 0.0
rows = []

for product in products:
    linked = fetch_product_gifts(product["id"])
    profit = calculate_profit(product, linked, promotions)
    total_lucro += profit.lucro_bruto
    total_receita += profit.preco_final_cliente

    margin_class = (
        "positive"
        if profit.margem_percent >= 10
        else "negative"
        if profit.margem_percent < 0
        else "warning"
    )

    rows.append(
        {
            "Produto": product["name"],
            "Estoque": profit.stock,
            "Custo peça": profit.custo_peca,
            "Custo brindes": profit.custo_brindes,
            "Repasse brinde": profit.repasse_brinde,
            "Preço catálogo": profit.preco_catalogo,
            "Desconto": profit.desconto,
            "Preço final": profit.preco_final_cliente,
            "Lucro": profit.lucro_bruto,
            "Margem %": profit.margem_percent,
            "Status": margin_class,
            "Promoção": profit.promotion_name or "—",
            "Brinde OK": profit.gift_stock_ok,
        }
    )

col1, col2, col3 = st.columns(3)
col1.metric("Produtos", len(products))
col2.metric("Receita potencial", format_currency(total_receita))
col3.metric("Lucro potencial", format_currency(total_lucro))

st.markdown("---")

for row in rows:
    product = next(p for p in products if p["name"] == row["Produto"])
    linked = fetch_product_gifts(product["id"])
    profit = calculate_profit(product, linked, promotions)

    icon = "🟢" if row["Status"] == "positive" else "🔴" if row["Status"] == "negative" else "🟡"
    if not row["Brinde OK"]:
        icon = "⚠️"

    with st.expander(f"{icon} {row['Produto']} — Lucro: {format_currency(row['Lucro'])}"):
        c1, c2, c3 = st.columns(3)
        c1.metric("Custo da peça", format_currency(profit.custo_peca))
        c2.metric("Custo brindes", format_currency(profit.custo_brindes))
        c3.metric("Margem", f"{profit.margem_percent:.1f}%")

        st.markdown(f"**Preço catálogo:** {format_currency(profit.preco_catalogo)}")
        if profit.desconto > 0:
            st.markdown(
                f"**Promoção:** {profit.promotion_name} "
                f"(-{format_currency(profit.desconto)})"
            )
        st.markdown(f"**Preço final ao cliente:** {format_currency(profit.preco_final_cliente)}")
        st.markdown(f"**Lucro bruto:** {format_currency(profit.lucro_bruto)}")

        if profit.gifts:
            st.markdown("**Brindes vinculados:**")
            for g in profit.gifts:
                st.markdown(
                    f"- {g.name} (x{g.quantity}): custo {format_currency(g.total_cost)}, "
                    f"repasse {format_currency(g.total_markup)}, "
                    f"você absorve {format_currency(g.absorbed_cost)}"
                )

        if profit.margem_percent < 0:
            st.error("Margem negativa! Revise preços ou custos.")
        elif profit.stock == 0:
            st.warning("Sem estoque.")
        elif not profit.gift_stock_ok:
            st.warning("Estoque de brinde insuficiente.")
