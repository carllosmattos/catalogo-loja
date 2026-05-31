"""CRUD de brindes."""

import streamlit as st

from lib.auth import require_auth, render_sidebar
from lib.branding import configure_page
from lib.catalog import (
    create_gift,
    fetch_all_gifts_admin,
    resize_image,
    set_gift_active,
    update_gift,
    upload_image,
)
from lib.utils import format_currency

configure_page("Admin — Brindes", layout="wide", sidebar_state="expanded")
render_sidebar()

if not require_auth():
    st.stop()
st.title("🎁 Brindes")

tab_list, tab_new = st.tabs(["Lista de brindes", "Novo brinde"])

with tab_new:
    with st.form("new_gift"):
        name = st.text_input("Nome do brinde")
        photo = st.file_uploader(
            "Foto do brinde",
            type=["png", "jpg", "jpeg", "webp"],
        )
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
        active = st.checkbox("Ativo", value=True)
        submitted = st.form_submit_button("Cadastrar brinde", use_container_width=True)
        if submitted:
            if not name:
                st.error("Informe o nome do brinde.")
            else:
                try:
                    data = {
                        "name": name,
                        "stock": stock,
                        "purchase_price": purchase_price,
                        "purchase_freight": purchase_freight,
                        "sale_markup": sale_markup,
                        "active": active,
                    }
                    if photo:
                        img_bytes = resize_image(photo.read())
                        data["image_url"] = upload_image(
                            img_bytes, photo.name, folder="gifts"
                        )
                    create_gift(data)
                    st.success("Brinde cadastrado!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")

with tab_list:
    filter_opt = st.radio(
        "Mostrar",
        ["Ativos", "Arquivados", "Todos"],
        horizontal=True,
        key="gift_filter",
    )
    active_filter = {"Ativos": True, "Arquivados": False, "Todos": None}[filter_opt]
    gifts = fetch_all_gifts_admin(active_filter=active_filter)

    st.caption("Arquivar remove brinde de novas vendas; histórico de vendas permanece.")
    if not gifts:
        st.info("Nenhum brinde neste filtro.")
    else:
        for gift in gifts:
            status = "✅" if gift.get("active", True) else "⏸️"
            with st.expander(
                f"{status} {gift['name']} — Estoque: {gift['stock']}"
            ):
                if gift.get("image_url"):
                    st.image(gift["image_url"], width=120)
                with st.form(f"edit_gift_{gift['id']}"):
                    name = st.text_input("Nome", value=gift["name"], key=f"name_{gift['id']}")
                    new_photo = st.file_uploader(
                        "Nova foto",
                        type=["png", "jpg", "jpeg", "webp"],
                        key=f"photo_{gift['id']}",
                    )
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
                    active = st.checkbox(
                        "Ativo",
                        value=gift.get("active", True),
                        key=f"active_{gift['id']}",
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
                        archive_label = (
                            "Reativar" if not gift.get("active", True) else "Arquivar"
                        )
                        archive = st.form_submit_button(
                            archive_label,
                            use_container_width=True,
                            type="secondary",
                        )

                    if save:
                        try:
                            data = {
                                "name": name,
                                "stock": stock,
                                "purchase_price": purchase_price,
                                "purchase_freight": purchase_freight,
                                "sale_markup": sale_markup,
                                "active": active,
                            }
                            if new_photo:
                                img_bytes = resize_image(new_photo.read())
                                data["image_url"] = upload_image(
                                    img_bytes, new_photo.name, folder="gifts"
                                )
                            update_gift(gift["id"], data)
                            st.success("Atualizado!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro: {e}")

                    if archive:
                        try:
                            is_active = gift.get("active", True)
                            set_gift_active(gift["id"], not is_active)
                            label = "reativado" if not is_active else "arquivado"
                            st.success(f"Brinde {label}!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro: {e}")
