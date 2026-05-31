"""Recorta margens e gera logo circular PNG (só o círculo magenta)."""

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "resources" / "lm.jpeg"
OUT = ROOT / "resources" / "lm_logo.png"


def is_logo_pixel(r: int, g: int, b: int) -> bool:
    """Ignora preto, branco e cinzas — mantém magenta, dourado e rosa."""
    if r < 30 and g < 30 and b < 30:
        return False
    if r > 240 and g > 240 and b > 240:
        return False
    if abs(r - g) < 15 and abs(g - b) < 15 and r > 200:
        return False
    return True


def crop_to_logo_content(img: Image.Image) -> Image.Image:
    rgb = img.convert("RGB")
    px = rgb.load()
    w, h = rgb.size
    min_x, min_y, max_x, max_y = w, h, 0, 0
    found = False
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            if is_logo_pixel(r, g, b):
                found = True
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
    if not found:
        return rgb
    cropped = rgb.crop((min_x, min_y, max_x + 1, max_y + 1))
    # Remove fina borda branca externa
    inset = max(4, int(min(cropped.size) * 0.012))
    w, h = cropped.size
    return cropped.crop((inset, inset, w - inset, h - inset))


def to_circle(img: Image.Image, size: int = 512) -> Image.Image:
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    square = img.crop((left, top, left + side, top + side)).resize(
        (size, size), Image.Resampling.LANCZOS
    )
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(square.convert("RGBA"), (0, 0), mask)
    return out


def main():
    img = Image.open(SRC)
    cropped = crop_to_logo_content(img)
    logo = to_circle(cropped)
    logo.save(OUT, "PNG", optimize=True)
    print(f"Logo salva em {OUT} ({logo.size[0]}x{logo.size[1]})")


if __name__ == "__main__":
    main()
