"""Catálogo público de roupas — mobile-first para iPhone."""

import math

import streamlit as st

from lib.branding import configure_page, merge_brand_settings
from lib.cart import (
    add_to_cart,
    cart_item_from_product,
    cart_piece_count,
    cart_totals,
    clear_cart,
    get_cart,
    remove_from_cart,
    update_qty,
)
from lib.catalog import (
    fetch_active_promotions,
    fetch_distinct_product_categories,
    fetch_product_gifts,
    fetch_products_page,
    fetch_store_settings,
)
from lib.catalog_display import build_product_card_html, render_catalog_header
from lib.categories import fetch_categories
from lib.customer_session import (
    customer_display_name,
    get_catalog_customer,
    logout_catalog_customer,
    lookup_by_phone,
    save_profile,
    set_catalog_customer,
)
from lib.profit import calculate_profit
from lib.theme import inject_theme
from lib.utils import format_cpf, format_currency, is_valid_cpf
from lib.whatsapp import build_cart_message, build_order_message, build_whatsapp_url

CATALOG_PAGE_SIZE = 20

configure_page("Catálogo", sidebar_state="collapsed")

try:
    settings = merge_brand_settings(fetch_store_settings())
except Exception as e:
    st.error(f"Erro ao conectar ao Supabase: {e}")
    st.info("Tente novamente em alguns instantes.")
    st.stop()

inject_theme(settings, hide_sidebar=True)

store_name = settings["store_name"]
whatsapp_number = settings.get("whatsapp_number", "")
catalog_customer = get_catalog_customer()
promotions = fetch_active_promotions()

render_catalog_header(settings, promotions)

if catalog_customer and catalog_customer.get("name"):
    st.caption(f"Olá, **{customer_display_name(catalog_customer)}**!")

if not whatsapp_number:
    st.warning("Catálogo em configuração. WhatsApp ainda não definido.")

piece_count = cart_piece_count()
nav_options = ["Catálogo", "Carrinho", "Minha conta"]
view = st.radio(
    "Navegação",
    options=nav_options,
    horizontal=True,
    label_visibility="collapsed",
    key="catalog_nav",
)
if piece_count > 0 and view != "Carrinho":
    st.caption(f"🛒 {piece_count} peça(s) no carrinho — toque em **Carrinho** para finalizar")

# ── Minha conta ─────────────────────────────────────────────
if view == "Minha conta":
    if catalog_customer and catalog_customer.get("id"):
        st.subheader(f"Olá, {customer_display_name(catalog_customer)}!")
        with st.form("edit_profile"):
            prof_name = st.text_input(
                "Nome *",
                value=catalog_customer.get("name", ""),
            )
            prof_phone = st.text_input(
                "WhatsApp / telefone *",
                value=catalog_customer.get("phone", ""),
            )
            prof_cpf = st.text_input(
                "CPF *",
                value=format_cpf(catalog_customer.get("cpf", "")),
            )
            prof_address = st.text_area(
                "Endereço de entrega",
                value=catalog_customer.get("address", ""),
                placeholder="Rua, número, bairro, cidade…",
            )
            save_prof = st.form_submit_button("Salvar cadastro", use_container_width=True)
            if save_prof:
                try:
                    updated = save_profile(
                        prof_name, prof_phone, prof_cpf, prof_address
                    )
                    set_catalog_customer(updated)
                    st.success("Cadastro atualizado!")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

        if st.button("Sair", use_container_width=True):
            logout_catalog_customer()
            st.rerun()

    elif catalog_customer and catalog_customer.get("is_new"):
        st.subheader("Complete seu cadastro")
        st.caption(f"Telefone: {catalog_customer.get('phone', '')}")
        with st.form("new_profile"):
            new_name = st.text_input("Nome *")
            new_cpf = st.text_input("CPF *", placeholder="000.000.000-00")
            new_address = st.text_area(
                "Endereço de entrega",
                placeholder="Rua, número, bairro, cidade…",
            )
            if st.form_submit_button("Salvar cadastro", use_container_width=True):
                try:
                    if not new_name.strip():
                        st.error("Informe seu nome.")
                    elif not is_valid_cpf(new_cpf):
                        st.error("CPF inválido.")
                    else:
                        created = save_profile(
                            new_name,
                            catalog_customer["phone"],
                            new_cpf,
                            new_address,
                        )
                        set_catalog_customer(created)
                        st.success("Cadastro criado!")
                        st.rerun()
                except Exception as e:
                    st.error(str(e))
        if st.button("Voltar", use_container_width=True):
            logout_catalog_customer()
            st.rerun()

    else:
        st.subheader("Entrar com seu telefone")
        st.caption("Informe o WhatsApp para reconhecermos você e agilizar seu pedido.")
        login_phone = st.text_input(
            "WhatsApp / telefone",
            placeholder="5511999999999",
            key="login_phone_input",
        )
        if st.button("Entrar", type="primary", use_container_width=True):
            found = lookup_by_phone(login_phone)
            if found:
                set_catalog_customer(found)
                st.rerun()
            elif len("".join(c for c in login_phone if c.isdigit())) >= 10:
                digits = "".join(c for c in login_phone if c.isdigit())
                set_catalog_customer({"phone": digits, "is_new": True})
                st.rerun()
            else:
                st.error("Informe um telefone válido.")

# ── Carrinho ────────────────────────────────────────────────
elif view == "Carrinho":
    cart = get_cart()
    totals = cart_totals()

    if not cart:
        st.info("Seu carrinho está vazio. Volte ao catálogo e adicione peças.")
    else:
        for item in cart:
            pid = item["product_id"]
            qty = int(item.get("quantity", 1))
            unit = float(item.get("preco_final", 0))
            subtotal = unit * qty

            st.markdown('<div class="cart-item">', unsafe_allow_html=True)
            st.markdown(f"**{item.get('name', 'Peça')}**")
            if item.get("size"):
                st.caption(f"Tam. {item['size']}")
            st.caption(
                f"Unit. {format_currency(unit)} · "
                f"Subtotal {format_currency(subtotal)}"
            )
            if item.get("promotion_name"):
                st.caption(f"Promo: {item['promotion_name']}")
            gifts = item.get("gifts") or []
            if gifts:
                gift_txt = ", ".join(
                    f"{g['name']} x{g['qty'] * qty}" for g in gifts
                )
                st.caption(f"Brinde(s): {gift_txt}")

            col_q, col_r = st.columns([2, 1])
            with col_q:
                new_qty = st.number_input(
                    "Qtd",
                    min_value=1,
                    max_value=int(item.get("max_stock", 1)),
                    value=qty,
                    step=1,
                    key=f"cart_qty_{pid}",
                )
                if new_qty != qty:
                    if update_qty(pid, new_qty):
                        st.rerun()
            with col_r:
                if st.button("Remover", key=f"cart_rm_{pid}", use_container_width=True):
                    remove_from_cart(pid)
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("")

        st.markdown('<div class="cart-summary">', unsafe_allow_html=True)
        st.markdown(
            f"**Total ({totals['pieces']} peça(s)):** "
            f"{format_currency(totals['total'])}"
        )
        st.markdown("</div>", unsafe_allow_html=True)

        col_wa, col_clear = st.columns([2, 1])
        with col_wa:
            if whatsapp_number:
                cart_msg = build_cart_message(cart, store_name, catalog_customer)
                wa_url = build_whatsapp_url(whatsapp_number, cart_msg)
                st.link_button(
                    "Finalizar no WhatsApp",
                    wa_url,
                    use_container_width=True,
                    type="primary",
                )
            else:
                st.info(
                    "WhatsApp da loja ainda não configurado. "
                    "Peça à loja para ativar o checkout."
                )
        with col_clear:
            if st.button("Limpar carrinho", key="clear_cart_btn", use_container_width=True):
                clear_cart()
                st.rerun()

# ── Catálogo ────────────────────────────────────────────────
else:
    db_categories = fetch_categories(active_only=True)
    if db_categories:
        filter_options = ["Todas"] + [c["name"] for c in db_categories]
        category_ids = {
            c["name"]: c["id"] for c in db_categories if c.get("id")
        }
    else:
        text_categories = fetch_distinct_product_categories(active_only=True)
        filter_options = ["Todas"] + text_categories
        category_ids = {}

    if "catalog_page" not in st.session_state:
        st.session_state.catalog_page = 1
    if "catalog_category" not in st.session_state:
        st.session_state.catalog_category = "Todas"

    st.markdown('<div class="catalog-filter-wrap">', unsafe_allow_html=True)
    selected_category = st.radio(
        "Categoria",
        options=filter_options,
        horizontal=True,
        label_visibility="collapsed",
        key="catalog_category_radio",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if selected_category != st.session_state.catalog_category:
        st.session_state.catalog_category = selected_category
        st.session_state.catalog_page = 1

    cat_id = category_ids.get(selected_category) if selected_category != "Todas" else None
    cat_name = selected_category if selected_category != "Todas" and not cat_id else None

    page_products, total_products = fetch_products_page(
        active_only=True,
        category_id=cat_id,
        category_name=cat_name,
        page=st.session_state.catalog_page,
        per_page=CATALOG_PAGE_SIZE,
    )

    if total_products == 0:
        if selected_category != "Todas":
            st.info(f"Nenhuma peça em **{selected_category}** no momento.")
        else:
            st.info("Em breve novidades por aqui!")
        st.stop()

    total_pages = max(1, math.ceil(total_products / CATALOG_PAGE_SIZE))
    if st.session_state.catalog_page > total_pages:
        st.session_state.catalog_page = total_pages
        st.rerun()

    start_idx = (st.session_state.catalog_page - 1) * CATALOG_PAGE_SIZE + 1
    end_idx = min(st.session_state.catalog_page * CATALOG_PAGE_SIZE, total_products)
    st.markdown(
        f'<div class="catalog-pagination">'
        f"{start_idx}–{end_idx} de {total_products} peça(s)"
        f"</div>",
        unsafe_allow_html=True,
    )

    def _render_product_cell(product: dict, col) -> None:
        with col:
            linked_gifts = fetch_product_gifts(product["id"])
            profit = calculate_profit(product, linked_gifts, promotions)
            out_of_stock = profit.stock <= 0
            pid = str(product["id"])

            st.markdown(
                build_product_card_html(
                    product, profit, out_of_stock, compact=True
                ),
                unsafe_allow_html=True,
            )

            if out_of_stock:
                st.button(
                    "Indisponível",
                    disabled=True,
                    use_container_width=True,
                    key=f"unavail_{pid}",
                )
            else:
                if st.button(
                    "Adicionar",
                    key=f"add_{pid}",
                    use_container_width=True,
                ):
                    item = cart_item_from_product(product, profit)
                    if add_to_cart(item):
                        st.toast("Adicionado ao carrinho!")
                        st.rerun()
                    else:
                        st.error("Estoque insuficiente.")
                if whatsapp_number:
                    message = build_order_message(
                        product, profit, store_name, catalog_customer
                    )
                    wa_url = build_whatsapp_url(whatsapp_number, message)
                    st.link_button(
                        "Comprar",
                        wa_url,
                        use_container_width=True,
                        type="primary",
                        key=f"buy_{pid}",
                    )
                else:
                    st.button(
                        "Comprar",
                        disabled=True,
                        use_container_width=True,
                        key=f"buy_off_{pid}",
                        help="WhatsApp da loja não configurado",
                    )

    for row_start in range(0, len(page_products), 2):
        col_left, col_right = st.columns(2, gap="small")
        _render_product_cell(page_products[row_start], col_left)
        if row_start + 1 < len(page_products):
            _render_product_cell(page_products[row_start + 1], col_right)

    st.markdown(
        f'<div class="catalog-pagination">'
        f"Página {st.session_state.catalog_page} de {total_pages}"
        f"</div>",
        unsafe_allow_html=True,
    )

    nav_prev, nav_mid, nav_next = st.columns([1, 2, 1])
    with nav_prev:
        if st.button(
            "← Anterior",
            disabled=st.session_state.catalog_page <= 1,
            use_container_width=True,
            key="catalog_prev_page",
        ):
            st.session_state.catalog_page -= 1
            st.rerun()
    with nav_mid:
        st.markdown(
            f"<p style='text-align:center;margin:0.4rem 0;color:#666;"
            f"font-size:0.85rem;'>"
            f"{st.session_state.catalog_page} / {total_pages}</p>",
            unsafe_allow_html=True,
        )
    with nav_next:
        if st.button(
            "Próxima →",
            disabled=st.session_state.catalog_page >= total_pages,
            use_container_width=True,
            key="catalog_next_page",
        ):
            st.session_state.catalog_page += 1
            st.rerun()

st.markdown("---")
st.caption(f"Catálogo {store_name} · Compre pelo WhatsApp")
