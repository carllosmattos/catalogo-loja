"""CRUD de promoções."""

from datetime import datetime

import streamlit as st

from lib.auth import require_auth, render_admin_nav
from lib.catalog import (
    create_promotion,
    delete_promotion,
    fetch_all_products,
    fetch_all_promotions,
    update_promotion,
)
from lib.utils import format_currency

st.set_page_config(page_title="Admin — Promoções", page_icon="🏷️", layout="wide")

if not require_auth():
    st.stop()

render_admin_nav()
st.title("🏷️ Promoções")

products = fetch_all_products()
product_options = {p["name"]: p["id"] for p in products}

tab_list, tab_new = st.tabs(["Lista de promoções", "Nova promoção"])

with tab_new:
    with st.form("new_promo"):
        name = st.text_input("Nome da promoção", placeholder="Ex: Black Friday")
        description = st.text_area("Descrição")
        discount_type = st.selectbox("Tipo de desconto", ["percent", "fixed"], format_func=lambda x: "% Percentual" if x == "percent" else "R$ Valor fixo")
        discount_value = st.number_input(
            "Valor do desconto",
            min_value=0.0,
            value=0.0,
            step=0.01,
            help="Percentual (ex: 15) ou valor fixo em R$",
        )
        applies_to = st.selectbox(
            "Aplica-se a",
            ["all", "selected"],
            format_func=lambda x: "Todos os produtos" if x == "all" else "Produtos selecionados",
        )
        selected_products = []
        if applies_to == "selected":
            selected_products = st.multiselect(
                "Produtos",
                options=list(product_options.keys()),
            )

        col1, col2 = st.columns(2)
        with col1:
            starts_at = st.date_input("Início", value=None)
        with col2:
            ends_at = st.date_input("Fim", value=None)

        active = st.checkbox("Ativa", value=True)
        submitted = st.form_submit_button("Cadastrar promoção", use_container_width=True)

        if submitted:
            if not name:
                st.error("Informe o nome da promoção.")
            else:
                try:
                    data = {
                        "name": name,
                        "description": description,
                        "discount_type": discount_type,
                        "discount_value": discount_value,
                        "applies_to": applies_to,
                        "product_ids": [product_options[p] for p in selected_products],
                        "starts_at": datetime.combine(starts_at, datetime.min.time()).isoformat() if starts_at else None,
                        "ends_at": datetime.combine(ends_at, datetime.max.time()).isoformat() if ends_at else None,
                        "active": active,
                    }
                    create_promotion(data)
                    st.success("Promoção cadastrada!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")

with tab_list:
    promos = fetch_all_promotions()
    if not promos:
        st.info("Nenhuma promoção cadastrada.")
    else:
        for promo in promos:
            status = "✅" if promo["active"] else "⏸️"
            dtype = promo["discount_type"]
            dval = float(promo["discount_value"])
            label = (
                f"{status} {promo['name']} — {dval:.0f}%"
                if dtype == "percent"
                else f"{status} {promo['name']} — {format_currency(dval)}"
            )
            with st.expander(label):
                with st.form(f"edit_promo_{promo['id']}"):
                    name = st.text_input("Nome", value=promo["name"], key=f"pn_{promo['id']}")
                    description = st.text_area(
                        "Descrição",
                        value=promo.get("description", ""),
                        key=f"pd_{promo['id']}",
                    )
                    discount_type = st.selectbox(
                        "Tipo",
                        ["percent", "fixed"],
                        index=0 if promo["discount_type"] == "percent" else 1,
                        format_func=lambda x: "% Percentual" if x == "percent" else "R$ Fixo",
                        key=f"dt_{promo['id']}",
                    )
                    discount_value = st.number_input(
                        "Valor",
                        min_value=0.0,
                        value=float(promo["discount_value"]),
                        step=0.01,
                        key=f"dv_{promo['id']}",
                    )
                    applies_to = st.selectbox(
                        "Aplica-se a",
                        ["all", "selected"],
                        index=0 if promo["applies_to"] == "all" else 1,
                        format_func=lambda x: "Todos" if x == "all" else "Selecionados",
                        key=f"at_{promo['id']}",
                    )

                    current_ids = promo.get("product_ids") or []
                    current_names = [
                        n for n, pid in product_options.items() if pid in current_ids
                    ]
                    selected = []
                    if applies_to == "selected":
                        selected = st.multiselect(
                            "Produtos",
                            options=list(product_options.keys()),
                            default=current_names,
                            key=f"ps_{promo['id']}",
                        )

                    active = st.checkbox(
                        "Ativa", value=promo["active"], key=f"pa_{promo['id']}"
                    )

                    col1, col2 = st.columns(2)
                    with col1:
                        save = st.form_submit_button("Salvar", use_container_width=True)
                    with col2:
                        remove = st.form_submit_button(
                            "Excluir", use_container_width=True, type="secondary"
                        )

                    if save:
                        try:
                            update_promotion(
                                promo["id"],
                                {
                                    "name": name,
                                    "description": description,
                                    "discount_type": discount_type,
                                    "discount_value": discount_value,
                                    "applies_to": applies_to,
                                    "product_ids": [product_options[p] for p in selected],
                                    "active": active,
                                },
                            )
                            st.success("Atualizado!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro: {e}")

                    if remove:
                        try:
                            delete_promotion(promo["id"])
                            st.success("Excluído!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro: {e}")
