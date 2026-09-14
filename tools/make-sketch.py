"""Turn the portrait photograph into an ink sketch that sits on the paper.

    python tools/make-sketch.py                     writes assets/sketch.webp
    python tools/make-sketch.py --preview out.png   also writes a preview on paper

A colour-dodge sketch rather than a straight luminance-to-alpha map: flat
areas go to paper and only drawn detail survives. That matters here because
the photograph's background and T-shirt are both near black — mapped straight
to ink they would print as two solid blocks, and the face would be lost
between them. An elliptical feather then lets the edges of the drawing fade
out into the page instead of stopping at a rectangle.

Pillow only — no numpy — so the tool runs anywhere the rest of the tools do.
"""
import math
import os
import sys

from PIL import Image, ImageFilter, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = "D:/claude/animation/cinematic-scroll/assets/portrait-source.png"   # the original photograph
OUT = os.path.join(ROOT, "assets", "sketch.webp")

CROP = (420, 0, 1360, 940)     # a square on the face, the hand and the glasses
WORK = 760                     # drawn at the output size: faster, and the lines stay crisp
INK = (38, 34, 30)             # --ink
PAPER = (250, 246, 236)        # --paper-3, for the preview only

GAIN = 2.6                     # how dark the drawn lines print
FLOOR = 30                     # alpha below this is grain, not drawing


def sketch(img):
    grey = ImageOps.autocontrast(ImageOps.grayscale(img), cutoff=1)
    blur = grey.filter(ImageFilter.GaussianBlur(7))
    w, h = grey.size

    g = grey.getdata()
    b = blur.getdata()
    cx, cy, rx, ry = w * 0.52, h * 0.47, w * 0.47, h * 0.58

    alpha = bytearray(w * h)
    for i in range(w * h):
        # colour dodge: equal to paper wherever the image is locally flat
        dodge = g[i] * 255.0 / (b[i] or 1)
        ink = 255.0 - (dodge if dodge < 255.0 else 255.0)
        a = ink * GAIN
        if a < FLOOR:
            continue
        x, y = i % w, i // w
        d = math.sqrt(((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2)
        feather = (1.1 - d) / 0.3
        if feather <= 0:
            continue
        a *= feather if feather < 1 else 1
        alpha[i] = int(a if a < 255 else 255)

    out = Image.new("RGBA", (w, h), INK + (0,))
    out.putalpha(Image.frombytes("L", (w, h), bytes(alpha)))
    return out


def main():
    src = Image.open(SRC).convert("RGB").crop(CROP).resize((WORK, WORK), Image.LANCZOS)
    out = sketch(src)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    out.save(OUT, "WEBP", quality=86, method=6)
    print("wrote", OUT, round(os.path.getsize(OUT) / 1024, 1), "KB")

    if "--preview" in sys.argv:
        path = sys.argv[sys.argv.index("--preview") + 1]
        paper = Image.new("RGBA", out.size, PAPER + (255,))
        paper.alpha_composite(out)
        paper.convert("RGB").save(path)
        print("preview", path)


if __name__ == "__main__":
    main()
