"""Estoque por tamanho P/M/G."""

from __future__ import annotations

from typing import Any

from lib.supabase_client import get_authenticated_client, get_supabase

SIZES = ("P", "M", "G")


def default_size_rows() -> list[dict[str, Any]]:
    return [{"size": s, "stock": 0} for s in SIZES]


def normalize_size(size: str | None) -> str:
    s = (size or "M").strip().upper()
    return s if s in SIZES else "M"


def merge_sizes(rows: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    by_size = {r["size"]: int(r.get("stock", 0)) for r in (rows or []) if r.get("size") in SIZES}
    return [{"size": s, "stock": by_size.get(s, 0)} for s in SIZES]


def total_stock(sizes: list[dict[str, Any]] | None) -> int:
    return sum(int(s.get("stock", 0)) for s in merge_sizes(sizes))


def stock_for_size(sizes: list[dict[str, Any]] | None, size: str) -> int:
    norm = normalize_size(size)
    for row in merge_sizes(sizes):
        if row["size"] == norm:
            return int(row["stock"])
    return 0


def fetch_product_sizes(product_id: str) -> list[dict[str, Any]]:
    try:
        client = get_supabase()
        rows = (
            client.table("product_sizes")
            .select("size, stock")
            .eq("product_id", product_id)
            .execute()
            .data
            or []
        )
        return merge_sizes(rows)
    except Exception:
        return default_size_rows()


def fetch_sizes_for_products(
    product_ids: list[str],
) -> tuple[dict[str, list[dict[str, Any]]], set[str]]:
    """Retorna mapa de tamanhos e IDs com linhas em product_sizes."""
    if not product_ids:
        return {}, set()
    try:
        client = get_supabase()
        rows = (
            client.table("product_sizes")
            .select("product_id, size, stock")
            .in_("product_id", product_ids)
            .execute()
            .data
            or []
        )
        grouped: dict[str, list[dict[str, Any]]] = {}
        has_rows: set[str] = set()
        for row in rows:
            pid = str(row["product_id"])
            has_rows.add(pid)
            grouped.setdefault(pid, []).append(row)
        result = {
            pid: merge_sizes(grouped.get(pid, [])) for pid in product_ids
        }
        return result, has_rows
    except Exception:
        return {}, set()


def set_product_sizes(product_id: str, sizes: dict[str, int]) -> None:
    client = get_authenticated_client()
    client.table("product_sizes").delete().eq("product_id", product_id).execute()
    payload = [
        {"product_id": product_id, "size": s, "stock": max(int(sizes.get(s, 0)), 0)}
        for s in SIZES
    ]
    client.table("product_sizes").insert(payload).execute()


def attach_sizes_to_products(products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ids = [str(p["id"]) for p in products if p.get("id")]
    size_map, has_rows = fetch_sizes_for_products(ids)
    for product in products:
        pid = str(product.get("id", ""))
        if pid in has_rows:
            product["sizes"] = size_map.get(pid, default_size_rows())
        else:
            # Fallback legado (sem migração 012)
            legacy = int(product.get("stock", 0))
            legacy_size = normalize_size(product.get("size"))
            rows = default_size_rows()
            for row in rows:
                if row["size"] == legacy_size:
                    row["stock"] = legacy
            product["sizes"] = rows
    return products


def size_stock_warnings(sizes: list[dict[str, Any]] | None) -> list[str]:
    merged = merge_sizes(sizes)
    warnings: list[str] = []
    if total_stock(merged) <= 0:
        warnings.append("Produto esgotado em todos os tamanhos.")
        return warnings
    for row in merged:
        if int(row["stock"]) <= 0:
            warnings.append(f"Tamanho {row['size']} esgotado.")
    return warnings
