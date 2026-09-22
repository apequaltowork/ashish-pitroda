"""
Write the Fixes pages from the fix folders.

    python tools/make-fixes.py          then: node build.js

Each fix is a folder under SOURCE with a README.md in the shape of
_template.md there: a block of fields between --- lines, then the sections
that become the page. Nothing is invented here — a field left blank is a
part of the page that is simply not written.

    D:/portfolio/fixes/0001-some-slug/README.md   ->   fixes/0001-some-slug.html
    D:/portfolio/fixes/0001-some-slug/thumb.png   ->   assets/fixes/0001-some-slug.webp

Run this, then `node build.js`, which puts the shared header and footer in and
writes the canonical link, the share tags and both sitemaps.
"""
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from journal_pages import (ARROW, BACK, FOOT, ROOT, RULE, SITE, embed, esc, head, ld,  # noqa: E402
                           thumbnail, upload_date, write, youtube_thumb)

# one line to change if the folder moves; FIXES_DIR overrides it for a dry run
SOURCE = os.environ.get("FIXES_DIR") or "D:/portfolio/fixes"
OUT = "fixes"
SECTION = {
    "title": "Fixes",
    "blurb": "Problems I have run into, or watched other people get stuck on, "
             "solved and written down: the symptom, the actual cause, and the fix.",
}
FIELDS = ("title", "topic", "date", "updated", "video", "source", "service", "summary",
          "search_title")


# ── reading a fix ──────────────────────────────────────────────

def parse(text):
    """The fields between the --- lines, and everything after them as the body.
    A field can run onto indented lines below it; `video` can list several."""
    m = re.search(r"^---\s*$(.*?)^---\s*$(.*)", text, re.S | re.M)
    if not m:
        raise SystemExit("no --- field block found")
    fields, key = {}, None
    for line in m.group(1).splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        head_m = re.match(r"^([a-z_]+):\s*(.*)$", line)
        if head_m:
            key = head_m.group(1)
            fields[key] = head_m.group(2).split(" #")[0].strip()
        elif key:                                  # a wrapped value
            fields[key] = (fields[key] + " " + line.strip()).strip()
    return fields, m.group(2).strip()


# ── Markdown, the part these write-ups use ─────────────────────
# Headings, paragraphs, lists, fenced code, tables, rules, images, links,
# `code`, **bold** and *italic*. Relative links and images are resolved
# against the original document, so nothing points at a file that is not here.

def slug_id(text):
    return re.sub(r"[^a-z0-9]+", "-", re.sub(r"<[^>]+>", "", text).lower()).strip("-")[:60]


def spans(s):
    """`code`, **bold** and *italic*. Code is set aside first, so bold may hold
    code (**deleted by `migrate`**) and nothing inside code is ever touched."""
    codes = []

    def keep(m):
        codes.append("<code>" + esc(m.group(1)) + "</code>")
        return "\x00" + str(len(codes) - 1) + "\x00"
    t = esc(re.sub(r"`([^`]+)`", keep, s))
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<![\w*])\*([^*\n]+?)\*(?![\w*])", r"<i>\1</i>", t)
    return re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], t)


def inline(s, link=lambda u: u):
    # Links are set aside first: their text may be `code` ([`notes/X.md`](...)),
    # and bold may wrap a whole link (**[the repo](...)**).
    links = []

    def keep(m):
        links.append('<a href="' + esc(link(m.group(2))) + '">' + spans(m.group(1)) + "</a>")
        return "\x01" + str(len(links) - 1) + "\x01"
    t = spans(re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", keep, s))
    return re.sub(r"\x01(\d+)\x01", lambda m: links[int(m.group(1))], t)


def table(rows, link):
    cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
    th = "".join("<th>" + inline(c, link) + "</th>" for c in cells[0])
    trs = "".join("<tr>" + "".join("<td>" + inline(c, link) + "</td>" for c in r) + "</tr>"
                  for r in cells[2:])
    return ('<div class="prose__table"><table><thead><tr>' + th + "</tr></thead><tbody>" +
            trs + "</tbody></table></div>")


LIST = re.compile(r"^(\s*)([-*]|\d+\.)\s+(.*)$")


def md(text, link=lambda u: u, image=lambda src, alt: None):
    lines, out, para, i = text.splitlines(), [], [], 0

    def flush():
        if para:
            out.append("<p>" + inline(" ".join(para), link) + "</p>")
            del para[:]

    while i < len(lines):
        line, s = lines[i], lines[i].strip()
        if re.match(r"^\s*```[\w+-]*\s*$", line):            # a fenced block
            flush()
            buf, i = [], i + 1
            while i < len(lines) and not re.match(r"^\s*```\s*$", lines[i]):
                buf.append(lines[i])
                i += 1
            i += 1
            pad = min((len(l) - len(l.lstrip()) for l in buf if l.strip()), default=0)
            out.append("<pre><code>" + esc("\n".join(l[pad:] for l in buf)) + "</code></pre>")
            continue
        if not s:
            flush()
            i += 1
            continue
        h = re.match(r"^(#{1,4})\s+(.*)$", s)
        if h:                                                 # the page has its own h1
            flush()
            tag = "h2" if len(h.group(1)) <= 2 else "h" + str(len(h.group(1)))
            txt = inline(h.group(2), link)
            out.append("<" + tag + ' id="' + slug_id(txt) + '">' + txt + "</" + tag + ">")
            i += 1
            continue
        if re.match(r"^(-{3,}|\*{3,})$", s):
            flush()
            out.append("<hr>")
            i += 1
            continue
        img = re.match(r"^!\[([^\]]*)\]\(([^)\s]+)\)$", s)
        if img:
            flush()
            got = image(img.group(2), img.group(1))
            if got:                                           # never a broken picture
                src, w, hh = got
                out.append('<figure class="prose__fig"><img src="' + esc(src) + '" width="' +
                           str(w) + '" height="' + str(hh) + '" loading="lazy" alt="' +
                           esc(img.group(1)) + '"><figcaption>' + inline(img.group(1), link) +
                           "</figcaption></figure>")
            i += 1
            continue
        if s.startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-{2,}", lines[i + 1]):
            flush()
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i])
                i += 1
            out.append(table(rows, link))
            continue
        lm = LIST.match(line)
        if lm:
            flush()
            ordered = lm.group(2)[0].isdigit()
            items = []
            while i < len(lines):
                mm = LIST.match(lines[i])
                if mm and mm.group(2)[0].isdigit() == ordered:
                    items.append(mm.group(3))
                elif (lines[i].strip() and lines[i][:1] in " \t" and items
                      and not re.match(r"^\s*```", lines[i])):
                    items[-1] += " " + lines[i].strip()       # a wrapped item
                else:
                    break
                i += 1
            first = int(lm.group(2)[:-1]) if ordered else 1
            tag = "ol" if ordered else "ul"
            start = ' start="' + str(first) + '"' if ordered and first != 1 else ""
            out.append("<" + tag + start + ">" +
                       "".join("<li>" + inline(x, link) + "</li>" for x in items) +
                       "</" + tag + ">")
            continue
        para.append(s)
        i += 1
    flush()
    return "\n      ".join(out)


def raw_url(url):
    """github.com/<u>/<r>/blob/<ref>/<path> -> raw.githubusercontent.com/<u>/<r>/<ref>/<path>"""
    m = re.match(r"https://github\.com/([^/]+)/([^/]+)/blob/(.+)$", url or "")
    return "https://raw.githubusercontent.com/%s/%s/%s" % m.groups() if m else url


def load():
    """Every fix folder, newest date first."""
    fixes = []
    for name in sorted(os.listdir(SOURCE)):
        folder = os.path.join(SOURCE, name)
        readme = os.path.join(folder, "README.md")
        if name.startswith("_") or not os.path.exists(readme):
            continue
        fields, body = parse(io.open(readme, encoding="utf-8").read())
        if not fields.get("title") or not fields.get("date"):
            print("skipped " + name + ": it needs at least a title and a date")
            continue
        videos = re.findall(r"(?:v=|youtu\.be/|embed/)([\w-]{11})", fields.get("video") or "")
        fixes.append({
            "slug": name, "fields": fields, "body": body, "folder": folder,
            "videos": videos, "video": videos[0] if videos else "",
            "thumb": os.path.join(folder, "thumb.png"),
        })
    fixes.sort(key=lambda f: f["fields"]["date"], reverse=True)
    return fixes


# ── writing the pages ──────────────────────────────────────────

def nice_date(iso):
    import datetime
    try:
        d = datetime.date(*[int(x) for x in iso.split("-")])
    except ValueError:
        return iso
    return d.strftime("%d %B %Y").lstrip("0")


def row(fix, has_video):
    """One line in the list: topic, date, the question, a little of the answer,
    and the link through. data-fix is what the search box reads."""
    f = fix["fields"]
    hay = " ".join([f["title"], f.get("summary", ""), f.get("topic", ""),
                    nice_date(f["date"])])
    return ('      <li class="qrow" data-fix="' + esc(hay.lower()) + '">\n'
            '        <p class="qrow__meta"><span class="qrow__tag">' +
            esc(f.get("topic", "Fix")) + "</span>"
            '<time datetime="' + esc(f["date"]) + '">' + nice_date(f["date"]) + "</time>" +
            ('<span class="qrow__film" title="This one has a video">with video</span>'
             if has_video else "") + "</p>\n"
            '        <h2 class="qrow__h"><a href="' + fix["slug"] + '.html">' +
            esc(f["title"]) + "</a></h2>\n" +
            ('        <p class="qrow__p">' + esc(f["summary"]) + "</p>\n"
             if f.get("summary") else "") +
            '        <p class="qrow__more"><a href="' + fix["slug"] + '.html">read the fix'
            '<svg viewBox="0 0 18 12" aria-hidden="true">'
            '<path d="M1 6 H16 M11 1 L16 6 L11 11"/></svg></a></p>\n'
            "      </li>")


def oembed_title(video):
    import json
    import urllib.request
    try:
        return json.loads(urllib.request.urlopen(
            "https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=" + video +
            "&format=json", timeout=20).read())["title"]
    except Exception:
        return ""


def fix_page(fix, has_thumb):
    import urllib.parse
    f, slug = fix["fields"], fix["slug"]
    title = f.get("search_title") or f["title"]
    origin = f.get("origin") or ""

    def link(u):
        if re.match(r"^(https?:|mailto:|#)", u) or not origin:
            return u
        return urllib.parse.urljoin(origin, u)

    def image(src, alt):
        """A picture in the write-up: the copy in the fix folder if there is one,
        otherwise fetched from beside the original, and stored on this site."""
        import io as _io
        import urllib.request
        from PIL import Image
        name = re.sub(r"[^a-z0-9]+", "-", os.path.splitext(os.path.basename(src))[0].lower())
        out_dir = os.path.join(ROOT, "assets", "fixes", slug)
        local = os.path.join(fix["folder"], src)
        try:
            if os.path.exists(local):
                img = Image.open(local)
            else:
                data = urllib.request.urlopen(urllib.parse.urljoin(raw_url(origin), src),
                                              timeout=30).read()
                img = Image.open(_io.BytesIO(data))
        except Exception as e:
            print("  picture skipped, could not read " + src + ": " + str(e))
            return None
        img = img.convert("RGB")
        if img.width > 1400:
            img = img.resize((1400, int(1400 * img.height / img.width)), Image.LANCZOS)
        os.makedirs(out_dir, exist_ok=True)
        img.save(os.path.join(out_dir, name + ".webp"), "WEBP", quality=82, method=6)
        return "../assets/fixes/" + slug + "/" + name + ".webp", img.width, img.height

    prose = md(fix["body"], link, image)

    # every video after the first sits at the end, under its own YouTube title
    later = ""
    for v in fix["videos"][1:]:
        later += ('\n    <div class="prose" data-reveal>\n      <h2>On video: ' +
                  esc(fix["titles"].get(v) or "the other video") + "</h2>\n    </div>\n" +
                  embed(v, fix["titles"].get(v) or title))

    meta = [esc(f.get("topic", "Fix")), nice_date(f["date"])]
    if f.get("updated"):
        meta.append("updated " + nice_date(f["updated"]))
    kicker = ' <span aria-hidden="true">·</span> '.join(meta)

    links = []
    if f.get("source"):
        links.append('<a href="' + esc(f["source"]) + '">the discussion this came from</a>')
    if f.get("code"):
        links.append('<a href="' + esc(f["code"]) + '">the code, with every step</a>')
    if origin:
        links.append('<a href="' + esc(origin) + '">this write-up on GitHub</a>')
    for v in fix["videos"]:
        links.append('<a href="https://www.youtube.com/watch?v=' + v + '">' +
                     ("watch it on YouTube" if len(fix["videos"]) == 1 else
                      esc(fix["titles"].get(v) or "the video") + " — on YouTube") + "</a>")
    if f.get("service"):
        links.append('<a href="../' + esc(f["service"]) + '">the work I do on this</a>')

    body = ('\n<main class="page">\n\n  <article>\n    <header class="phead" id="top">\n'
            '      <a class="back" href="index.html">' + BACK + "All fixes</a>\n"
            '      <p class="hero__kicker" data-reveal>' + kicker + "</p>\n"
            '      <h1 class="phead__h" data-reveal style="--d:.08s">' + esc(f["title"]) + "</h1>\n"
            "      " + RULE + "\n" +
            ('      <p class="hero__lede" data-reveal style="--d:.3s">' + esc(f["summary"]) + "</p>\n"
             if f.get("summary") else "") +
            "    </header>\n\n" +
            (embed(fix["video"], fix["titles"].get(fix["video"]) or title) + "\n"
             if fix["video"] else "") +
            '    <div class="prose" data-reveal>\n      ' + prose + "\n    </div>\n" + later +
            "  </article>\n\n" +
            ('  <section class="sec">\n    <div class="prose" data-reveal>\n      <p>' +
             " · ".join(links) + "</p>\n    </div>\n  </section>\n\n" if links else "") +
            '  <section class="sec">\n    <div class="cta" data-reveal data-perch>\n      <div>\n'
            '        <p class="cta__h">Stuck on something like this?</p>\n'
            '        <p class="cta__p">Tell me what you have and what it is doing instead. '
            'I will tell you honestly whether I am the right person for it.</p>\n      </div>\n'
            '      <div>\n        <a class="btn" href="../contact.html"><span>Write to me</span>' +
            ARROW + "</a>\n"
            '        <a class="cta__alt" href="index.html">or read the other fixes</a>\n'
            "      </div>\n    </div>\n  </section>\n\n  " + FOOT)

    article = {
        "@context": "https://schema.org", "@type": "TechArticle",
        "headline": title, "datePublished": f["date"],
        "dateModified": f.get("updated") or f["date"],
        "author": {"@type": "Person", "name": "Ashish Pitroda", "url": SITE},
        "publisher": {"@type": "Person", "name": "Ashish Pitroda", "url": SITE},
        "mainEntityOfPage": SITE + OUT + "/" + slug + ".html",
    }
    if f.get("topic"):
        article["about"] = f["topic"]
    if f.get("summary"):
        article["description"] = f["summary"]
    if has_thumb:
        article["image"] = SITE + "assets/fixes/" + slug + ".jpg"

    schema = ld(article) + ld({
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE},
            {"@type": "ListItem", "position": 2, "name": SECTION["title"], "item": SITE + OUT + "/"},
            {"@type": "ListItem", "position": 3, "name": f["title"],
             "item": SITE + OUT + "/" + slug + ".html"},
        ],
    })
    for v in fix["videos"]:
        video = {
            "@context": "https://schema.org", "@type": "VideoObject",
            "name": fix["titles"].get(v) or title,
            "description": f.get("summary") or f["title"],
            "thumbnailUrl": "https://i.ytimg.com/vi/" + v + "/maxresdefault.jpg",
            "embedUrl": "https://www.youtube.com/embed/" + v,
            "contentUrl": "https://www.youtube.com/watch?v=" + v,
            "author": {"@type": "Person", "name": "Ashish Pitroda", "url": SITE},
        }
        if fix["uploaded"].get(v):
            video["uploadDate"] = fix["uploaded"][v]
        schema += ld(video)

    desc = (f.get("summary") or f["title"]).replace('"', "&quot;")[:155]
    return head(title + " — " + SECTION["title"], desc, schema, "learn") + body


def waiting_page():
    """The section before the first fix is written: it says plainly that
    nothing is here yet, and what will be. No invented fixes. It is indexable
    so the address is known early; Google may well hold it back until there
    is something to read, which is fine."""
    body = ('\n<main class="page">\n\n  <section class="phead" id="top">\n'
            '    <a class="back" href="../index.html">' + BACK + "Back to the journal</a>\n"
            '    <p class="hero__kicker" data-reveal>Solved problems, written down</p>\n'
            '    <h1 class="phead__h" data-reveal style="--d:.08s">' + SECTION["title"] + "</h1>\n"
            "    " + RULE + "\n"
            '    <p class="hero__lede" data-reveal style="--d:.3s">' + SECTION["blurb"] + "</p>\n"
            '    <p class="hand" data-reveal style="--d:.55s">— the first one is being written</p>\n'
            "  </section>\n\n"
            '  <section class="sec">\n    <div class="prose" data-reveal>\n'
            "      <h2>What will be here</h2>\n"
            "      <p>Errors that people are genuinely stuck on, taken apart properly: what you "
            "see, why it actually happens, and the fix — with the commands and the code. Some "
            "will come with a video walking through it.</p>\n"
            "      <p>Nothing is posted here until it is real and it works, so the page is empty "
            "rather than padded.</p>\n"
            '      <p>In the meantime, <a href="../learn/index.html">Wagtail Unboxed</a> is a '
            "video series that builds a Wagtail site from an empty folder and explains every "
            "file on the way.</p>\n    </div>\n  </section>\n\n"
            '  <section class="sec">\n    <div class="cta" data-reveal data-perch>\n      <div>\n'
            '        <p class="cta__h">Stuck on something?</p>\n'
            '        <p class="cta__p">If you are staring at an error nobody seems to have '
            "written up, tell me about it. It may well end up here.</p>\n      </div>\n"
            '      <div>\n        <a class="btn" href="../contact.html"><span>Write to me</span>' +
            ARROW + "</a>\n      </div>\n    </div>\n  </section>\n\n  " + FOOT)
    return head(SECTION["title"] + " — errors solved and written up, by Ashish Pitroda",
                "Solved problems, written up: the symptom, the actual cause, and the fix. "
                "The first one is being written.", "", "learn") + body


def index_page(fixes, thumbs):
    rows = "\n".join(row(fx, bool(fx["video"])) for fx in fixes)
    body = ('\n<main class="page">\n\n  <section class="phead" id="top">\n'
            '    <a class="back" href="../index.html">' + BACK + "Back to the journal</a>\n"
            '    <p class="hero__kicker" data-reveal>Solved problems, written down</p>\n'
            '    <h1 class="phead__h" data-reveal style="--d:.08s">' + SECTION["title"] + "</h1>\n"
            "    " + RULE + "\n"
            '    <p class="hero__lede" data-reveal style="--d:.3s">' + SECTION["blurb"] + "</p>\n"
            "  </section>\n\n"
            # the whole list is in the page; fixes.js filters and pages it
            '  <section class="sec sec--eps" id="list">\n'
            '    <form class="qfind" role="search" data-reveal>\n'
            '      <label for="q">Search the fixes</label>\n'
            '      <input id="q" type="search" name="q" data-fix-search autocomplete="off"\n'
            '        placeholder="an error, a word from it, or a topic">\n'
            '      <span class="qfind__n" data-fix-count>' + str(len(fixes)) +
            (" fix" if len(fixes) == 1 else " fixes") + "</span>\n    </form>\n\n"
            '    <ul class="qlist" data-fixes data-per="10" data-reveal>\n' + rows +
            "\n    </ul>\n\n"
            '    <p class="qfind__none" data-fix-empty hidden>Nothing here matches that. '
            'Try fewer words, or the error text itself.</p>\n'
            '    <nav class="qpager" data-fix-pager aria-label="More fixes" hidden></nav>\n'
            "  </section>\n\n"
            '  <section class="sec">\n    <div class="cta" data-reveal data-perch>\n      <div>\n'
            '        <p class="cta__h">Stuck on something?</p>\n'
            '        <p class="cta__p">If you are staring at an error that nobody seems to have '
            'written up, tell me about it.</p>\n      </div>\n      <div>\n'
            '        <a class="btn" href="../contact.html"><span>Write to me</span>' + ARROW +
            "</a>\n      </div>\n    </div>\n  </section>\n\n  " +
            FOOT.replace('<script src="../journal.js">',
                         '<script src="../fixes.js"></script>\n<script src="../journal.js">'))

    schema = ld({
        "@context": "https://schema.org", "@type": "CollectionPage",
        "name": SECTION["title"], "description": SECTION["blurb"], "url": SITE + OUT + "/",
        "author": {"@type": "Person", "name": "Ashish Pitroda", "url": SITE},
        "mainEntity": {
            "@type": "ItemList",
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": fx["fields"]["title"],
                 "url": SITE + OUT + "/" + fx["slug"] + ".html"}
                for i, fx in enumerate(fixes)],
        },
    })
    return head(SECTION["title"] + " — errors solved and written up, by Ashish Pitroda",
                "Solved problems, written up: the symptom, the actual cause, and the fix. "
                "Wagtail, Django, Python and whatever else broke.", schema, "learn") + body


def main():
    fixes = load() if os.path.isdir(SOURCE) else []
    if not fixes:
        write(OUT + "/index.html", waiting_page())
        print("\nno fixes written yet, so the section says so. Start from "
              + SOURCE + "/_template.md")
        print("now run: node build.js")
        return
    thumbs = set()
    for fx in fixes:
        # thumb.png if you made one, otherwise the video's own thumbnail
        got = thumbnail(fx["thumb"], "assets/fixes", fx["slug"])
        if not got and fx["video"]:
            got = youtube_thumb(fx["video"], "assets/fixes", fx["slug"])
        if got:
            thumbs.add(fx["slug"])
        fx["titles"] = {v: oembed_title(v) for v in fx["videos"]}
        fx["uploaded"] = {v: upload_date(v) for v in fx["videos"]}
    write(OUT + "/index.html", index_page(fixes, thumbs))
    for fx in fixes:
        write(OUT + "/" + fx["slug"] + ".html", fix_page(fx, fx["slug"] in thumbs))
    print("\nnow run: node build.js")
    print("and register these in PAGES in build.js if they are new")


if __name__ == "__main__":
    main()
