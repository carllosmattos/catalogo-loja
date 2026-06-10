"""Endereço estruturado do cliente."""

from __future__ import annotations

from typing import Any

import streamlit as st

BRAZILIAN_STATES = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
    "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
    "RS", "RO", "RR", "SC", "SP", "SE", "TO",
]


def address_fields_from_customer(customer: dict[str, Any] | None) -> dict[str, str]:
    c = customer or {}
    return {
        "zip": c.get("address_zip", "") or "",
        "street": c.get("address_street", "") or "",
        "number": c.get("address_number", "") or "",
        "complement": c.get("address_complement", "") or "",
        "neighborhood": c.get("address_neighborhood", "") or "",
        "city": c.get("address_city", "") or "",
        "state": (c.get("address_state", "") or "").upper(),
    }


def _format_address_lines(fields: dict[str, str]) -> str:
    street = fields.get("street", "").strip()
    number = fields.get("number", "").strip()
    complement = fields.get("complement", "").strip()
    line1 = street
    if number:
        line1 = f"{line1}, {number}" if line1 else number
    if complement:
        line1 = f"{line1} — {complement}" if line1 else complement

    parts: list[str] = []
    if fields.get("neighborhood", "").strip():
        parts.append(fields["neighborhood"].strip())
    city = fields.get("city", "").strip()
    state = fields.get("state", "").strip()
    if city and state:
        parts.append(f"{city}/{state}")
    elif city:
        parts.append(city)
    elif state:
        parts.append(state)
    zip_digits = "".join(c for c in fields.get("zip", "") if c.isdigit())
    if len(zip_digits) == 8:
        parts.append(f"CEP {zip_digits[:5]}-{zip_digits[5:]}")
    elif zip_digits:
        parts.append(f"CEP {zip_digits}")

    line2 = " — ".join(parts)
    return "\n".join([x for x in [line1, line2] if x])


def format_customer_address(customer: dict[str, Any] | None) -> str:
    if not customer:
        return ""
    fields = address_fields_from_customer(customer)
    if any(fields.values()):
        return _format_address_lines(fields)
    return (customer.get("address") or "").strip()


def render_address_fields(
    customer: dict[str, Any] | None,
    *,
    key_prefix: str = "addr",
) -> dict[str, str]:
    """Campos de endereço no formulário Streamlit."""
    fields = address_fields_from_customer(customer)
    c1, c2 = st.columns([1, 2])
    with c1:
        zip_code = st.text_input(
            "CEP",
            value=fields["zip"],
            placeholder="00000-000",
            key=f"{key_prefix}_zip",
        )
    with c2:
        street = st.text_input(
            "Rua",
            value=fields["street"],
            key=f"{key_prefix}_street",
        )
    c3, c4 = st.columns([1, 2])
    with c3:
        number = st.text_input(
            "Número",
            value=fields["number"],
            key=f"{key_prefix}_number",
        )
    with c4:
        complement = st.text_input(
            "Complemento",
            value=fields["complement"],
            key=f"{key_prefix}_complement",
        )
    neighborhood = st.text_input(
        "Bairro",
        value=fields["neighborhood"],
        key=f"{key_prefix}_neighborhood",
    )
    c5, c6 = st.columns([2, 1])
    with c5:
        city = st.text_input(
            "Cidade",
            value=fields["city"],
            key=f"{key_prefix}_city",
        )
    with c6:
        state_idx = (
            BRAZILIAN_STATES.index(fields["state"])
            if fields["state"] in BRAZILIAN_STATES
            else 0
        )
        state = st.selectbox(
            "UF",
            BRAZILIAN_STATES,
            index=state_idx,
            key=f"{key_prefix}_state",
        )
    return {
        "zip": zip_code,
        "street": street,
        "number": number,
        "complement": complement,
        "neighborhood": neighborhood,
        "city": city,
        "state": state,
    }
