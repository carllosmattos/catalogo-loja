"""CRUD de produtos com upload de imagens e vínculo de brindes."""

import streamlit as st

from lib.auth import require_auth, render_admin_nav
from lib.catalog import (
    create_product,
    delete_product,
    fetch_all_gifts_admin,
    fetch_all_products,
    fetch_product_gifts,
    resize_image,
    set_product_gifts,
    update_product,
    upload_image,
)
from lib.profit import calculate_profit
from lib.utils import format_currency

st.set_page_config(page_title="Admin — Produtos", page_icon="👗", layout="wide")

if not require_auth():
    st.stop()

render_admin_nav()
st.title("👗 Produtos")

gifts = fetch_all_gifts_admin()
gift_options = {g["name"]: g["id"] for g in gifts}

tab_list, tab_new = st.tabs(["Lista de produtos", "Novo produto"])

with tab_new:
    with st.form("new_product"):
        name = st.text_input("Nome da peça")
        description = st.text_area("Descrição")
        category = st.text_input("Categoria", placeholder="Ex: Vestidos, Blusas")
        size = st.text_input("Tamanho", placeholder="Ex: P, M, G")

        col1, col2 = st.columns(2)
        with col1:
            purchase_price = st.number_input(
                "Preço de compra (R$)", min_value=0.0, value=0.0, step=0.01
            )
            purchase_freight = st.number_input(
                "Frete na compra (R$)", min_value=0.0, value=0.0, step=0.01
            )
            sale_price = st.number_input(
                "Preço de venda (R$)", min_value=0.0, value=0.0, step=0.01
            )
        with col2:
            sale_freight = st.number_input(
                "Frete cobrado do cliente (R$)",
                min_value=0.0,
                value=0.0,
                step=0.01,
                help="0 se você absorver o frete",
            )
            stock = st.number_input("Estoque", min_value=0, value=0, step=1)
            active = st.checkbox("Ativo no catálogo", value=True)

        images = st.file_uploader(
            "Fotos do produto",
            type=["png", "jpg", "jpeg", "webp"],
            accept_multiple_files=True,
        )

        st.markdown("**Brindes vinculados**")
        selected_gifts = st.multiselect(
            "Selecione brindes",
            options=list(gift_options.keys()),
        )
        gift_qty = {}
        for gn in selected_gifts:
            gift_qty[gn] = st.number_input(
                f"Qtd de '{gn}' por venda",
                min_value=1,
                value=1,
                step=1,
                key=f"new_qty_{gn}",
            )

        submitted = st.form_submit_button("Cadastrar produto", use_container_width=True)

        if submitted:
            if not name:
                st.error("Informe o nome do produto.")
            else:
                try:
                    image_urls = []
                    for img in images or []:
                        img_bytes = resize_image(img.read())
                        url = upload_image(img_bytes, img.name)
                        image_urls.append(url)

                    product = create_product(
                        {
                            "name": name,
                            "description": description,
                            "category": category,
                            "size": size,
                            "image_urls": image_urls,
                            "purchase_price": purchase_price,
                            "purchase_freight": purchase_freight,
                            "sale_price": sale_price,
                            "sale_freight": sale_freight,
                            "stock": stock,
                            "active": active,
                        }
                    )

                    if selected_gifts and product.get("id"):
                        links = [
                            {
                                "product_id": product["id"],
                                "gift_id": gift_options[gn],
                                "quantity_per_sale": gift_qty[gn],
                            }
                            for gn in selected_gifts
                        ]
                        set_product_gifts(product["id"], links)

                    st.success("Produto cadastrado!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")

with tab_list:
    products = fetch_all_products()
    if not products:
        st.info("Nenhum produto cadastrado.")
    else:
        for product in products:
            status = "✅" if product["active"] else "⏸️"
            with st.expander(
                f"{status} {product['name']} — {format_currency(float(product['sale_price']))}"
            ):
                linked = fetch_product_gifts(product["id"])
                profit = calculate_profit(product, linked)

                col_img, col_form = st.columns([1, 2])
                with col_img:
                    urls = product.get("image_urls") or []
                    if urls:
                        st.image(urls[0], use_container_width=True)

                with col_form:
                    with st.form(f"edit_product_{product['id']}"):
                        name = st.text_input(
                            "Nome", value=product["name"], key=f"n_{product['id']}"
                        )
                        description = st.text_area(
                            "Descrição",
                            value=product.get("description", ""),
                            key=f"d_{product['id']}",
                        )
                        category = st.text_input(
                            "Categoria",
                            value=product.get("category", ""),
                            key=f"c_{product['id']}",
                        )
                        size = st.text_input(
                            "Tamanho",
                            value=product.get("size", ""),
                            key=f"s_{product['id']}",
                        )

                        c1, c2 = st.columns(2)
                        with c1:
                            purchase_price = st.number_input(
                                "Preço compra",
                                min_value=0.0,
                                value=float(product["purchase_price"]),
                                step=0.01,
                                key=f"pp_{product['id']}",
                            )
                            purchase_freight = st.number_input(
                                "Frete compra",
                                min_value=0.0,
                                value=float(product["purchase_freight"]),
                                step=0.01,
                                key=f"pf_{product['id']}",
                            )
                            sale_price = st.number_input(
                                "Preço venda",
                                min_value=0.0,
                                value=float(product["sale_price"]),
                                step=0.01,
                                key=f"sp_{product['id']}",
                            )
                        with c2:
                            sale_freight = st.number_input(
                                "Frete cliente",
                                min_value=0.0,
                                value=float(product["sale_freight"]),
                                step=0.01,
                                key=f"sf_{product['id']}",
                            )
                            stock = st.number_input(
                                "Estoque",
                                min_value=0,
                                value=int(product["stock"]),
                                step=1,
                                key=f"st_{product['id']}",
                            )
                            active = st.checkbox(
                                "Ativo",
                                value=product["active"],
                                key=f"ac_{product['id']}",
                            )

                        current_gift_names = [
                            lg["gifts"]["name"]
                            for lg in linked
                            if lg.get("gifts")
                        ]
                        selected = st.multiselect(
                            "Brindes",
                            options=list(gift_options.keys()),
                            default=current_gift_names,
                            key=f"gifts_{product['id']}",
                        )
                        edit_qty = {}
                        for gn in selected:
                            existing = next(
                                (
                                    lg
                                    for lg in linked
                                    if lg.get("gifts", {}).get("name") == gn
                                ),
                                None,
                            )
                            default_qty = (
                                existing["quantity_per_sale"] if existing else 1
                            )
                            edit_qty[gn] = st.number_input(
                                f"Qtd '{gn}'",
                                min_value=1,
                                value=int(default_qty),
                                step=1,
                                key=f"eq_{product['id']}_{gn}",
                            )

                        new_images = st.file_uploader(
                            "Adicionar fotos",
                            type=["png", "jpg", "jpeg", "webp"],
                            accept_multiple_files=True,
                            key=f"img_{product['id']}",
                        )

                        margin_class = (
                            "profit-positive"
                            if profit.margem_percent >= 10
                            else "profit-negative"
                            if profit.margem_percent < 0
                            else "profit-warning"
                        )
                        st.markdown(
                            f"Lucro estimado: "
                            f"<span class='{margin_class}'>"
                            f"{format_currency(profit.lucro_bruto)} "
                            f"({profit.margem_percent:.1f}%)</span>",
                            unsafe_allow_html=True,
                        )

                        col_save, col_del = st.columns(2)
                        with col_save:
                            save = st.form_submit_button("Salvar", use_container_width=True)
                        with col_del:
                            remove = st.form_submit_button(
                                "Excluir", use_container_width=True, type="secondary"
                            )

                        if save:
                            try:
                                data = {
                                    "name": name,
                                    "description": description,
                                    "category": category,
                                    "size": size,
                                    "purchase_price": purchase_price,
                                    "purchase_freight": purchase_freight,
                                    "sale_price": sale_price,
                                    "sale_freight": sale_freight,
                                    "stock": stock,
                                    "active": active,
                                }
                                if new_images:
                                    urls = list(product.get("image_urls") or [])
                                    for img in new_images:
                                        img_bytes = resize_image(img.read())
                                        urls.append(upload_image(img_bytes, img.name))
                                    data["image_urls"] = urls

                                update_product(product["id"], data)
                                links = [
                                    {
                                        "product_id": product["id"],
                                        "gift_id": gift_options[gn],
                                        "quantity_per_sale": edit_qty[gn],
                                    }
                                    for gn in selected
                                ]
                                set_product_gifts(product["id"], links)
                                st.success("Atualizado!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro: {e}")

                        if remove:
                            try:
                                delete_product(product["id"])
                                st.success("Excluído!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro: {e}")
