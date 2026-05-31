"""Cliente Supabase singleton."""

from __future__ import annotations

import os

import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError
from supabase import Client, create_client


def _get_credentials() -> tuple[str, str]:
    """Lê credenciais de secrets.toml ou variáveis de ambiente."""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_ANON_KEY")

    try:
        if not url and "SUPABASE_URL" in st.secrets:
            url = st.secrets["SUPABASE_URL"]
        if not key and "SUPABASE_ANON_KEY" in st.secrets:
            key = st.secrets["SUPABASE_ANON_KEY"]
    except StreamlitSecretNotFoundError:
        pass

    if not url or not key:
        st.error(
            "Configure o Supabase em `.streamlit/secrets.toml`:\n\n"
            "```toml\n"
            "SUPABASE_URL = \"https://seu-projeto.supabase.co\"\n"
            "SUPABASE_ANON_KEY = \"eyJ...\"\n"
            "```"
        )
        st.stop()

    # Remove sufixo incorreto se colado da API REST
    url = url.rstrip("/").removesuffix("/rest/v1")
    return url, key


@st.cache_resource
def get_supabase() -> Client:
    url, key = _get_credentials()
    return create_client(url, key)


def get_authenticated_client() -> Client:
    """Retorna cliente com token JWT da sessão atual."""
    client = get_supabase()
    session = st.session_state.get("auth_session")
    if session and session.get("access_token"):
        client.postgrest.auth(session["access_token"])
        if session.get("refresh_token"):
            client.auth.set_session(
                session["access_token"], session["refresh_token"]
            )
    return client
