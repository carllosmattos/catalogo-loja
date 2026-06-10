"""Ajustes de layout do catálogo via JS no documento pai (efetivo com Streamlit)."""

from __future__ import annotations

import streamlit.components.v1 as components


def inject_catalog_layout_fix() -> None:
    """Posiciona menu do header e iguala altura dos botões carrinho/Pix/WhatsApp."""
    components.html(
        """
        <script>
        (function () {
            const doc = window.parent.document;
            if (!doc) return;

            function cssVar(name, fallback) {
                const v = getComputedStyle(doc.documentElement)
                    .getPropertyValue(name)
                    .trim();
                return v || fallback;
            }

            function fixHeader() {
                const bar = doc.querySelector(".catalog-header-bar");
                if (!bar) return;

                const headerH = cssVar("--catalog-header-height", "4rem");
                bar.style.setProperty("height", headerH, "important");
                bar.style.setProperty("min-height", headerH, "important");
                bar.style.setProperty("max-height", headerH, "important");
                bar.style.setProperty("display", "grid", "important");
                bar.style.setProperty("align-items", "center", "important");

                const menuRoot = doc.querySelector('[class*="catalog_menu_toggle"]');
                const slot = doc.querySelector(".catalog-header-bar__menu");
                if (!menuRoot || !slot) return;

                const sr = slot.getBoundingClientRect();
                menuRoot.style.setProperty("position", "fixed", "important");
                menuRoot.style.setProperty("top", sr.top + "px", "important");
                menuRoot.style.setProperty("left", sr.left + "px", "important");
                menuRoot.style.setProperty("width", sr.width + "px", "important");
                menuRoot.style.setProperty("height", sr.height + "px", "important");
                menuRoot.style.setProperty("z-index", "10012", "important");
                menuRoot.style.setProperty("margin", "0", "important");
                menuRoot.style.setProperty("padding", "0", "important");

                menuRoot.querySelectorAll("div.stButton, button").forEach(function (el) {
                    el.style.setProperty("width", "100%", "important");
                    el.style.setProperty("height", "100%", "important");
                    el.style.setProperty("min-width", "100%", "important");
                    el.style.setProperty("min-height", "100%", "important");
                    el.style.setProperty("max-width", "100%", "important");
                    el.style.setProperty("max-height", "100%", "important");
                    el.style.setProperty("padding", "0", "important");
                    el.style.setProperty("margin", "0", "important");
                    el.style.setProperty("display", "flex", "important");
                    el.style.setProperty("align-items", "center", "important");
                    el.style.setProperty("justify-content", "center", "important");
                    el.style.setProperty("box-sizing", "border-box", "important");
                    if (el.tagName === "BUTTON") {
                        el.style.setProperty("border-radius", "0", "important");
                        el.style.setProperty(
                            "padding",
                            cssVar("--catalog-header-menu-padding", "0.45rem"),
                            "important"
                        );
                    }
                });
            }

            function fixActionRows() {
                const h = cssVar("--catalog-action-btn-height", "2.25rem");
                doc.querySelectorAll(
                    '.catalog-product-grid [data-testid="stHorizontalBlock"]'
                ).forEach(function (row) {
                    const cols = row.querySelectorAll(
                        ':scope > [data-testid="column"]'
                    );
                    if (cols.length !== 3) return;
                    if (!row.querySelector(
                        '[class*="st-key-add_"], [class*="buy_pix"], a.catalog-brand-wa'
                    )) return;

                    row.style.setProperty("align-items", "stretch", "important");
                    cols.forEach(function (col) {
                        col.style.setProperty("display", "flex", "important");
                        col.style.setProperty("align-items", "stretch", "important");
                        col.querySelectorAll(
                            ".stElementContainer, div.stButton, " +
                            '[data-testid="stMarkdownContainer"], .catalog-action-cell'
                        ).forEach(function (wrap) {
                            wrap.style.setProperty("height", h, "important");
                            wrap.style.setProperty("min-height", h, "important");
                            wrap.style.setProperty("max-height", h, "important");
                            wrap.style.setProperty("width", "100%", "important");
                            wrap.style.setProperty("margin", "0", "important");
                            wrap.style.setProperty("padding", "0", "important");
                            wrap.style.setProperty("display", "flex", "important");
                            wrap.style.setProperty("align-items", "stretch", "important");
                            wrap.style.setProperty("box-sizing", "border-box", "important");
                        });
                        col.querySelectorAll("button, a.catalog-brand-wa").forEach(function (el) {
                            el.style.setProperty("height", h, "important");
                            el.style.setProperty("min-height", h, "important");
                            el.style.setProperty("max-height", h, "important");
                            el.style.setProperty("width", "100%", "important");
                            el.style.setProperty("padding", "0", "important");
                            el.style.setProperty("margin", "0", "important");
                            el.style.setProperty("display", "flex", "important");
                            el.style.setProperty("align-items", "center", "important");
                            el.style.setProperty("justify-content", "center", "important");
                            el.style.setProperty("box-sizing", "border-box", "important");
                        });
                    });
                });
            }

            function initStoreBannerCarousel() {
                doc.querySelectorAll(".store-banner-carousel").forEach(function (carousel) {
                    if (carousel._bannerTimer) {
                        clearInterval(carousel._bannerTimer);
                        carousel._bannerTimer = null;
                    }
                    const slides = carousel.querySelectorAll(".store-banner-slide");
                    const dots = carousel.querySelectorAll(".store-banner-dot");
                    if (!slides.length) return;

                    let idx = 0;
                    function show(i) {
                        slides.forEach(function (slide, j) {
                            slide.classList.toggle("is-active", j === i);
                        });
                        dots.forEach(function (dot, j) {
                            dot.classList.toggle("is-active", j === i);
                        });
                    }
                    show(0);
                    if (slides.length < 2) return;

                    const ms = parseInt(carousel.getAttribute("data-interval") || "5000", 10);
                    carousel._bannerTimer = setInterval(function () {
                        idx = (idx + 1) % slides.length;
                        show(idx);
                    }, ms);
                });
            }

            function run() {
                fixHeader();
                fixActionRows();
                initStoreBannerCarousel();
            }

            run();
            window.parent.addEventListener("resize", run);
            new MutationObserver(function () {
                requestAnimationFrame(run);
            }).observe(doc.body, { childList: true, subtree: true, attributes: true });
        })();
        </script>
        """,
        height=0,
    )
