"""Cliente Supabase singleton."""

from __future__ import annotations

import os
from typing import Any

import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError
from supabase import Client, create_client

_URL_KEYS = ("SUPABASE_URL", "supabase_url", "SUPABASE_PROJECT_URL")
_KEY_KEYS = (
    "SUPABASE_ANON_KEY",
    "supabase_anon_key",
    "SUPABASE_KEY",
    "supabase_key",
    "SUPABASE_ANON",
)


def _clean(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip().strip('"').strip("'")
    return text or None


def _from_environ(names: tuple[str, ...]) -> str | None:
    for name in names:
        value = _clean(os.environ.get(name))
        if value:
            return value
    return None


def _walk_secrets(node: Any, path: str = "") -> dict[str, str]:
    """Achata st.secrets — suporta chaves no topo ou dentro de [seções]."""
    found: dict[str, str] = {}
    if node is None:
        return found

    try:
        keys = list(node.keys())  # type: ignore[attr-defined]
    except (AttributeError, TypeError):
        return found

    for key in keys:
        try:
            value = node[key]
        except (KeyError, TypeError):
            continue

        full_path = f"{path}.{key}" if path else str(key)

        if isinstance(value, dict) or hasattr(value, "keys"):
            found.update(_walk_secrets(value, full_path))
        else:
            cleaned = _clean(value)
            if cleaned:
                found[str(key)] = cleaned
                found[full_path] = cleaned
    return found


def _from_streamlit_secrets(names: tuple[str, ...]) -> str | None:
    try:
        flat = _walk_secrets(st.secrets)
    except StreamlitSecretNotFoundError:
        return None
    except Exception:
        return None

    for name in names:
        value = flat.get(name)
        if value:
            return value

    # Atalhos comuns quando o usuário usa [supabase] url = "..."
    if "url" in flat and any(n.endswith("URL") for n in names):
        return flat["url"]
    if "anon_key" in flat and any("KEY" in n for n in names):
        return flat["anon_key"]

    return None


def _secrets_debug() -> dict[str, Any]:
    env_url = bool(_from_environ(_URL_KEYS))
    env_key = bool(_from_environ(_KEY_KEYS))

    secret_keys: list[str] = []
    secrets_error: str | None = None
    try:
        secret_keys = sorted(_walk_secrets(st.secrets).keys())
    except StreamlitSecretNotFoundError:
        secrets_error = "st.secrets não encontrado (painel Secrets vazio ou app não reiniciado)"
    except Exception as exc:
        secrets_error = f"erro ao ler st.secrets: {exc}"

    return {
        "env_url": env_url,
        "env_key": env_key,
        "secret_keys": secret_keys,
        "secrets_error": secrets_error,
    }


def _get_credentials() -> tuple[str, str]:
    """Lê credenciais de secrets.toml, st.secrets (Cloud) ou variáveis de ambiente."""
    url = _from_environ(_URL_KEYS) or _from_streamlit_secrets(_URL_KEYS)
    key = _from_environ(_KEY_KEYS) or _from_streamlit_secrets(_KEY_KEYS)

    if not url or not key:
        debug = _secrets_debug()
        st.error(
            "Supabase não configurado. O app não encontrou `SUPABASE_URL` e/ou "
            "`SUPABASE_ANON_KEY`."
        )
        st.markdown(
            "**Streamlit Cloud:** **Manage app** → **Settings** → **Secrets** — "
            "cole **somente** isto (sem `[seção]` em cima, sem markdown):\n\n"
            "```toml\n"
            "SUPABASE_URL = \"https://seu-projeto.supabase.co\"\n"
            "SUPABASE_ANON_KEY = \"eyJ...\"\n"
            "```"
        )
        st.markdown(
            "Salve e clique em **Reboot app**. "
            "Use a chave **anon public** do Supabase (Settings → API), não a `service_role`."
        )

        with st.expander("Diagnóstico (sem expor valores)"):
            st.write(f"- Variável de ambiente URL: {'sim' if debug['env_url'] else 'não'}")
            st.write(f"- Variável de ambiente KEY: {'sim' if debug['env_key'] else 'não'}")
            if debug["secrets_error"]:
                st.write(f"- st.secrets: {debug['secrets_error']}")
            elif debug["secret_keys"]:
                st.write(
                    "- Chaves lidas em st.secrets:",
                    ", ".join(f"`{k}`" for k in debug["secret_keys"][:20]),
                )
                if "SUPABASE_URL" not in debug["secret_keys"] and "url" not in debug["secret_keys"]:
                    st.warning(
                        "Nenhuma chave de URL encontrada. "
                        "Se você usou `[supabase]` ou outra seção, remova o cabeçalho "
                        "e deixe as duas linhas no topo do arquivo."
                    )
            else:
                st.write("- st.secrets: vazio — confira se salvou no app certo e deu Reboot.")

        st.stop()

    url = url.rstrip("/").removesuffix("/rest/v1")
    return url, key


@st.cache_resource
def get_supabase() -> Client:
    url, key = _get_credentials()
    return create_client(url, key)


def get_authenticated_client() -> Client:
    """Retorna cliente com JWT da sessão admin (sem reutilizar refresh token)."""
    client = get_supabase()
    session = st.session_state.get("auth_session")
    if session and session.get("access_token"):
        client.postgrest.auth(session["access_token"])
    return client
