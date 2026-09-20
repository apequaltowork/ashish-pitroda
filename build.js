/* Sync the shared chrome into every page of the field journal.
     node build.js           write it
     node build.js --check   exit 1 if any page has drifted

   Every page carries the same head links, bird canvas, header and footer.
   Rather than emit a separate output tree, the build writes that chrome INTO
   each page between markers, so every page stays a plain file that opens
   straight from disk with no server. Running it twice is a no-op.

     <!-- @chrome NAME -->  ...generated...  <!-- @end NAME -->

   Links in the partials are written root-relative (journal.css, about.html)
   and prefixed with ../ per directory depth on the way in.
*/

const fs = require("fs");
const path = require("path");

const here = __dirname;
const read = (f) => fs.readFileSync(path.join(here, f), "utf8");
const exists = (f) => fs.existsSync(path.join(here, f));

/* ── the site, as data ─────────────────────────────────────────
   `section` decides which header link is marked as the current one.
   Pages waiting on real content (reviews, a case study, writing) are kept
   out of the published site, in drafts/. */

// Fixes is listed only once there is a fix to read: an empty section in the
// menu is worse than no section.
const HAS_FIXES = fs.existsSync(path.join(here, "fixes", "index.html"));

const PAGES = [
  { file: "index.html",                       section: "home" },
  { file: "services/index.html",              section: "guide" },
  { file: "services/wagtail-cms.html",        section: "guide" },
  { file: "services/django.html",             section: "guide" },
  { file: "services/frontend-vue-next.html",  section: "guide" },
  { file: "services/api-integrations.html",   section: "guide" },
  { file: "services/aws-performance.html",    section: "guide" },
  { file: "services/project-takeover.html",   section: "guide" },
  { file: "about.html",                       section: "about" },
  { file: "contact.html",                     section: "write" },
  { file: "colophon.html",                    section: "colophon" },
  { file: "404.html",                         section: null },
  { file: "work/index.html",                  section: "specimens" },
  { file: "learn/index.html",                          section: "learn" },
  { file: "learn/00a-what-this-series-is.html",        section: "learn" },
  { file: "learn/00b-setting-up-your-machine.html",    section: "learn" },
  { file: "learn/01-what-wagtail-actually-is.html",    section: "learn" },
  { file: "learn/02-every-file-explained.html",        section: "learn" },
  { file: "learn/03-the-page-model-and-the-tree.html", section: "learn" },
  { file: "learn/04-templates-and-static-files.html",  section: "learn" },
  { file: "learn/05-streamfield-properly.html",        section: "learn" }
];

// Fix pages are found rather than listed: their names come from the fix
// folders, and tools/make-fixes.py writes whatever is there.
if (HAS_FIXES) {
  for (const f of fs.readdirSync(path.join(here, "fixes")).sort()) {
    if (f.endsWith(".html")) PAGES.push({ file: "fixes/" + f, section: "fixes" });
  }
}

const NAV = [
  { key: "guide",     label: "Field guide", href: "services/index.html" },
  { key: "specimens", label: "Projects",    href: "work/index.html" },
  { key: "learn",     label: "Learn",       href: "learn/index.html" },
  { key: "fixes",     label: "Fixes",       href: "fixes/index.html", held: !HAS_FIXES },
  { key: "about",     label: "About",       href: "about.html" },
  { key: "write",     label: "Write to me", href: "contact.html", cta: true }
].filter((n) => !n.held);

const FOOT = [
  ["Home", "index.html"],
  ["Field guide", "services/index.html"],
  ["Projects", "work/index.html"],
  ["Learn", "learn/index.html"],
  ...(HAS_FIXES ? [["Fixes", "fixes/index.html"]] : []),
  ["About", "about.html"],
  ["Write to me", "contact.html"],
  ["Colophon", "colophon.html"]
];

/* ── paths ────────────────────────────────────────────────── */

const depthOf = (file) => file.split("/").length - 1;

function reroot(html, page) {
  const depth = depthOf(page.file);
  let out = html;
  if (depth) {
    const up = "../".repeat(depth);
    out = out.replace(/\b(href|src)="(?!https?:|mailto:|data:|#|\/)([^"]*)"/g,
      (m, attr, val) => attr + '="' + up + val + '"');
  }
  // On the home page itself, a link to index.html#x must stay a fragment:
  // served from "/", "index.html#x" is a different URL and would reload.
  if (page.file === "index.html") {
    out = out.replace(/href="index\.html#/g, 'href="#')
             .replace(/href="index\.html"/g, 'href="#top"');
  }
  return out;
}

/* ── regions ──────────────────────────────────────────────── */

function setRegion(html, name, body) {
  const open = "<!-- @chrome " + name + " -->";
  const close = "<!-- @end " + name + " -->";
  const i = html.indexOf(open);
  if (i === -1) return html;
  const j = html.indexOf(close, i);
  if (j === -1) throw new Error("unclosed @chrome " + name);
  const lineStart = html.lastIndexOf("\n", i) + 1;
  const indent = html.slice(lineStart, i).match(/^[ \t]*/)[0];
  const inner = body.trim().split("\n").map((l) => (l.length ? indent + l : l)).join("\n");
  return html.slice(0, i + open.length) + "\n" + inner + "\n" + indent + html.slice(j);
}

/* ── generated blocks ─────────────────────────────────────── */

function navFor(page) {
  return NAV.map((n) => {
    const on = page.section === n.key;
    const cls = [n.cta ? "nav__cta" : "", on ? "is-active" : ""].filter(Boolean).join(" ");
    return "<li" + (n.cta ? ' class="nav__keep"' : "") + "><a" +
      (cls ? ' class="' + cls + '"' : "") + ' href="' + n.href + '"' +
      (on ? ' aria-current="page"' : "") + ">" + n.label + "</a></li>";
  }).join("\n        ");   // the partial already indents the first item
}

function footFor(page) {
  const links = FOOT.filter(([, href]) => href !== page.file)
    .map(([label, href]) => '<a href="' + href + '">' + label + "</a>")
    .join("");
  return read("partials/foot.html").replace("@links", () => links);
}

// the colophon's numbers, measured on every build rather than typed in
function stats() {
  const kb = (f) => (fs.statSync(path.join(here, f)).size / 1024).toFixed(1) + " KB";
  const scripts = ["journal.js", "bird.js", "theme.js", "palette.js", "letter.js", "specimens.js", "projects.js", "fixes.js"].filter(exists);
  const jsBytes = scripts.reduce((n, f) => n + fs.statSync(path.join(here, f)).size, 0);
  const pages = PAGES.filter((p) => !p.held && p.file !== "404.html" && exists(p.file)).length;
  const rows = [
    ["Dependencies", "0", "No framework, no animation library, nothing to install."],
    ["The bird", kb("bird.js"), "One canvas, drawn from ellipses and a few lines."],
    ["All scripts", (jsBytes / 1024).toFixed(1) + " KB", scripts.length + " hand-written files, unminified."],
    ["Stylesheet", kb("journal.css"), "One file. The paper, the ink, every layout."],
    ["Pages", String(pages), "Plain HTML. Every one opens straight from disk."]
  ];
  return ['<dl class="figures">',
    rows.map(([k, v, note]) =>
      "  <div><dt>" + k + "</dt><dd>" + v + "</dd><p>" + note + "</p></div>").join("\n"),
    "</dl>"].join("\n");
}

/* ── search engines and link previews ─────────────────────── */

const SITE = "https://apequaltowork.github.io/ashish-pitroda/";
const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

// the public address of a page: folders end in "/", not "index.html"
const urlOf = (file) => SITE + file.replace(/(^|\/)index\.html$/, "$1");

// canonical link and share tags, from the page's own <title> and description
function seoFor(page, html) {
  const title = (html.match(/<title>([^<]*)<\/title>/) || [])[1] || "";
  const desc = (html.match(/<meta name="description" content="([^"]*)"/) || [])[1] || "";
  // an episode page previews with its own thumbnail; everything else with the share card
  const dir = page.file.split("/")[0];
  const own = (dir === "learn" || dir === "fixes") &&
    "assets/" + dir + "/" + path.basename(page.file, ".html") + ".jpg";
  const url = urlOf(page.file), img = SITE + (own && exists(own) ? own : "assets/share-card.png");
  return [
    '<link rel="canonical" href="' + url + '">',
    '<meta property="og:type" content="' + (page.file === "index.html" ? "profile" : "website") + '">',
    '<meta property="og:site_name" content="Ashish Pitroda">',
    '<meta property="og:title" content="' + title + '">',
    '<meta property="og:description" content="' + desc + '">',
    '<meta property="og:url" content="' + url + '">',
    '<meta property="og:image" content="' + img + '">',
    '<meta property="og:image:width" content="1200">',
    '<meta property="og:image:height" content="630">',
    '<meta name="twitter:card" content="summary_large_image">',
    '<meta name="twitter:title" content="' + title + '">',
    '<meta name="twitter:description" content="' + desc + '">',
    '<meta name="twitter:image" content="' + img + '">'
  ].concat(page.file === "work/index.html" ? [projectsHtml().ld] : []).join("\n");
}

// the projects as plain HTML, for crawlers and visitors without JavaScript
function projectsHtml() {
  const sandbox = { window: {} };
  require("vm").runInNewContext(read("projects.js"), sandbox);
  const list = (sandbox.window.PROJECTS || []).filter((p) => p && p.title);
  const abs = (u) => /^https?:/.test(u) ? u : SITE + u;
  const items = list.map((p) => {
    const links = [[p.demo, p.demoLabel || "View demo"], [p.video, "watch the video"],
      [p.page, p.pageLabel || "read more"], [p.source, "source code"]]
      .filter(([u]) => u).map(([u, l]) => '<a href="' + esc(abs(u)) + '">' + esc(l) + "</a>").join(" · ");
    return "  <li><h3>" + esc(p.title) + "</h3>" +
      (p.summary ? "<p>" + esc(p.summary) + "</p>" : "") +
      (p.stack && p.stack.length ? "<p>" + esc(p.stack.join(", ")) + "</p>" : "") +
      (links ? "<p>" + links + "</p>" : "") + "</li>";
  });
  const ld = {
    "@context": "https://schema.org", "@type": "ItemList",
    itemListElement: list.map((p, i) => ({
      "@type": "ListItem", position: i + 1,
      item: Object.assign({ "@type": "CreativeWork", name: p.title, description: p.summary,
        author: { "@type": "Person", name: "Ashish Pitroda" } },
        p.year ? { dateCreated: String(p.year) } : {},
        p.images && p.images[0] ? { image: abs(p.images[0]) } : {},
        p.demo ? { url: p.demo } : {})
    }))
  };
  const html = list.length ? ["<ol>", items.join("\n"), "</ol>"].join("\n") : '<p class="empty__k">Nothing pinned in yet</p>';
  return { html, ld: '<script type="application/ld+json">' + JSON.stringify(ld).replace(/</g, "\\u003c") + "</script>" };
}

// a page that asks not to be indexed stays out of both sitemaps
const publicPages = () => PAGES.filter((p) =>
  p.file !== "404.html" && exists(p.file) && !/<meta name="robots" content="noindex">/.test(read(p.file)));

// when a page last really changed, from git rather than from the file's
// timestamp, which every rebuild would otherwise bump
function lastChanged(file) {
  try {
    const out = require("child_process")
      .execFileSync("git", ["log", "-1", "--format=%cs", "--", file], { cwd: here })
      .toString().trim();
    return /^\d{4}-\d{2}-\d{2}$/.test(out) ? out : "";
  } catch (e) {
    return "";
  }
}

function sitemap() {
  return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    publicPages().map((p) => {
      const when = lastChanged(p.file);
      return "  <url><loc>" + urlOf(p.file) + "</loc>" +
        (when ? "<lastmod>" + when + "</lastmod>" : "") + "</url>";
    }).join("\n") + "\n</urlset>\n";
}

// robots.txt. On a project site this file answers at /ashish-pitroda/robots.txt,
// and a crawler only reads the one at the domain root — which belongs to
// github.io, not to us. It is written anyway: it is correct, it is what other
// tools look for, and the sitemap is submitted in Search Console regardless.
function robots() {
  return ["User-agent: *", "Allow: /", "", "Sitemap: " + SITE + "sitemap.xml", ""].join("\n");
}

// the same list as plain text, one address a line: a second thing Search
// Console can be pointed at when it will not fetch the XML one
const sitemapTxt = () => publicPages().map((p) => urlOf(p.file)).join("\n") + "\n";

/* ── run ──────────────────────────────────────────────────── */

const CHECK = process.argv.includes("--check");
const stale = [];
let missing = 0;

for (const page of PAGES) {
  if (!exists(page.file)) { missing++; continue; }
  const before = read(page.file);
  let html = before;
  // journal.css?v=<hash of its contents>: a changed stylesheet gets a new
  // address, so no browser keeps showing the old one from its cache
  const cssv = require("crypto").createHash("sha1").update(read("journal.css")).digest("hex").slice(0, 8);
  html = setRegion(html, "head", reroot(read("partials/head.html"), page)
    .replace(/journal\.css"/, 'journal.css?v=' + cssv + '"'));
  html = setRegion(html, "top", reroot(read("partials/top.html").replace("@nav", () => navFor(page)), page));
  html = setRegion(html, "foot", reroot(footFor(page), page));
  html = setRegion(html, "stats", stats());
  html = setRegion(html, "seo", seoFor(page, html));
  html = setRegion(html, "projects", projectsHtml().html);
  if (html === before) continue;
  stale.push(page.file);
  if (!CHECK) fs.writeFileSync(path.join(here, page.file), html, "utf8");
}

for (const [file, body] of [["sitemap.xml", sitemap()], ["sitemap.txt", sitemapTxt()],
                            ["robots.txt", robots()]]) {
  if (exists(file) && read(file) === body) continue;
  stale.push(file);
  if (!CHECK) fs.writeFileSync(path.join(here, file), body, "utf8");
}

console.log("pages".padEnd(10), (PAGES.length - missing) + " on disk" +
  (missing ? ", " + missing + " not built yet" : ""));
console.log((CHECK ? "stale" : "written").padEnd(10), stale.length ? stale.join(", ") : "none — already in sync");
if (CHECK && stale.length) process.exit(1);
