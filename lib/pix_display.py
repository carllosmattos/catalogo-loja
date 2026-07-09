"""Exibição de PIX com QR e botão Copiar."""

from __future__ import annotations

import base64
import html

import streamlit as st
import streamlit.components.v1 as components


def render_pix_payment(
    pix_copy_paste: str,
    *,
    key: str,
    qr_base64: str | None = None,
) -> None:
    """QR (se houver) + código resumido + botão Copiar sempre visível."""
    if not pix_copy_paste:
        return

    if qr_base64:
        raw = qr_base64
        if raw.startswith("data:"):
            st.image(raw, caption="PIX QR Code", use_container_width=False)
        else:
            try:
                st.image(base64.b64decode(raw), caption="PIX QR Code")
            except Exception:
                pass

    preview = pix_copy_paste if len(pix_copy_paste) <= 120 else pix_copy_paste[:117] + "…"
    st.caption(preview)

    safe = html.escape(pix_copy_paste, quote=True)
    btn_id = html.escape(f"pix_copy_{key}", quote=True)
    components.html(
        f"""
        <div style="margin:0.25rem 0 0.5rem">
          <button id="{btn_id}" type="button" style="
            width:100%; padding:0.65rem 1rem; font-size:1rem; font-weight:600;
            background:var(--primary,#8B0A50); color:#fff; border:none;
            border-radius:8px; cursor:pointer;
          ">Copiar PIX</button>
          <span id="{btn_id}_msg" style="display:block;margin-top:0.35rem;font-size:0.85rem;color:#28a745"></span>
        </div>
        <script>
        (function() {{
          const btn = document.getElementById("{btn_id}");
          const msg = document.getElementById("{btn_id}_msg");
          const text = "{safe}";
          if (!btn) return;
          btn.addEventListener("click", function() {{
            const done = function() {{
              msg.textContent = "Código copiado!";
              setTimeout(function() {{ msg.textContent = ""; }}, 2500);
            }};
            if (navigator.clipboard && navigator.clipboard.writeText) {{
              navigator.clipboard.writeText(text).then(done).catch(function() {{
                fallbackCopy();
              }});
            }} else {{
              fallbackCopy();
            }}
            function fallbackCopy() {{
              const ta = document.createElement("textarea");
              ta.value = text;
              document.body.appendChild(ta);
              ta.select();
              try {{ document.execCommand("copy"); done(); }} catch (e) {{}}
              document.body.removeChild(ta);
            }}
          }});
        }})();
        </script>
        """,
        height=90,
    )
