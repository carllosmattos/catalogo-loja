"""Cotação Melhor Envio (API pública de fretes)."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from lib.payments.factory import _secret

API_BASE = "https://melhorenvio.com.br/api/v2/me/shipment/calculate"


def melhor_envio_enabled() -> bool:
    token = (_secret("MELHOR_ENVIO_TOKEN", "") or "").strip()
    return bool(token)


def quote_shipping(
    *,
    from_postal: str,
    to_postal: str,
    weight_kg: float,
    height_cm: float = 4,
    width_cm: float = 16,
    length_cm: float = 20,
    insurance_value: float = 0,
) -> float | None:
    """
    Retorna o menor preço entre transportadoras ou None se indisponível.
    Requer MELHOR_ENVIO_TOKEN nos secrets.
    """
    token = (_secret("MELHOR_ENVIO_TOKEN", "") or "").strip()
    if not token:
        return None

    from_zip = "".join(c for c in from_postal if c.isdigit())
    to_zip = "".join(c for c in to_postal if c.isdigit())
    if len(from_zip) != 8 or len(to_zip) != 8:
        return None

    body = {
        "from": {"postal_code": from_zip},
        "to": {"postal_code": to_zip},
        "products": [
            {
                "weight": max(weight_kg, 0.1),
                "height": height_cm,
                "width": width_cm,
                "length": length_cm,
                "insurance_value": max(insurance_value, 0),
                "quantity": 1,
            }
        ],
    }
    req = urllib.request.Request(
        API_BASE,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "catalogo-loja (contato@loja.local)",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
        return None

    if not isinstance(data, list):
        return None

    prices: list[float] = []
    for option in data:
        if not isinstance(option, dict):
            continue
        if option.get("error"):
            continue
        price = option.get("price") or option.get("custom_price")
        try:
            prices.append(float(price))
        except (TypeError, ValueError):
            continue
    return min(prices) if prices else None
