"""Sessão do cliente no catálogo público."""

from __future__ import annotations

from typing import Any

import streamlit as st

from lib.supabase_client import get_supabase
from lib.utils import (
    format_cpf,
    is_valid_cpf,
    is_valid_email,
    normalize_email,
    normalize_phone_br,
    parse_whatsapp_number,
)

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


def _parse_rpc_payload(data: Any) -> Any:
    import json

    if data is None:
        return None
    if isinstance(data, str):
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return None
    return data


def lookup_by_phone(phone: str) -> dict[str, Any] | None:
    digits = normalize_phone_br(parse_whatsapp_number(phone))
    if len(digits) < 12:
        return None
    client = get_supabase()
    result = client.rpc("lookup_customer_by_phone", {"p_phone": digits}).execute()
    data = _parse_rpc_payload(result.data)
    if isinstance(data, list):
        data = data[0] if data else None
    return data if isinstance(data, dict) else None


def save_profile(
    name: str,
    phone: str,
    cpf: str,
    address: str = "",
    email: str = "",
    *,
    address_fields: dict[str, str] | None = None,
) -> dict[str, Any]:
    if not is_valid_cpf(cpf):
        raise ValueError("CPF inválido.")
    if not is_valid_email(email):
        raise ValueError("E-mail inválido.")
    digits = normalize_phone_br(parse_whatsapp_number(phone))
    if len(digits) < 12:
        raise ValueError("Telefone inválido.")

    addr = address_fields or {}
    payload = {
        "p_name": name.strip(),
        "p_phone": digits,
        "p_cpf": "".join(c for c in cpf if c.isdigit()),
        "p_address": address.strip(),
        "p_email": normalize_email(email),
        "p_address_zip": addr.get("zip", ""),
        "p_address_street": addr.get("street", ""),
        "p_address_number": addr.get("number", ""),
        "p_address_complement": addr.get("complement", ""),
        "p_address_neighborhood": addr.get("neighborhood", ""),
        "p_address_city": addr.get("city", ""),
        "p_address_state": addr.get("state", ""),
    }

    client = get_supabase()
    try:
        result = client.rpc("save_customer_profile", payload).execute()
    except Exception:
        basic = {
            "p_name": payload["p_name"],
            "p_phone": payload["p_phone"],
            "p_cpf": payload["p_cpf"],
            "p_address": payload["p_address"],
            "p_email": payload["p_email"],
        }
        if addr.get("street") or addr.get("city"):
            from lib.address import _format_address_lines

            basic["p_address"] = _format_address_lines(addr)
        result = client.rpc("save_customer_profile", basic).execute()
    data = _parse_rpc_payload(result.data)
    if isinstance(data, list):
        data = data[0] if data else None
    if not data:
        raise ValueError("Erro ao salvar cadastro.")
    return data


def customer_display_name(customer: dict[str, Any]) -> str:
    return customer.get("name") or "Cliente"


def customer_profile_complete(customer: dict[str, Any] | None) -> bool:
    """Perfil mínimo para checkout (nome, CPF, telefone, e-mail)."""
    if not customer or not customer.get("id"):
        return False
    if not customer.get("name", "").strip():
        return False
    if not is_valid_cpf(customer.get("cpf", "")):
        return False
    if len(parse_whatsapp_number(customer.get("phone", ""))) < 10:
        return False
    return is_valid_email(customer.get("email", ""))


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
    if customer.get("address") or customer.get("address_street"):
        from lib.address import format_customer_address

        formatted = format_customer_address(customer)
        if formatted:
            lines.append(f"Endereço: {formatted.replace(chr(10), ', ')}")
    if customer.get("email"):
        lines.append(f"E-mail: {customer['email']}")
    if lines:
        lines.append("")
    return lines
