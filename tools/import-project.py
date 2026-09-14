"""
Import a project's images from a prepared portfolio folder.

    python tools/import-project.py "D:/portfolio/DrParchi" drparchi

Reads thumbnail.png and gallery-NN-*.png from the folder and writes WebP
copies to assets/projects/<slug>/:

  cover.webp    the 4:3 thumbnail, trimmed to the cards' 16:10 (a little off
                the top, the rest off the bottom, so the title stays)
  NN-name.webp  each gallery image, full size so small UI text stays sharp

Then prints the `images` list to paste into projects.js. Videos are not
copied — link them on YouTube instead. Pillow only.
"""
import glob
import os
import re
import sys

from PIL import Image

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def save(im, path):
    im.save(path, "WEBP", quality=88, method=6)
    return round(os.path.getsize(path) / 1024)


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    src, slug = sys.argv[1], sys.argv[2]
    if not re.fullmatch(r"[a-z0-9-]+", slug):
        raise SystemExit("slug: lowercase letters, digits and hyphens only")
    dst = os.path.join(ROOT, "assets", "projects", slug)
    os.makedirs(dst, exist_ok=True)

    written, total = [], 0
    thumb = os.path.join(src, "thumbnail.png")
    if os.path.exists(thumb):
        im = Image.open(thumb).convert("RGB")
        w, h = im.size
        ch = round(w * 10 / 16)
        if ch < h:
            top = min(50, h - ch)
            im = im.crop((0, top, w, top + ch))
        kb = save(im, os.path.join(dst, "cover.webp"))
        total += kb
        written.append("cover.webp")
        print("cover.webp", im.size, kb, "KB")

    for f in sorted(glob.glob(os.path.join(src, "gallery-*.*"))):
        if os.path.splitext(f)[1].lower() not in (".png", ".jpg", ".jpeg", ".webp"):
            continue
        name = re.sub(r"^gallery-", "", os.path.splitext(os.path.basename(f))[0]) + ".webp"
        im = Image.open(f).convert("RGB")
        kb = save(im, os.path.join(dst, name))
        total += kb
        written.append(name)
        print(name, im.size, kb, "KB")

    if not written:
        raise SystemExit("no thumbnail.png or gallery-*.png found in " + src)
    print("total", total, "KB\n\n    images:  [")
    print(",\n".join('      "assets/projects/%s/%s"' % (slug, n) for n in written))
    print("    ],")


if __name__ == "__main__":
    main()
