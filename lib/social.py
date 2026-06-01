"""Links sociais da loja e do desenvolvedor."""

from __future__ import annotations

import html

import streamlit as st

STORE_INSTAGRAM_URL = "https://www.instagram.com/lm_modafeminina_/"

DEV_NAME = "Carlos Eduardo"
DEV_WHATSAPP = "55859971613663"
DEV_INSTAGRAM_URL = "https://www.instagram.com/carllo_s_eduardo/"
DEV_LINKEDIN_URL = (
    "https://www.linkedin.com/in/carlos-eduardo-vieira-de-matos-7068b5158/"
)


def render_store_social_bar() -> None:
    """Instagram da loja — logo abaixo do banner."""
    ig = html.escape(STORE_INSTAGRAM_URL)
    st.markdown(
        f'<div class="store-social-bar">'
        f'<a href="{ig}" target="_blank" rel="noopener noreferrer" '
        f'class="store-social-link">'
        f"📷 @lm_modafeminina_"
        f"</a></div>",
        unsafe_allow_html=True,
    )


def render_developer_footer() -> None:
    """Rodapé discreto com contato do desenvolvedor."""
    wa = html.escape(f"https://wa.me/{DEV_WHATSAPP}")
    ig = html.escape(DEV_INSTAGRAM_URL)
    li = html.escape(DEV_LINKEDIN_URL)
    name = html.escape(DEV_NAME)

    st.markdown(
        f'<div class="dev-footer">'
        f'<span class="dev-footer-label">Desenvolvido por {name}</span>'
        f'<span class="dev-footer-links">'
        f'<a href="{wa}" target="_blank" rel="noopener noreferrer">WhatsApp</a>'
        f'<span class="dev-footer-sep">·</span>'
        f'<a href="{ig}" target="_blank" rel="noopener noreferrer">Instagram</a>'
        f'<span class="dev-footer-sep">·</span>'
        f'<a href="{li}" target="_blank" rel="noopener noreferrer">LinkedIn</a>'
        f"</span></div>",
        unsafe_allow_html=True,
    )
