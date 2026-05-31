"""Operações de dados do catálogo."""

from __future__ import annotations

import io
import uuid
from typing import Any

from lib.supabase_client import get_authenticated_client, get_supabase


from lib.branding import DEFAULT_SETTINGS


def fetch_store_settings() -> dict[str, Any]:
    client = get_supabase()
    result = client.table("store_settings").select("*").limit(1).execute()
    if result.data:
        return {**DEFAULT_SETTINGS, **result.data[0]}
    return dict(DEFAULT_SETTINGS)


def update_store_settings(data: dict[str, Any]) -> dict[str, Any]:
    client = get_authenticated_client()
    settings = fetch_store_settings()
    settings_id = settings.get("id")
    if settings_id:
        result = (
            client.table("store_settings")
            .update(data)
            .eq("id", settings_id)
            .execute()
        )
    else:
        result = client.table("store_settings").insert(data).execute()
    return result.data[0] if result.data else {}


def fetch_products(active_only: bool = True) -> list[dict[str, Any]]:
    client = get_supabase()
    query = client.table("products").select("*").order("created_at", desc=True)
    if active_only:
        query = query.eq("active", True)
    return query.execute().data or []


def fetch_all_products() -> list[dict[str, Any]]:
    client = get_authenticated_client()
    return (
        client.table("products")
        .select("*")
        .order("created_at", desc=True)
        .execute()
        .data
        or []
    )


def create_product(data: dict[str, Any]) -> dict[str, Any]:
    client = get_authenticated_client()
    result = client.table("products").insert(data).execute()
    return result.data[0] if result.data else {}


def update_product(product_id: str, data: dict[str, Any]) -> dict[str, Any]:
    client = get_authenticated_client()
    result = (
        client.table("products").update(data).eq("id", product_id).execute()
    )
    return result.data[0] if result.data else {}


def set_product_active(product_id: str, active: bool):
    client = get_authenticated_client()
    client.table("products").update({"active": active}).eq("id", product_id).execute()


def duplicate_product(product_id: str) -> dict[str, Any]:
    """Copia produto e vínculos de brindes; estoque zerado, ativo."""
    client = get_authenticated_client()
    result = client.table("products").select("*").eq("id", product_id).limit(1).execute()
    if not result.data:
        raise ValueError("Produto não encontrado.")
    source = result.data[0]

    new_product = create_product(
        {
            "name": f"{source['name']} (cópia)",
            "description": source.get("description", ""),
            "category": source.get("category", ""),
            "size": source.get("size", ""),
            "image_urls": list(source.get("image_urls") or []),
            "purchase_price": source.get("purchase_price", 0),
            "purchase_freight": source.get("purchase_freight", 0),
            "sale_price": source.get("sale_price", 0),
            "sale_freight": source.get("sale_freight", 0),
            "stock": 0,
            "active": True,
        }
    )
    new_id = new_product.get("id")
    if not new_id:
        raise ValueError("Erro ao duplicar produto.")

    linked = fetch_product_gifts(product_id, active_gifts_only=False)
    if linked:
        links = [
            {
                "product_id": new_id,
                "gift_id": lg["gift_id"],
                "quantity_per_sale": lg.get("quantity_per_sale", 1),
            }
            for lg in linked
            if lg.get("gift_id")
        ]
        set_product_gifts(new_id, links)

    return new_product


def fetch_gifts(active_only: bool = True) -> list[dict[str, Any]]:
    client = get_supabase()
    query = client.table("gifts").select("*").order("name")
    if active_only:
        query = query.eq("active", True)
    return query.execute().data or []


def fetch_all_gifts_admin(
    active_filter: bool | None = None,
) -> list[dict[str, Any]]:
    """Lista brindes no admin. active_filter: True=ativos, False=arquivados, None=todos."""
    client = get_authenticated_client()
    query = client.table("gifts").select("*").order("name")
    if active_filter is True:
        query = query.eq("active", True)
    elif active_filter is False:
        query = query.eq("active", False)
    return query.execute().data or []


def create_gift(data: dict[str, Any]) -> dict[str, Any]:
    client = get_authenticated_client()
    result = client.table("gifts").insert(data).execute()
    return result.data[0] if result.data else {}


def update_gift(gift_id: str, data: dict[str, Any]) -> dict[str, Any]:
    client = get_authenticated_client()
    result = client.table("gifts").update(data).eq("id", gift_id).execute()
    return result.data[0] if result.data else {}


def set_gift_active(gift_id: str, active: bool):
    client = get_authenticated_client()
    client.table("gifts").update({"active": active}).eq("id", gift_id).execute()


def fetch_product_gifts(
    product_id: str,
    active_gifts_only: bool = True,
) -> list[dict[str, Any]]:
    """Busca vínculos produto-brinde com dados completos do brinde."""
    client = get_supabase()
    links = (
        client.table("product_gifts")
        .select("*")
        .eq("product_id", product_id)
        .execute()
        .data
        or []
    )
    if not links:
        return []

    gift_ids = [link["gift_id"] for link in links if link.get("gift_id")]
    if not gift_ids:
        return links

    gifts = (
        client.table("gifts")
        .select("*")
        .in_("id", gift_ids)
        .execute()
        .data
        or []
    )
    gifts_by_id = {gift["id"]: gift for gift in gifts}

    result = []
    for link in links:
        gift = gifts_by_id.get(link.get("gift_id"))
        if not gift:
            continue
        if active_gifts_only and not gift.get("active", True):
            continue
        result.append({**link, "gift_data": gift})
    return result


def set_product_gifts(product_id: str, gift_links: list[dict[str, Any]]):
    client = get_authenticated_client()
    client.table("product_gifts").delete().eq("product_id", product_id).execute()
    if gift_links:
        client.table("product_gifts").insert(gift_links).execute()


def fetch_active_promotions() -> list[dict[str, Any]]:
    client = get_supabase()
    return (
        client.table("promotions")
        .select("*")
        .eq("active", True)
        .execute()
        .data
        or []
    )


def fetch_all_promotions() -> list[dict[str, Any]]:
    client = get_authenticated_client()
    return (
        client.table("promotions")
        .select("*")
        .order("created_at", desc=True)
        .execute()
        .data
        or []
    )


def create_promotion(data: dict[str, Any]) -> dict[str, Any]:
    client = get_authenticated_client()
    result = client.table("promotions").insert(data).execute()
    return result.data[0] if result.data else {}


def update_promotion(promo_id: str, data: dict[str, Any]) -> dict[str, Any]:
    client = get_authenticated_client()
    result = (
        client.table("promotions").update(data).eq("id", promo_id).execute()
    )
    return result.data[0] if result.data else {}


def set_promotion_active(promo_id: str, active: bool):
    client = get_authenticated_client()
    client.table("promotions").update({"active": active}).eq("id", promo_id).execute()


def upload_image(file_bytes: bytes, filename: str, folder: str = "products") -> str:
    """Upload para Supabase Storage e retorna URL pública."""
    client = get_authenticated_client()
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "jpg"
    path = f"{folder}/{uuid.uuid4()}.{ext}"
    content_type = f"image/{ext}" if ext != "jpg" else "image/jpeg"
    if ext == "png":
        content_type = "image/png"
    elif ext == "webp":
        content_type = "image/webp"

    client.storage.from_("store-assets").upload(
        path,
        file_bytes,
        file_options={"content-type": content_type},
    )
    return client.storage.from_("store-assets").get_public_url(path)


def resize_image(file_bytes: bytes, max_size: int = 1200) -> bytes:
    from PIL import Image

    img = Image.open(io.BytesIO(file_bytes))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()
