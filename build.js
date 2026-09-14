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
  { file: "work/index.html",                  section: "specimens" }
];

const NAV = [
  { key: "guide",     label: "Field guide", href: "services/index.html" },
  { key: "specimens", label: "Projects",    href: "work/index.html" },
  { key: "about",     label: "About",       href: "about.html" },
  { key: "write",     label: "Write to me", href: "contact.html", cta: true }
];

const FOOT = [
  ["Home", "index.html"],
  ["Field guide", "services/index.html"],
  ["Projects", "work/index.html"],
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
  const scripts = ["journal.js", "bird.js", "theme.js", "palette.js", "letter.js", "specimens.js", "projects.js"].filter(exists);
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

/* ── run ──────────────────────────────────────────────────── */

const CHECK = process.argv.includes("--check");
const stale = [];
let missing = 0;

for (const page of PAGES) {
  if (!exists(page.file)) { missing++; continue; }
  const before = read(page.file);
  let html = before;
  html = setRegion(html, "head", reroot(read("partials/head.html"), page));
  html = setRegion(html, "top", reroot(read("partials/top.html").replace("@nav", () => navFor(page)), page));
  html = setRegion(html, "foot", reroot(footFor(page), page));
  html = setRegion(html, "stats", stats());
  if (html === before) continue;
  stale.push(page.file);
  if (!CHECK) fs.writeFileSync(path.join(here, page.file), html, "utf8");
}

console.log("pages".padEnd(10), (PAGES.length - missing) + " on disk" +
  (missing ? ", " + missing + " not built yet" : ""));
console.log((CHECK ? "stale" : "written").padEnd(10), stale.length ? stale.join(", ") : "none — already in sync");
if (CHECK && stale.length) process.exit(1);
