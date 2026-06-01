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
    resolve_default_banner_url,
    resolve_logo_url,
)
from lib.catalog import fetch_store_settings, resize_image, update_store_settings, upload_image
from lib.catalog_display import build_banner_header_html, render_catalog_header
from lib.theme import inject_theme
from lib.utils import parse_whatsapp_number

configure_page("Admin — Loja", layout="wide", sidebar_state="expanded")
render_sidebar()

if not require_auth():
    st.stop()
st.title("🏪 Configurações da Loja")

settings = merge_brand_settings(fetch_store_settings())
inject_theme(settings)

st.subheader("Banner do catálogo")
st.caption(
    "O banner substitui logo e nome no topo do catálogo — a imagem já pode trazer a identidade da loja."
)

banner_preview_url = resolve_default_banner_url(settings)
if banner_preview_url:
    st.markdown(
        build_banner_header_html("single", [banner_preview_url]),
        unsafe_allow_html=True,
    )
else:
    st.info("Nenhum banner configurado. Envie abaixo ou use o banner padrão em `resources/banner.png`.")

with st.form("banner_form"):
    banner_file = st.file_uploader(
        "Enviar banner padrão",
        type=["png", "jpg", "jpeg", "webp"],
        help="Recomendado: imagem horizontal (aprox. 2:1), até 1600px de largura.",
    )
    save_banner = st.form_submit_button("Salvar banner", use_container_width=True)

    if save_banner:
        if not banner_file:
            st.error("Selecione uma imagem para o banner.")
        else:
            try:
                img_bytes = resize_image(banner_file.read(), max_size=1600)
                banner_url = upload_image(img_bytes, banner_file.name, folder="banners")
                update_store_settings({"default_banner_url": banner_url})
                st.success("Banner salvo!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao enviar banner: {e}")

if settings.get("default_banner_url"):
    if st.button("Remover banner padrão", use_container_width=True):
        try:
            update_store_settings({"default_banner_url": None})
            st.success("Banner removido. O catálogo usará o arquivo local ou logo+nome.")
            st.rerun()
        except Exception as e:
            st.error(f"Erro: {e}")

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
render_catalog_header(preview_settings, [])
