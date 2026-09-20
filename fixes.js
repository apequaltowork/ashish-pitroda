/* ============================================================
   FIXES — the search box and the pager on the fixes list.
   Every fix is in the HTML already: without JS the whole list is
   there, unfiltered and unpaged, which is also what a crawler sees.
   ============================================================ */

window.FIXES = (function () {
  "use strict";

  var list = document.querySelector("[data-fixes]");
  if (!list) return {};

  var rows = Array.prototype.slice.call(list.querySelectorAll("[data-fix]"));
  var box = document.querySelector("[data-fix-search]");
  var count = document.querySelector("[data-fix-count]");
  var pager = document.querySelector("[data-fix-pager]");
  var empty = document.querySelector("[data-fix-empty]");
  var PER = parseInt(list.getAttribute("data-per") || "10", 10);

  var matches = rows.slice();
  var page = 1;

  function haystack(row) {
    return (row.getAttribute("data-fix") || "").toLowerCase();
  }

  function draw() {
    var pages = Math.max(1, Math.ceil(matches.length / PER));
    if (page > pages) page = pages;
    var from = (page - 1) * PER;

    rows.forEach(function (r) { r.hidden = true; });
    matches.slice(from, from + PER).forEach(function (r) { r.hidden = false; });

    if (empty) empty.hidden = matches.length !== 0;
    if (count) {
      count.textContent = matches.length === rows.length
        ? rows.length + (rows.length === 1 ? " fix" : " fixes")
        : matches.length + " of " + rows.length;
    }
    if (pager) {
      pager.innerHTML = "";
      pager.hidden = pages < 2;
      for (var n = 1; n <= pages; n++) {
        var b = document.createElement("button");
        b.type = "button";
        b.textContent = String(n);
        b.className = n === page ? "is-on" : "";
        if (n === page) b.setAttribute("aria-current", "page");
        b.setAttribute("data-page", String(n));
        pager.appendChild(b);
      }
    }
  }

  function search(q) {
    var terms = q.toLowerCase().split(/\s+/).filter(Boolean);
    matches = rows.filter(function (r) {
      var hay = haystack(r);
      return terms.every(function (t) { return hay.indexOf(t) !== -1; });
    });
    page = 1;
    draw();
  }

  if (box) {
    box.addEventListener("input", function () { search(box.value); });
    box.closest("form").addEventListener("submit", function (e) { e.preventDefault(); });
  }
  if (pager) {
    pager.addEventListener("click", function (e) {
      var n = e.target.getAttribute && e.target.getAttribute("data-page");
      if (!n) return;
      page = parseInt(n, 10);
      draw();
      list.scrollIntoView({ block: "start", behavior: "smooth" });
    });
  }

  draw();

  return {
    search: search,
    state: function () { return { rows: rows.length, matches: matches.length, page: page }; }
  };
})();
