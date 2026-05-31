"""Autenticação via Supabase Auth."""

from __future__ import annotations

import streamlit as st

from lib.supabase_client import get_supabase


def init_session():
    if "auth_session" not in st.session_state:
        st.session_state.auth_session = None
    if "auth_user" not in st.session_state:
        st.session_state.auth_user = None


def is_authenticated() -> bool:
    init_session()
    return st.session_state.auth_session is not None


def get_user_email() -> str | None:
    init_session()
    if st.session_state.auth_user:
        return st.session_state.auth_user.get("email")
    return None


def login(email: str, password: str) -> tuple[bool, str]:
    init_session()
    try:
        client = get_supabase()
        response = client.auth.sign_in_with_password(
            {"email": email, "password": password}
        )
        session = response.session
        user = response.user
        if session and user:
            st.session_state.auth_session = {
                "access_token": session.access_token,
                "refresh_token": session.refresh_token,
            }
            st.session_state.auth_user = {
                "id": user.id,
                "email": user.email,
            }
            client.auth.set_session(session.access_token, session.refresh_token)
            return True, "Login realizado com sucesso!"
        return False, "Credenciais inválidas."
    except Exception as e:
        return False, f"Erro ao fazer login: {e}"


def logout():
    init_session()
    try:
        get_supabase().auth.sign_out()
    except Exception:
        pass
    st.session_state.auth_session = None
    st.session_state.auth_user = None


def require_auth() -> bool:
    """Guard para páginas admin. Retorna True se autenticado."""
    init_session()
    if is_authenticated():
        return True

    st.warning("Faça login para acessar o painel administrativo.")
    with st.form("login_form"):
        email = st.text_input("E-mail")
        password = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar", use_container_width=True)
        if submitted:
            ok, msg = login(email, password)
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
    return False


def render_admin_nav():
    """Barra de navegação do painel admin."""
    if not is_authenticated():
        return

    st.sidebar.markdown(f"**{get_user_email()}**")
    st.sidebar.markdown("---")
    st.sidebar.page_link("pages/2_Admin_Produtos.py", label="Produtos")
    st.sidebar.page_link("pages/3_Admin_Promocoes.py", label="Promoções")
    st.sidebar.page_link("pages/4_Admin_Brindes.py", label="Brindes")
    st.sidebar.page_link("pages/5_Admin_Loja.py", label="Configurações da Loja")
    st.sidebar.page_link("pages/6_Admin_Lucro.py", label="Lucro & Margem")
    st.sidebar.markdown("---")
    if st.sidebar.button("Sair", use_container_width=True):
        logout()
        st.rerun()
