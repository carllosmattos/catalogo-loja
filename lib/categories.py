"""Categorias de produtos."""

from __future__ import annotations

from typing import Any

from lib.supabase_client import get_authenticated_client, get_supabase


def fetch_categories(active_only: bool = True) -> list[dict[str, Any]]:
    """Lista categorias para o catálogo público."""
    try:
        client = get_supabase()
        query = client.table("categories").select("*").order("sort_order").order("name")
        if active_only:
            query = query.eq("active", True)
        return query.execute().data or []
    except Exception:
        return []


def fetch_all_categories_admin(
    active_filter: bool | None = None,
) -> list[dict[str, Any]]:
    """Lista categorias no admin."""
    try:
        client = get_authenticated_client()
        query = client.table("categories").select("*").order("sort_order").order("name")
        if active_filter is True:
            query = query.eq("active", True)
        elif active_filter is False:
            query = query.eq("active", False)
        return query.execute().data or []
    except Exception:
        return []


def create_category(name: str, sort_order: int = 0) -> dict[str, Any]:
    client = get_authenticated_client()
    result = (
        client.table("categories")
        .insert({"name": name.strip(), "sort_order": sort_order, "active": True})
        .execute()
    )
    return result.data[0] if result.data else {}


def update_category(category_id: str, data: dict[str, Any]) -> dict[str, Any]:
    client = get_authenticated_client()
    result = (
        client.table("categories").update(data).eq("id", category_id).execute()
    )
    return result.data[0] if result.data else {}


def set_category_active(category_id: str, active: bool):
    client = get_authenticated_client()
    client.table("categories").update({"active": active}).eq("id", category_id).execute()


def category_choices(categories: list[dict[str, Any]]) -> dict[str, str]:
    """Mapa nome → id para selectboxes."""
    return {c["name"]: c["id"] for c in categories if c.get("name") and c.get("id")}


def resolve_category_id(
    categories: list[dict[str, Any]],
    category_id: str | None = None,
    category_name: str | None = None,
) -> str | None:
    if category_id:
        return category_id
    if not category_name:
        return None
    name_lower = category_name.strip().lower()
    for cat in categories:
        if cat.get("name", "").strip().lower() == name_lower:
            return cat["id"]
    return None
