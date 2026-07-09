"""Autenticação via Supabase Auth com sessão persistente em cookie."""

from __future__ import annotations

import json
from datetime import datetime, timedelta

import extra_streamlit_components as stx
import streamlit as st

from lib.supabase_client import get_supabase

COOKIE_NAME = "lm_catalog_auth"
SESSION_DAYS = 7


def _cookie_manager() -> stx.CookieManager:
    if "lm_cookie_manager" not in st.session_state:
        st.session_state.lm_cookie_manager = stx.CookieManager(
            key="lm_auth_cookie_mgr"
        )
    return st.session_state.lm_cookie_manager


def init_session():
    if "auth_session" not in st.session_state:
        st.session_state.auth_session = None
    if "auth_user" not in st.session_state:
        st.session_state.auth_user = None
    if "_cookies_ready" not in st.session_state:
        st.session_state._cookies_ready = False


def _set_auth_state(access_token: str, refresh_token: str, user_id: str, email: str):
    st.session_state.auth_session = {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }
    st.session_state.auth_user = {"id": user_id, "email": email}


def _apply_session_from_response(session, user, fallback_email: str = "") -> bool:
    if not session or not user:
        return False
    email = user.email or fallback_email
    _set_auth_state(session.access_token, session.refresh_token, user.id, email)
    _save_session_cookie(session.access_token, session.refresh_token, user.id, email)
    return True


def _save_session_cookie(access_token: str, refresh_token: str, user_id: str, email: str):
    cm = _cookie_manager()
    payload = json.dumps(
        {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "id": user_id,
            "email": email,
        }
    )
    expires = datetime.now() + timedelta(days=SESSION_DAYS)
    cm.set(COOKIE_NAME, payload, expires_at=expires, key="save_auth_cookie")


def _clear_session_cookie():
    cm = _cookie_manager()
    cm.delete(COOKIE_NAME, key="delete_auth_cookie")


def _wait_for_cookies() -> bool:
    if st.session_state.get("_cookies_ready"):
        return True
    cm = _cookie_manager()
    cookies = cm.get_all()
    if cookies is None:
        return False
    st.session_state._cookies_ready = True
    return True


def restore_session() -> bool:
    init_session()
    if is_authenticated():
        return True
    if not _wait_for_cookies():
        return False

    cm = _cookie_manager()
    raw = cm.get(COOKIE_NAME)
    if not raw:
        return False

    try:
        data = json.loads(raw)
        refresh_token = data.get("refresh_token")
        fallback_email = data.get("email", "")
        if not refresh_token:
            _clear_session_cookie()
            return False

        client = get_supabase()
        response = client.auth.refresh_session(refresh_token)
        if _apply_session_from_response(
            response.session, response.user, fallback_email
        ):
            return True

        _clear_session_cookie()
        return False
    except Exception:
        st.session_state.auth_session = None
        st.session_state.auth_user = None
        _clear_session_cookie()
        return False


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
            email_val = user.email or email
            _set_auth_state(session.access_token, session.refresh_token, user.id, email_val)
            _save_session_cookie(session.access_token, session.refresh_token, user.id, email_val)
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
    _clear_session_cookie()


def require_auth() -> bool:
    init_session()
    restore_session()
    if is_authenticated():
        return True

    st.session_state.auth_session = None
    st.session_state.auth_user = None
    st.switch_page("pages/1_Admin_Login.py")
    st.stop()
    return False


def render_sidebar():
    restore_session()
    st.sidebar.page_link("app.py", label="Catálogo", icon="👗")
    st.sidebar.markdown("---")
    if is_authenticated():
        render_admin_nav()
    else:
        st.sidebar.page_link("pages/1_Admin_Login.py", label="Login admin", icon="🔒")


def render_admin_nav():
    if not is_authenticated():
        return

    st.sidebar.markdown(f"**{get_user_email()}**")
    st.sidebar.page_link("pages/2_Admin_Produtos.py", label="Produtos", icon="👗")
    st.sidebar.page_link("pages/3_Admin_Promocoes.py", label="Promoções", icon="🏷️")
    st.sidebar.page_link("pages/4_Admin_Brindes.py", label="Brindes", icon="🎁")
    st.sidebar.page_link("pages/5_Admin_Loja.py", label="Configurações", icon="🏪")
    st.sidebar.page_link("pages/6_Admin_Lucro.py", label="Lucro & Margem", icon="📊")
    st.sidebar.page_link("pages/7_Admin_Vendas.py", label="Vendas", icon="🛒")
    st.sidebar.page_link("pages/8_Admin_Pagamentos.py", label="Pagamentos", icon="💳")
    st.sidebar.page_link("pages/9_Admin_Frete.py", label="Frete", icon="🚚")
    st.sidebar.markdown("---")
    if st.sidebar.button("Sair", use_container_width=True):
        logout()
        st.rerun()
