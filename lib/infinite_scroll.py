"""Gatilho de scroll infinito e botão voltar ao topo."""

from __future__ import annotations

import streamlit.components.v1 as components
import streamlit as st


def render_infinite_scroll_trigger(*, next_limit: int, filter_key: str) -> None:
    """Quando o usuário chega ao fim da lista, pede mais itens via query string."""
    safe_key = filter_key.replace('"', "")
    components.html(
        f"""
        <script>
        (function () {{
            let fired = false;
            const el = document.createElement("div");
            el.style.height = "1px";
            el.style.width = "100%";
            document.body.appendChild(el);
            const observer = new IntersectionObserver(
                (entries) => {{
                    if (!entries[0].isIntersecting || fired) return;
                    fired = true;
                    const url = new URL(window.parent.location.href);
                    if (url.searchParams.get("cl") === "{next_limit}") return;
                    url.searchParams.set("cl", "{next_limit}");
                    url.searchParams.set("ck", "{safe_key}");
                    window.parent.location.replace(url.toString());
                }},
                {{ root: null, rootMargin: "160px", threshold: 0 }}
            );
            observer.observe(el);
        }})();
        </script>
        """,
        height=8,
    )


def render_back_to_top() -> None:
    """Botão flutuante para rolar ao topo (no documento pai do Streamlit)."""
    components.html(
        """
        <script>
        (function () {
            const doc = window.parent.document;
            if (!doc) return;

            function scrollRoot() {
                return (
                    doc.querySelector('[data-testid="stAppViewContainer"]') ||
                    doc.querySelector("section.main") ||
                    doc.documentElement
                );
            }

            let btn = doc.getElementById("catalog-back-top-btn");
            if (!btn) {
                btn = doc.createElement("button");
                btn.id = "catalog-back-top-btn";
                btn.type = "button";
                btn.className = "catalog-back-top";
                btn.setAttribute("aria-label", "Voltar ao topo");
                btn.textContent = "↑";
                btn.addEventListener("click", function (e) {
                    e.preventDefault();
                    e.stopPropagation();
                    scrollRoot().scrollTo({ top: 0, behavior: "smooth" });
                });
                doc.body.appendChild(btn);
            }
        })();
        </script>
        """,
        height=0,
    )
