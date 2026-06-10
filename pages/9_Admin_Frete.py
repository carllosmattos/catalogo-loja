"""Admin — zonas de frete e endereço remetente."""

import streamlit as st

from lib.address import BRAZILIAN_STATES, render_address_fields
from lib.auth import require_auth, render_sidebar
from lib.branding import configure_page
from lib.catalog import fetch_store_settings, update_store_settings
from lib.shipping.zones import (
    delete_shipping_zone,
    fetch_shipping_zones,
    upsert_shipping_zone,
)

configure_page("Admin — Frete", layout="wide", sidebar_state="expanded")
render_sidebar()

if not require_auth():
    st.stop()

st.title("🚚 Frete e entrega")

settings = fetch_store_settings()

st.subheader("Endereço remetente (Melhor Envio)")
st.caption("Usado para cotação automática quando não houver zona configurada.")

with st.form("sender_form"):
    c1, c2 = st.columns(2)
    with c1:
        sender_zip = st.text_input("CEP origem", value=settings.get("sender_zip", ""))
        sender_street = st.text_input("Rua", value=settings.get("sender_street", ""))
        sender_number = st.text_input("Número", value=settings.get("sender_number", ""))
    with c2:
        sender_city = st.text_input("Cidade", value=settings.get("sender_city", ""))
        sender_state = st.selectbox(
            "UF",
            BRAZILIAN_STATES,
            index=BRAZILIAN_STATES.index(settings["sender_state"])
            if settings.get("sender_state") in BRAZILIAN_STATES
            else BRAZILIAN_STATES.index("SP"),
        )
        weight = st.number_input(
            "Peso padrão (kg)",
            min_value=0.1,
            max_value=30.0,
            value=float(settings.get("default_package_weight_kg") or 0.3),
            step=0.1,
        )
    sender_complement = st.text_input(
        "Complemento", value=settings.get("sender_complement", "")
    )
    sender_neighborhood = st.text_input(
        "Bairro", value=settings.get("sender_neighborhood", "")
    )
    me_enabled = st.checkbox(
        "Usar Melhor Envio quando não houver zona",
        value=bool(settings.get("melhor_envio_enabled")),
        help="Requer MELHOR_ENVIO_TOKEN nos secrets do Streamlit.",
    )
    if st.form_submit_button("Salvar remetente", use_container_width=True):
        update_store_settings(
            {
                "sender_zip": sender_zip,
                "sender_street": sender_street,
                "sender_number": sender_number,
                "sender_complement": sender_complement,
                "sender_neighborhood": sender_neighborhood,
                "sender_city": sender_city,
                "sender_state": sender_state,
                "default_package_weight_kg": weight,
                "melhor_envio_enabled": me_enabled,
            }
        )
        st.success("Endereço remetente salvo.")
        st.rerun()

st.markdown("---")
st.subheader("Zonas de entrega")
st.caption(
    "Prioridade: bairro > cidade > UF > país. "
    "**Bloqueado** impede checkout; **Grátis** zera o frete; **Pago** usa valor fixo."
)

zones = fetch_shipping_zones()
if zones:
    for z in zones:
        scope = z.get("scope", "")
        loc = z.get("label") or f"{scope}: {z.get('state', '')} {z.get('city', '')}"
        active = "ativo" if z.get("active") else "inativo"
        with st.expander(f"{z.get('zone_type')} — {loc} ({active})"):
            st.markdown(
                f"Escopo **{scope}** · UF `{z.get('state', '')}` · "
                f"Cidade `{z.get('city', '')}` · Bairro `{z.get('neighborhood', '')}`"
            )
            if z.get("zone_type") == "paid":
                st.markdown(f"Valor: R$ {float(z.get('freight_amount', 0)):.2f}")
            if st.button("Excluir zona", key=f"del_zone_{z['id']}", type="secondary"):
                delete_shipping_zone(str(z["id"]))
                st.success("Zona removida.")
                st.rerun()
else:
    st.info("Nenhuma zona cadastrada. Frete virá do produto ou Melhor Envio.")

with st.form("new_zone"):
    zone_type = st.selectbox("Tipo", ["free", "paid", "blocked"])
    scope = st.selectbox("Escopo", ["state", "city", "neighborhood", "country"])
    label = st.text_input("Nome (opcional)", placeholder="Ex: SP capital grátis")
    c1, c2, c3 = st.columns(3)
    with c1:
        state = st.selectbox("UF", [""] + BRAZILIAN_STATES)
    with c2:
        city = st.text_input("Cidade", disabled=scope in ("state", "country"))
    with c3:
        neighborhood = st.text_input(
            "Bairro", disabled=scope != "neighborhood"
        )
    freight_amount = 0.0
    if zone_type == "paid":
        freight_amount = st.number_input("Valor do frete (R$)", min_value=0.0, step=1.0)
    priority = st.number_input("Prioridade", min_value=0, value=0, step=1)
    if st.form_submit_button("Adicionar zona", use_container_width=True):
        if scope == "state" and not state:
            st.error("Informe a UF.")
        elif scope == "city" and (not state or not city.strip()):
            st.error("Informe UF e cidade.")
        elif scope == "neighborhood" and (
            not state or not city.strip() or not neighborhood.strip()
        ):
            st.error("Informe UF, cidade e bairro.")
        else:
            upsert_shipping_zone(
                {
                    "zone_type": zone_type,
                    "scope": scope,
                    "state": state,
                    "city": city.strip(),
                    "neighborhood": neighborhood.strip(),
                    "freight_amount": freight_amount,
                    "priority": priority,
                    "label": label,
                    "active": True,
                }
            )
            st.success("Zona adicionada.")
            st.rerun()
