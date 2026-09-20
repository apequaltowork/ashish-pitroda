"""
Write the Wagtail Unboxed pages under learn/ from the episode data below.

    python tools/make-learn.py

Every fact here — titles, runtimes, video ids, chapters — is copied from
D:/django/wagtail-unboxed/youtube/epNN/README.md. Nothing is invented: to add
episode 2, add a block to EPISODES and run this, then `node build.js` to put
the shared header and footer in. The pages are written with empty @chrome
markers for build.js to fill.
"""
import io
import os

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
REPO = "https://github.com/apequaltowork/wagtail-unbox"
CHANNEL = "https://www.youtube.com/@apequaltowork"
SITE = "https://apequaltowork.github.io/ashish-pitroda/"

SERIES = {
    "slug": "wagtail-unboxed",          # the series page is learn/<slug>/
    "title": "Wagtail Unboxed",
    "blurb": "Build a real Wagtail site from an empty folder — and understand every file in it.",
}

EPISODES = [
    {
        "slug": "00a-what-this-series-is",
        "no": "0a",
        "video": "ck4T3lnkhqs",
        "uploaded": "2026-09-16T10:35:40-07:00",   # from the YouTube watch page
        "runtime": "5:21",
        "iso": "PT5M21S",
        "title": "What this series is, and who it is for",
        "search_title": "What Is Wagtail CMS and Should You Learn It?",
        "lede": "The honest version of “is this series for you?” — what Wagtail is, who it is for, "
                "what you need to know first, and exactly what we are building.",
        "covers": [
            "Wagtail Unboxed is a build-along series: we open a brand new Wagtail project, read every "
            "single file it generates, and then build a real client site from it — pages, StreamField, "
            "a blog, snippets, navigation, a contact form, search, and a live deploy.",
            "This first episode sets expectations. It covers what Wagtail actually is, why it is not a "
            "fork of Django or a rival to it, and why a Django developer already knows most of what is "
            "coming. It also says plainly what the series is not.",
        ],
        "prereq": True,
        "chapters": [
            ("0:00", "The site we're building"), ("0:18", "What Wagtail actually is"),
            ("0:25", "Not a fork, not a rival"), ("0:48", "If you write Django, you know 70% of this"),
            ("0:57", "Who this series is for"), ("1:19", "What you need to know first"),
            ("1:48", "If you don't know Django yet"), ("2:08", "What is NOT required"),
            ("2:21", "A note for Mac and Linux viewers"), ("2:37", "The 14-episode roadmap"),
            ("2:50", "Act 1 — Unboxing"), ("3:08", "Act 2 — Building the site"),
            ("3:25", "Act 3 — Shipping it"), ("3:38", "How to follow along with the repo"),
            ("3:53", "Why the database isn't committed"), ("4:07", "What this series is NOT"),
            ("4:34", "Pinned versions"), ("4:56", "Next episode"),
        ],
        "tag": None,
        "commands": None,
    },
    {
        "slug": "00b-setting-up-your-machine",
        "no": "0b",
        "video": "7AtlyySq4l4",
        "uploaded": "2026-09-16T20:43:13-07:00",   # from the YouTube watch page
        "runtime": "4:48",
        "iso": "PT4M48S",
        "title": "Setting up your machine",
        "search_title": "Wagtail Setup: Install Python, Git and Virtualenv",
        "lede": "Short, skippable, and it shows the failure modes rather than only the happy path. "
                "Already have Python 3.12, git and a virtualenv habit? Skip to episode 1.",
        "covers": [
            "We install Python 3.12, git and an editor on Windows, macOS and Linux, then spend real "
            "time on virtual environments: what they actually are, why they matter, and the mistake "
            "that breaks people three episodes later — forgetting to activate in a new terminal.",
            "Two things we are deliberately not installing: Postgres, because episodes 1 to 12 use the "
            "SQLite that ships inside Python and Postgres arrives in episode 13; and Node.js, because "
            "there is no front-end build step in this series at any point.",
        ],
        "prereq": False,
        "chapters": [
            ("0:00", "Already set up? Skip this one"), ("0:18", "Four things, that's it"),
            ("0:30", "What we are NOT installing"), ("0:53", "Python 3.12 — Windows, macOS, Linux"),
            ("1:15", "The “Add to PATH” mistake"), ("1:34", "Check it worked"), ("1:53", "An editor"),
            ("2:11", "git"), ("2:30", "What a virtualenv actually is"), ("2:54", "Making one"),
            ("3:05", "The (.venv) prefix"), ("3:16", "The trap: new terminal, activate again"),
            ("3:37", "Windows: “running scripts is disabled”"), ("3:55", "Verify your starting line"),
            ("4:07", "No Wagtail yet — on purpose"), ("4:28", "Next episode"),
        ],
        "tag": None,
        "commands": "youtube/ep00b/commands.md",
    },
    {
        "slug": "01-what-wagtail-actually-is",
        "no": "01",
        "video": "X7FgE9j1XLY",
        "uploaded": "2026-09-16T22:51:37-07:00",   # from the YouTube watch page
        "runtime": "5:19",
        "iso": "PT5M19S",
        "title": "What Wagtail actually is",
        "search_title": "How to Install Wagtail and Create Your First Project",
        "lede": "We install Wagtail, create a project, and get a real CMS admin running — then stop, "
                "because episode 2 opens up every single file it generated.",
        "covers": [
            "First, the question nobody answers clearly: what is Wagtail? It is not an alternative to "
            "Django, it runs on Django. We compare it to plain Django, to the Django admin and to "
            "WordPress, and say where each one actually wins.",
            "Also covered: why you should never name a Django project “site”, because Python already "
            "has a module with that name; and why we pin both Wagtail and Django, since Wagtail 7.4 "
            "declares a minimum of Django 5.2 with no upper limit, so an unpinned install will not "
            "match what is on screen.",
            "No database to install. SQLite ships inside Python, and Postgres arrives in episode 13.",
        ],
        "prereq": False,
        "chapters": [
            ("0:00", "What you'll have by the end"), ("0:20", "Wagtail vs Django vs WordPress"),
            ("0:40", "But Django already has an admin?"), ("1:02", "The one-sentence version"),
            ("1:14", "A folder and a virtualenv"), ("1:35", "Installing Wagtail"),
            ("1:53", "Why pin Django too?"), ("2:14", "Creating the project"),
            ("2:20", "Those two arguments"), ("2:41", "Never name your project “site”"),
            ("3:04", "migrate — 184 migrations before you write any code"),
            ("3:21", "No database server"), ("3:40", "createsuperuser"), ("3:52", "Running it"),
            ("3:59", "The two addresses"), ("4:15", "One page already exists"),
            ("4:36", "git and the episode tag"), ("4:50", "Next episode"),
        ],
        "tag": "ep01-end",
        "commands": "youtube/ep01/commands.md",
    },
    {
        "slug": "02-every-file-explained",
        "no": "02",
        "video": "FoElBiKp_fI",
        "uploaded": "2026-09-17T09:59:52-07:00",   # from the YouTube watch page
        "runtime": "7:51",
        "iso": "PT7M51S",
        "title": "Opening the box: every file explained",
        "search_title": "Wagtail Project Structure Explained: Every File",
        "lede": "The wagtail start command generates 29 files. Most tutorials explain three of them. We read all "
                "of them, because the ones you are told to ignore decide how your site behaves.",
        "covers": [
            "The highlight is the data migration that quietly created your homepage. Nobody opens "
            "<code>0002_create_homepage.py</code>, and it explains the page tree, content types and "
            "Wagtail's multi-site model all at once, including why your homepage's database row has "
            "a path of <code>00010001</code>.",
            "Also covered: Wagtail is about eleven Django apps in <code>INSTALLED_APPS</code>, and that "
            "is the whole mental model; why the <code>wagtail_urls</code> catch-all must be the last "
            "URL pattern; <code>PROJECT_DIR</code> against <code>BASE_DIR</code>, and "
            "<code>STATIC_ROOT</code> against <code>STATICFILES_DIRS</code> against "
            "<code>MEDIA_ROOT</code>; the settings split into dev.py, production.py and the local.py "
            "escape hatch; two settings that ship as broken placeholders; and a real inconsistency, "
            "where the generated requirements.txt caps Django below 6.1 but pip installs 6.1.1.",
            "No code is written this episode. Read the box before you rebuild it.",
        ],
        "prereq": False,
        "chapters": [
            ("0:00", "29 files, and why we're reading all of them"), ("0:20", "No code today"),
            ("0:32", "manage.py and the settings split"), ("0:51", "PROJECT_DIR vs BASE_DIR"),
            ("1:07", "INSTALLED_APPS"), ("1:13", "Wagtail is just Django apps"),
            ("1:31", "The one middleware addition"), ("1:46", "Static vs media"),
            ("2:09", "The Wagtail settings block"), ("2:36", "dev.py, production.py, and local.py"),
            ("3:01", "urls.py"), ("3:06", "Why the catch-all must be last"),
            ("3:30", "HomePage(Page) — six lines"), ("3:51", "How templates find themselves"),
            ("4:10", "The migration nobody opens"), ("4:30", "Inside the migration"),
            ("4:48", "Treebeard: what “00010001” means"), ("5:22", "Two pages, not one"),
            ("5:38", "The Site row"), ("5:54", "The search app"),
            ("6:13", "base.html and the Wagtail userbar"), ("6:30", "The requirements.txt discrepancy"),
            ("7:02", "Five things to remember"), ("7:31", "Next episode"),
        ],
        "tag": "ep02-end",
        "commands": "youtube/ep02/commands.md",
    },
    {
        "slug": "03-the-page-model-and-the-tree",
        "no": "03",
        "video": "1Oxev2holT4",
        "uploaded": "2026-09-19T11:46:25-07:00",   # from the YouTube watch page
        "runtime": "5:08",
        "iso": "PT5M8S",
        "title": "The page model and the tree",
        "search_title": "Wagtail Page Model Explained: Custom Page Types",
        "lede": "We finally change code: two fields on the homepage, a second page type, and the one "
                "migration line that explains how every Wagtail page is stored.",
        "covers": [
            "Last episode predicted that a page one level under Home would get the tree path "
            "<code>000100010001</code>. This episode we build that page and check it in the database.",
            "Along the way: adding fields to a Wagtail page, and why they do not appear in the admin "
            "without <code>content_panels</code>; creating a second page type, "
            "<code>StandardPage</code>, and why it needs its own template; and multi-table "
            "inheritance, where every page lives in two tables joined by <code>page_ptr</code>.",
            "Also covered: reading the page tree from the shell, why <code>url_path</code> says "
            "<code>/home/about/</code> while the page is served at <code>/about/</code>, and the "
            "<code>.specific</code> gotcha, where <code>Page.objects</code> hands you a page with "
            "your fields missing.",
        ],
        "prereq": False,
        "chapters": [
            ("0:00", "Last episode's prediction"), ("0:19", "Where we left HomePage"),
            ("0:38", "Adding intro and body fields"),
            ("0:56", "A field is not a form field: content_panels"),
            ("1:17", "A second page type: StandardPage"), ("1:31", "Every page type needs a template"),
            ("1:54", "makemigrations and migrate"), ("2:02", "The page_ptr line"),
            ("2:15", "Every page lives in two tables"), ("2:45", "Editing the homepage in the admin"),
            ("2:56", "Adding a child page"), ("3:08", "Printing the tree"),
            ("3:14", "The prediction checks out"), ("3:31", "url_path is not the URL"),
            ("3:59", "Why is my field missing? .specific"), ("4:20", "What's still wrong"),
            ("4:38", "Commit and tag"), ("4:46", "Next episode"),
        ],
        "tag": "ep03-end",
        "commands": "youtube/ep03/commands.md",
    },
    {
        "slug": "04-templates-and-static-files",
        "no": "04",
        "video": "e-FeE6O9AhM",
        "uploaded": "2026-09-19T21:36:44-07:00",   # from the YouTube watch page
        "runtime": "5:38",
        "iso": "PT5M38S",
        "title": "Templates and static files",
        "search_title": "Wagtail Templates and Static Files Explained",
        "lede": "The teal egg finally goes. We delete Wagtail's welcome page, write a real base "
                "template, list child pages from the page tree, and style the site with plain CSS.",
        "covers": [
            "Where the welcome page lives and how to delete it properly; how Wagtail finds a "
            "template from the model name, and the two places templates can live; and a real "
            "<code>base.html</code> with a header, main and footer, keeping the generated bits that "
            "are worth keeping.",
            "Then the template work itself: <code>pageurl</code>, <code>slugurl</code> and the "
            "<code>richtext</code> filter, why you should never build links from "
            "<code>url_path</code>, and listing child pages with <code>get_children.live</code> "
            "straight from the page tree.",
            "Plus the ten-minute trap nobody warns you about: you write your CSS, reload, and the "
            "page is still completely unstyled — with nothing wrong with your code. We cover why "
            "<code>studio.css</code> ships at 0 bytes, how <code>{% static %}</code> resolves it, "
            "and the browser-cache trap, with proof of what is actually happening.",
            "No build step, no framework, no Node. Plain CSS, hand-written, for the whole series.",
        ],
        "prereq": False,
        "chapters": [
            ("0:00", "Four episodes in, still an egg"), ("0:16", "Where the welcome page lives"),
            ("0:30", "How Wagtail finds a template"), ("0:46", "Two places templates live"),
            ("1:06", "base.html — keep the head"), ("1:23", "Header, main, footer"),
            ("1:35", "pageurl, slugurl, richtext"), ("1:58", "Never build links from url_path"),
            ("2:14", "Listing child pages from the tree"),
            ("2:32", "The stylesheet that ships empty"), ("2:56", "static and STATICFILES_DIRS"),
            ("3:14", "You write the CSS. Nothing changes."), ("3:30", "What's actually happening"),
            ("3:52", "Hard-reload"), ("4:09", "The result"), ("4:22", "The About page"),
            ("4:36", "One media query"), ("4:50", "Why the 404 page hasn't changed"),
            ("5:09", "Commit and tag"), ("5:12", "Next episode"),
        ],
        "tag": "ep04-end",
        "commands": "youtube/ep04/commands.md",
    },
    {
        "slug": "05-streamfield-properly",
        "no": "05",
        "video": "8_wrJLU57Qw",
        "uploaded": "2026-09-19T22:15:37-07:00",   # from the YouTube watch page
        "runtime": "7:56",
        "iso": "PT7M56S",
        "title": "StreamField, properly",
        "search_title": "Wagtail StreamField Tutorial: Blocks and StructBlock",
        "lede": "We replace the rich-text blob with real content blocks — and hit the migration "
                "error that stops most people on their first try.",
        "covers": [
            "If you have ever seen <code>CHECK constraint failed: JSON_VALID</code> and had no idea "
            "why, that is in here, with the fix and the reason: why the migration fails on any page "
            "that already has content, and how to write a data migration that runs before the "
            "column changes type.",
            "The blocks themselves: what StreamField actually is, a JSON column holding an ordered "
            "list of typed blocks; the four kinds of block and when to reach for each; "
            "<code>StructBlock</code> against <code>ListBlock</code>, which is record against "
            "repeat and the one people mix up; and <code>Meta</code> — icon, label and template, "
            "and what the editor sees.",
            "Then the template side: the one-line change on the page template, how tiny a block "
            "template really is, and <code>block_counts</code> on a StreamBlock against "
            "<code>max_num</code> on a ListBlock.",
            "Two gotchas, both hit while building the episode: the migration failure, and the "
            "reason a call to action rendered as a teal box inside a teal box. Also: stop passing "
            "<code>use_json_field=True</code> — Wagtail 7.4 accepts it and ignores it.",
        ],
        "prereq": False,
        "chapters": [
            ("0:00", "One field, one blob"), ("0:20", "What StreamField actually is"),
            ("0:38", "The four kinds of block"), ("1:01", "StructBlock vs ListBlock"),
            ("1:21", "Writing a StructBlock"), ("1:40", "A struct containing a list"),
            ("1:57", "The top-level StreamBlock"), ("2:14", "The model change"),
            ("2:27", "use_json_field is dead"), ("2:48", "The migration blows up"),
            ("3:01", "What that error actually means"), ("3:24", "Nothing is broken"),
            ("3:47", "The fix: convert the data first"), ("4:07", "Writing the data migration"),
            ("4:33", "It applies"), ("4:42", "That unreadable block_lookup"),
            ("5:04", "One line in the page template"), ("5:17", "Inside a block template"),
            ("5:33", "A teal box inside a teal box"), ("5:47", "Wagtail already wrapped your block"),
            ("6:06", "Style the wrapper instead"), ("6:19", "What the client sees"),
            ("6:41", "Two ways to say “max”"), ("7:01", "The finished home page"),
            ("7:17", "The migrated About page"), ("7:31", "Commit and tag"),
            ("7:34", "Next episode"),
        ],
        "tag": "ep05-end",
        "commands": "youtube/ep05/commands.md",
    },
    {
        "slug": "06-images-and-documents",
        "no": "06",
        "video": "YYxtwAx4a0w",
        "uploaded": "2026-09-20T10:08:02-07:00",   # from the YouTube watch page
        "runtime": "7:49",
        "iso": "PT7M49S",
        "title": "Images and documents",
        "search_title": "Wagtail Images and Documents: Renditions and Focal Points",
        "lede": "Six episodes into a design studio's website and there is not one picture on it. We "
                "fix that — and hit the image bug that only shows up after you deploy.",
        "covers": [
            "Renditions are database rows, not files. Wipe your media folder, restore a backup onto "
            "a new server, and Wagtail will keep serving URLs for files that are gone: eleven rows, "
            "eleven 404s. There is a one-line fix and it ships with Wagtail.",
            "The groundwork: images and documents are already installed, nothing to add; why "
            "<code>media/</code> is gitignored and what that means for your deploys; and the image "
            "ForeignKey, with <code>on_delete=SET_NULL</code> rather than <code>CASCADE</code>.",
            "Then the template side: what the <code>image</code> tag actually does, filter specs "
            "(width, height, fill, max, min, format), <code>srcset_image</code> for responsive "
            "images in one tag, and focal points with a real before and after at the same fill spec.",
            "Also: <code>ImageBlock</code> instead of <code>ImageChooserBlock</code>, and why alt "
            "text is content rather than a filing label; documents, and why they are served by a "
            "view rather than as static files; and <code>WAGTAILIMAGES_IMAGE_MODEL</code>, a "
            "day-one decision we name and deliberately do not take.",
        ],
        "prereq": False,
        "chapters": [
            ("0:00", "A studio site with no pictures"), ("0:19", "Nothing to install"),
            ("0:43", "Why media/ is gitignored"), ("1:03", "The image ForeignKey"),
            ("1:15", "SET_NULL, never CASCADE"), ("1:37", "What the image tag actually does"),
            ("2:01", "Filter specs"), ("2:19", "Responsive images in one tag"),
            ("2:44", "Focal points, before and after"), ("3:07", "Two things to know about them"),
            ("3:28", "Renditions are rows, not files"), ("3:45", "Eleven rows, eleven 404s"),
            ("4:15", "The fix that ships with Wagtail"),
            ("4:32", "The default alt text is a filing label"),
            ("4:54", "ImageBlock, not ImageChooserBlock"), ("5:17", "Alt text is content"),
            ("5:37", "Documents"), ("5:50", "Why documents go through a view"),
            ("6:10", "A day-one decision, named not done"), ("6:37", "The finished hero"),
            ("6:49", "Further down the page"), ("7:09", "The About page"),
            ("7:22", "Commit and tag"), ("7:29", "Next episode"),
        ],
        "tag": "ep06-end",
        "commands": "youtube/ep06/commands.md",
    },
]

VERSIONS = "Wagtail 7.4.3 · Django 6.1.1 · Python 3.12"
PREREQ = ("You need basic Django — models, migrations, templates, settings.py. Not deeply, but "
          "Wagtail <em>is</em> Django, so this series teaches Wagtail, not Django. New to Django? "
          "Do the official Django tutorial first, about a weekend of work, then come back.")

CHROME = ('<!-- @chrome head -->\n<!-- @end head -->\n</head>\n<body class="learn">\n\n'
          "<!-- @chrome top -->\n<!-- @end top -->\n")
FOOT = ("<!-- @chrome foot -->\n  <!-- @end foot -->\n\n</main>\n\n"
        # without these the reveals never run and the page renders blank
        '<script src="../journal.js"></script>\n<script src="../bird.js"></script>\n'
        "</body>\n</html>\n")

ARROW = ('<svg viewBox="0 0 18 12" aria-hidden="true"><path d="M1 6 H16 M11 1 L16 6 L11 11"/></svg>')
BACK = ('<svg viewBox="0 0 22 12" aria-hidden="true"><path d="M21 6H1M6 1 1 6l5 5"/></svg>')
RULE = ('<svg class="hero__line ink" data-reveal data-perch="mid" data-perch-first style="--d:.2s" '
        'viewBox="0 0 640 16" preserveAspectRatio="none" aria-hidden="true">'
        '<path pathLength="1" d="M3 10 C 110 4, 220 13, 330 8 S 540 5, 637 9"/></svg>')


SOURCE = "D:/django/wagtail-unboxed/youtube"   # where the episode folders live


def thumbs():
    """Copy each episode's own thumb.png in as a WebP. Skipped if Pillow or the
    source folder is missing: the cards then fall back to a plain link."""
    try:
        from PIL import Image
    except ImportError:
        print("no Pillow — thumbnails skipped")
        return set()
    out = os.path.join(ROOT, "assets", "learn")
    os.makedirs(out, exist_ok=True)
    done = set()
    for ep in EPISODES:
        src = os.path.join(SOURCE, "ep" + ep["no"].replace("0a", "00a").replace("0b", "00b"),
                           "assets", "thumb.png")
        if not os.path.exists(src):
            print("missing", src)
            continue
        img = Image.open(src).convert("RGB")
        img = img.resize((960, int(960 * img.height / img.width)), Image.LANCZOS)
        img.save(os.path.join(out, ep["slug"] + ".webp"), "WEBP", quality=82, method=6)
        # a JPEG too: the link preview when a page is shared (some networks skip WebP)
        img.save(os.path.join(out, ep["slug"] + ".jpg"), "JPEG", quality=84, optimize=True)
        done.add(ep["slug"])
    return done


def head(title, desc, extra=""):
    return ('<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            "<title>" + title + "</title>\n"
            '<meta name="description" content="' + desc + '">\n'
            "<!-- @chrome seo -->\n<!-- @end seo -->\n" + extra + CHROME)


def embed(video, title):
    return ('    <figure class="tube" data-reveal data-perch>\n'
            '      <div><iframe src="https://www.youtube-nocookie.com/embed/' + video + '" '
            'title="' + title + '" loading="lazy" allowfullscreen\n'
            '        allow="accelerometer; clipboard-write; encrypted-media; gyroscope; '
            'picture-in-picture"></iframe></div>\n    </figure>\n')


def ld(obj):
    import json
    return '<script type="application/ld+json">' + json.dumps(obj).replace("<", "\\u003c") + "</script>\n"


def episode_page(i, ep):
    nxt = EPISODES[i + 1] if i + 1 < len(EPISODES) else None
    chapters = "\n".join(
        '        <li><b>' + t + '</b> ' + n + "</li>" for t, n in ep["chapters"])
    links = ['<a class="btn" href="https://www.youtube.com/watch?v=' + ep["video"] +
             '"><span>Watch on YouTube</span>' + ARROW + "</a>"]
    if ep["tag"]:
        links.append('<a class="cta__alt" href="' + REPO + "/releases/tag/" + ep["tag"] +
                     '">the code at the end of this episode (<code>' + ep["tag"] + "</code>)</a>")
    if ep["commands"]:
        links.append('<a class="cta__alt" href="' + REPO + "/blob/main/" + ep["commands"] +
                     '">every command, for Windows, macOS and Linux</a>')

    body = ('\n<main class="page">\n\n  <article>\n    <header class="phead" id="top">\n'
            '      <a class="back" href="' + SERIES["slug"] + '/">' + BACK + "All episodes</a>\n"
            '      <p class="hero__kicker" data-reveal>' + SERIES["title"] +
            ' <span aria-hidden="true">·</span> episode ' + ep["no"] +
            ' <span aria-hidden="true">·</span> ' + ep["runtime"] + "</p>\n"
            '      <h1 class="phead__h" data-reveal style="--d:.08s">' + ep["title"] + "</h1>\n"
            "      " + RULE + "\n"
            '      <p class="hero__lede" data-reveal style="--d:.3s">' + ep["lede"] + "</p>\n"
            "    </header>\n\n" + embed(ep["video"], ep["search_title"]) +
            '\n    <div class="prose" data-reveal>\n'
            "      <h2>What this episode covers</h2>\n" +
            "\n".join("      <p>" + p + "</p>" for p in ep["covers"]) + "\n" +
            ('      <p class="note"><b>Before you start:</b> ' + PREREQ + "</p>\n" if ep["prereq"] else "") +
            "\n      <h2>Chapters</h2>\n      <ol class=\"chapters\">\n" + chapters + "\n      </ol>\n"
            "\n      <h2>Versions on screen</h2>\n      <p>" + VERSIONS +
            ". Recorded on Windows; macOS and Linux commands are in the repository for every "
            "episode.</p>\n    </div>\n  </article>\n\n"
            '  <section class="sec">\n    <div class="cta" data-reveal data-perch>\n      <div>\n'
            '        <p class="cta__h">' +
            ("Next: episode " + nxt["no"] + ", " + nxt["title"] if nxt else "More episodes are coming") +
            "</p>\n        <p class=\"cta__p\">" +
            ("Carry on from here." if nxt else
             "New episodes are added to the series as they are published.") + "</p>\n      </div>\n"
            "      <div>\n        " +
            ('<a class="btn" href="' + nxt["slug"] + '.html"><span>Episode ' + nxt["no"] + "</span>" +
             ARROW + "</a>" if nxt else
             '<a class="btn" href="' + CHANNEL + '"><span>The channel</span>' + ARROW + "</a>") +
            "\n        <a class=\"cta__alt\" href=\"index.html\">or see all episodes</a>\n"
            "      </div>\n    </div>\n  </section>\n\n"
            '  <section class="sec">\n    <div class="prose" data-reveal>\n      <p>' +
            " · ".join(links) + "</p>\n    </div>\n  </section>\n\n  " + FOOT)

    schema = ld({
        "@context": "https://schema.org", "@type": "VideoObject",
        "name": ep["search_title"], "description": ep["lede"],
        "thumbnailUrl": "https://i.ytimg.com/vi/" + ep["video"] + "/maxresdefault.jpg",
        "embedUrl": "https://www.youtube.com/embed/" + ep["video"],
        "contentUrl": "https://www.youtube.com/watch?v=" + ep["video"],
        "duration": ep["iso"], "uploadDate": ep["uploaded"],
        "isPartOf": {"@type": "CreativeWorkSeries", "name": SERIES["title"], "url": SITE + "learn/"},
        "author": {"@type": "Person", "name": "Ashish Pitroda", "url": SITE},
    }) + ld({
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE},
            {"@type": "ListItem", "position": 2, "name": SERIES["title"],
             "item": SITE + "learn/" + SERIES["slug"] + "/"},
            {"@type": "ListItem", "position": 3, "name": ep["title"],
             "item": SITE + "learn/" + ep["slug"] + ".html"},
        ],
    })
    title = ep["search_title"] + " — " + SERIES["title"] + " " + ep["no"]
    return head(title, ep["lede"].replace('"', "&quot;")[:155], schema) + body


def card(i, ep, has_thumb):
    fig = ('        <span class="ep__fig">' +
           ('<img src="../../assets/learn/' + ep["slug"] + '.webp" width="960" height="540" '
            'loading="lazy" alt="Thumbnail for episode ' + ep["no"] + ': ' + ep["title"] + '">'
            if has_thumb else "") +
           '<span class="ep__play" aria-hidden="true"></span>'
           '<span class="ep__time">' + ep["runtime"] + "</span></span>\n")
    return ('      <li><a class="ep" href="../' + ep["slug"] + '.html" data-reveal '
            'style="--d:.' + str(i + 2) + 's">\n' + fig +
            '        <span class="ep__body">\n'
            '          <span class="ep__no">Episode ' + ep["no"] + "</span>\n"
            '          <span class="ep__h">' + ep["title"] + "</span>\n"
            '          <span class="ep__p">' + ep["lede"] + "</span>\n"
            "        </span>\n      </a></li>")


def index_page(have=frozenset()):
    cards = "\n".join(card(i, ep, ep["slug"] in have) for i, ep in enumerate(EPISODES))

    body = ('\n<main class="page">\n\n  <section class="phead" id="top">\n'
            '    <a class="back" href="../index.html">' + BACK + "Back to the journal</a>\n"
            '    <p class="hero__kicker" data-reveal>A video series <span aria-hidden="true">·</span> '
            'Wagtail and Django</p>\n'
            '    <h1 class="phead__h" data-reveal style="--d:.08s">' + SERIES["title"] + "</h1>\n"
            "    " + RULE + "\n"
            '    <p class="hero__lede" data-reveal style="--d:.3s">' + SERIES["blurb"] +
            " We open a brand new Wagtail project, read all 29 files it generates, then build a "
            "working client site: pages, StreamField, images, a blog, snippets, navigation, a "
            "contact form, search, and a live deployment.</p>\n"
            '    <p class="hand" data-reveal style="--d:.55s">— ' + str(len(EPISODES)) +
            " episodes published so far, new ones every Tuesday</p>\n  </section>\n\n"
            # the episodes come first: a visitor is here to watch, not to read about it
            '  <section class="sec sec--eps">\n    <ol class="eps">\n' + cards +
            "\n    </ol>\n  </section>\n\n"
            '  <section class="sec">\n    <div class="prose" data-reveal>\n'
            '      <p class="note"><b>Before you start:</b> ' + PREREQ + "</p>\n"
            "      <h2>What makes this different</h2>\n"
            "      <p>Most tutorials tell you to ignore the files Wagtail generates. We read them, "
            "including the data migration that quietly creates your homepage, and what "
            "<code>00010001</code> in your database actually means. The goal is that you can modify "
            "this code, not just copy it.</p>\n"
            "      <h2>The series</h2>\n      <ul>\n"
            "        <li><b>Act 1 — Unboxing</b> (episodes 1–3): install, create, and read every "
            "generated file.</li>\n"
            "        <li><b>Act 2 — Building</b> (episodes 4–11): templates, StreamField, images, "
            "blog, snippets, navigation, forms, search.</li>\n"
            "        <li><b>Act 3 — Shipping</b> (episodes 12–14): editor polish, production "
            "settings, deploy.</li>\n      </ul>\n"
            "      <p>Not covered, on purpose: no React, no Tailwind, no Node, no Docker deep-dive. "
            "Plain CSS written by hand, so the episodes stay about Wagtail.</p>\n"
            "      <h2>The code</h2>\n      <p>Every episode ends on a git tag, so you can start "
            'anywhere: <a href="' + REPO + '">the repository is on GitHub</a>. Versions on screen are '
            + VERSIONS + ".</p>\n    </div>\n  </section>\n\n  " +
            # this page sits two levels down, so its scripts do too
            FOOT.replace('src="../', 'src="../../'))

    schema = ld({
        "@context": "https://schema.org", "@type": "CreativeWorkSeries",
        "name": SERIES["title"], "description": SERIES["blurb"],
        "author": {"@type": "Person", "name": "Ashish Pitroda"},
        "numberOfEpisodes": len(EPISODES),
        "url": SITE + "learn/" + SERIES["slug"] + "/",
        "hasPart": [{"@type": "VideoObject", "name": ep["search_title"], "description": ep["lede"],
                     "thumbnailUrl": "https://i.ytimg.com/vi/" + ep["video"] + "/maxresdefault.jpg",
                     "uploadDate": ep["uploaded"], "duration": ep["iso"],
                     "embedUrl": "https://www.youtube.com/embed/" + ep["video"],
                     "url": SITE + "learn/" + ep["slug"] + ".html"} for ep in EPISODES],
    })
    return head("Wagtail Unboxed — a Wagtail 7 and Django video series",
                "A build-along Wagtail CMS video series: open a new project, read every file it "
                "generates, then build and deploy a real site.", schema) + body


def hub_page(have=frozenset()):
    """learn/ — the shelf the series sit on. One card per series, so a second
    one is a second entry here and nothing existing moves."""
    newest = EPISODES[-1]
    cover = ('<img src="../assets/learn/' + newest["slug"] + '.webp" width="960" height="540" '
             'loading="lazy" alt="Wagtail Unboxed">' if newest["slug"] in have else "")
    card_html = ('      <li><a class="ep" href="' + SERIES["slug"] + '/" data-reveal '
                 'style="--d:.2s">\n'
                 '        <span class="ep__fig">' + cover +
                 '<span class="ep__play" aria-hidden="true"></span>'
                 '<span class="ep__time">' + str(len(EPISODES)) + " episodes</span></span>\n"
                 '        <span class="ep__body">\n'
                 '          <span class="ep__no">Wagtail and Django</span>\n'
                 '          <span class="ep__h">' + SERIES["title"] + "</span>\n"
                 '          <span class="ep__p">' + SERIES["blurb"] + "</span>\n"
                 "        </span>\n      </a></li>")

    body = ('\n<main class="page">\n\n  <section class="phead" id="top">\n'
            '    <a class="back" href="../index.html">' + BACK + "Back to the journal</a>\n"
            '    <p class="hero__kicker" data-reveal>Video series, free to watch</p>\n'
            '    <h1 class="phead__h" data-reveal style="--d:.08s">Learn</h1>\n'
            "    " + RULE + "\n"
            '    <p class="hero__lede" data-reveal style="--d:.3s">Series where something real gets '
            "built from an empty folder, with every file explained on the way. Each episode has a "
            "page here with what it covers and its chapters, and the video itself.</p>\n"
            "  </section>\n\n"
            '  <section class="sec sec--eps">\n    <ol class="eps">\n' + card_html +
            "\n    </ol>\n  </section>\n\n"
            '  <section class="sec">\n    <div class="cta" data-reveal data-perch>\n      <div>\n'
            '        <p class="cta__h">Want a series on something else?</p>\n'
            '        <p class="cta__p">If there is a part of Wagtail or Django you keep having to '
            "explain to people, tell me and it may become one.</p>\n      </div>\n      <div>\n"
            '        <a class="btn" href="../contact.html"><span>Write to me</span>' + ARROW +
            "</a>\n      </div>\n    </div>\n  </section>\n\n  " + FOOT)

    schema = ld({
        "@context": "https://schema.org", "@type": "CollectionPage",
        "name": "Learn", "url": SITE + "learn/",
        "description": "Video series on Wagtail and Django, with a page per episode.",
        "author": {"@type": "Person", "name": "Ashish Pitroda", "url": SITE},
        "mainEntity": {"@type": "ItemList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": SERIES["title"],
             "url": SITE + "learn/" + SERIES["slug"] + "/"}]},
    })
    return head("Learn — Wagtail and Django video series by Ashish Pitroda",
                "Free video series on Wagtail and Django, each episode with a page of its own: "
                "what it covers, its chapters, and the video.", schema) + body


def main():
    out = os.path.join(ROOT, "learn")
    os.makedirs(os.path.join(out, SERIES["slug"]), exist_ok=True)
    have = thumbs()
    # learn/ is the hub, learn/<slug>/ is this series, and the episodes stay
    # where they have always been — learn/<episode>.html — so no indexed
    # address changes when a second series arrives.
    files = [("index.html", hub_page(have)),
             (SERIES["slug"] + "/index.html", index_page(have))]
    files += [(ep["slug"] + ".html", episode_page(i, ep)) for i, ep in enumerate(EPISODES)]
    for name, html in files:
        io.open(os.path.join(out, name), "w", encoding="utf-8", newline="").write(html)
        print("learn/" + name)
    print("\nnow run: node build.js")


if __name__ == "__main__":
    main()
