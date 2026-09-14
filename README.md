# Field journal — a second design for Ashish Pitroda's portfolio

A deliberately different direction from `../cinematic-scroll` (the dark,
film-reel site that is live on GitHub Pages). This one is a naturalist's
notebook: warm paper, ink, a red pencil for annotations — and a live pied
wagtail that lives on the page. Wagtail CMS is named after the bird, and
Wagtail is the framework Ashish is hired for most, so the mascot means
something here that it couldn't on anyone else's site.

Published with GitHub Pages from
`git@github.com:apequaltowork/ashish-pitroda.git` (branch `main`, folder
`/`), at https://apequaltowork.github.io/ashish-pitroda/. `.nojekyll` stops
GitHub running Jekyll over it. `versions/` holds local snapshots and is not
pushed — git history is the record from here on.

## Run it

```bash
python -m http.server 5180 --directory D:/claude/animation/field-journal
```

Then open http://localhost:5180. Opening any page straight from disk also
works — every path is relative and nothing is fetched.

## Pages

```
index.html                  the cover: approach, field guide, specimen drawer,
                            method, habitat, correspondence
about.html                  who keeps the journal, with a taped-in photograph
contact.html                write to me — a letter that composes an email
colophon.html               how it is made, with a live log of the bird
404.html                    no sighting recorded
services/index.html         the field guide: six plates
services/*.html             one plate per kind of work

HELD — built, kept in sync, linked from nowhere, noindex:
work/01-example.html        the specimen record template, with example content
proof.html                  sightings: empty slots for real client reviews
writing/index.html          the notebook: no entries yet
writing/_template.html      copy this to write an entry
```

## Files

```
journal.css         the paper, the ink, every layout
journal.js          reveals, the header rule, the colophon's bird log, copy buttons
bird.js             the wagtail, its cage, its seeds and its song
theme.js            the light / dark switch in the header
palette.js          the hidden palette preview bar (?palettes)
letter.js           the contact letter: validation, signature, mailto
build.js            writes the shared chrome into every page
partials/           that chrome: head links, bird canvas + header, footer
tools/import-project.py  converts a prepared portfolio folder's thumbnail and
                    gallery-NN images to WebP in assets/projects/<slug>/ and
                    prints the images list for projects.js (videos: YouTube links)
tools/make-portrait.py  crops and sizes a photo for the About page (4:5, 900 × 1125)
assets/portrait.webp  its output — the print border, tilt, tape and tone are CSS (.photo)
tools/make-sketch.py  the earlier ink-sketch treatment of the photograph (not used now)
assets/sketch.webp  its output
```

No framework, no animation library. The site runs straight from these files;
`build.js` is only needed when the shared chrome changes.

## The shared chrome

The head links, the bird's canvas, the header and the footer are the same on
every page, so they live once in `partials/` and `build.js` writes them into
each page between markers:

```html
<!-- @chrome head --><!-- @end head -->     inside <head>
<!-- @chrome top --><!-- @end top -->       first thing in <body>
<!-- @chrome foot --><!-- @end foot -->     at the end of <main>
```

```bash
node build.js          # write
node build.js --check  # exit 1 if any page has drifted
```

Running it twice is a no-op. Links in the partials are written from the root
and prefixed with `../` automatically for pages in `services/`, `work/` and
`writing/`. The page list, the header links and the footer links are all data
at the top of `build.js`.

### Adding a page

1. Copy a similar page — `404.html` is the smallest.
2. Keep the three markers.
3. Add it to `PAGES` in `build.js`, with `section` set to the header link it
   belongs under.
4. Mark somewhere for the bird to land first with `data-perch-first` — usually
   the drawn line under the page heading.
5. `node build.js`.

## The wagtail

It only ever stands on real lines: any element marked `data-perch` offers
its top edge, or its midline with `data-perch="mid"` (used for the drawn
rules). It never lands on something that has not revealed yet.

- pumps its tail in bursts, the way the real bird does
- watches the cursor from up to ~560px away
- hops along its line towards the cursor, but stops about 46px short
- startles and flies to another line if the cursor lunges at it, or gets
  within 26px
- follows the reader down the page, flying to a new line whenever its own
  scrolls out of view
- pecks, turns and potters about when left alone
- calls "chis-ick!" if you click beside it
- counts its tail wags in the footer

It never takes the pointer (`pointer-events: none`), so it can't get in the
way of a link. With `prefers-reduced-motion` it stands still on a line near
the middle of the screen and reappears there as you scroll.

For testing where `requestAnimationFrame` doesn't run (a hidden tab):

```js
BIRD.step(1000)   // advance one second and redraw
BIRD.stats()      // mode, position, which line it is on, counts
BIRD.remap()      // re-read the lines from the layout
```

## Adding a project

Projects live in one file: **`projects.js`**. There is no form and nothing to
build.

1. Open `projects.js` and copy the template block.
2. Paste it inside the square brackets, remove the `//`, and fill it in.
   Only `title` is required.
3. Save and refresh.

Each project becomes a card on `work/index.html` (the Projects page, with a
filter by kind), and the first six also fill the specimen drawer on the cover.
List them newest first — that is the order they show in.

```js
{
  title:   "Project name",
  kind:    "Wagtail CMS",          // becomes the filter
  summary: "One or two sentences.",
  stack:   ["Wagtail", "Django"],
  year:    2026,
  images:  ["assets/projects/name-1.webp", "assets/projects/name-2.webp"],
  video:   "https://www.youtube.com/watch?v=…",   // or "assets/projects/name.mp4"
  demo:    "https://…",            // optional
  source:  "https://github.com/…", // optional
  page:    ""                      // optional longer write-up
}
```

### Photos and video

- **`images`** — put the files in `assets/projects/` (about 1200 × 750). The
  first is the card's cover; all of them appear in the gallery.
- **`video`** — a YouTube link (watch, youtu.be or shorts), a Vimeo link, or
  your own `.mp4` / `.webm` file. It plays inside the gallery. YouTube and
  Vimeo are not contacted until someone presses play — until then the viewer
  shows the project's first photo. Any other link becomes "watch the video".

Clicking a card opens the viewer: the video first, then the photos, with
arrows, thumbnails, swipe on phones, and Esc or the × to close. The address
gains `#project-name`, so a single project can be linked to directly.

A project without any picture gets a lettered plate. Links are checked —
anything that isn't `http(s)` or a relative path is ignored.

### The sample projects

`projects.js` also holds six **sample projects** — sketched screenshots and
two tour videos, drawn by `tools/make-samples.py` into `assets/samples/`.
They show how the page, the gallery and the video player work. Every one is
stamped **Sample** on its card and says so in the viewer.

When your own projects are in, set `window.SHOW_SAMPLES = false` at the top of
`projects.js`, or delete the `SAMPLE_PROJECTS` block and `assets/samples/`.
`/work/?example` shows only the samples, under a flag, whatever the switch
says.

## The cage (version-02)

The wagtail has a home: a hand-drawn cage hanging from the header in the top
right. When there is nowhere left to stand, the bird flies into it instead of
off the screen:

- the door swings open as it arrives, and the cage sways when it lands
- inside, it still wags its tail, hops along the rod and watches the cursor
- it lets itself out once there is a line on screen to stand on again
- clicking the cage calls it home, and it stays until the cage is clicked
  again; every so often it also pops home by itself for a moment
- it starts every page inside the cage and flies out to the first line

The cage is an SVG button in `partials/top.html`, stacked above the bird's
canvas so its bars sit in front of the bird. `bird.js` reads points on it in
viewBox units — the ring, the perch rod, the door — so change the drawing and
those numbers together. The cage only fits in the margin of screens 1300px
and wider; on narrower screens it is hidden and the bird leaves by the edge
of the screen, as in version-01. With reduced motion the bird simply sits in
the cage, and clicking moves it out onto a line and back.

### Feeding it

A packet of seeds is taped to the page under the cage. Click it and it tips,
throwing four to six seeds onto a line:

- onto the bird's own line, a little ahead of it, if it is standing on one;
  otherwise onto the nearest line in view to the packet
- the bird goes straight to them — out of the cage if it is inside, even if
  it was called home — and eats them one at a time: a few quick hops, a bow,
  two pecks and a scatter of crumbs
- while there are seeds in front of it, it is too busy eating to watch, follow
  or be startled by the cursor
- after the last one it **sings**: a twitter of short whistled notes around
  its "chis-ick" call, different every time, lasting about two seconds. Its
  head goes up, its beak opens on each note and musical notes drift up from
  it. The sound is made with Web Audio as it plays — no audio files — and is
  panned towards wherever the bird is standing
- the **song switch** under the packet turns the sound off or on (the notes
  still show); "off" is remembered on this device. Browsers only allow sound
  after a click, so it is the click on the packet that starts the audio —
  nothing ever plays by itself on page load
- more than eight seeds already down and the packet just shakes; with no line
  in view it shakes and says so
- the colophon's live log counts the seeds eaten, and `BIRD.feed()` throws a
  handful from the console

The packet hides with the cage on screens narrower than 1300px.

version-01, version-02 and version-03 (this feeding) are kept, untouched, in
`versions/`.

## Light and dark

A round switch in the header moves between two themes:

- **Light — Sepia archive**: aged paper, brown-black ink, oxblood pencil
- **Dark — Night journal**: charcoal paper, chalk ink, amber pencil

Before the page paints, the script in `partials/head.html` picks the
visitor's own earlier choice (localStorage `fj-theme`), or else their
system setting; `theme.js` wires the switch and follows the system setting
until someone chooses. The bird, the cage and the seeds recolour with it.

Every colour in `journal.css` is written against theme tokens — `--paper`,
`--ink`, `--red` and friends, channel tokens such as `rgba(var(--ink-rgb), .2)`,
and `--bird-*` for the wagtail — so a theme is just a set of values.

On the dark theme the drawn sample sketches and the About portrait are
inverted so they stay legible. Real project screenshots never are.

### The other palettes (hidden, kept)

Field notebook (the original), Indigo ink, Botanical and Seaside are still in
the PALETTES block of `journal.css`, with the preview bar in
`partials/top.html` and `palette.js`. The bar is hidden; add `?palettes` to
any address to show it, or `?palette=indigo` (any name) to open a page in one.
Nothing picked there is remembered.

## The contact letter

**Switched off for now.** `contact.html` shows contact details only — the
email address with a copy button, what to include, and status. The letter form
is still in the page with `hidden`; to bring it back, remove `hidden` from the
`<form>` and `write--direct` from the `<div class="write">` around it.

A static site has nowhere to POST to, so `letter.js` composes the letter into
an email and opens the visitor's own mail app — it genuinely arrives, with
nothing to host. To use a real form endpoint instead, set `ENDPOINT` at the
top of `letter.js` (Formspree or similar); validation and the "Posted" stamp
already work for both.

## Content rules

Every word of real content comes from the live site. Nothing is invented:

- **The specimen drawer on the cover is empty on purpose.** No projects have
  been supplied, and nothing may be presented as client work until it is real.
- **Every service plate's "What it costs"** explains what decides the price
  but states no numbers. There is a TODO where the real bands go.
- **`proof.html` holds no reviews at all**, only labelled empty slots.
- **`work/01-example.html`** carries example prose under a band that says so.

Each held page opens with a comment listing exactly what finishing it needs.
