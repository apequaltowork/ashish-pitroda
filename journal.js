/* ============================================================
   JOURNAL — the page's own small behaviours.
   Everything tagged [data-reveal] inks in the first time it is seen.
   Nothing is hidden without JS: the .js class on <html> is what
   switches the hidden starting states on.
   ============================================================ */

window.JOURNAL = (function () {
  "use strict";

  var items = Array.prototype.slice.call(document.querySelectorAll("[data-reveal]"));
  var reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;

  function show(el) { el.classList.add("is-in"); }
  function revealAll() { items.forEach(show); }

  // A block taller than the screen can never be mostly in view, so waiting
  // for it to be is how a long article stays invisible. It is shown at once;
  // the fade is for things that fit.
  items = items.filter(function (el) {
    if (el.offsetHeight > innerHeight) { show(el); return false; }
    return true;
  });

  if (reduced || !("IntersectionObserver" in window)) {
    revealAll();
  } else {
    // In view means 6% of the element, or, for one taller than the screen can
    // ever show 6% of (a long article), a quarter of the screen's height.
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        if (e.intersectionRatio < 0.06 && e.intersectionRect.height < innerHeight * 0.25) return;
        show(e.target);
        io.unobserve(e.target);
      });
    }, { rootMargin: "0px 0px -10% 0px", threshold: [0, 0.01, 0.03, 0.06] });
    items.forEach(function (el) { io.observe(el); });
  }

  // the header gains its rule once the page has moved off the cover
  var top = document.querySelector("[data-top]");
  if (top) {
    var onScroll = function () { top.classList.toggle("is-scrolled", window.scrollY > 8); };
    addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  /* ── colophon: the bird, observed live ─────────────────────── */

  // The colophon describes what the bird does; this card shows it doing it,
  // read straight from BIRD.stats(), so the description is checkable.
  var log = document.querySelector("[data-birdlog]");
  var paintLog = function () {};
  if (log) {
    var fields = {};
    Array.prototype.forEach.call(log.querySelectorAll("[data-k]"), function (el) {
      fields[el.getAttribute("data-k")] = el;
    });
    var PLACES = [
      ["birdlog__card", "this very card"],
      ["hero__line", "the line under the heading"],
      ["rule", "a section rule"],
      ["plate", "a field guide plate"],
      ["label", "a specimen label"],
      ["slot", "an empty specimen slot"],
      ["note-card", "a pinned note"],
      ["figures-wrap", "the table of figures"],
      ["cta", "the note at the foot of the page"],
      ["post", "the postcard"]
    ];
    var place = function (cls) {
      var parts = String(cls || "").split(/\s+/);
      for (var i = 0; i < PLACES.length; i++) if (parts.indexOf(PLACES[i][0]) >= 0) return PLACES[i][1];
      return "a line on the page";
    };
    var set = function (k, v) {
      var el = fields[k];
      v = String(v);
      if (el && el.textContent !== v) el.textContent = v;
    };
    paintLog = function () {
      var s = window.BIRD && window.BIRD.stats ? window.BIRD.stats() : null;
      if (!s) return;
      var MODES = { perched: "Perched", flying: "In flight", caged: "In its cage",
        entering: "Going into its cage", leaving: "Leaving its cage", away: "Out of sight" };
      set("mode", s.singing ? "Singing" : s.eating ? "Eating seeds" : MODES[s.mode] || s.mode);
      set("songs", (s.songs || 0).toLocaleString());
      set("seeds", (s.seedsEaten || 0).toLocaleString());
      set("perch", s.mode === "perched" ? place(s.perch) : s.mode === "caged" ? "the rod in its cage" : "—");
      set("flights", s.flights.toLocaleString());
      set("hops", s.hops.toLocaleString());
      set("wags", s.wags.toLocaleString());
    };
    setInterval(paintLog, 250);
  }

  /* ── copy an address ───────────────────────────────────────── */

  // Not everyone has a mail app set up, so an address can be copied instead.
  Array.prototype.forEach.call(document.querySelectorAll("[data-copy]"), function (btn) {
    var label = btn.textContent;
    var timer = 0;
    btn.addEventListener("click", function () {
      var text = btn.getAttribute("data-copy");
      var done = function (ok) {
        btn.textContent = ok ? "copied" : "could not copy — select it instead";
        clearTimeout(timer);
        timer = setTimeout(function () { btn.textContent = label; }, 2000);
      };
      var fallback = function () {
        var ta = document.createElement("textarea");
        ta.value = text;
        ta.setAttribute("readonly", "");
        ta.style.position = "fixed";
        ta.style.opacity = "0";
        document.body.appendChild(ta);
        ta.select();
        var ok = false;
        try { ok = document.execCommand("copy"); } catch (e) {}
        document.body.removeChild(ta);
        done(ok);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(function () { done(true); }, fallback);
      } else {
        fallback();
      }
    });
  });

  /* ── the menu, on narrow screens ────────────────────────────
     The pages are a panel under the bar; this opens and closes it.
     Nothing is hidden without JS: the panel only exists as a panel
     inside the same media query that shows the button. */
  (function () {
    var btn = document.querySelector("[data-menu]");
    var bar = document.querySelector("[data-top]");
    if (!btn || !bar) return;

    function set(open) {
      bar.classList.toggle("is-open", open);
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    }
    btn.addEventListener("click", function () {
      set(bar.className.indexOf("is-open") === -1);
    });
    // a tap outside, Escape, or following a link closes it again
    document.addEventListener("click", function (e) {
      if (!bar.contains(e.target)) set(false);
      else if (e.target.closest && e.target.closest("#pages a")) set(false);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") set(false);
    });

    /* The series panel hangs off the Learn item, but should start at the
       bar's own bottom edge. That distance is the header's padding plus
       however the row is centred in it, so it is measured rather than
       guessed, and measured again when the window changes. */
    var has = document.querySelector(".nav__has");
    function alignPanel() {
      if (!has) return;
      var gap = Math.round(bar.getBoundingClientRect().bottom -
                           has.getBoundingClientRect().bottom);
      document.documentElement.style.setProperty("--bar-gap", Math.max(gap, 0) + "px");
    }
    alignPanel();
    addEventListener("resize", alignPanel);
    // and again the moment it is about to be seen, which is the only time it
    // has to be right: by then the fonts have loaded and the bar has settled
    if (has) {
      has.addEventListener("mouseenter", alignPanel);
      has.addEventListener("focusin", alignPanel);
    }
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(alignPanel);
    addEventListener("resize", function () { set(false); });
  })();

  return { revealAll: revealAll, paintLog: function () { paintLog(); } };
})();
