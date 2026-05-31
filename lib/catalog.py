"""Operações de dados do catálogo."""

from __future__ import annotations

import io
import uuid
from typing import Any

from lib.supabase_client import get_authenticated_client, get_supabase


def fetch_store_settings() -> dict[str, Any]:
    client = get_supabase()
    result = client.table("store_settings").select("*").limit(1).execute()
    if result.data:
        return result.data[0]
    return {
        "store_name": "Minha Loja",
        "whatsapp_number": "",
        "primary_color": "#E1306C",
        "secondary_color": "#833AB4",
        "accent_color": "#FCAF45",
        "logo_url": None,
    }


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


def delete_product(product_id: str):
    client = get_authenticated_client()
    client.table("products").delete().eq("id", product_id).execute()


def fetch_gifts() -> list[dict[str, Any]]:
    client = get_supabase()
    return client.table("gifts").select("*").order("name").execute().data or []


def fetch_all_gifts_admin() -> list[dict[str, Any]]:
    client = get_authenticated_client()
    return client.table("gifts").select("*").order("name").execute().data or []


def create_gift(data: dict[str, Any]) -> dict[str, Any]:
    client = get_authenticated_client()
    result = client.table("gifts").insert(data).execute()
    return result.data[0] if result.data else {}


def update_gift(gift_id: str, data: dict[str, Any]) -> dict[str, Any]:
    client = get_authenticated_client()
    result = client.table("gifts").update(data).eq("id", gift_id).execute()
    return result.data[0] if result.data else {}


def delete_gift(gift_id: str):
    client = get_authenticated_client()
    client.table("gifts").delete().eq("id", gift_id).execute()


def fetch_product_gifts(product_id: str) -> list[dict[str, Any]]:
    client = get_supabase()
    return (
        client.table("product_gifts")
        .select("*, gifts(*)")
        .eq("product_id", product_id)
        .execute()
        .data
        or []
    )


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


def delete_promotion(promo_id: str):
    client = get_authenticated_client()
    client.table("promotions").delete().eq("id", promo_id).execute()


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
