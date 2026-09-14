/* ============================================================
   PALETTE PREVIEW — hidden.

   The site runs on two of the six palettes: Sepia archive (light) and
   Night journal (dark), switched by theme.js. The other four — Field
   notebook, Indigo ink, Botanical and Seaside — are kept, not deleted,
   in the PALETTES block of journal.css.

   This bar is hidden. Add ?palettes to any address to bring it back
   for a look; ?palette=indigo (or any name) opens a page in that
   palette. Nothing chosen here is remembered — the theme switch in the
   header is what visitors use.
   ============================================================ */

window.PALETTE = (function () {
  "use strict";

  var NAMES = ["field", "indigo", "botanical", "seaside", "sepia", "night"];
  var root = document.documentElement;
  var bar = document.querySelector("[data-pbar]");

  function current() { return root.getAttribute("data-palette") || "field"; }

  function mark() {
    if (!bar) return;
    var now = current();
    Array.prototype.forEach.call(bar.querySelectorAll("[data-palette-choice]"), function (b) {
      b.setAttribute("aria-checked", b.getAttribute("data-palette-choice") === now ? "true" : "false");
    });
  }

  function apply(name) {
    if (NAMES.indexOf(name) < 0) name = "sepia";
    if (name === "field") root.removeAttribute("data-palette");
    else root.setAttribute("data-palette", name);
    mark();
    window.dispatchEvent(new CustomEvent("palettechange", { detail: name }));
  }

  // only shown when the address asks for it (partials/head.html sets the flag)
  if (bar && root.hasAttribute("data-palettes")) {
    bar.hidden = false;
    bar.addEventListener("click", function (e) {
      var b = e.target.closest("[data-palette-choice]");
      if (b) apply(b.getAttribute("data-palette-choice"));
    });
    // arrow keys move between the options, as in any radio group
    bar.addEventListener("keydown", function (e) {
      if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
      var i = NAMES.indexOf(current()) + (e.key === "ArrowRight" ? 1 : -1);
      var next = NAMES[(i + NAMES.length) % NAMES.length];
      apply(next);
      var btn = bar.querySelector('[data-palette-choice="' + next + '"]');
      if (btn) btn.focus();
      e.preventDefault();
    });
  }
  mark();

  return { apply: apply, current: current, names: NAMES.slice() };
})();
