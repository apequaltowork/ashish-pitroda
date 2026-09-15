"""
Draw the link-preview card shown when the site is shared (LinkedIn, WhatsApp,
Slack, X): assets/share-card.png at 1200 x 630, paper ground, the pencil
sketch on the left, name and line of work on the right.

    python tools/make-share-card.py

Pillow only. Uses Georgia from C:/Windows/Fonts.
"""
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
OUT = os.path.join(ROOT, "assets", "share-card.png")
W, H = 1200, 630
PAPER, INK, PENCIL, RULE = (241, 234, 219), (38, 34, 30), (163, 45, 45), (205, 193, 170)
FONTS = "C:/Windows/Fonts/"


def font(name, size):
    return ImageFont.truetype(FONTS + name, size)


def main():
    card = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(card)

    for y in range(90, H, 42):                       # notebook rules
        d.line([(0, y), (W, y)], fill=RULE, width=1)
    d.line([(520, 0), (520, H)], fill=PENCIL, width=2)  # margin line

    src = Image.open(os.path.join(ROOT, "assets", "sketch.webp")).convert("RGBA")
    white = Image.new("RGBA", src.size, (255, 255, 255, 255))
    sketch = Image.alpha_composite(white, src).convert("L")   # transparent edges become paper, not ink
    sketch = sketch.resize((470, 470), Image.LANCZOS)
    mask = Image.eval(sketch, lambda v: 255 - v)     # ink only, paper shows through
    card.paste(Image.new("RGB", sketch.size, INK), (30, 80), mask)

    x = 570
    d.text((x, 150), "Ashish Pitroda", font=font("georgiab.ttf", 68), fill=INK)
    d.text((x, 250), "Senior full-stack developer", font=font("georgiai.ttf", 40), fill=PENCIL)
    for i, line in enumerate(["Wagtail CMS, Django and Python,", "Vue, Next.js and AWS"]):
        d.text((x, 335 + i * 50), line, font=font("georgia.ttf", 36), fill=INK)
    d.text((x, 500), "apequaltowork.github.io/ashish-pitroda", font=font("georgia.ttf", 26), fill=INK)

    card.save(OUT, optimize=True)
    print(OUT, os.path.getsize(OUT) // 1024, "KB")


if __name__ == "__main__":
    main()
