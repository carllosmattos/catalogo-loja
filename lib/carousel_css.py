"""CSS de carrossel crossfade dinâmico (sem gaps entre slides)."""

from __future__ import annotations


def build_crossfade_carousel_css(
    n: int,
    duration: float,
    *,
    scope: str,
    slide_class: str,
    dot_class: str = "",
) -> str:
    """Gera keyframes por slide: cada uma visível 100/n % do ciclo."""
    if n < 2:
        return ""
    fade = max(2.0, min(8.0, 50.0 / n))
    blocks: list[str] = []
    for i in range(n):
        start = 100.0 * i / n
        end = 100.0 * (i + 1) / n
        in_end = min(start + fade, end)
        out_start = max(end - fade, start)
        name = f"crossfade_{scope}_{n}_{i}"
        blocks.append(
            f"@keyframes {name} {{"
            f"0%, {start:.2f}% {{ opacity: 0; z-index: 0; }}"
            f"{in_end:.2f}%, {out_start:.2f}% {{ opacity: 1; z-index: 1; }}"
            f"{end:.2f}%, 100% {{ opacity: 0; z-index: 0; }}"
            f"}}"
            f"{scope} .{slide_class}:nth-child({i + 1}) {{"
            f"animation: {name} {duration}s infinite linear;"
            f"animation-delay: {-i * duration / n:.4f}s;"
            f"}}"
        )
        if dot_class:
            dot_name = f"dot_{scope}_{n}_{i}"
            blocks.append(
                f"@keyframes {dot_name} {{"
                f"0%, {start:.2f}% {{ background: var(--primary); transform: scale(1.25); }}"
                f"{in_end:.2f}%, {out_start:.2f}% {{ background: var(--primary); transform: scale(1.25); }}"
                f"{end:.2f}%, 100% {{ background: #d0d0d0; transform: scale(1); }}"
                f"}}"
                f"{scope} .{dot_class}:nth-child({i + 1}) {{"
                f"animation: {dot_name} {duration}s infinite linear;"
                f"animation-delay: {-i * duration / n:.4f}s;"
                f"}}"
            )
    return f"<style>{''.join(blocks)}</style>"
