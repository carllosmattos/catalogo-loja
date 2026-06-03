"""Mapeamento de status Mercado Pago."""

from lib.payments.models import PaymentStatus

MP_STATUS_MAP = {
    "approved": PaymentStatus.APPROVED,
    "pending": PaymentStatus.PENDING,
    "in_process": PaymentStatus.IN_PROCESS,
    "rejected": PaymentStatus.REJECTED,
    "cancelled": PaymentStatus.CANCELLED,
    "refunded": PaymentStatus.REFUNDED,
}


def map_mp_status(status: str) -> PaymentStatus:
    return MP_STATUS_MAP.get((status or "").lower(), PaymentStatus.PENDING)


def extract_pix_copy_paste(payment: dict) -> str:
    poi = payment.get("point_of_interaction") or {}
    tx = poi.get("transaction_data") or {}
    return tx.get("qr_code") or tx.get("qr_code_base64") or ""
