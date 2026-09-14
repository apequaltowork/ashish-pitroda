/* ============================================================
   SPECIMENS — project cards, and the viewer that opens from them.

   Everything comes from projects.js — no form, no server, no build.
   A project can carry a photo gallery and a video:

     images: ["assets/projects/a.webp", "assets/projects/b.webp"]
     video:  a YouTube or Vimeo link   → plays inside the viewer
             an .mp4 / .webm file      → plays inside the viewer
             any other https link      → a "watch the video" link

   YouTube and Vimeo are only contacted when someone presses play;
   until then the viewer shows the project's own first photo.

   Clicking a card opens the viewer; the address gains #project-name,
   so one project can be linked to directly.

   Loaded BEFORE journal.js, so the cards exist by the time the reveal
   observer and the bird's perches are collected.
   ============================================================ */

window.SPECIMENS = (function () {
  "use strict";

  /* ── the list ─────────────────────────────────────────────── */

  var EXAMPLE = /(^|&)example(=|&|$)/.test(location.search.slice(1));

  var samples = (Array.isArray(window.SAMPLE_PROJECTS) ? window.SAMPLE_PROJECTS : [])
    .map(function (p) { return Object.assign({}, p, { sample: true }); });
  var real = Array.isArray(window.PROJECTS) ? window.PROJECTS : [];
  // Samples only show when projects.js explicitly asks for them.
  var source = EXAMPLE ? samples : real.concat(window.SHOW_SAMPLES === true ? samples : []);

  var used = {};
  var projects = source
    .filter(function (p) { return p && typeof p.title === "string" && p.title.trim(); })
    .map(function (p) { return Object.assign({}, p, { slug: slugify(p.title) }); });

  var ICON = {
    arrow: '<svg viewBox="0 0 18 12" aria-hidden="true"><path d="M1 6 H16 M11 1 L16 6 L11 11"/></svg>',
    play:  '<svg viewBox="0 0 16 18" aria-hidden="true"><path d="M1.5 1.5v15l13-7.5z"/></svg>',
    prev:  '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M10.5 2.5 5 8l5.5 5.5"/></svg>',
    next:  '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M5.5 2.5 11 8l-5.5 5.5"/></svg>',
    close: '<svg viewBox="0 0 14 14" aria-hidden="true"><path d="M2 2l10 10M12 2 2 12"/></svg>'
  };

  /* ── helpers ──────────────────────────────────────────────── */

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;      // text only — nothing from projects.js goes through innerHTML
    return n;
  }

  function slugify(title) {
    var base = "project-" + (title.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "") || "untitled");
    var s = base, n = 2;
    while (used[s]) s = base + "-" + n++;
    used[s] = true;
    return s;
  }

  // Links come from a hand-edited file, so be strict about what becomes an href.
  function href(url, base) {
    if (!url) return null;
    url = String(url).trim();
    if (!url) return null;
    if (url === "#") return "#top";                              // placeholder links
    if (/^https?:\/\//i.test(url)) return url;
    if (/^[a-z][a-z0-9+.-]*:/i.test(url)) return null;            // javascript:, data: and friends
    return base + url.replace(/^\/+/, "");
  }

  function external(a) {
    if (/^https?:/i.test(a.getAttribute("href"))) { a.target = "_blank"; a.rel = "noopener"; }
  }

  function cssUrl(u) { return 'url("' + String(u).replace(/["\\\n\r]/g, "") + '")'; }

  function initials(title) {
    var words = title.split(/\s+/).filter(function (w) {
      return w && !/^(a|an|the|of|and|for|on|in)$/i.test(w);
    });
    return (words.slice(0, 2).map(function (w) { return w.charAt(0); }).join("") || "?").toUpperCase();
  }

  function plate(title) {
    var d = el("div", "spec__plate", initials(title));
    d.setAttribute("aria-hidden", "true");
    return d;
  }

  function stamp() {
    var s = el("span", "spec__sample", "Sample");
    s.title = "A sample project, shown until real projects are added";
    return s;
  }

  function videoOf(url, base) {
    if (!url) return null;
    url = String(url).trim();
    var m = url.match(/^https?:\/\/(?:www\.|m\.)?(?:youtube\.com\/(?:watch\?(?:[^#]*&)?v=|embed\/|shorts\/|live\/)|youtu\.be\/)([A-Za-z0-9_-]{11})/i);
    if (m) return { type: "embed", provider: "YouTube", href: url,
      src: "https://www.youtube-nocookie.com/embed/" + m[1] + "?autoplay=1&rel=0" };
    m = url.match(/^https?:\/\/(?:www\.|player\.)?vimeo\.com\/(?:video\/)?(\d+)/i);
    if (m) return { type: "embed", provider: "Vimeo", href: url,
      src: "https://player.vimeo.com/video/" + m[1] + "?autoplay=1" };
    var h = href(url, base);
    if (!h || h === "#top") return null;
    if (/\.(mp4|webm|ogv|ogg|m4v)(?:[?#]|$)/i.test(h)) return { type: "file", src: h };
    if (/^https?:/i.test(h)) return { type: "link", href: h };
    return null;
  }

  // a project's media, with paths resolved for the page it is shown on
  function media(p, base) {
    var images = [];
    var add = function (u) {
      var h = href(u, base);
      if (h && h !== "#top" && images.indexOf(h) < 0) images.push(h);
    };
    if (p.image) add(p.image);
    if (Array.isArray(p.images)) p.images.forEach(add);
    var video = videoOf(p.video, base);
    return { base: base, images: images, video: video, playable: !!video && video.type !== "link" };
  }

  function links(p, m) {
    var row = el("div", "spec__links");
    var demo = href(p.demo, m.base), code = href(p.source, m.base), page = href(p.page, m.base);
    if (demo) {
      var a = el("a", "btn btn--sm");
      a.href = demo;
      var label = p.demoLabel ? String(p.demoLabel) : "View demo";
      a.setAttribute("aria-label", label + ": " + p.title);
      var t = document.createElement("span");
      t.textContent = label;                                     // the label is text, never markup
      a.appendChild(t);
      a.insertAdjacentHTML("beforeend", ICON.arrow);             // static markup only
      external(a);
      row.appendChild(a);
    }
    if (m.video && m.video.type === "link") {
      var w = el("a", "cta__alt", "watch the video");
      w.href = m.video.href;
      external(w);
      row.appendChild(w);
    }
    if (code) {
      var s = el("a", "cta__alt", "source code");
      s.href = code;
      s.setAttribute("aria-label", "Source code: " + p.title);
      external(s);
      row.appendChild(s);
    }
    if (page) {
      var r = el("a", "cta__alt", p.pageLabel ? String(p.pageLabel) : "read the write-up");
      r.href = page;
      if (/^https?:/i.test(page)) external(r);                  // another site: a new tab
      row.appendChild(r);
    }
    return row.childNodes.length ? row : null;
  }

  function meta(p) {
    var i = projects.indexOf(p);
    var bits = ["No. " + (i < 9 ? "0" : "") + (i + 1)];
    if (p.kind) bits.push(p.kind);
    if (p.year) bits.push(String(p.year));
    return el("p", "spec__meta", bits.join(" · "));
  }

  function tags(p) {
    if (!Array.isArray(p.stack) || !p.stack.length) return null;
    var ul = el("ul", "tags tags--sm");
    p.stack.forEach(function (s) { if (s) ul.appendChild(el("li", "tag", String(s))); });
    return ul;
  }

  /* ── a card ───────────────────────────────────────────────── */

  function card(p, i, base) {
    var m = media(p, base);
    var c = el("article", "spec");
    c.setAttribute("data-reveal", "");
    c.setAttribute("data-perch", "");
    c.setAttribute("data-kind", p.kind || "Other");
    if (i % 3) c.style.setProperty("--d", ((i % 3) * 0.08).toFixed(2) + "s");

    if (p.sample) {
      c.classList.add("spec--sample");     // its drawn sketches may be inverted on dark paper
      c.appendChild(stamp());
    }
    var pin = el("span", "slot__pin");
    pin.setAttribute("aria-hidden", "true");
    c.appendChild(pin);

    var opens = m.images.length > 0 || m.playable;
    var fig = el(opens ? "button" : "div", "spec__fig");
    if (opens) {
      fig.type = "button";
      fig.setAttribute("aria-label", (m.playable ? "Play the video and see the photos: " : "See the photos: ") + p.title);
      fig.addEventListener("click", function () { open(p, m, 0, fig, m.playable); });
    }

    if (m.images.length) {
      var img = el("img");
      // the listener goes on BEFORE src, so a failure can never slip past it
      img.addEventListener("error", function () { img.replaceWith(plate(p.title)); });
      img.alt = opens ? "" : "Screenshot of " + p.title;        // the button carries the label
      if (i >= 3) img.loading = "lazy";                          // the first row is on screen at load
      img.src = m.images[0];
      fig.appendChild(img);
    } else {
      fig.appendChild(plate(p.title));
    }

    if (m.playable) {
      var play = el("span", "spec__play");
      play.innerHTML = ICON.play;
      play.setAttribute("aria-hidden", "true");
      fig.appendChild(play);
    }
    var badges = [];
    if (m.playable) badges.push("Video");
    if (m.images.length > 1) badges.push(m.images.length + " photos");
    if (badges.length) {
      var b = el("span", "spec__badges");
      b.setAttribute("aria-hidden", "true");
      badges.forEach(function (t) { b.appendChild(el("span", "spec__badge", t)); });
      fig.appendChild(b);
    }
    c.appendChild(fig);

    c.appendChild(meta(p));
    c.appendChild(el("h3", "spec__h", p.title));
    if (p.summary) c.appendChild(el("p", "spec__p", p.summary));
    var t = tags(p);
    if (t) c.appendChild(t);
    var row = links(p, m);
    if (row) c.appendChild(row);
    return c;
  }

  /* ── the viewer ───────────────────────────────────────────── */

  var V = null;

  function buildViewer() {
    var d = document.createElement("dialog");
    d.className = "viewer";
    d.setAttribute("aria-labelledby", "viewer-title");
    d.innerHTML =                                                 // static markup only
      '<div class="viewer__sheet">' +
        '<button class="viewer__close" type="button" aria-label="Close" data-v="close">' + ICON.close + '</button>' +
        '<div class="viewer__media">' +
          '<div class="viewer__stage" data-v="stage"></div>' +
          '<button class="viewer__nav viewer__nav--prev" type="button" aria-label="Previous" data-v="prev">' + ICON.prev + '</button>' +
          '<button class="viewer__nav viewer__nav--next" type="button" aria-label="Next" data-v="next">' + ICON.next + '</button>' +
          '<p class="viewer__count" data-v="count" aria-live="polite"></p>' +
          '<div class="viewer__thumbs" data-v="thumbs"></div>' +
        '</div>' +
        '<div class="viewer__info" data-v="info"></div>' +
      '</div>';
    document.body.appendChild(d);

    var get = function (k) { return d.querySelector('[data-v="' + k + '"]'); };
    V = { d: d, stage: get("stage"), prev: get("prev"), next: get("next"), count: get("count"),
          thumbs: get("thumbs"), info: get("info"), p: null, m: null, slides: [], i: 0, opener: null };

    get("close").addEventListener("click", close);
    V.prev.addEventListener("click", function () { show(V.i - 1); });
    V.next.addEventListener("click", function () { show(V.i + 1); });
    d.addEventListener("click", function (e) { if (e.target === d) close(); });   // the backdrop
    d.addEventListener("close", cleanup);                                         // Esc lands here too
    d.addEventListener("keydown", function (e) {
      // Esc is handled here rather than left to the browser, so the viewer
      // cleans up immediately instead of whenever the close event arrives
      if (e.key === "Escape") { e.preventDefault(); close(); return; }
      if (e.target && e.target.tagName === "VIDEO") return;       // arrows seek inside a video
      if (e.key === "ArrowLeft")  { e.preventDefault(); show(V.i - 1); }
      if (e.key === "ArrowRight") { e.preventDefault(); show(V.i + 1); }
    });

    // Any other way the dialog loses its open attribute — a script, a form
    // with method="dialog" — is caught here. Mutation callbacks run promptly,
    // where the dialog's own close event can lag well behind.
    new MutationObserver(function () { if (!d.open) cleanup(); })
      .observe(d, { attributes: true, attributeFilter: ["open"] });

    // swipe between photos on touch screens
    var sx = null;
    V.stage.addEventListener("pointerdown", function (e) { if (e.pointerType !== "mouse") sx = e.clientX; });
    V.stage.addEventListener("pointerup", function (e) {
      if (sx === null) return;
      var dx = e.clientX - sx;
      sx = null;
      if (Math.abs(dx) > 50) show(V.i + (dx < 0 ? 1 : -1));
    });
  }

  function slidesOf(m) {
    var s = [];
    if (m.playable) s.push({ kind: "video" });
    m.images.forEach(function (src, n) { s.push({ kind: "image", src: src, n: n + 1 }); });
    return s;
  }

  function missing(text) {
    V.stage.textContent = "";
    V.stage.classList.remove("is-video");
    V.stage.appendChild(el("p", "viewer__missing", text));
  }

  function mountEmbed() {
    V.stage.textContent = "";
    var f = el("iframe");
    f.title = V.p.title + " — video";
    f.allow = "autoplay; encrypted-media; picture-in-picture; fullscreen";
    f.allowFullscreen = true;
    f.referrerPolicy = "strict-origin-when-cross-origin";
    f.src = V.m.video.src;
    V.stage.appendChild(f);
  }

  // YouTube and Vimeo stay unloaded until someone actually asks for them
  function facade() {
    var b = el("button", "viewer__facade");
    b.type = "button";
    b.setAttribute("aria-label", "Play the video on " + V.m.video.provider);
    if (V.m.images[0]) b.style.backgroundImage = cssUrl(V.m.images[0]);
    var play = el("span", "spec__play");
    play.innerHTML = ICON.play;
    play.setAttribute("aria-hidden", "true");
    b.appendChild(play);
    b.appendChild(el("span", "viewer__facade-k", "plays from " + V.m.video.provider));
    b.addEventListener("click", mountEmbed);
    return b;
  }

  function show(i, autoplay) {
    var n = V.slides.length;
    if (!n) return;
    V.i = ((i % n) + n) % n;
    var s = V.slides[V.i];

    V.stage.textContent = "";                       // unloads whatever was playing
    V.stage.classList.toggle("is-video", s.kind === "video");

    if (s.kind === "image") {
      var img = el("img");
      img.addEventListener("error", function () { missing("This photo could not be loaded."); });
      img.alt = "Photo " + s.n + " of " + V.m.images.length + " — " + V.p.title;
      img.src = s.src;
      V.stage.appendChild(img);
    } else if (V.m.video.type === "file") {
      var v = el("video");
      v.controls = true;
      v.playsInline = true;
      v.preload = "metadata";
      if (V.m.images[0]) v.poster = V.m.images[0];
      v.addEventListener("error", function () { missing("This video could not be loaded."); });
      v.src = V.m.video.src;
      V.stage.appendChild(v);
      if (autoplay) {
        var started = v.play();
        if (started && started.catch) started.catch(function () {});   // blocked autoplay just leaves the play button
      }
    } else if (autoplay) {
      mountEmbed();
    } else {
      V.stage.appendChild(facade());
    }

    Array.prototype.forEach.call(V.thumbs.children, function (t, k) {
      t.setAttribute("aria-current", k === V.i ? "true" : "false");
    });
    V.count.textContent = (V.i + 1) + " / " + n;
    V.prev.hidden = V.next.hidden = V.count.hidden = V.thumbs.hidden = n < 2;
  }

  function fill() {
    var p = V.p, m = V.m, info = V.info;
    info.textContent = "";
    if (p.sample) info.appendChild(stamp());
    var sheet = info.closest(".viewer");
    if (sheet) sheet.classList.toggle("is-sample", !!p.sample);
    info.appendChild(meta(p));
    var h = el("h2", "viewer__h", p.title);
    h.id = "viewer-title";
    info.appendChild(h);
    if (p.summary) info.appendChild(el("p", "viewer__p", p.summary));
    var t = tags(p);
    if (t) info.appendChild(t);
    var row = links(p, m);
    if (row) info.appendChild(row);
    if (p.credit) info.appendChild(el("p", "viewer__credit", String(p.credit)));

    V.thumbs.textContent = "";
    V.slides.forEach(function (s, k) {
      var b = el("button", "viewer__thumb" + (s.kind === "video" ? " viewer__thumb--video" : ""));
      b.type = "button";
      b.setAttribute("aria-label", s.kind === "video" ? "Video" : "Photo " + s.n);
      if (s.kind === "image") b.style.backgroundImage = cssUrl(s.src);
      else if (m.images[0]) b.style.backgroundImage = "linear-gradient(rgba(28,25,22,.5), rgba(28,25,22,.5)), " + cssUrl(m.images[0]);
      b.addEventListener("click", function () { show(k, s.kind === "video"); });
      V.thumbs.appendChild(b);
    });
  }

  function open(p, m, start, opener, autoplay) {
    if (!V) buildViewer();
    V.p = p;
    V.m = m;
    V.opener = opener || null;
    V.slides = slidesOf(m);
    V.cleaned = false;
    fill();
    document.documentElement.classList.add("is-viewing");
    if (!V.d.open) {
      if (typeof V.d.showModal === "function") V.d.showModal();
      else V.d.setAttribute("open", "");
    }
    show(start || 0, autoplay);
    if (history.replaceState && location.hash !== "#" + p.slug) history.replaceState(null, "", "#" + p.slug);
  }

  function close() {
    if (!V || !V.d.open) return;
    if (typeof V.d.close === "function") V.d.close();
    else V.d.removeAttribute("open");
    // Clean up now rather than waiting for the dialog's close event: that
    // event is queued, not synchronous, and can arrive late — the video would
    // keep playing and the page stay locked in the meantime.
    cleanup();
  }

  // Runs once per opening, whichever arrives first: close(), or the native
  // close event when the browser shuts the dialog itself (Esc).
  function cleanup() {
    if (!V || V.cleaned) return;
    V.cleaned = true;
    V.stage.textContent = "";                       // stops the video
    document.documentElement.classList.remove("is-viewing");
    if (V.p && location.hash === "#" + V.p.slug && history.replaceState) {
      history.replaceState(null, "", location.pathname + location.search);
    }
    if (V.opener && document.contains(V.opener)) V.opener.focus();
  }

  // A #project- link followed on a page that is already open changes only the
  // hash, so nothing reloads — open (or close) the viewer to match it. Our own
  // replaceState calls never fire this event, so there is no loop.
  addEventListener("hashchange", function () {
    var slug = decodeURIComponent(location.hash.slice(1));
    if (/^project-/.test(slug)) {
      if (!V || !V.d.open || V.p.slug !== slug) openBySlug(slug, false);
    } else if (V && V.d.open) {
      close();
    }
  });

  /* ── render every listing on the page ─────────────────────── */

  var filled = [];
  Array.prototype.forEach.call(document.querySelectorAll("[data-specimens]"), function (host) {
    var base = host.getAttribute("data-base") || "";
    var limit = parseInt(host.getAttribute("data-limit"), 10) || 0;
    var items = limit ? projects.slice(0, limit) : projects;
    var empty = host.parentNode.querySelector("[data-specimens-empty]");

    if (!items.length) {
      if (empty) empty.hidden = false;       // otherwise the markup's own fallback stays
      return;
    }
    host.textContent = "";
    items.forEach(function (p, i) { host.appendChild(card(p, i, base)); });
    host.classList.add("is-filled");
    filled.push(host);
  });

  /* ── filter by kind, on the full listing only ─────────────── */

  var bar = document.querySelector("[data-specimen-filters]");
  var listing = bar && document.querySelector("[data-specimens]:not([data-limit])");
  if (bar && listing && listing.classList.contains("is-filled")) {
    var kinds = [];
    projects.forEach(function (p) {
      var k = p.kind || "Other";
      if (kinds.indexOf(k) < 0) kinds.push(k);
    });

    if (kinds.length > 1) {
      var buttons = [];
      var add = function (label, kind, count) {
        var b = el("button", "chip");
        b.type = "button";
        b.setAttribute("aria-pressed", kind === null ? "true" : "false");
        b.appendChild(document.createTextNode(label));
        b.appendChild(el("span", null, String(count)));
        b.addEventListener("click", function () {
          buttons.forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
          Array.prototype.forEach.call(listing.children, function (c) {
            var show = kind === null || c.getAttribute("data-kind") === kind;
            c.hidden = !show;
            if (show) c.classList.add("is-in");  // never leave a filtered-in card waiting on a reveal
          });
        });
        buttons.push(b);
        bar.appendChild(b);
      };
      add("All", null, projects.length);
      kinds.forEach(function (k) {
        add(k, k, projects.filter(function (p) { return (p.kind || "Other") === k; }).length);
      });
      bar.hidden = false;
    }
  }

  /* ── the example flag ─────────────────────────────────────── */

  if (EXAMPLE && filled.length) {
    var flag = el("p", "flag");
    flag.setAttribute("role", "note");
    flag.appendChild(el("b", null, "Example layout."));
    flag.appendChild(document.createTextNode(
      " Only the sample projects are showing. Remove ?example from the address to see the real list."));
    var main = document.querySelector("main");
    if (main) main.parentNode.insertBefore(flag, main);
  }

  /* ── open a project linked to directly: #project-name ──────── */

  function openBySlug(slug, autoplay) {
    var host = filled[0];
    for (var i = 0; i < projects.length; i++) {
      if (projects[i].slug !== slug) continue;
      var m = media(projects[i], host ? host.getAttribute("data-base") || "" : "");
      if (!m.images.length && !m.playable) return false;
      open(projects[i], m, 0, null, !!autoplay);
      return true;
    }
    return false;
  }
  var linked = decodeURIComponent(location.hash.slice(1));
  if (/^project-/.test(linked) && filled.length) openBySlug(linked, false);

  return {
    count: projects.length,
    example: EXAMPLE,
    rendered: filled.length,
    open: function (which, autoplay) {
      return openBySlug(typeof which === "number" ? (projects[which] || {}).slug : which, autoplay);
    },
    close: close,
    next: function () { if (V && V.d.open) show(V.i + 1); },
    state: function () {
      if (!V) return { open: false };
      var first = V.stage.firstElementChild;
      return {
        open: V.d.open,
        project: V.p && V.p.title,
        slide: V.i + 1,
        slides: V.slides.length,
        kind: V.slides[V.i] ? V.slides[V.i].kind : null,
        stage: first ? first.tagName.toLowerCase() + (first.className ? "." + first.className : "") : null,
        hash: location.hash
      };
    },
    slugs: function () { return projects.map(function (p) { return p.slug; }); }
  };
})();
