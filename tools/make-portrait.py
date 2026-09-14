"""
Crop and size a portrait photograph for the About page.

    python tools/make-portrait.py PHOTO                    centred 4:5 crop
    python tools/make-portrait.py PHOTO --focus 0.5,0.35   centre the crop on a point
                                                           (fractions of width, height)
    python tools/make-portrait.py PHOTO --crop X,Y,W       an exact 4:5 box, W pixels wide

Writes assets/portrait.webp at 900 x 1125 (4:5). Nothing else is done to the
photo: the warm tone, the white print border and the tape are all CSS, so
the same file looks right on the light and the dark theme. Pillow only —
JPG and PNG work; HEIC from an iPhone needs exporting as JPG first.
"""
import os
import sys

from PIL import Image, ImageOps

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
OUT = os.path.join(ROOT, "assets", "portrait.webp")
W, H = 900, 1125


def arg(name):
    if name in sys.argv:
        return sys.argv[sys.argv.index(name) + 1]
    return None


def main():
    if len(sys.argv) < 2 or sys.argv[1].startswith("--"):
        raise SystemExit(__doc__)
    # phones store the rotation separately; apply it before cropping
    img = ImageOps.exif_transpose(Image.open(sys.argv[1])).convert("RGB")
    iw, ih = img.size

    crop = arg("--crop")
    if crop:
        x, y, w = [int(float(v)) for v in crop.split(",")]
        h = int(w * 5 / 4)
    else:
        # the largest 4:5 box that fits, centred on the focus point
        fx, fy = [float(v) for v in (arg("--focus") or "0.5,0.4").split(",")]
        w = min(iw, int(ih * 4 / 5))
        h = int(w * 5 / 4)
        x = int(iw * fx - w / 2)
        y = int(ih * fy - h / 2)
    w, h = min(w, iw), min(h, ih)
    x = min(max(x, 0), iw - w)
    y = min(max(y, 0), ih - h)
    box = (x, y, x + w, y + h)

    out = img.crop(box).resize((W, H), Image.LANCZOS)
    out.save(OUT, "WEBP", quality=86, method=6)
    print("wrote", os.path.relpath(OUT, ROOT), out.size, "from", img.size, "crop", box,
          round(os.path.getsize(OUT) / 1024), "KB")


if __name__ == "__main__":
    main()
