"""Draw original Steel & Sakura infantry card art in observed Shogun 2 TGA sizes."""

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "infantry"
NAME = "steel_sakura_automatic_rifle_squad.tga"
SIZES = {
    "icons": (64, 118),
    "icons_square": (46, 46),
    "info": (128, 236),
    "recruitment_large": (75, 75),
    "recruitment_small": (64, 64),
}


def make_card(size):
    width, height = size
    scale = 4
    w, h = width * scale, height * scale
    image = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    inset = max(4, w // 36)
    draw.rounded_rectangle((inset, inset, w - inset - 1, h - inset - 1), radius=w // 9,
                           fill=(54, 30, 35, 250), outline=(188, 150, 94, 255), width=max(3, w // 32))
    draw.rounded_rectangle((inset * 2, inset * 2, w - inset * 2 - 1, h - inset * 2 - 1),
                           radius=w // 11, outline=(110, 79, 65, 255), width=max(2, w // 80))
    cx, cy = w // 2, int(h * (0.40 if h > w else 0.46))
    radius = int(w * 0.30)
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius),
                 fill=(184, 61, 48, 255), outline=(224, 171, 107, 255), width=max(2, w // 70))
    # Five pale petals around a dark sakura center: wholly original geometry.
    petal = max(5, w // 12)
    import math
    for angle in range(0, 360, 72):
        radians = math.radians(angle - 90)
        px = cx + int(radius * 0.48 * math.cos(radians))
        py = cy + int(radius * 0.48 * math.sin(radians))
        draw.ellipse((px - petal, py - petal, px + petal, py + petal),
                     fill=(243, 216, 186, 255), outline=(95, 48, 46, 255), width=max(1, w // 120))
    draw.ellipse((cx - petal // 2, cy - petal // 2, cx + petal // 2, cy + petal // 2), fill=(222, 164, 87, 255))
    # A single diagonal steel rifle silhouette stays legible at 46 px.
    x0, y0 = int(w * 0.20), int(h * (0.77 if h > w else 0.78))
    x1, y1 = int(w * 0.80), int(h * (0.18 if h > w else 0.20))
    stroke = max(5, w // 18)
    draw.line((x0, y0, x1, y1), fill=(30, 35, 39, 255), width=stroke + 3)
    draw.line((x0, y0, x1, y1), fill=(167, 177, 175, 255), width=stroke)
    draw.line((x0 - stroke, y0 + stroke, x0 + stroke, y0 - stroke),
              fill=(129, 79, 49, 255), width=stroke + 2)
    draw.line((int(w * 0.49), int(h * 0.52), int(w * 0.61), int(h * 0.61)),
              fill=(31, 34, 37, 255), width=max(3, stroke // 2))
    draw.line((x1 - stroke // 2, y1 + stroke // 2, x1 + stroke // 3, y1 - stroke // 3),
              fill=(236, 214, 167, 255), width=max(2, stroke // 3))
    return image.resize(size, Image.Resampling.LANCZOS)


def main():
    for folder, size in SIZES.items():
        destination = OUT / folder / NAME
        destination.parent.mkdir(parents=True, exist_ok=True)
        image = make_card(size)
        image.save(destination, format="TGA")
        print(f"{destination.relative_to(ROOT)}: {size[0]}x{size[1]}")


if __name__ == "__main__":
    main()
