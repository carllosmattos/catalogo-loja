"""Página de login do painel administrativo."""

import streamlit as st

from lib.auth import init_session, is_authenticated, login, logout, render_admin_nav

st.set_page_config(page_title="Admin — Login", page_icon="🔒", layout="centered")

init_session()

if is_authenticated():
    render_admin_nav()
    st.success(f"Logada como {st.session_state.auth_user['email']}")
    st.markdown("Use o menu lateral para gerenciar sua loja.")
    if st.button("Ir para Produtos"):
        st.switch_page("pages/2_Admin_Produtos.py")
    if st.button("Sair"):
        logout()
        st.rerun()
    st.stop()

st.title("🔒 Painel Administrativo")
st.markdown("Faça login para gerenciar seu catálogo.")

with st.form("login_form"):
    email = st.text_input("E-mail")
    password = st.text_input("Senha", type="password")
    submitted = st.form_submit_button("Entrar", use_container_width=True)

    if submitted:
        if not email or not password:
            st.error("Preencha e-mail e senha.")
        else:
            ok, msg = login(email, password)
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

st.markdown("---")
st.caption(
    "Acesso restrito à dona da loja. "
    "Crie sua conta no painel do Supabase (Authentication > Users)."
)
