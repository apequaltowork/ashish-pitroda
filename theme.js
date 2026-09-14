/* ============================================================
   THEME — light or dark.

   Light is the Sepia archive palette, dark is Night journal. The
   script in partials/head.html sets the theme before the page paints:
   the visitor's own choice if they have made one, otherwise their
   system setting. This file wires up the switch in the header,
   remembers a choice, and keeps following the system setting for as
   long as no choice has been made. Everything drawn in colour — the
   bird, the cage, the seeds — listens for the same "palettechange".
   ============================================================ */

window.THEME = (function () {
  "use strict";

  var KEY = "fj-theme";
  var root = document.documentElement;
  var buttons = document.querySelectorAll("[data-theme-toggle]");
  var media = window.matchMedia ? matchMedia("(prefers-color-scheme: dark)") : null;
  var chosen = null;
  try { chosen = localStorage.getItem(KEY); } catch (e) {}
  // a ?palette= preview link is left alone until the switch is used
  var previewing = /[?&]palette=/.test(location.search);

  function current() { return root.getAttribute("data-palette") === "night" ? "dark" : "light"; }

  function paint() {
    var dark = current() === "dark";
    Array.prototype.forEach.call(buttons, function (b) {
      b.setAttribute("aria-pressed", dark ? "true" : "false");
      b.title = dark ? "Switch to the light theme" : "Switch to the dark theme";
    });
  }

  function set(theme, remember) {
    root.setAttribute("data-palette", theme === "dark" ? "night" : "sepia");
    if (remember) {
      chosen = theme;
      try { localStorage.setItem(KEY, theme); } catch (e) {}
    }
    paint();
    window.dispatchEvent(new CustomEvent("palettechange", { detail: root.getAttribute("data-palette") }));
  }

  Array.prototype.forEach.call(buttons, function (b) {
    b.addEventListener("click", function () {
      previewing = false;
      set(current() === "dark" ? "light" : "dark", true);
    });
  });

  // follow the system setting until the visitor picks one themselves
  if (media) {
    var follow = function (e) { if (!chosen && !previewing) set(e.matches ? "dark" : "light", false); };
    if (media.addEventListener) media.addEventListener("change", follow);
    else if (media.addListener) media.addListener(follow);
  }

  paint();

  return { set: function (theme) { set(theme, true); }, current: current };
})();
