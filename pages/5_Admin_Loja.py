"""Configurações da loja: banner, logo, cores e WhatsApp."""

import streamlit as st

from lib.auth import require_auth, render_sidebar
from lib.branding import (
    PRIMARY,
    SECONDARY,
    ACCENT,
    configure_page,
    get_logo_path,
    merge_brand_settings,
    resolve_logo_url,
)
from lib.catalog import (
    create_store_banner,
    delete_store_banner,
    fetch_store_banners,
    fetch_store_settings,
    resize_image,
    set_store_banner_active,
    update_store_settings,
    upload_image,
)
from lib.catalog_display import build_banner_header_markup, render_catalog_header
from lib.theme import inject_theme
from lib.utils import parse_whatsapp_number

configure_page("Admin — Loja", layout="wide", sidebar_state="expanded")
render_sidebar()

if not require_auth():
    st.stop()
st.title("🏪 Configurações da Loja")

settings = merge_brand_settings(fetch_store_settings())
inject_theme(settings)

st.subheader("Banners do catálogo")
st.caption(
    "Envie um ou mais banners. Vários **ativos** aparecem em carrossel no topo do catálogo. "
    "Promoções com banner ativo têm prioridade sobre estes."
)

store_banners = fetch_store_banners()
if not store_banners and settings.get("default_banner_url"):
    st.info(
        "Execute a migração `019_store_banners.sql` no Supabase para gerenciar vários banners. "
        "Enquanto isso, vale o banner único legado abaixo."
    )
    legacy_url = settings["default_banner_url"]
    st.markdown(
        build_banner_header_markup("single", [legacy_url]),
        unsafe_allow_html=True,
    )

active_urls = [b["image_url"] for b in store_banners if b.get("active") and b.get("image_url")]
if active_urls:
    mode = "carousel" if len(active_urls) >= 2 else "single"
    st.markdown(
        build_banner_header_markup(mode, active_urls),
        unsafe_allow_html=True,
    )
elif store_banners:
    st.warning("Nenhum banner ativo — ative ao menos um ou envie uma imagem.")
else:
    st.info("Nenhum banner cadastrado. Envie abaixo ou use `resources/banner.png` como fallback.")

with st.form("banner_upload_form"):
    banner_files = st.file_uploader(
        "Adicionar banner(s)",
        type=["png", "jpg", "jpeg", "webp"],
        accept_multiple_files=True,
        help="Horizontal (aprox. 2:1). Selecione várias imagens de uma vez.",
    )
    save_banners = st.form_submit_button("Enviar banner(s)", use_container_width=True)
    if save_banners:
        if not banner_files:
            st.error("Selecione ao menos uma imagem.")
        else:
            try:
                for bf in banner_files:
                    img_bytes = resize_image(bf.read(), max_size=1600)
                    url = upload_image(img_bytes, bf.name, folder="banners")
                    create_store_banner(url)
                st.success(f"{len(banner_files)} banner(s) adicionado(s)!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao enviar: {e}")

if store_banners:
    st.markdown("**Banners cadastrados**")
    for banner in store_banners:
        bid = banner["id"]
        cols = st.columns([2, 1, 1, 1])
        with cols[0]:
            if banner.get("image_url"):
                st.image(banner["image_url"], use_container_width=True)
        with cols[1]:
            active = st.toggle(
                "Ativo",
                value=bool(banner.get("active")),
                key=f"banner_active_{bid}",
            )
            if active != bool(banner.get("active")):
                try:
                    set_store_banner_active(bid, active)
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
        with cols[2]:
            st.caption(f"Ordem: {banner.get('sort_order', 0)}")
        with cols[3]:
            if st.button("Excluir", key=f"banner_del_{bid}", type="secondary"):
                try:
                    delete_store_banner(bid)
                    st.success("Banner excluído.")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

st.markdown("---")

with st.form("store_form"):
    col1, col2 = st.columns(2)

    with col1:
        store_name = st.text_input("Nome da loja", value=settings.get("store_name", ""))
        whatsapp = st.text_input(
            "WhatsApp (com DDD e país)",
            value=settings.get("whatsapp_number", ""),
            placeholder="5511999999999",
            help="Somente números. Ex: 5511999999999",
        )
        primary = st.color_picker("Cor principal", value=settings.get("primary_color", PRIMARY))
        secondary = st.color_picker("Cor secundária", value=settings.get("secondary_color", SECONDARY))
        accent = st.color_picker("Cor de destaque", value=settings.get("accent_color", ACCENT))

    with col2:
        st.markdown("**Logo (ícone do navegador)**")
        st.caption("Usado só como favicon — não aparece no catálogo quando há banner.")
        if settings.get("logo_url"):
            st.image(settings["logo_url"], width=80)
        else:
            logo_path = get_logo_path()
            if logo_path:
                st.image(str(logo_path), width=80)
        logo_file = st.file_uploader(
            "Enviar logo",
            type=["png", "jpg", "jpeg", "webp"],
        )

        st.markdown("**Preview das cores**")
        st.markdown(
            f"""
            <div style="display:flex;gap:8px;margin-top:8px;">
                <div style="width:60px;height:60px;background:{primary};border-radius:8px;"></div>
                <div style="width:60px;height:60px;background:{secondary};border-radius:8px;"></div>
                <div style="width:60px;height:60px;background:{accent};border-radius:8px;"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    submitted = st.form_submit_button("Salvar configurações", use_container_width=True)

    if submitted:
        data = {
            "store_name": store_name,
            "whatsapp_number": parse_whatsapp_number(whatsapp),
            "primary_color": primary,
            "secondary_color": secondary,
            "accent_color": accent,
        }

        if logo_file:
            try:
                img_bytes = resize_image(logo_file.read(), max_size=400)
                logo_url = upload_image(img_bytes, logo_file.name, folder="logo")
                data["logo_url"] = logo_url
            except Exception as e:
                st.error(f"Erro ao enviar logo: {e}")
                st.stop()

        try:
            update_store_settings(data)
            st.success("Configurações salvas!")
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao salvar: {e}")

st.markdown("---")
st.subheader("Preview mobile")
preview_settings = merge_brand_settings(fetch_store_settings())
inject_theme(preview_settings)
render_catalog_header(preview_settings, [], fetch_store_banners(active_only=True))