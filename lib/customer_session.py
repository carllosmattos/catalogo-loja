"""Sessão do cliente no catálogo público."""

from __future__ import annotations

from typing import Any

import streamlit as st

from lib.supabase_client import get_supabase
from lib.utils import format_cpf, is_valid_cpf, parse_whatsapp_number

SESSION_KEY = "catalog_customer"


def get_catalog_customer() -> dict[str, Any] | None:
    return st.session_state.get(SESSION_KEY)


def set_catalog_customer(customer: dict[str, Any] | None) -> None:
    if customer:
        st.session_state[SESSION_KEY] = customer
    else:
        st.session_state.pop(SESSION_KEY, None)


def logout_catalog_customer() -> None:
    set_catalog_customer(None)


def lookup_by_phone(phone: str) -> dict[str, Any] | None:
    digits = parse_whatsapp_number(phone)
    if len(digits) < 10:
        return None
    client = get_supabase()
    result = client.rpc("lookup_customer_by_phone", {"p_phone": digits}).execute()
    data = result.data
    if not data:
        return None
    if isinstance(data, list):
        data = data[0] if data else None
    return data if isinstance(data, dict) else None


def save_profile(
    name: str,
    phone: str,
    cpf: str,
    address: str = "",
) -> dict[str, Any]:
    if not is_valid_cpf(cpf):
        raise ValueError("CPF inválido.")
    digits = parse_whatsapp_number(phone)
    if len(digits) < 10:
        raise ValueError("Telefone inválido.")

    client = get_supabase()
    result = client.rpc(
        "save_customer_profile",
        {
            "p_name": name.strip(),
            "p_phone": digits,
            "p_cpf": "".join(c for c in cpf if c.isdigit()),
            "p_address": address.strip(),
        },
    ).execute()
    data = result.data
    if isinstance(data, list):
        data = data[0] if data else None
    if not data:
        raise ValueError("Erro ao salvar cadastro.")
    return data


def customer_display_name(customer: dict[str, Any]) -> str:
    return customer.get("name") or "Cliente"


def customer_for_whatsapp(customer: dict[str, Any] | None) -> list[str]:
    """Linhas extras para mensagem WhatsApp."""
    if not customer:
        return []
    lines = []
    if customer.get("name"):
        lines.append(f"Nome: {customer['name']}")
    if customer.get("phone"):
        lines.append(f"Telefone: {customer['phone']}")
    if customer.get("cpf"):
        lines.append(f"CPF: {format_cpf(customer['cpf'])}")
    if customer.get("address"):
        lines.append(f"Endereço: {customer['address']}")
    if lines:
        lines.append("")
    return lines
