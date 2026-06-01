"""CRUD de produtos com upload de imagens e vínculo de brindes."""

import streamlit as st

from lib.auth import require_auth, render_sidebar
from lib.branding import configure_page
from lib.catalog import (
    create_product,
    duplicate_product,
    fetch_all_gifts_admin,
    fetch_all_products,
    fetch_product_gifts,
    resize_image,
    set_product_active,
    set_product_gifts,
    update_product,
    upload_image,
)
from lib.categories import (
    category_choices,
    create_category,
    fetch_all_categories_admin,
    set_category_active,
    update_category,
)
from lib.images import normalize_image_urls, render_admin_gallery
from lib.product_sizes import (
    SIZES,
    fetch_product_sizes,
    set_product_sizes,
    size_stock_warnings,
)
from lib.profit import calculate_profit
from lib.utils import format_currency

configure_page("Admin — Produtos", layout="wide", sidebar_state="expanded")
render_sidebar()

if not require_auth():
    st.stop()
st.title("👗 Produtos")

gifts = fetch_all_gifts_admin(active_filter=True)
gift_options = {g["name"]: g["id"] for g in gifts}
admin_categories = fetch_all_categories_admin(active_filter=True)
category_options = category_choices(admin_categories)


def _category_fields(
    key_prefix: str,
    default_name: str = "",
    default_id: str | None = None,
) -> tuple[str | None, str]:
    if category_options:
        names = list(category_options.keys())
        default_name = default_name or (names[0] if names else "")
        if default_name not in names and default_id:
            for name, cid in category_options.items():
                if cid == default_id:
                    default_name = name
                    break
        idx = names.index(default_name) if default_name in names else 0
        picked = st.selectbox(
            "Categoria",
            options=names,
            index=idx,
            key=f"{key_prefix}_cat",
        )
        return category_options[picked], picked
    return None, st.text_input(
        "Categoria",
        value=default_name,
        placeholder="Ex: Vestidos, Blusas",
        key=f"{key_prefix}_cat_text",
    )

tab_list, tab_new, tab_cats = st.tabs(
    ["Lista de produtos", "Novo produto", "Categorias"]
)

with tab_new:
    with st.form("new_product"):
        name = st.text_input("Nome da peça")
        description = st.text_area("Descrição")
        category_id, category = _category_fields("new")

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
            active = st.checkbox("Ativo no catálogo", value=True)

        st.markdown("**Estoque por tamanho**")
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            stock_p = st.number_input("P", min_value=0, value=0, step=1, key="new_st_p")
        with sc2:
            stock_m = st.number_input("M", min_value=0, value=0, step=1, key="new_st_m")
        with sc3:
            stock_g = st.number_input("G", min_value=0, value=0, step=1, key="new_st_g")

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
                            "category_id": category_id,
                            "size": "",
                            "image_urls": image_urls,
                            "purchase_price": purchase_price,
                            "purchase_freight": purchase_freight,
                            "sale_price": sale_price,
                            "sale_freight": sale_freight,
                            "stock": stock_p + stock_m + stock_g,
                            "active": active,
                        }
                    )

                    if product.get("id"):
                        set_product_sizes(
                            product["id"],
                            {"P": stock_p, "M": stock_m, "G": stock_g},
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
    filter_opt = st.radio(
        "Mostrar",
        ["Ativos", "Arquivados", "Todos"],
        horizontal=True,
        key="product_filter",
    )
    active_filter = {"Ativos": True, "Arquivados": False, "Todos": None}[filter_opt]
    all_products = fetch_all_products()
    if active_filter is True:
        products = [p for p in all_products if p.get("active")]
    elif active_filter is False:
        products = [p for p in all_products if not p.get("active")]
    else:
        products = all_products

    st.caption(
        "Arquivar remove do catálogo; vendas passadas permanecem nos relatórios."
    )
    if not products:
        st.info("Nenhum produto neste filtro.")
    else:
        st.caption(
            "Duplicar cria cópia com estoque 0 — ideal para nova leva com preço/custo diferente."
        )
        for product in products:
            status = "✅" if product["active"] else "⏸️"
            with st.expander(
                f"{status} {product['name']} — {format_currency(float(product['sale_price']))}"
            ):
                if st.button("Duplicar", key=f"dup_{product['id']}"):
                    try:
                        duplicate_product(product["id"])
                        st.success("Cópia criada com estoque 0!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")
                linked = fetch_product_gifts(product["id"], active_gifts_only=False)
                sizes = product.get("sizes") or fetch_product_sizes(product["id"])
                for warn in size_stock_warnings(sizes):
                    if "todos" in warn.lower():
                        st.error(f"⚠️ {warn}")
                    else:
                        st.warning(f"⚠️ {warn}")

                urls = normalize_image_urls(product)
                st.markdown("**Fotos**")
                render_admin_gallery(
                    urls,
                    f"prod_{product['id']}",
                    lambda new_urls: update_product(
                        product["id"], {"image_urls": new_urls}
                    ),
                )

                profit = calculate_profit(product, linked)

                with st.form(f"edit_product_{product['id']}"):
                        name = st.text_input(
                            "Nome", value=product["name"], key=f"n_{product['id']}"
                        )
                        description = st.text_area(
                            "Descrição",
                            value=product.get("description", ""),
                            key=f"d_{product['id']}",
                        )
                        category_id, category = _category_fields(
                            f"edit_{product['id']}",
                            default_name=product.get("category", ""),
                            default_id=product.get("category_id"),
                        )

                        st.markdown("**Estoque por tamanho**")
                        size_stocks = {}
                        sc1, sc2, sc3 = st.columns(3)
                        for sz, scol in zip(SIZES, (sc1, sc2, sc3)):
                            current = next(
                                (int(s["stock"]) for s in sizes if s["size"] == sz),
                                0,
                            )
                            with scol:
                                size_stocks[sz] = st.number_input(
                                    sz,
                                    min_value=0,
                                    value=current,
                                    step=1,
                                    key=f"st_{product['id']}_{sz}",
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
                            active = st.checkbox(
                                "Ativo",
                                value=product["active"],
                                key=f"ac_{product['id']}",
                            )

                        new_images = st.file_uploader(
                            "Adicionar fotos",
                            type=["png", "jpg", "jpeg", "webp"],
                            accept_multiple_files=True,
                            key=f"img_{product['id']}",
                        )

                        current_gift_names = [
                            lg["gift_data"]["name"]
                            for lg in linked
                            if lg.get("gift_data")
                        ]
                        edit_gift_options = dict(gift_options)
                        for lg in linked:
                            gd = lg.get("gift_data")
                            if gd and gd["name"] not in edit_gift_options:
                                edit_gift_options[gd["name"]] = gd["id"]
                        selected = st.multiselect(
                            "Brindes",
                            options=list(edit_gift_options.keys()),
                            default=current_gift_names,
                            key=f"gifts_{product['id']}",
                        )
                        edit_qty = {}
                        for gn in selected:
                            existing = next(
                                (
                                    lg
                                    for lg in linked
                                    if lg.get("gift_data", {}).get("name") == gn
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

                        col_save, col_archive = st.columns(2)
                        with col_save:
                            save = st.form_submit_button("Salvar", use_container_width=True)
                        with col_archive:
                            archive_label = (
                                "Reativar" if not product["active"] else "Arquivar"
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
                                    "description": description,
                                    "category": category,
                                    "category_id": category_id,
                                    "size": "",
                                    "purchase_price": purchase_price,
                                    "purchase_freight": purchase_freight,
                                    "sale_price": sale_price,
                                    "sale_freight": sale_freight,
                                    "stock": sum(size_stocks.values()),
                                    "active": active,
                                }
                                if new_images:
                                    urls = list(normalize_image_urls(product))
                                    for img in new_images:
                                        img_bytes = resize_image(img.read())
                                        urls.append(upload_image(img_bytes, img.name))
                                    data["image_urls"] = urls

                                update_product(product["id"], data)
                                set_product_sizes(product["id"], size_stocks)
                                links = [
                                    {
                                        "product_id": product["id"],
                                        "gift_id": edit_gift_options[gn],
                                        "quantity_per_sale": edit_qty[gn],
                                    }
                                    for gn in selected
                                ]
                                set_product_gifts(product["id"], links)
                                st.success("Atualizado!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro: {e}")

                        if archive:
                            try:
                                set_product_active(product["id"], not product["active"])
                                label = "reativado" if not product["active"] else "arquivado"
                                st.success(f"Produto {label}!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro: {e}")

with tab_cats:
    st.caption(
        "Categorias aparecem no filtro do catálogo. "
        "Rode a migração `010_categories.sql` no Supabase se a aba estiver vazia."
    )
    with st.form("new_category"):
        new_cat_name = st.text_input("Nova categoria")
        new_cat_order = st.number_input("Ordem", min_value=0, value=0, step=1)
        if st.form_submit_button("Cadastrar categoria", use_container_width=True):
            if not new_cat_name.strip():
                st.error("Informe o nome da categoria.")
            else:
                try:
                    create_category(new_cat_name.strip(), int(new_cat_order))
                    st.success("Categoria criada!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")

    all_cats = fetch_all_categories_admin(active_filter=None)
    if not all_cats:
        st.info(
            "Nenhuma categoria cadastrada. Execute `010_categories.sql` no Supabase "
            "ou cadastre acima."
        )
    else:
        for cat in all_cats:
            status = "✅" if cat.get("active") else "⏸️"
            with st.expander(f"{status} {cat['name']}"):
                with st.form(f"edit_cat_{cat['id']}"):
                    cat_name = st.text_input(
                        "Nome",
                        value=cat["name"],
                        key=f"cn_{cat['id']}",
                    )
                    cat_order = st.number_input(
                        "Ordem",
                        min_value=0,
                        value=int(cat.get("sort_order") or 0),
                        step=1,
                        key=f"co_{cat['id']}",
                    )
                    cat_active = st.checkbox(
                        "Ativa no catálogo",
                        value=cat.get("active", True),
                        key=f"ca_{cat['id']}",
                    )
                    save_cat = st.form_submit_button("Salvar", use_container_width=True)
                    archive_cat = st.form_submit_button(
                        "Arquivar" if cat.get("active") else "Reativar",
                        use_container_width=True,
                    )
                    if save_cat:
                        try:
                            update_category(
                                cat["id"],
                                {
                                    "name": cat_name.strip(),
                                    "sort_order": int(cat_order),
                                    "active": cat_active,
                                },
                            )
                            st.success("Categoria atualizada!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro: {e}")
                    if archive_cat:
                        try:
                            set_category_active(cat["id"], not cat.get("active", True))
                            st.success("Categoria atualizada!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro: {e}")

