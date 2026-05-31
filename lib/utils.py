"""Formatação de moeda e utilitários."""

from __future__ import annotations


def format_currency(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def parse_whatsapp_number(raw: str) -> str:
    """Remove tudo que não é dígito."""
    return "".join(c for c in raw if c.isdigit())
