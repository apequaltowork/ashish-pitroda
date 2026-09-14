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

  if (reduced || !("IntersectionObserver" in window)) {
    revealAll();
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        show(e.target);
        io.unobserve(e.target);
      });
    }, { rootMargin: "0px 0px -10% 0px", threshold: 0.06 });
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

  return { revealAll: revealAll, paintLog: function () { paintLog(); } };
})();
