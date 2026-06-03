"""Formatação de moeda e utilitários."""

from __future__ import annotations


def format_currency(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def parse_whatsapp_number(raw: str) -> str:
    """Remove tudo que não é dígito."""
    return "".join(c for c in raw if c.isdigit())


def normalize_cpf(raw: str) -> str:
    """Retorna CPF com 11 dígitos ou string vazia."""
    digits = "".join(c for c in raw if c.isdigit())
    return digits if len(digits) == 11 else ""


def format_cpf(cpf: str) -> str:
    """Formata CPF para exibição 000.000.000-00."""
    d = normalize_cpf(cpf) or "".join(c for c in cpf if c.isdigit())
    if len(d) != 11:
        return cpf
    return f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}"


def normalize_email(raw: str) -> str:
    """Retorna e-mail normalizado ou string vazia."""
    return raw.strip().lower()


def is_valid_email(raw: str) -> bool:
    email = normalize_email(raw)
    if not email or " " in email:
        return False
    parts = email.split("@")
    if len(parts) != 2:
        return False
    local, domain = parts
    if not local or not domain or "." not in domain:
        return False
    return True


def is_valid_cpf(raw: str) -> bool:
    cpf = normalize_cpf(raw)
    if not cpf or len(set(cpf)) == 1:
        return False

    def digit(nums: list[int], weights: list[int]) -> int:
        total = sum(n * w for n, w in zip(nums, weights, strict=False))
        rest = total % 11
        return 0 if rest < 2 else 11 - rest

    nums = [int(c) for c in cpf]
    if digit(nums[:9], list(range(10, 1, -1))) != nums[9]:
        return False
    if digit(nums[:10], list(range(11, 1, -1))) != nums[10]:
        return False
    return True
