"""Zonas de frete no Supabase."""

from __future__ import annotations

from typing import Any

from lib.supabase_client import get_authenticated_client, get_supabase


def resolve_shipping_zone(address: dict[str, str]) -> dict[str, Any]:
    """Retorna zone_type (free|paid|blocked|none) e freight_amount."""
    client = get_supabase()
    result = client.rpc(
        "resolve_shipping_zone",
        {
            "p_country": "BR",
            "p_state": (address.get("state") or "").upper(),
            "p_city": address.get("city") or "",
            "p_neighborhood": address.get("neighborhood") or "",
        },
    ).execute()
    data = result.data
    if isinstance(data, list):
        data = data[0] if data else None
    return data if isinstance(data, dict) else {"zone_type": "none", "freight_amount": 0}


def fetch_shipping_zones() -> list[dict[str, Any]]:
    client = get_authenticated_client()
    result = (
        client.table("shipping_zones")
        .select("*")
        .order("priority", desc=True)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data or []


def upsert_shipping_zone(data: dict[str, Any]) -> dict[str, Any]:
    client = get_authenticated_client()
    zone_id = data.get("id")
    payload = {
        "zone_type": data["zone_type"],
        "scope": data["scope"],
        "country": (data.get("country") or "BR").upper(),
        "state": (data.get("state") or "").upper(),
        "city": data.get("city") or "",
        "neighborhood": data.get("neighborhood") or "",
        "freight_amount": float(data.get("freight_amount") or 0),
        "priority": int(data.get("priority") or 0),
        "label": data.get("label") or "",
        "active": bool(data.get("active", True)),
    }
    if zone_id:
        result = (
            client.table("shipping_zones")
            .update(payload)
            .eq("id", zone_id)
            .execute()
        )
    else:
        result = client.table("shipping_zones").insert(payload).execute()
    rows = result.data or []
    return rows[0] if rows else payload


def delete_shipping_zone(zone_id: str) -> None:
    client = get_authenticated_client()
    client.table("shipping_zones").delete().eq("id", zone_id).execute()
