"""
Add Wagtail Unboxed episodes to the site straight from their YouTube links.

    python tools/import-episode.py <youtube link> [<youtube link> ...]
    python tools/make-learn.py
    node build.js

For each link it finds the episode folder whose README.md records that link,
checks the video is public and embeddable, reads the real upload date from the
YouTube watch page, and writes an EPISODES block into tools/make-learn.py and
a PAGES line into build.js. Everything on the page comes from the README —
the description, the "what you'll learn" list, the chapters, the git tag.
Nothing is invented; a link with no matching README is refused.
"""
import io
import json
import os
import re
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from journal_pages import ROOT, esc, upload_date  # noqa: E402

SOURCE = "D:/django/wagtail-unboxed/youtube"
LEARN = os.path.join(ROOT, "tools", "make-learn.py")
BUILD = os.path.join(ROOT, "build.js")

# words that look like code by shape but are ordinary names
NOT_CODE = {"YouTube", "JavaScript", "PostgreSQL", "GitHub", "LinkedIn", "WordPress", "StreamField"}


def vid(link):
    m = re.search(r"(?:v=|youtu\.be/|embed/)([\w-]{11})", link)
    if not m:
        raise SystemExit("not a YouTube link: " + link)
    return m.group(1)


def youtube_title(video):
    """The title YouTube has for it, and proof it is public and embeddable."""
    url = "https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=" + video + "&format=json"
    try:
        return json.loads(urllib.request.urlopen(url, timeout=20).read())["title"]
    except Exception:
        raise SystemExit(video + " is not public and embeddable (oembed refused it)")


def folder_for(video):
    for name in sorted(os.listdir(SOURCE)):
        readme = os.path.join(SOURCE, name, "README.md")
        if os.path.exists(readme) and video in io.open(readme, encoding="utf-8").read():
            return name, io.open(readme, encoding="utf-8").read()
    raise SystemExit("no episode README records " + video + " — add the URL to it first")


def codeify(text):
    """Escape, then set identifiers in code type: calls, dotted paths,
    snake_case and CamelCase names."""
    text = esc(text)

    def wrap(m):
        w = m.group(0)
        return w if w in NOT_CODE else "<code>" + w + "</code>"
    pattern = (r"\b[\w.]+\(\)"                         # in_menu()
               r"|\b[a-z]\w*(?:\.[A-Za-z_]\w*)+\b"      # wagtail.contrib.settings
               r"|\b[a-z]+_[a-z0-9_]+\b"                 # show_in_menus
               r"|\b[A-Z][a-z]+[A-Z]\w*\b")              # BaseSiteSetting
    return re.sub(pattern, wrap, text)


def sentence_case(h1):
    t = h1.split("—", 1)[-1].strip().replace("&", "and")
    words = t.split()
    return " ".join([words[0]] + [w if w.isupper() else w.lower() for w in words[1:]])


def slugify(no, title):
    return no + "-" + re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def parse(no, readme):
    runtime = re.search(r"\*\*Runtime\*\*\s*\|\s*(\d+):(\d{2})", readme)
    tag = re.search(r"`(ep\d+-end)`", readme)
    desc = re.search(r"## Description\s*```(.*?)```", readme, re.S).group(1)
    before, _, after = desc.partition("WHAT YOU'LL LEARN")
    intro = [" ".join(p.split()) for p in re.split(r"\n\s*\n", before.strip()) if p.strip()]
    bullets = [l.strip()[2:].strip() for l in after.splitlines() if l.strip().startswith("• ")]
    # paragraphs after the list and before the first link line are part of the story
    tail = after.split("📋")[0]
    tail = "\n".join(l for l in tail.splitlines() if not l.strip().startswith("• "))
    extra = [" ".join(p.split()) for p in re.split(r"\n\s*\n", tail.strip()) if p.strip()]
    chapters = re.findall(r"^(\d+:\d{2}) (.+)$", desc, re.M)
    commands = "youtube/ep" + no + "/commands.md"
    return {
        "runtime": runtime.group(1) + ":" + runtime.group(2),
        "iso": "PT" + str(int(runtime.group(1))) + "M" + str(int(runtime.group(2))) + "S",
        "lede": intro[0], "covers": intro[1:] + extra, "learn": bullets,
        "chapters": chapters, "tag": tag.group(1) if tag else None,
        "commands": commands if os.path.exists(os.path.join(SOURCE, "ep" + no, "commands.md")) else None,
    }


def block(ep):
    """An EPISODES entry, written out as Python in make-learn.py's own style."""
    r = repr
    lines = ["    {",
             '        "slug": ' + r(ep["slug"]) + ",",
             '        "no": ' + r(ep["no"]) + ",",
             '        "video": ' + r(ep["video"]) + ",",
             '        "uploaded": ' + r(ep["uploaded"]) + ",   # from the YouTube watch page",
             '        "runtime": ' + r(ep["runtime"]) + ",",
             '        "iso": ' + r(ep["iso"]) + ",",
             '        "title": ' + r(ep["title"]) + ",",
             '        "search_title": ' + r(ep["search_title"]) + ",",
             '        "lede": ' + r(esc(ep["lede"])) + ",",
             '        "covers": ['] + \
            ["            " + r(codeify(p)) + "," for p in ep["covers"]] + \
            ["        ],", '        "learn": ['] + \
            ["            " + r(codeify(b)) + "," for b in ep["learn"]] + \
            ["        ],", '        "prereq": False,', '        "chapters": ['] + \
            ["            (" + r(t) + ", " + r(n) + ")," for t, n in ep["chapters"]] + \
            ["        ],",
             '        "tag": ' + r(ep["tag"]) + ",",
             '        "commands": ' + r(ep["commands"]) + ",",
             "    },"]
    return "\n".join(lines) + "\n"


def main():
    links = sys.argv[1:]
    if not links:
        raise SystemExit(__doc__)
    learn_src = io.open(LEARN, encoding="utf-8").read()
    build_src = io.open(BUILD, encoding="utf-8").read()
    added = []
    for link in links:
        video = vid(link)
        if '"video": "' + video + '"' in learn_src:
            print("already on the site: " + video)
            continue
        yt = youtube_title(video)
        folder, readme = folder_for(video)
        no = folder[2:]
        ep = parse(no, readme)
        ep.update({
            "no": no, "video": video,
            "title": sentence_case(readme.splitlines()[0]),
            "search_title": re.split(r"\s+\|\s+Wagtail", yt)[0].strip(),
            "uploaded": upload_date(video),
        })
        if not ep["uploaded"]:
            raise SystemExit("could not read the upload date for " + video)
        ep["slug"] = slugify(no, ep["title"])
        learn_src = learn_src.replace("\n]\n\nVERSIONS", "\n" + block(ep) + "]\n\nVERSIONS", 1)
        page = '  { file: "learn/' + ep["slug"] + '.html",'
        if page not in build_src:
            # after the last episode line in PAGES, giving that line its comma
            last = re.findall(r'  \{ file: "learn/\d[^\n]*\n', build_src)[-1]
            prev = last.rstrip("\n")
            if not prev.endswith(","):
                prev += ","
            build_src = build_src.replace(
                last, prev + "\n" + page.ljust(54) + 'section: "learn" }\n', 1)
        added.append((no, ep["slug"], ep["runtime"], len(ep["chapters"])))
    if "\n]\n\nVERSIONS" not in io.open(LEARN, encoding="utf-8").read():
        raise SystemExit("could not find the end of EPISODES in make-learn.py")
    io.open(LEARN, "w", encoding="utf-8", newline="").write(learn_src)
    io.open(BUILD, "w", encoding="utf-8", newline="").write(build_src)
    for no, slug, rt, ch in added:
        print("added ep" + no + "  " + slug + "  " + rt + "  " + str(ch) + " chapters")
    print("\nnow run: python tools/make-learn.py && node build.js")


if __name__ == "__main__":
    main()
