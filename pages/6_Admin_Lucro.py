"""Dashboard de lucro e margem por produto."""

from datetime import date

import streamlit as st

from lib.auth import require_auth, render_sidebar
from lib.branding import configure_page
from lib.catalog import fetch_all_products, fetch_product_gifts, fetch_active_promotions
from lib.profit import calculate_profit
from lib.sales import fetch_sales, sales_summary
from lib.utils import format_currency

configure_page("Admin — Lucro", layout="wide", sidebar_state="expanded")
render_sidebar()

if not require_auth():
    st.stop()
st.title("📊 Lucro & Margem")

all_products = fetch_all_products()
promotions = fetch_active_promotions()

if not all_products:
    st.info("Cadastre produtos para ver a análise de lucro.")
    st.stop()

filter_opt = st.radio(
    "Mostrar",
    ["Ativos", "Arquivados", "Todos"],
    horizontal=True,
    key="lucro_filter",
)
if filter_opt == "Ativos":
    products = [p for p in all_products if p.get("active")]
elif filter_opt == "Arquivados":
    products = [p for p in all_products if not p.get("active")]
else:
    products = all_products

st.caption(
    "Simulação com preços e promoções atuais. Não altera vendas passadas. "
    "Detalhes de vendas reais em Admin → Vendas → Relatórios."
)

month_start = date.today().replace(day=1)
month_sales = fetch_sales(month_start, date.today())
month_summary = sales_summary(month_sales)

st.subheader("Realizado este mês")
r1, r2, r3 = st.columns(3)
r1.metric("Vendas no mês", month_summary["count"])
r2.metric("Receita realizada", format_currency(month_summary["receita"]))
r3.metric("Lucro realizado", format_currency(month_summary["lucro"]))

st.markdown("---")
st.subheader("Potencial no estoque")

if not products:
    st.info("Nenhum produto neste filtro.")
    st.stop()

total_lucro = 0.0
total_receita = 0.0
rows = []

for product in products:
    linked = fetch_product_gifts(product["id"])
    profit = calculate_profit(product, linked, promotions)
    stock = profit.stock
    lucro_estoque = profit.lucro_bruto * stock
    receita_estoque = profit.preco_final_cliente * stock
    total_lucro += lucro_estoque
    total_receita += receita_estoque

    margin_class = (
        "positive"
        if profit.margem_percent >= 10
        else "negative"
        if profit.margem_percent < 0
        else "warning"
    )

    rows.append(
        {
            "id": product["id"],
            "active": product.get("active", True),
            "Produto": product["name"],
            "Estoque": stock,
            "Lucro unit": profit.lucro_bruto,
            "Lucro estoque": lucro_estoque,
            "Receita estoque": receita_estoque,
            "Margem %": profit.margem_percent,
            "Status": margin_class,
            "Brinde OK": profit.gift_stock_ok,
        }
    )

col1, col2, col3 = st.columns(3)
col1.metric("Produtos", len(products))
col2.metric("Receita potencial", format_currency(total_receita))
col3.metric("Lucro potencial", format_currency(total_lucro))

st.markdown("---")

products_by_id = {p["id"]: p for p in products}

for row in rows:
    product = products_by_id[row["id"]]
    linked = fetch_product_gifts(product["id"])
    profit = calculate_profit(product, linked, promotions)

    icon = "🟢" if row["Status"] == "positive" else "🔴" if row["Status"] == "negative" else "🟡"
    if not row["Brinde OK"]:
        icon = "⚠️"
    archived = "" if row["active"] else " ⏸️"

    with st.expander(
        f"{icon}{archived} {row['Produto']} — "
        f"Lucro/peça: {format_currency(row['Lucro unit'])} · "
        f"Estoque: {row['Estoque']}"
    ):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Custo da peça", format_currency(profit.custo_peca))
        c2.metric("Custo brindes", format_currency(profit.custo_brindes))
        c3.metric("Margem", f"{profit.margem_percent:.1f}%")
        c4.metric("Lucro no estoque", format_currency(row["Lucro estoque"]))

        st.markdown(f"**Preço catálogo:** {format_currency(profit.preco_catalogo)}")
        if profit.desconto > 0:
            st.markdown(
                f"**Promoção:** {profit.promotion_name} "
                f"(-{format_currency(profit.desconto)})"
            )
        st.markdown(f"**Preço final ao cliente:** {format_currency(profit.preco_final_cliente)}")
        st.markdown(f"**Lucro por peça:** {format_currency(profit.lucro_bruto)}")
        if profit.stock > 0:
            st.markdown(
                f"**Receita se vender todo estoque:** "
                f"{format_currency(row['Receita estoque'])}"
            )

        if profit.gifts:
            st.markdown("**Brindes vinculados:**")
            for g in profit.gifts:
                st.markdown(
                    f"- {g.name} (x{g.quantity}): custo {format_currency(g.total_cost)}, "
                    f"repasse {format_currency(g.total_markup)}, "
                    f"você absorve {format_currency(g.absorbed_cost)}"
                )
                if g.total_cost == 0:
                    st.caption(
                        "Custo R$ 0 — preencha preço de compra e frete em Admin → Brindes."
                    )
        elif profit.custo_brindes == 0:
            if not linked:
                st.caption("Nenhum brinde vinculado a este produto (Admin → Produtos).")

        if profit.margem_percent < 0:
            st.error("Margem negativa! Revise preços ou custos.")
        elif profit.stock == 0:
            st.warning("Sem estoque.")
        elif not profit.gift_stock_ok:
            st.warning("Estoque de brinde insuficiente.")
