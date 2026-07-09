"""Orquestra zonas + Melhor Envio + fallback do produto."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from lib.address import address_fields_from_customer
from lib.catalog import fetch_store_settings
from lib.shipping.melhor_envio import melhor_envio_enabled, quote_shipping
from lib.shipping.zones import resolve_shipping_zone


@dataclass
class ShippingQuote:
    amount: float
    zone_type: str
    label: str
    blocked: bool
    source: str


def _fallback_freight(lines: list[dict[str, Any]]) -> float:
    return sum(float(line.get("sale_freight", 0)) for line in lines)


def calculate_shipping(
    customer: dict[str, Any],
    lines: list[dict[str, Any]],
) -> ShippingQuote:
    """
    Calcula frete para checkout.
    Prioridade: zona blocked > zona free/paid > Melhor Envio > sale_freight dos produtos.
    """
    address = address_fields_from_customer(customer)
    zone = resolve_shipping_zone(address)
    zone_type = str(zone.get("zone_type") or "none")
    label = str(zone.get("label") or "")

    if zone_type == "blocked":
        return ShippingQuote(
            amount=0,
            zone_type=zone_type,
            label=label or "Região indisponível para entrega",
            blocked=True,
            source="zone",
        )

    if zone_type == "free":
        return ShippingQuote(
            amount=0,
            zone_type=zone_type,
            label=label or "Frete grátis",
            blocked=False,
            source="zone",
        )

    if zone_type == "paid":
        return ShippingQuote(
            amount=float(zone.get("freight_amount") or 0),
            zone_type=zone_type,
            label=label or "Frete da região",
            blocked=False,
            source="zone",
        )

    settings = fetch_store_settings()
    if melhor_envio_enabled() and settings.get("melhor_envio_enabled"):
        from_zip = settings.get("sender_zip") or ""
        to_zip = address.get("zip") or ""
        weight = float(settings.get("default_package_weight_kg") or 0.3)
        pieces = sum(int(line.get("quantity", 1)) for line in lines)
        me_price = quote_shipping(
            from_postal=from_zip,
            to_postal=to_zip,
            weight_kg=weight * max(pieces, 1),
            insurance_value=sum(float(line.get("preco_final_line", 0)) for line in lines),
        )
        if me_price is not None:
            return ShippingQuote(
                amount=me_price,
                zone_type="quoted",
                label="Frete Melhor Envio",
                blocked=False,
                source="melhor_envio",
            )

    fallback = _fallback_freight(lines)
    return ShippingQuote(
        amount=fallback,
        zone_type="fallback",
        label="Frete do produto" if fallback > 0 else "",
        blocked=False,
        source="product",
    )
