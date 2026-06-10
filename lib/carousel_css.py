"""CSS de carrossel crossfade com nomes de animação seguros."""

from __future__ import annotations


def build_crossfade_carousel_css(n: int, duration: float, *, carousel_id: str) -> str:
    """Keyframes dinâmicos: cada slide visível 100/n % do ciclo, sem gaps."""
    if n < 2:
        return ""
    fade = max(2.0, min(8.0, 50.0 / n))
    blocks: list[str] = []
    scope = f'.store-banner-carousel[data-carousel-id="{carousel_id}"]'
    for i in range(n):
        start = 100.0 * i / n
        end = 100.0 * (i + 1) / n
        in_end = min(start + fade, end)
        out_start = max(end - fade, start)
        anim = f"storeBannerCf_{carousel_id}_{i}"
        blocks.append(
            f"@keyframes {anim} {{"
            f"0%, {start:.2f}% {{ opacity: 0; z-index: 0; }}"
            f"{in_end:.2f}%, {out_start:.2f}% {{ opacity: 1; z-index: 1; }}"
            f"{end:.2f}%, 100% {{ opacity: 0; z-index: 0; }}"
            f"}}"
            f"{scope} .store-banner-slide:nth-child({i + 1}) {{"
            f"animation: {anim} {duration}s infinite linear;"
            f"animation-delay: {-i * duration / n:.4f}s;"
            f"}}"
        )
        dot_anim = f"storeBannerDot_{carousel_id}_{i}"
        blocks.append(
            f"@keyframes {dot_anim} {{"
            f"0%, {start:.2f}% {{ background: var(--primary); transform: scale(1.25); }}"
            f"{in_end:.2f}%, {out_start:.2f}% {{ background: var(--primary); transform: scale(1.25); }}"
            f"{end:.2f}%, 100% {{ background: #d0d0d0; transform: scale(1); }}"
            f"}}"
            f"{scope} .store-banner-dot:nth-child({i + 1}) {{"
            f"animation: {dot_anim} {duration}s infinite linear;"
            f"animation-delay: {-i * duration / n:.4f}s;"
            f"}}"
        )
    return f"<style>{''.join(blocks)}</style>"
