/* ============================================================
   LETTER — the contact form, written as a letter.

   There is no backend on a static host, so a POST has nowhere to land.
   Rather than show a success message and quietly drop the message, the
   letter is composed into a mailto and handed to the visitor's own mail
   app. It genuinely arrives, with nothing to host.

   To move to a real endpoint later, set ENDPOINT to a Formspree (or
   similar) URL. Validation and the "posted" stamp already work for both.
   ============================================================ */

window.LETTER = (function () {
  "use strict";

  var form = document.querySelector("[data-letter]");
  if (!form) return null;

  var ENDPOINT = "";                        // e.g. "https://formspree.io/f/xxxxxxx"
  var TO = "apequaltowork@gmail.com";

  var errEl = form.querySelector("[data-letter-err]");
  var okEl = document.querySelector("[data-letter-ok]");
  var sig = form.querySelector("[data-signature]");
  var reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;

  function val(name) {
    var el = form.elements[name];
    return el ? el.value.trim() : "";
  }

  // the sign-off writes itself in as the name is typed
  function sign() {
    if (!sig) return;
    var v = val("name");
    sig.textContent = v || "your name";
    sig.classList.toggle("is-empty", !v);
  }
  if (form.elements.name) form.elements.name.addEventListener("input", sign);
  sign();

  function fail(msg, focusName) {
    errEl.textContent = msg;
    errEl.hidden = false;
    var el = form.elements[focusName];
    if (el) { el.classList.add("is-bad"); el.focus(); }
    return false;
  }

  function clearErrors() {
    errEl.hidden = true;
    Array.prototype.forEach.call(form.querySelectorAll(".is-bad"), function (el) {
      el.classList.remove("is-bad");
    });
  }

  // Deliberately loose: over-strict email patterns turn away real addresses.
  function looksLikeEmail(v) { return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v); }

  function validate() {
    clearErrors();
    if (!val("name")) return fail("Add your name, so I know who I am writing back to.", "name");
    if (!looksLikeEmail(val("email"))) return fail("That email address does not look right — I need a working one to reply to.", "email");
    if (val("brief").length < 20) return fail("Tell me a little more — a sentence or two is enough to start.", "brief");
    return true;
  }

  function compose() {
    var lines = [
      "Dear Ashish,",
      "",
      val("brief"),
      "",
      "Kind of work:  " + val("project"),
      "Budget:        " + val("budget"),
      "Timeline:      " + val("timeline"),
      "",
      "Yours,",
      val("name") + (val("company") ? ", " + val("company") : ""),
      val("email")
    ];
    return {
      subject: "A note about a project — " + (val("company") || val("name")),
      body: lines.join("\n")
    };
  }

  function posted() {
    form.classList.add("is-posted");
    if (okEl) {
      okEl.hidden = false;
      okEl.scrollIntoView({ behavior: reduced ? "auto" : "smooth", block: "center" });
    }
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    if (!validate()) return;

    if (ENDPOINT) {
      fetch(ENDPOINT, { method: "POST", body: new FormData(form), headers: { Accept: "application/json" } })
        .then(function (r) {
          if (r.ok) posted();
          else fail("That did not send. Write to " + TO + " directly and I will pick it up.", "name");
        })
        .catch(function () {
          fail("That did not send — you may be offline. Write to " + TO + " directly.", "name");
        });
      return;
    }

    var msg = compose();
    window.location.href = "mailto:" + TO +
      "?subject=" + encodeURIComponent(msg.subject) +
      "&body=" + encodeURIComponent(msg.body);
    posted();
  });

  form.addEventListener("input", function (e) {
    if (e.target.classList.contains("is-bad")) {
      e.target.classList.remove("is-bad");
      errEl.hidden = true;
    }
  });

  // for verification: exercise validation and composition without opening mail
  return { validate: validate, compose: compose };
})();
