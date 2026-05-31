"""Configurações da loja: logo, cores e WhatsApp."""

import streamlit as st

from lib.auth import require_auth, render_sidebar
from lib.branding import PRIMARY, SECONDARY, ACCENT, configure_page, get_logo_path, merge_brand_settings, resolve_logo_url
from lib.catalog import fetch_store_settings, resize_image, update_store_settings, upload_image
from lib.theme import inject_theme
from lib.utils import parse_whatsapp_number

configure_page("Admin — Loja", layout="wide", sidebar_state="expanded")
render_sidebar()

if not require_auth():
    st.stop()
st.title("🏪 Configurações da Loja")

settings = merge_brand_settings(fetch_store_settings())
inject_theme(settings)

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
        st.markdown("**Logo da loja**")
        logo_src = resolve_logo_url(settings)
        logo_path = get_logo_path()
        if settings.get("logo_url"):
            st.image(settings["logo_url"], width=120)
        elif logo_path:
            st.image(str(logo_path), width=120)
        logo_file = st.file_uploader(
            "Enviar novo logo",
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

logo_preview = resolve_logo_url(preview_settings)
logo_path = get_logo_path()
if preview_settings.get("logo_url"):
    st.image(preview_settings["logo_url"], width=80)
elif logo_path:
    st.image(str(logo_path), width=80)
st.markdown(
    f"<p class='store-name'>{preview_settings.get('store_name', '')}</p>",
    unsafe_allow_html=True,
)
