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
from journal_pages import (ARROW, BACK, FOOT, RULE, SITE, embed, esc, head, ld,  # noqa: E402
                           thumbnail, upload_date, write)

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
    """The fields between the --- lines, then the sections after them."""
    m = re.search(r"^---\s*$(.*?)^---\s*$(.*)", text, re.S | re.M)
    if not m:
        raise SystemExit("no --- field block found")
    fields, body = {}, m.group(2)
    key = None
    for line in m.group(1).splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        head_m = re.match(r"^([a-z_]+):\s*(.*)$", line)
        if head_m:
            key = head_m.group(1)
            fields[key] = head_m.group(2).split("#")[0].strip()
        elif key:                                  # a wrapped value
            fields[key] = (fields[key] + " " + line.strip()).strip()
    sections = []
    for sm in re.finditer(r"^## +(.+?)\s*$(.*?)(?=^## |\Z)", body, re.S | re.M):
        sections.append((sm.group(1).strip(), sm.group(2).strip()))
    return fields, sections


def md(text):
    """The small part of Markdown these notes use: fenced code, ordered and
    unordered lists, paragraphs, links, `code` and **bold**."""
    out, i = [], 0
    # a fence may be indented, because steps often carry their own code
    blocks = re.split(r"^[ \t]*```[a-zA-Z0-9+-]*[ \t]*$", text, flags=re.M)
    for i, block in enumerate(blocks):
        if i % 2:                                    # inside a fence
            lines = [l for l in block.strip("\n").splitlines()]
            pad = min((len(l) - len(l.lstrip()) for l in lines if l.strip()), default=0)
            out.append("<pre><code>" + esc("\n".join(l[pad:] for l in lines)) + "</code></pre>")
            continue
        for para in re.split(r"\n\s*\n", block):
            para = para.strip()
            if not para:
                continue
            lines = para.splitlines()
            if all(re.match(r"^\d+\.\s", l.strip()) for l in lines):
                items = [re.sub(r"^\d+\.\s", "", l.strip()) for l in lines]
                # steps carry on across the code blocks between them, so the
                # list starts at the number actually written
                first = int(re.match(r"^\s*(\d+)\.", lines[0]).group(1))
                start = ' start="' + str(first) + '"' if first != 1 else ""
                out.append("<ol" + start + ">" +
                           "".join("<li>" + inline(x) + "</li>" for x in items) + "</ol>")
            elif all(l.strip().startswith(("- ", "* ")) for l in lines):
                items = [l.strip()[2:] for l in lines]
                out.append("<ul>" + "".join("<li>" + inline(x) + "</li>" for x in items) + "</ul>")
            else:
                out.append("<p>" + inline(" ".join(l.strip() for l in lines)) + "</p>")
    return "\n      ".join(out)


def inline(s):
    s = esc(s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    return re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)


def load():
    """Every fix folder, newest date first."""
    if not os.path.isdir(SOURCE):
        raise SystemExit("no fix folders yet: " + SOURCE)
    fixes = []
    for name in sorted(os.listdir(SOURCE)):
        folder = os.path.join(SOURCE, name)
        readme = os.path.join(folder, "README.md")
        if name.startswith("_") or not os.path.exists(readme):
            continue
        fields, sections = parse(io.open(readme, encoding="utf-8").read())
        if not fields.get("title") or not fields.get("date"):
            print("skipped " + name + ": it needs at least a title and a date")
            continue
        video = fields.get("video") or ""
        vid = re.search(r"(?:v=|youtu\.be/|embed/)([\w-]{11})", video)
        fixes.append({
            "slug": name, "fields": fields, "sections": sections,
            "video": vid.group(1) if vid else "",
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


def card(i, fix, has_thumb):
    f = fix["fields"]
    fig = ('        <span class="ep__fig">' +
           ('<img src="../assets/fixes/' + fix["slug"] + '.webp" width="960" height="540" '
            'loading="lazy" alt="Thumbnail for: ' + esc(f["title"]) + '">'
            '<span class="ep__play" aria-hidden="true"></span>'
            if has_thumb else
            '<span class="ep__plain" aria-hidden="true">' + esc(f.get("topic", "")) + "</span>") +
           "</span>\n")
    return ('      <li><a class="ep" href="' + fix["slug"] + '.html" data-reveal '
            'style="--d:.' + str(i + 2) + 's">\n' + fig +
            '        <span class="ep__body">\n'
            '          <span class="ep__no">' + esc(f.get("topic", "Fix")) +
            ' <span aria-hidden="true">·</span> ' + nice_date(f["date"]) + "</span>\n"
            '          <span class="ep__h">' + esc(f["title"]) + "</span>\n" +
            ('          <span class="ep__p">' + esc(f["summary"]) + "</span>\n"
             if f.get("summary") else "") +
            "        </span>\n      </a></li>")


def fix_page(fix, has_thumb):
    f, slug = fix["fields"], fix["slug"]
    title = f.get("search_title") or f["title"]
    prose = []
    for heading, body in fix["sections"]:
        prose.append("      <h2>" + esc(heading) + "</h2>\n      " + md(body))

    meta = [esc(f.get("topic", "Fix")), nice_date(f["date"])]
    if f.get("updated"):
        meta.append("updated " + nice_date(f["updated"]))
    kicker = ' <span aria-hidden="true">·</span> '.join(meta)

    links = []
    if f.get("source"):
        links.append('<a href="' + esc(f["source"]) + '">the discussion this came from</a>')
    if f.get("video"):
        links.append('<a href="' + esc(f["video"]) + '">watch it on YouTube</a>')
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
            (embed(fix["video"], title) + "\n" if fix["video"] else "") +
            '    <div class="prose" data-reveal>\n' + "\n\n".join(prose) + "\n    </div>\n"
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
    if fix["video"]:
        video = {
            "@context": "https://schema.org", "@type": "VideoObject",
            "name": title, "description": f.get("summary") or f["title"],
            "thumbnailUrl": "https://i.ytimg.com/vi/" + fix["video"] + "/maxresdefault.jpg",
            "embedUrl": "https://www.youtube.com/embed/" + fix["video"],
            "contentUrl": "https://www.youtube.com/watch?v=" + fix["video"],
            "author": {"@type": "Person", "name": "Ashish Pitroda", "url": SITE},
        }
        when = fix.get("uploaded")
        if when:
            video["uploadDate"] = when
        schema += ld(video)

    desc = (f.get("summary") or f["title"]).replace('"', "&quot;")[:155]
    return head(title + " — " + SECTION["title"], desc, schema, "learn") + body


def index_page(fixes, thumbs):
    cards = "\n".join(card(i, fx, fx["slug"] in thumbs) for i, fx in enumerate(fixes))
    body = ('\n<main class="page">\n\n  <section class="phead" id="top">\n'
            '    <a class="back" href="../index.html">' + BACK + "Back to the journal</a>\n"
            '    <p class="hero__kicker" data-reveal>Solved problems, written down</p>\n'
            '    <h1 class="phead__h" data-reveal style="--d:.08s">' + SECTION["title"] + "</h1>\n"
            "    " + RULE + "\n"
            '    <p class="hero__lede" data-reveal style="--d:.3s">' + SECTION["blurb"] + "</p>\n"
            '    <p class="hand" data-reveal style="--d:.55s">— ' + str(len(fixes)) +
            (" fix" if len(fixes) == 1 else " fixes") + " so far</p>\n  </section>\n\n"
            '  <section class="sec sec--eps">\n    <ol class="eps">\n' + cards +
            "\n    </ol>\n  </section>\n\n"
            '  <section class="sec">\n    <div class="cta" data-reveal data-perch>\n      <div>\n'
            '        <p class="cta__h">Stuck on something?</p>\n'
            '        <p class="cta__p">If you are staring at an error that nobody seems to have '
            'written up, tell me about it.</p>\n      </div>\n      <div>\n'
            '        <a class="btn" href="../contact.html"><span>Write to me</span>' + ARROW +
            "</a>\n      </div>\n    </div>\n  </section>\n\n  " + FOOT)

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
    fixes = load()
    if not fixes:
        raise SystemExit("no fixes yet — nothing written. Start from " + SOURCE + "/_template.md")
    thumbs = set()
    for fx in fixes:
        if thumbnail(fx["thumb"], "assets/fixes", fx["slug"]):
            thumbs.add(fx["slug"])
        if fx["video"]:
            fx["uploaded"] = upload_date(fx["video"])
    write(OUT + "/index.html", index_page(fixes, thumbs))
    for fx in fixes:
        write(OUT + "/" + fx["slug"] + ".html", fix_page(fx, fx["slug"] in thumbs))
    print("\nnow run: node build.js")
    print("and register these in PAGES in build.js if they are new")


if __name__ == "__main__":
    main()
