"""CRUD de brindes."""

import streamlit as st

from lib.auth import require_auth, render_admin_nav
from lib.catalog import (
    create_gift,
    delete_gift,
    fetch_all_gifts_admin,
    update_gift,
)
from lib.utils import format_currency

st.set_page_config(page_title="Admin — Brindes", page_icon="🎁", layout="wide")

if not require_auth():
    st.stop()

render_admin_nav()
st.title("🎁 Brindes")

tab_list, tab_new = st.tabs(["Lista de brindes", "Novo brinde"])

with tab_new:
    with st.form("new_gift"):
        name = st.text_input("Nome do brinde")
        stock = st.number_input("Estoque", min_value=0, value=0, step=1)
        purchase_price = st.number_input(
            "Preço de compra (R$)", min_value=0.0, value=0.0, step=0.01
        )
        purchase_freight = st.number_input(
            "Frete de compra (R$)", min_value=0.0, value=0.0, step=0.01
        )
        sale_markup = st.number_input(
            "Repasse ao cliente (R$)",
            min_value=0.0,
            value=0.0,
            step=0.01,
            help="Quanto do custo do brinde será repassado no preço. 0 = você absorve tudo.",
        )
        submitted = st.form_submit_button("Cadastrar brinde", use_container_width=True)
        if submitted:
            if not name:
                st.error("Informe o nome do brinde.")
            else:
                try:
                    create_gift(
                        {
                            "name": name,
                            "stock": stock,
                            "purchase_price": purchase_price,
                            "purchase_freight": purchase_freight,
                            "sale_markup": sale_markup,
                        }
                    )
                    st.success("Brinde cadastrado!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")

with tab_list:
    gifts = fetch_all_gifts_admin()
    if not gifts:
        st.info("Nenhum brinde cadastrado.")
    else:
        for gift in gifts:
            with st.expander(f"🎁 {gift['name']} — Estoque: {gift['stock']}"):
                with st.form(f"edit_gift_{gift['id']}"):
                    name = st.text_input("Nome", value=gift["name"], key=f"name_{gift['id']}")
                    stock = st.number_input(
                        "Estoque",
                        min_value=0,
                        value=int(gift["stock"]),
                        step=1,
                        key=f"stock_{gift['id']}",
                    )
                    purchase_price = st.number_input(
                        "Preço de compra",
                        min_value=0.0,
                        value=float(gift["purchase_price"]),
                        step=0.01,
                        key=f"pp_{gift['id']}",
                    )
                    purchase_freight = st.number_input(
                        "Frete de compra",
                        min_value=0.0,
                        value=float(gift["purchase_freight"]),
                        step=0.01,
                        key=f"pf_{gift['id']}",
                    )
                    sale_markup = st.number_input(
                        "Repasse ao cliente",
                        min_value=0.0,
                        value=float(gift["sale_markup"]),
                        step=0.01,
                        key=f"sm_{gift['id']}",
                    )

                    custo_total = float(purchase_price) + float(purchase_freight)
                    absorvido = custo_total - float(sale_markup)
                    st.caption(
                        f"Custo total: {format_currency(custo_total)} | "
                        f"Você absorve: {format_currency(max(absorvido, 0))}"
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
                            update_gift(
                                gift["id"],
                                {
                                    "name": name,
                                    "stock": stock,
                                    "purchase_price": purchase_price,
                                    "purchase_freight": purchase_freight,
                                    "sale_markup": sale_markup,
                                },
                            )
                            st.success("Atualizado!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro: {e}")

                    if remove:
                        try:
                            delete_gift(gift["id"])
                            st.success("Excluído!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro: {e}")
