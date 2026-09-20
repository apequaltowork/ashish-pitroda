"""
The bits both page generators need — make-learn.py and make-fixes.py.

A generated page is written with empty @chrome markers; `node build.js` fills
in the head, the header and the footer, and adds the canonical link and the
share tags. Nothing here writes chrome itself.
"""
import io
import json
import os

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = "https://apequaltowork.github.io/ashish-pitroda/"

# the page skeleton: markers for build.js, and the two scripts every page needs
# (without them the reveals never run and the page renders blank)
CHROME = '<!-- @chrome head -->\n<!-- @end head -->\n</head>\n<body{body}>\n\n<!-- @chrome top -->\n<!-- @end top -->\n'
FOOT = ('<!-- @chrome foot -->\n  <!-- @end foot -->\n\n</main>\n\n'
        '<script src="../journal.js"></script>\n<script src="../bird.js"></script>\n'
        "</body>\n</html>\n")

ARROW = '<svg viewBox="0 0 18 12" aria-hidden="true"><path d="M1 6 H16 M11 1 L16 6 L11 11"/></svg>'
BACK = '<svg viewBox="0 0 22 12" aria-hidden="true"><path d="M21 6H1M6 1 1 6l5 5"/></svg>'
RULE = ('<svg class="hero__line ink" data-reveal data-perch="mid" data-perch-first style="--d:.2s" '
        'viewBox="0 0 640 16" preserveAspectRatio="none" aria-hidden="true">'
        '<path pathLength="1" d="M3 10 C 110 4, 220 13, 330 8 S 540 5, 637 9"/></svg>')


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def head(title, desc, extra="", body_class=""):
    """The top of a page, up to and including the header's markers."""
    return ('<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            "<title>" + title + "</title>\n"
            '<meta name="description" content="' + desc + '">\n'
            "<!-- @chrome seo -->\n<!-- @end seo -->\n" + extra +
            CHROME.format(body=' class="' + body_class + '"' if body_class else ""))


def embed(video, title):
    """A YouTube player, full width of the text column. nocookie: no tracking
    until the visitor actually presses play."""
    return ('    <figure class="tube" data-reveal data-perch>\n'
            '      <div><iframe src="https://www.youtube-nocookie.com/embed/' + video + '" '
            'title="' + esc(title) + '" loading="lazy" allowfullscreen\n'
            '        allow="accelerometer; clipboard-write; encrypted-media; gyroscope; '
            'picture-in-picture"></iframe></div>\n    </figure>\n')


def ld(obj):
    """One schema.org block, for search engines."""
    return '<script type="application/ld+json">' + json.dumps(obj).replace("<", "\\u003c") + "</script>\n"


def thumbnail(src, out_dir, name, width=960):
    """Copy a thumbnail in as WebP (for the page) and JPEG (for link previews).
    Returns False if Pillow or the source file is missing, and the card then
    falls back to a plain block."""
    try:
        from PIL import Image
    except ImportError:
        print("no Pillow — thumbnails skipped")
        return False
    if not os.path.exists(src):
        return False
    out = os.path.join(ROOT, out_dir)
    os.makedirs(out, exist_ok=True)
    img = Image.open(src).convert("RGB")
    img = img.resize((width, int(width * img.height / img.width)), Image.LANCZOS)
    img.save(os.path.join(out, name + ".webp"), "WEBP", quality=82, method=6)
    img.save(os.path.join(out, name + ".jpg"), "JPEG", quality=84, optimize=True)
    return True


def write(rel, html):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    io.open(path, "w", encoding="utf-8", newline="").write(html)
    print(rel)


def upload_date(video):
    """The real upload date from the YouTube watch page. Returns None if it
    cannot be read — better a missing field than an invented one."""
    import re
    import urllib.request
    req = urllib.request.Request("https://www.youtube.com/watch?v=" + video,
                                 headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "en"})
    try:
        page = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "replace")
    except Exception as e:                                    # offline, or YouTube says no
        print("could not read the upload date for " + video + ": " + str(e))
        return None
    m = re.search(r'itemprop="uploadDate" content="([^"]+)"', page)
    return m.group(1) if m else None
