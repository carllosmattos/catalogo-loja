"""Cálculo de custo, lucro e margem."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class GiftCost:
    gift_id: str
    name: str
    quantity: int
    purchase_price: float
    purchase_freight: float
    sale_markup: float
    image_url: str | None = None
    image_urls: list[str] | None = None

    @property
    def total_cost(self) -> float:
        return (self.purchase_price + self.purchase_freight) * self.quantity

    @property
    def total_markup(self) -> float:
        return self.sale_markup * self.quantity

    @property
    def absorbed_cost(self) -> float:
        return self.total_cost - self.total_markup


@dataclass
class ProfitResult:
    product_name: str
    custo_peca: float
    custo_brindes: float
    repasse_brinde: float
    preco_catalogo: float
    desconto: float
    preco_final_cliente: float
    lucro_bruto: float
    margem_percent: float
    promotion_name: str | None
    gifts: list[GiftCost]
    stock: int
    gift_stock_ok: bool


def extract_gift_from_link(link: dict[str, Any]) -> dict[str, Any] | None:
    """Extrai dados do brinde de um vínculo product_gifts."""
    for key in ("gift_data", "gifts", "gift"):
        value = link.get(key)
        if isinstance(value, dict) and value.get("id"):
            return value
    return None


def apply_promotion(
    sale_price: float,
    product_id: str,
    promotions: list[dict[str, Any]],
) -> tuple[float, str | None]:
    """Retorna (desconto, nome_promocao) para o melhor desconto aplicável."""
    best_discount = 0.0
    best_name: str | None = None

    pid = str(product_id)
    for promo in promotions:
        product_ids = [str(x) for x in (promo.get("product_ids") or [])]
        applies = promo.get("applies_to") == "all" or pid in product_ids
        if not applies:
            continue

        discount_type = promo.get("discount_type", "percent")
        discount_value = float(promo.get("discount_value", 0))

        if discount_type == "percent":
            discount = sale_price * (discount_value / 100)
        else:
            discount = min(discount_value, sale_price)

        if discount > best_discount:
            best_discount = discount
            best_name = promo.get("name")

    return best_discount, best_name


from lib.product_sizes import stock_for_size, total_stock


def calculate_profit(
    product: dict[str, Any],
    linked_gifts: list[dict[str, Any]],
    promotions: list[dict[str, Any]] | None = None,
    *,
    selected_size: str | None = None,
) -> ProfitResult:
    purchase_price = float(product.get("purchase_price", 0))
    purchase_freight = float(product.get("purchase_freight", 0))
    sale_price = float(product.get("sale_price", 0))
    sale_freight = float(product.get("sale_freight", 0))
    sizes = product.get("sizes")
    if sizes is not None:
        stock = (
            stock_for_size(sizes, selected_size)
            if selected_size
            else total_stock(sizes)
        )
    else:
        stock = int(product.get("stock", 0))

    custo_peca = purchase_price + purchase_freight

    gift_costs: list[GiftCost] = []
    custo_brindes = 0.0
    repasse_brinde = 0.0
    gift_stock_ok = True

    for lg in linked_gifts:
        gift = extract_gift_from_link(lg)
        if not gift:
            continue

        qty = int(lg.get("quantity_per_sale", 1))
        gc = GiftCost(
            gift_id=str(gift.get("id", "")),
            name=gift.get("name", "Brinde"),
            quantity=qty,
            purchase_price=float(gift.get("purchase_price", 0)),
            purchase_freight=float(gift.get("purchase_freight", 0)),
            sale_markup=float(gift.get("sale_markup", 0)),
            image_url=(gift.get("image_url") or (gift.get("image_urls") or [None])[0]),
            image_urls=gift.get("image_urls") or [],
        )
        gift_costs.append(gc)
        custo_brindes += gc.total_cost
        repasse_brinde += gc.total_markup
        if int(gift.get("stock", 0)) < qty:
            gift_stock_ok = False

    preco_catalogo = sale_price + repasse_brinde

    desconto = 0.0
    promotion_name: str | None = None
    if promotions:
        desconto, promotion_name = apply_promotion(
            preco_catalogo, str(product.get("id", "")), promotions
        )

    preco_final_cliente = preco_catalogo - desconto + sale_freight
    lucro_bruto = preco_final_cliente - custo_peca - custo_brindes

    margem = (
        (lucro_bruto / preco_final_cliente * 100) if preco_final_cliente > 0 else 0.0
    )

    return ProfitResult(
        product_name=product.get("name", ""),
        custo_peca=custo_peca,
        custo_brindes=custo_brindes,
        repasse_brinde=repasse_brinde,
        preco_catalogo=preco_catalogo,
        desconto=desconto,
        preco_final_cliente=preco_final_cliente,
        lucro_bruto=lucro_bruto,
        margem_percent=margem,
        promotion_name=promotion_name,
        gifts=gift_costs,
        stock=stock,
        gift_stock_ok=gift_stock_ok,
    )
