"""CRUD de promoções."""

from datetime import datetime

import streamlit as st

from lib.auth import require_auth, render_sidebar
from lib.branding import configure_page
from lib.catalog import (
    create_promotion,
    fetch_all_products,
    fetch_all_promotions,
    resize_image,
    set_promotion_active,
    update_promotion,
    upload_image,
)
from lib.catalog_display import build_banner_header_markup
from lib.images import normalize_image_urls, render_admin_gallery
from lib.utils import format_currency

configure_page("Admin — Promoções", layout="wide", sidebar_state="expanded")
render_sidebar()

if not require_auth():
    st.stop()
st.title("🏷️ Promoções")

products = fetch_all_products()
product_options = {p["name"]: p["id"] for p in products}

tab_list, tab_new = st.tabs(["Lista de promoções", "Nova promoção"])


def _upload_promo_banner(file) -> str:
    img_bytes = resize_image(file.read(), max_size=1600)
    return upload_image(img_bytes, file.name, folder="banners")


with tab_new:
    with st.form("new_promo"):
        name = st.text_input("Nome da promoção", placeholder="Ex: Black Friday")
        description = st.text_area("Descrição")
        discount_type = st.selectbox(
            "Tipo de desconto",
            ["percent", "fixed"],
            format_func=lambda x: "% Percentual" if x == "percent" else "R$ Valor fixo",
        )
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
        show_banner = st.checkbox(
            "Exibir banner no catálogo",
            value=False,
            help="Substitui o banner padrão enquanto a promoção estiver ativa.",
        )
        banner_file = None
        gallery_files = st.file_uploader(
            "Fotos da promoção (carrossel no catálogo)",
            type=["png", "jpg", "jpeg", "webp"],
            accept_multiple_files=True,
            help="Opcional. Várias fotos aparecem em carrossel na página da promoção.",
        )
        if show_banner:
            banner_file = st.file_uploader(
                "Imagem do banner da promoção",
                type=["png", "jpg", "jpeg", "webp"],
                help="Horizontal (aprox. 2:1). Várias promoções com banner formam um carrossel.",
            )

        submitted = st.form_submit_button("Cadastrar promoção", use_container_width=True)

        if submitted:
            if not name:
                st.error("Informe o nome da promoção.")
            elif show_banner and not banner_file:
                st.error("Envie a imagem do banner ou desmarque \"Exibir banner no catálogo\".")
            else:
                try:
                    data = {
                        "name": name,
                        "description": description,
                        "discount_type": discount_type,
                        "discount_value": discount_value,
                        "applies_to": applies_to,
                        "product_ids": [product_options[p] for p in selected_products],
                        "starts_at": (
                            datetime.combine(starts_at, datetime.min.time()).isoformat()
                            if starts_at
                            else None
                        ),
                        "ends_at": (
                            datetime.combine(ends_at, datetime.max.time()).isoformat()
                            if ends_at
                            else None
                        ),
                        "active": active,
                        "show_banner": show_banner,
                    }
                    if show_banner and banner_file:
                        data["banner_url"] = _upload_promo_banner(banner_file)
                    if gallery_files:
                        data["image_urls"] = [
                            _upload_promo_banner(f) for f in gallery_files
                        ]
                    create_promotion(data)
                    st.success("Promoção cadastrada!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")

with tab_list:
    filter_opt = st.radio(
        "Mostrar",
        ["Ativas", "Arquivadas", "Todas"],
        horizontal=True,
        key="promo_filter",
    )
    all_promos = fetch_all_promotions()
    if filter_opt == "Ativas":
        promos = [p for p in all_promos if p.get("active")]
    elif filter_opt == "Arquivadas":
        promos = [p for p in all_promos if not p.get("active")]
    else:
        promos = all_promos

    st.caption(
        "Desativar remove do catálogo; vendas passadas mantêm o nome da promoção. "
        "Promoções com banner ativo aparecem no topo do catálogo (carrossel se houver mais de uma)."
    )
    if not promos:
        st.info("Nenhuma promoção cadastrada.")
    else:
        for promo in promos:
            status = "✅" if promo["active"] else "⏸️"
            dtype = promo["discount_type"]
            dval = float(promo["discount_value"])
            banner_tag = " 🖼️" if promo.get("show_banner") and promo.get("banner_url") else ""
            label = (
                f"{status} {promo['name']}{banner_tag} — {dval:.0f}%"
                if dtype == "percent"
                else f"{status} {promo['name']}{banner_tag} — {format_currency(dval)}"
            )
            with st.expander(label):
                if promo.get("banner_url"):
                    st.markdown(
                        build_banner_header_markup("single", [promo["banner_url"]]),
                        unsafe_allow_html=True,
                    )

                promo_urls = normalize_image_urls(promo)
                if promo_urls:
                    st.markdown("**Fotos da promoção**")
                    render_admin_gallery(
                        promo_urls,
                        f"promo_{promo['id']}",
                        lambda new_urls, pid=promo["id"]: update_promotion(
                            pid, {"image_urls": new_urls}
                        ),
                    )

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
                    show_banner = st.checkbox(
                        "Exibir banner no catálogo",
                        value=bool(promo.get("show_banner")),
                        key=f"sb_{promo['id']}",
                    )
                    banner_file = None
                    gallery_files = st.file_uploader(
                        "Adicionar fotos da promoção",
                        type=["png", "jpg", "jpeg", "webp"],
                        accept_multiple_files=True,
                        key=f"gf_{promo['id']}",
                    )
                    if show_banner:
                        if promo.get("banner_url"):
                            st.caption("Banner atual salvo. Envie novo arquivo para substituir.")
                        banner_file = st.file_uploader(
                            "Banner da promoção",
                            type=["png", "jpg", "jpeg", "webp"],
                            key=f"bf_{promo['id']}",
                        )

                    col1, col2 = st.columns(2)
                    with col1:
                        save = st.form_submit_button("Salvar", use_container_width=True)
                    with col2:
                        archive_label = "Reativar" if not promo["active"] else "Arquivar"
                        archive = st.form_submit_button(
                            archive_label,
                            use_container_width=True,
                            type="secondary",
                        )

                    if save:
                        if show_banner and not promo.get("banner_url") and not banner_file:
                            st.error("Envie o banner ou desmarque \"Exibir banner no catálogo\".")
                        else:
                            try:
                                payload = {
                                    "name": name,
                                    "description": description,
                                    "discount_type": discount_type,
                                    "discount_value": discount_value,
                                    "applies_to": applies_to,
                                    "product_ids": [product_options[p] for p in selected],
                                    "active": active,
                                    "show_banner": show_banner,
                                }
                                if not show_banner:
                                    payload["banner_url"] = None
                                elif banner_file:
                                    payload["banner_url"] = _upload_promo_banner(banner_file)
                                if gallery_files:
                                    merged = list(normalize_image_urls(promo))
                                    for gf in gallery_files:
                                        merged.append(_upload_promo_banner(gf))
                                    payload["image_urls"] = merged

                                update_promotion(promo["id"], payload)
                                st.success("Atualizado!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro: {e}")

                    if archive:
                        try:
                            set_promotion_active(promo["id"], not promo["active"])
                            label = "reativada" if not promo["active"] else "arquivada"
                            st.success(f"Promoção {label}!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro: {e}")
