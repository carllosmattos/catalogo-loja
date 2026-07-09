"""Gateway Mercado Pago — PIX."""

from __future__ import annotations

from typing import Any

import mercadopago

from lib.payments.mercado_pago.mapper import extract_pix_copy_paste, map_mp_status
from lib.payments.models import CheckoutRequest, CheckoutResult, PaymentStatus, WebhookEvent
from lib.payments.protocols import PaymentGateway
from lib.utils import normalize_cpf


class MercadoPagoGateway(PaymentGateway):
    def __init__(self, access_token: str) -> None:
        self._sdk = mercadopago.SDK(access_token)

    @property
    def provider_name(self) -> str:
        return "mercado_pago"

    def create_pix_checkout(self, request: CheckoutRequest) -> CheckoutResult:
        cpf = normalize_cpf(request.payer.cpf)
        first_name = (request.payer.name or "Cliente").split()[0][:50]
        payment_data = {
            "transaction_amount": round(float(request.amount), 2),
            "description": request.description[:200],
            "payment_method_id": "pix",
            "external_reference": str(request.order_id),
            "payer": {
                "email": request.payer.email,
                "first_name": first_name,
                "identification": {"type": "CPF", "number": cpf},
            },
        }
        if request.notification_url:
            payment_data["notification_url"] = request.notification_url
        if request.expires_at_iso:
            payment_data["date_of_expiration"] = request.expires_at_iso

        response = self._sdk.payment().create(payment_data)
        payment = response.get("response") or {}
        if response.get("status", 0) >= 400:
            msg = payment.get("message") or payment.get("error") or str(response)
            raise ValueError(f"Mercado Pago: {msg}")

        pid = str(payment.get("id", ""))
        status = map_mp_status(payment.get("status", "pending"))
        pix = extract_pix_copy_paste(payment)
        ticket = (payment.get("point_of_interaction") or {}).get("transaction_data", {}).get(
            "ticket_url", ""
        )

        return CheckoutResult(
            provider_payment_id=pid,
            status=status,
            pix_copy_paste=pix if isinstance(pix, str) and len(pix) < 5000 else "",
            ticket_url=ticket or "",
            raw=payment,
        )

    def cancel_payment(self, provider_payment_id: str) -> dict[str, Any]:
        pid: int | str = provider_payment_id
        if str(provider_payment_id).isdigit():
            pid = int(provider_payment_id)
        response = self._sdk.payment().cancel(pid)
        if response.get("status", 0) >= 400:
            payment = response.get("response") or {}
            msg = payment.get("message") or str(response)
            raise ValueError(f"Mercado Pago: {msg}")
        return response.get("response") or {}

    def get_payment(self, provider_payment_id: str) -> dict[str, Any]:
        response = self._sdk.payment().get(provider_payment_id)
        return response.get("response") or {}

    def refund_payment(
        self, provider_payment_id: str, amount: float | None = None
    ) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if amount is not None:
            body["amount"] = round(float(amount), 2)
        response = self._sdk.refund().create(provider_payment_id, body)
        return response.get("response") or response

    def parse_webhook(self, headers: dict[str, str], body: dict[str, Any]) -> WebhookEvent | None:
        data = body.get("data") or {}
        pid = str(data.get("id") or body.get("id") or "")
        if not pid and body.get("type") == "payment":
            return None
        if body.get("action") in ("payment.created", "payment.updated") or body.get("type") == "payment":
            payment = self.get_payment(pid) if pid else {}
            if not payment:
                return None
            status = map_mp_status(payment.get("status", ""))
            return WebhookEvent(
                provider_payment_id=pid,
                external_reference=str(payment.get("external_reference", "")),
                status=status,
                amount=float(payment.get("transaction_amount", 0)),
                pix_copy_paste=extract_pix_copy_paste(payment),
                raw=payment,
            )
        return None
