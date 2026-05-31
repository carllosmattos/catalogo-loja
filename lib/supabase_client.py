"""Cliente Supabase singleton."""

from __future__ import annotations

import streamlit as st
from supabase import Client, create_client


@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_ANON_KEY"]
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
