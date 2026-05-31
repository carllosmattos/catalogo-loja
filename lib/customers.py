"""Cadastro e busca de clientes."""

from __future__ import annotations

from typing import Any

from lib.supabase_client import get_authenticated_client
from lib.utils import normalize_cpf, parse_whatsapp_number


def search_customers(query: str, limit: int = 20) -> list[dict[str, Any]]:
    """Busca por CPF parcial, nome ou telefone."""
    q = query.strip()
    if len(q) < 3:
        return []

    client = get_authenticated_client()
    cpf_digits = normalize_cpf(q) or "".join(c for c in q if c.isdigit())
    phone_digits = parse_whatsapp_number(q)

    if cpf_digits and len(cpf_digits) >= 3:
        result = (
            client.table("customers")
            .select("*")
            .ilike("cpf", f"{cpf_digits}%")
            .order("name")
            .limit(limit)
            .execute()
        )
        if result.data:
            return result.data

    if phone_digits and len(phone_digits) >= 3:
        result = (
            client.table("customers")
            .select("*")
            .ilike("phone", f"%{phone_digits}%")
            .order("name")
            .limit(limit)
            .execute()
        )
        if result.data:
            return result.data

    return (
        client.table("customers")
        .select("*")
        .ilike("name", f"%{q}%")
        .order("name")
        .limit(limit)
        .execute()
        .data
        or []
    )


def get_customer_by_cpf(cpf: str) -> dict[str, Any] | None:
    normalized = normalize_cpf(cpf)
    if not normalized:
        return None
    client = get_authenticated_client()
    result = (
        client.table("customers")
        .select("*")
        .eq("cpf", normalized)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def fetch_customer(customer_id: str) -> dict[str, Any] | None:
    client = get_authenticated_client()
    result = (
        client.table("customers")
        .select("*")
        .eq("id", customer_id)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def upsert_customer(
    name: str,
    phone: str,
    cpf: str,
    address: str = "",
) -> dict[str, Any]:
    """Cria ou atualiza cliente pelo CPF."""
    normalized = normalize_cpf(cpf)
    if not normalized:
        raise ValueError("CPF inválido.")

    client = get_authenticated_client()
    phone_clean = parse_whatsapp_number(phone)
    existing = get_customer_by_cpf(normalized)

    payload = {
        "name": name.strip(),
        "phone": phone_clean,
        "cpf": normalized,
        "address": address.strip(),
    }

    if existing:
        result = (
            client.table("customers")
            .update(payload)
            .eq("id", existing["id"])
            .execute()
        )
    else:
        result = client.table("customers").insert({**payload, "points": 0}).execute()

    if not result.data:
        raise ValueError("Erro ao salvar cliente.")
    return result.data[0]
