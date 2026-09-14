/* ============================================================
   THE WAGTAIL — a pied wagtail that lives on the page.

   It lands only on real lines: every element marked [data-perch]
   offers its top edge (or its midline, for drawn rules) as
   somewhere to stand. From there it behaves like the bird does:

     · pumps its tail almost constantly, in bursts
     · turns to watch the cursor, and hops towards it along the
       perch — but stops short, keeping a wary distance
     · startles and flies off if the cursor lunges at it
     · follows the reader down the page, flying to a new perch
       whenever its own one scrolls out of view
     · pecks, turns and potters about when left alone
     · calls "chis-ick" if you click right beside it

   version-02 gives it a home: a cage hanging in the corner. When
   there is nowhere left to stand it flies into the cage instead of
   off the screen, and lets itself out again once there is. Click
   the cage to call it home; click again to let it out. On screens
   too narrow for the cage it leaves by the edge, as it used to.

   Under the cage hangs a packet of seeds. Clicking it throws four to
   six seeds onto a line near the bird; it goes to them, bows and
   pecks them up one at a time, and ignores the cursor until the
   last one is gone. Then it sings — notes drift up from its beak,
   and, if the song switch is on, it is heard: a song made with Web
   Audio as it plays, different every time.

   rAF does not run in a hidden tab, so the simulation is also
   exposed for stepping by hand:

     BIRD.step(ms)        advance the simulation and redraw
     BIRD.stats()         what the bird is doing, and where
     BIRD.remap()         re-read the perches from the layout
     BIRD.callHome()      send it to the cage
     BIRD.release()       let it out
     BIRD.feed()          scatter a handful of seeds
     BIRD.sing()          sing now (returns the song's length in ms)
     BIRD.renderSong()    render one song silently and measure it
   ============================================================ */

window.BIRD = (function () {
  "use strict";

  var cv = document.querySelector("[data-bird]");
  var api = { step: function () { return null; }, stats: function () { return null; }, remap: function () {} };
  if (!cv || !cv.getContext) return api;

  var g = cv.getContext("2d");
  var reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  var wagsEl = document.querySelector("[data-wags]");

  var S = 1.38;                        // drawing scale for the bird, out on the page
  var VW = 0, VH = 0, dpr = 1;

  var clamp = function (v, a, b) { return v < a ? a : v > b ? b : v; };
  var rand = function (a, b) { return a + Math.random() * (b - a); };
  var lerp = function (a, b, t) { return a + (b - a) * t; };
  var ease = function (t) { return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2; };

  /* ── state ─────────────────────────────────────────────── */

  // Positions are DOCUMENT coordinates, so a perched bird scrolls with the
  // page like anything else printed on it. Converted to screen when drawn.
  var B = {
    mode: "away",                      // away | flying | perched | caged | entering | leaving
    x: 0, y: 0, face: -1, lift: 0, tilt: 0, scale: S,
    perchEl: null,
    hop: null, rest: 0,
    idle: 0, nextIdle: 2600,
    fly: null, flap: 0,
    wagPhase: 0, wagAmp: 0, wagOn: true, wagTimer: 700,
    peck: 0,
    say: null,
    entered: false,
    cageX: 55, cageRest: 0, releaseAfter: 2000, stayHome: false,
    move: null, doorClose: 0,
    eat: null, bow: 0, seedsEaten: 0, handfuls: 0,
    sing: null, songs: 0,
    wags: 0, flights: 0, hops: 0, homecomings: 0
  };

  // the pointer, in client coordinates — scrolling alone is not movement
  var P = { cx: -9999, cy: -9999, on: false, speed: 0 };

  var perches = [];

  // seeds thrown from the packet, and the crumbs they leave when eaten
  var seeds = [];
  var crumbs = [];
  var MAX_SEEDS = 12;

  /* ── the cage ──────────────────────────────────────────── */

  // The cage is an SVG button in partials/top.html, stacked above this
  // canvas so its bars are drawn in front of the bird. Points on it are given
  // in the SVG's own viewBox units (110 × 180) — keep them in step with the
  // drawing: the ring it hangs from, the perch rod, the door and the room
  // between the bars.
  var cageEl = document.querySelector("[data-cage]");
  var cageTip = document.querySelector("[data-cage-tip]");
  var packEl = document.querySelector("[data-feed]");
  var packTip = document.querySelector("[data-feed-tip]");
  var header = document.querySelector("[data-top]");
  var VB_W = 110;
  var PIVOT = { x: 55, y: 0 };
  var ROD = 128;
  var DOOR = { x: 46, y: 121 };
  var WALL = { x0: 18, x1: 92 };       // just inside the side bars
  var INSIDE = 0.92;                   // the bird's size in the cage, against a 132px-wide cage

  var cage = null;                     // left, top, k (px per unit), w — measured at rest
  var sway = { a: 0, v: 0, shown: "" };  // degrees, degrees per ms

  function measureCage() {
    cage = null;
    if (!cageEl || getComputedStyle(cageEl).display === "none") return;
    // hang it from the bottom edge of the header, whatever height that is
    if (header) {
      var top = Math.round(header.getBoundingClientRect().bottom) + "px";
      if (cageEl.style.top !== top) cageEl.style.top = top;
    }
    // measure without the sway, which would give a rotated bounding box
    var was = cageEl.style.rotate;
    cageEl.style.rotate = "";
    var r = cageEl.getBoundingClientRect();
    cageEl.style.rotate = was;
    if (!r.width) return;
    cage = { left: r.left, top: r.top, k: r.width / VB_W, w: r.width };
    // the seed packet is taped to the page just under the cage
    if (packEl) {
      var pt = Math.round(r.bottom + 18) + "px";
      if (packEl.style.top !== pt) packEl.style.top = pt;
      // and the song switch is lettered just under the packet
      if (songEl) {
        var st = Math.round(packEl.getBoundingClientRect().bottom + 8) + "px";
        if (songEl.style.top !== st) songEl.style.top = st;
      }
    }
  }

  // the bird is drawn smaller inside, sized to the cage rather than the page
  function cageScale() { return cage ? INSIDE * (cage.w / 132) : S; }

  // Where on the rod it can stand without its beak or tail poking through the
  // side bars. The drawing reaches 26 units ahead of the feet and 40 behind;
  // inside, one drawing unit is INSIDE × 110/132 cage units, at any cage size.
  function room(face) {
    var u = INSIDE * VB_W / 132, ahead = 26 * u, behind = 40 * u;
    return face > 0 ? [WALL.x0 + behind, WALL.x1 - ahead] : [WALL.x0 + ahead, WALL.x1 - behind];
  }

  // a point on the cage, in its own units → document coordinates, swinging
  // with the cage about the ring it hangs from
  function cagePoint(ux, uy) {
    var px = cage.left + PIVOT.x * cage.k, py = cage.top + PIVOT.y * cage.k;
    var dx = (ux - PIVOT.x) * cage.k, dy = (uy - PIVOT.y) * cage.k;
    var a = sway.a * Math.PI / 180, c = Math.cos(a), s = Math.sin(a);
    return { x: px + dx * c - dy * s, y: py + dx * s + dy * c + window.scrollY };
  }

  function door(open) { if (cageEl) cageEl.classList.toggle("is-open", open); }
  function nudge(v) { if (!reduced) sway.v += v; }

  function label() {
    if (!cageEl) return;
    var inside = B.mode === "caged" || B.mode === "entering";
    var text = inside ? "let it out" : "call it home";
    if (cageTip && cageTip.textContent !== text) cageTip.textContent = text;
    var aria = inside ? "Let the wagtail out of its cage" : "Call the wagtail back to its cage";
    if (cageEl.getAttribute("aria-label") !== aria) cageEl.setAttribute("aria-label", aria);
  }

  /* ── layout ────────────────────────────────────────────── */

  function resize() {
    dpr = Math.min(2, window.devicePixelRatio || 1);
    VW = document.documentElement.clientWidth;
    VH = window.innerHeight;
    cv.width = Math.max(1, Math.round(VW * dpr));
    cv.height = Math.max(1, Math.round(VH * dpr));
    cv.style.width = VW + "px";
    cv.style.height = VH + "px";
    g.setTransform(dpr, 0, 0, dpr, 0, 0);
    measureCage();
    mapPerches();
  }

  function mapPerches() {
    var sy = window.scrollY;
    var js = document.documentElement.classList.contains("js");
    var els = document.querySelectorAll("[data-perch]");
    perches = [];
    for (var i = 0; i < els.length; i++) {
      var el = els[i];
      // never land on something that has not appeared yet
      var rev = el.closest("[data-reveal]");
      if (js && rev && !rev.classList.contains("is-in")) continue;
      var r = el.getBoundingClientRect();
      if (r.width < 80 || r.height === 0) continue;
      var mode = el.getAttribute("data-perch");
      var y = mode === "mid" ? (r.top + r.bottom) / 2 : mode === "base" ? r.bottom : r.top;
      perches.push({
        el: el,
        x0: r.left + 24,
        x1: r.right - 24,
        y: y + sy,
        first: el.hasAttribute("data-perch-first")
      });
    }
  }

  function perchOf(el) {
    for (var i = 0; i < perches.length; i++) if (perches[i].el === el) return perches[i];
    return null;
  }

  function onScreen(p) {
    var vy = p.y - window.scrollY;
    return vy > VH * 0.16 && vy < VH * 0.93;
  }

  function pickPerch(avoid) {
    var best = null, bestScore = -1e9;
    for (var i = 0; i < perches.length; i++) {
      var p = perches[i];
      if (p.el === B.perchEl || !onScreen(p)) continue;
      var vy = p.y - window.scrollY;
      var score = rand(0, 170) - Math.abs(vy - VH * 0.5) * 0.35;
      if (avoid) {
        var cx = (p.x0 + p.x1) / 2;
        score += Math.min(700, Math.hypot(cx - avoid.x, p.y - avoid.y)) * 1.2;
      }
      if (score > bestScore) { bestScore = score; best = p; }
    }
    return best;
  }

  /* ── movement ──────────────────────────────────────────── */

  function beginFlight(x0, y0, x1, y1, el, home) {
    var dist = Math.hypot(x1 - x0, y1 - y0);
    B.fly = {
      x0: x0, y0: y0, x1: x1, y1: y1,
      cx: (x0 + x1) / 2,
      // a lower arc on the way home: the cage hangs near the top of the screen
      cy: Math.min(y0, y1) - (home ? 26 + dist * 0.05 : 40 + dist * 0.16),
      t: 0,
      dur: clamp(dist * 1.3, 420, 1300),
      el: el,
      home: !!home,
      doorOpened: false
    };
    B.mode = "flying";
    B.hop = null; B.lift = 0; B.peck = 0; B.move = null;
    B.eat = null; B.bow = 0;
    B.scale = S;
    B.face = x1 >= x0 ? 1 : -1;
    B.perchEl = null;
    B.flights++;
  }

  function flyTo(p, tx) {
    var x1 = tx != null ? clamp(tx, p.x0, p.x1) : rand(p.x0, p.x1);
    var x0 = B.x, y0 = B.y;
    if (B.mode === "away") {
      // arrive from whichever side of the screen is nearer the landing spot
      x0 = x1 > VW / 2 ? VW + 50 : -50;
      y0 = window.scrollY + VH * rand(0.08, 0.3);
    }
    beginFlight(x0, y0, x1, p.y, p.el);
  }

  // Nowhere left to stand. With a cage, that means going home; without one
  // (a narrow screen), it leaves by the edge of the screen as it always did.
  function flyAway() {
    if (cage) { flyHome(); return; }
    beginFlight(B.x, B.y, B.face > 0 ? VW + 70 : -70, window.scrollY + VH * rand(0.05, 0.25), null);
  }

  function flyHome() {
    if (!cage) { flyAway(); return; }
    var d = cagePoint(DOOR.x, DOOR.y);
    beginFlight(B.x, B.y, d.x, d.y, null, true);
  }

  // in through the door and onto the rod
  function startEntering() {
    B.mode = "entering";
    B.fly = null; B.tilt = 0; B.hop = null;
    var r = room(1);
    var to = clamp(rand(52, 64), r[0], r[1]);
    B.move = { t: 0, dur: 300, fromX: DOOR.x, fromY: DOOR.y, toX: to, toY: ROD, fromScale: B.scale };
    B.face = 1;
    door(true);
    B.homecomings++;
  }

  // a beat at the door, a hop out, then away to the perch
  function startLeaving(p, tx) {
    B.mode = "leaving";
    B.hop = null; B.peck = 0;
    B.move = { t: 0, wait: 260, dur: 240, fromX: B.cageX, fromY: ROD, toX: DOOR.x, toY: DOOR.y, perch: p, tx: tx };
    B.face = -1;
    door(true);
    nudge(-0.01);
  }

  function hopToward(goal) {
    var d = goal - B.x;
    var s = Math.sign(d) * Math.min(Math.abs(d), 26);
    B.hop = { from: B.x, to: B.x + s, t: 0 };
    B.face = s >= 0 ? 1 : -1;
    B.hops++;
  }

  /* ── the simulation ────────────────────────────────────── */

  function step(dt) {
    var sy = window.scrollY;
    P.speed *= Math.pow(0.8, dt / 16);
    stepSeeds(dt);
    if (B.sing) singStep(dt);
    else if (!B.eat && B.bow) B.bow = Math.abs(B.bow) < 0.002 ? 0 : B.bow - B.bow * Math.min(1, dt / 70);

    // the cage: a damped spring, kicked when the bird lands in it or leaves
    if (cage && !reduced) {
      sway.v += (-sway.a * 0.00005 - sway.v * 0.0034) * dt;
      sway.a += sway.v * dt;
      if (Math.abs(sway.a) < 0.02 && Math.abs(sway.v) < 0.0004) { sway.a = 0; sway.v = 0; }
      var shown = sway.a === 0 ? "" : sway.a.toFixed(2) + "deg";
      if (shown !== sway.shown) { cageEl.style.rotate = shown; sway.shown = shown; }
    }
    if (B.doorClose > 0) {
      B.doorClose -= dt;
      var passing = B.mode === "entering" || B.mode === "leaving" || (B.fly && B.fly.home && B.fly.doorOpened);
      if (B.doorClose <= 0 && !passing) door(false);
    }

    // tail: pumped in bursts, and only while standing
    B.wagTimer -= dt;
    if (B.wagTimer <= 0) {
      B.wagOn = !B.wagOn;
      B.wagTimer = B.wagOn ? rand(700, 1900) : rand(250, 1100);
    }
    var standing = B.mode === "perched" || B.mode === "caged";
    B.wagAmp += ((standing && B.wagOn ? 1 : 0) - B.wagAmp) * Math.min(1, dt / 90);
    var before = Math.sin(B.wagPhase);
    B.wagPhase += dt * 0.017;
    if (before < 0 && Math.sin(B.wagPhase) >= 0 && B.wagAmp > 0.55) B.wags++;

    if (B.say) { B.say.t += dt; if (B.say.t > 1100) B.say = null; }
    if (B.peck > 0) B.peck = Math.max(0, B.peck - dt);

    /* flying */
    if (B.mode === "flying") {
      var f = B.fly;
      // seeds are more interesting than wherever it was going
      if (!B.stayHome) {
        var snack = nearestFood();
        if (snack && f.el !== snack.p.el) {
          if (f.home && f.doorOpened) B.doorClose = 300;
          beginFlight(B.x, B.y, standFor(snack, B.x), snack.p.y, snack.p.el);
          f = B.fly;
        }
      }
      var target = f.el && perchOf(f.el);
      if (target) f.y1 = target.y;             // the landing line may have moved
      if (f.home) {
        if (cage) {
          var dp = cagePoint(DOOR.x, DOOR.y);  // the page may scroll mid-flight
          f.x1 = dp.x; f.y1 = dp.y;
        } else {
          f.home = false;                      // the cage went away (a resize)
        }
      }
      f.t += dt;
      var u = Math.min(1, f.t / f.dur);
      var e = ease(u);
      var ie = 1 - e;
      var nx = ie * ie * f.x0 + 2 * ie * e * f.cx + e * e * f.x1;
      // wagtails fly in bounding undulations, not straight glides
      var ny = ie * ie * f.y0 + 2 * ie * e * f.cy + e * e * f.y1 +
               Math.sin(e * Math.PI * 3) * 7 * (1 - Math.abs(2 * e - 1));
      B.tilt = clamp(Math.atan2(ny - B.y, Math.abs(nx - B.x) + 0.001), -0.5, 0.5);
      B.x = nx; B.y = ny;
      B.flap += dt * 0.045;
      if (f.home) {
        if (!f.doorOpened && u > 0.55) { f.doorOpened = true; door(true); }
        // it seems to draw away into the cage as it nears the door
        B.scale = lerp(S, cageScale() * 1.15, clamp((u - 0.6) / 0.4, 0, 1));
      }
      if (u >= 1) {
        B.tilt = 0;
        B.fly = null;
        if (target) {
          B.mode = "perched";
          B.perchEl = f.el;
          B.y = target.y;
          B.idle = 0; B.nextIdle = rand(1800, 3800);
          B.rest = 280;
        } else if (f.home && cage) {
          startEntering();
        } else {
          B.mode = "away";
          B.idle = 0;
        }
      }
      return;
    }

    /* entering: through the door and onto the rod */
    if (B.mode === "entering") {
      if (!cage) { B.mode = "away"; B.move = null; door(false); return; }
      var m = B.move;
      m.t += dt;
      var et = clamp(m.t / m.dur, 0, 1), ee = ease(et);
      var ip = cagePoint(lerp(m.fromX, m.toX, ee), lerp(m.fromY, m.toY, ee));
      B.x = ip.x; B.y = ip.y;
      B.lift = Math.sin(et * Math.PI) * 5;
      B.scale = lerp(m.fromScale, cageScale(), ee);
      if (et >= 1) {
        B.mode = "caged";
        B.cageX = m.toX;
        B.move = null; B.lift = 0;
        B.cageRest = 0; B.releaseAfter = rand(1600, 2800);
        B.idle = 0; B.nextIdle = rand(900, 1800);
        B.doorClose = 280;
        nudge(0.016);
      }
      return;
    }

    /* leaving: a beat at the door, a hop out, then away */
    if (B.mode === "leaving") {
      if (!cage) { B.mode = "away"; B.move = null; return; }
      var lm = B.move;
      lm.t += dt;
      var lt = clamp((lm.t - lm.wait) / lm.dur, 0, 1), le = ease(lt);
      var op = cagePoint(lerp(lm.fromX, lm.toX, le), lerp(lm.fromY, lm.toY, le));
      B.x = op.x; B.y = op.y;
      B.lift = Math.sin(lt * Math.PI) * 5;
      B.scale = lerp(cageScale(), S, le);
      if (lt >= 1) {
        var goal = perchOf(lm.perch.el) || lm.perch;   // the perch list is rebuilt as the page moves
        B.lift = 0;
        B.doorClose = 520;
        var x1 = lm.tx != null ? clamp(lm.tx, goal.x0, goal.x1) : rand(goal.x0, goal.x1);
        beginFlight(B.x, B.y, x1, goal.y, goal.el);
      }
      return;
    }

    /* caged: at home, until there is somewhere to go */
    if (B.mode === "caged") {
      if (!cage) { B.mode = "away"; B.idle = 0; return; }
      B.scale = cageScale();
      var home = cagePoint(B.cageX, ROD);
      var hx = P.cx, hy = P.cy + sy;
      // it still watches the cursor, through the bars
      if (P.on && !B.hop && Math.hypot(hx - home.x, hy - home.y) < 560 && Math.abs(hx - home.x) > 10) {
        B.face = hx >= home.x ? 1 : -1;
      }
      // turning round can leave its tail through the bars: shuffle along
      if (!B.hop) {
        var rm = room(B.face);
        if (B.cageX < rm[0] - 0.5 || B.cageX > rm[1] + 0.5) {
          B.hop = { from: B.cageX, to: clamp(B.cageX, rm[0], rm[1]), t: 0 };
        }
      }
      if (B.hop) {
        B.hop.t += dt;
        var chu = Math.min(1, B.hop.t / 170);
        B.cageX = lerp(B.hop.from, B.hop.to, chu);
        B.lift = Math.sin(chu * Math.PI) * 5;
        if (chu >= 1) { B.hop = null; B.lift = 0; nudge(0.004); }
      }
      var at = cagePoint(B.cageX, ROD);
      B.x = at.x; B.y = at.y;

      // let itself out once there is somewhere to stand — unless it was called home
      B.cageRest += dt;
      // seeds bring it straight out
      if (B.entered && !B.stayHome && !B.hop) {
        var meal = nearestFood();
        if (meal) { startLeaving(meal.p, standFor(meal, cagePoint(DOOR.x, DOOR.y).x)); return; }
      }
      if (B.entered && !B.stayHome && !B.hop && B.cageRest > B.releaseAfter) {
        var out = pickPerch();
        if (out) { startLeaving(out); return; }
        B.releaseAfter = B.cageRest + 900;           // look again shortly
      }

      // potter about inside
      B.idle += dt;
      if (!B.hop && B.idle > B.nextIdle) {
        B.idle = 0;
        B.nextIdle = rand(1400, 3200);
        var cr = Math.random();
        if (cr < 0.45) {
          var dir = Math.random() < 0.5 ? -1 : 1;
          var ri = room(dir);
          var to = clamp(B.cageX + dir * rand(8, 16), ri[0], ri[1]);
          if (Math.abs(to - B.cageX) > 3) {
            B.hop = { from: B.cageX, to: to, t: 0 };
            B.face = dir;
            B.hops++;
          } else {
            B.face = dir;
          }
        } else if (cr < 0.75) {
          B.peck = 520;
        } else {
          B.face *= -1;
        }
      }
      return;
    }

    /* away: off-screen, only when there is no cage to go to */
    if (B.mode === "away") {
      if (!B.entered) return;
      var feedAt = nearestFood();
      if (feedAt) { flyTo(feedAt.p, standFor(feedAt, feedAt.x > VW / 2 ? VW : 0)); return; }
      B.idle += dt;
      if (B.idle > 700) {
        B.idle = 0;
        var landing = pickPerch();
        if (landing) flyTo(landing);
      }
      return;
    }

    /* perched */
    var p = perchOf(B.perchEl);
    if (!p || !onScreen(p)) {
      var next = pickPerch();
      if (next) flyTo(next); else flyAway();
      return;
    }
    B.y = p.y;
    B.x = clamp(B.x, p.x0 - 4, p.x1 + 4);

    if (B.sing) return;                    // mid-song, it does nothing else

    // food: it goes to it, and is too busy eating to mind the cursor
    if (B.eat) { eating(dt); return; }
    var food = nearestFood();
    if (food) {
      if (food.p.el !== B.perchEl) { flyTo(food.p, standFor(food, B.x)); return; }
      forage(food, dt);
      return;
    }

    var px = P.cx, py = P.cy + sy;
    var dPointer = Math.hypot(px - B.x, py - (B.y - 18));

    // startle: a lunge, or simply getting too close
    if (P.on && ((P.speed > 24 && dPointer < 120) || dPointer < 26)) {
      var escape = pickPerch({ x: px, y: py });
      if (escape) flyTo(escape); else flyAway();
      return;
    }

    // it keeps an eye on the cursor from much further off than it will
    // approach it — a bird that looks away from you reads as broken
    var watching = P.on && dPointer < 560;
    if (watching && !B.hop && Math.abs(px - B.x) > 14) B.face = px >= B.x ? 1 : -1;

    if (B.hop) {
      B.hop.t += dt;
      var hu = Math.min(1, B.hop.t / 170);
      B.x = B.hop.from + (B.hop.to - B.hop.from) * hu;
      B.lift = Math.sin(hu * Math.PI) * 7;
      if (hu >= 1) { B.hop = null; B.lift = 0; B.rest = rand(70, 170); }
      return;
    }
    if (B.rest > 0) { B.rest -= dt; return; }

    // curiosity: the cursor is near this line
    var near = P.on && Math.abs(py - B.y) < 180 && px > p.x0 - 80 && px < p.x1 + 80;
    if (near) {
      if (Math.abs(px - B.x) > 12) B.face = px >= B.x ? 1 : -1;
      var aim = clamp(px - B.face * 46, p.x0, p.x1);     // stop short of it
      if (Math.abs(aim - B.x) > 16) hopToward(aim);
      B.idle = 0;
      return;
    }

    // left alone: potter about — and now and then, pop home for a while
    B.idle += dt;
    if (B.idle > B.nextIdle) {
      B.idle = 0;
      B.nextIdle = rand(2200, 4600);
      var r = Math.random();
      if (r < 0.34) hopToward(clamp(B.x + (Math.random() < 0.5 ? -1 : 1) * rand(30, 80), p.x0, p.x1));
      else if (r < 0.58) { if (!watching) B.face *= -1; else B.peck = 520; }
      else if (r < 0.86) B.peck = 520;
      else if (cage && r < 0.9) { B.stayHome = false; flyHome(); }
      else { var wander = pickPerch(); if (wander) flyTo(wander); }
    }
  }

  /* ── seeds ─────────────────────────────────────────────── */

  // Each seed belongs to a line, stored as a fraction of the way along it, so
  // it stays put on the page however the layout moves.
  function seedPos(s) {
    var p = perchOf(s.el);
    if (p) { s.lx = p.x0 + s.rel * (p.x1 - p.x0); s.ly = p.y; }
    return p;
  }

  // the nearest seed it can see; ones still in the air count for less
  function nearestFood() {
    var best = null, bestD = 1e9;
    for (var i = 0; i < seeds.length; i++) {
      var s = seeds[i];
      if (s.state === "eaten") continue;
      var p = perchOf(s.el);
      if (!p || !onScreen(p)) continue;
      var x = p.x0 + s.rel * (p.x1 - p.x0);
      var d = Math.hypot(x - B.x, p.y - B.y) + (s.state === "ground" ? 0 : 400);
      if (d < bestD) { bestD = d; best = { seed: s, p: p, x: x }; }
    }
    return best;
  }

  // Where to stand to eat a seed: one beak's reach to its side — the side
  // nearer the bird, unless that would be off the end of the line. The reach
  // is where the beak meets the ground at the bottom of a peck, in drawing units.
  var REACH = 29.5;
  function standFor(food, fromX) {
    var p = food.p, r = REACH * S, lo = p.x0 - 4, hi = p.x1 + 4;
    var left = food.x - r, right = food.x + r;
    var okL = left >= lo, okR = right <= hi;
    if (okL && (!okR || Math.abs(left - fromX) <= Math.abs(right - fromX))) return left;
    if (okR) return right;
    return clamp(left, lo, hi);
  }

  // on its way to the next seed: small quick hops, then wait for it to land
  function forage(food, dt) {
    if (B.hop) {
      B.hop.t += dt;
      var hu = Math.min(1, B.hop.t / 150);
      B.x = lerp(B.hop.from, B.hop.to, hu);
      B.lift = Math.sin(hu * Math.PI) * 6;
      if (hu >= 1) { B.hop = null; B.lift = 0; B.rest = rand(40, 110); }
      return;
    }
    if (B.rest > 0) { B.rest -= dt; return; }
    var stand = standFor(food, B.x);
    if (Math.abs(stand - B.x) > 5) { hopToward(stand); return; }
    B.face = B.x <= food.x ? 1 : -1;
    if (food.seed.state !== "ground") return;
    B.peck = 0;
    B.eat = { t: 0, dur: 700, seed: food.seed, done: false };
  }

  // a bow, a peck that takes the seed, a second peck, and up again
  function eating(dt) {
    var e = B.eat;
    e.t += dt;
    var u = Math.min(1, e.t / e.dur);
    B.bow = 0.42 * Math.min(1, Math.sin(Math.PI * u) * 1.8);
    if (!e.done && u >= 1 / 6) {
      e.done = true;
      if (e.seed.state !== "eaten") {
        e.seed.state = "eaten";
        B.seedsEaten++;
        for (var i = 0; i < 3; i++) {
          crumbs.push({ x: e.seed.lx, y: e.seed.ly - 2, vx: rand(-0.06, 0.06), vy: -rand(0.04, 0.1), age: 0 });
        }
      }
    }
    if (u >= 1) {
      B.eat = null;
      B.rest = rand(120, 300);
      if (!nearestFood()) {
        // all gone: a song, and a good long wag
        startSong();
        B.wagOn = true; B.wagTimer = 1500;
        B.idle = 0; B.nextIdle = rand(2400, 4200);
      }
    }
  }

  function stepSeeds(dt) {
    for (var i = seeds.length - 1; i >= 0; i--) {
      var s = seeds[i];
      if (s.state === "eaten" || !s.el.isConnected) { seeds.splice(i, 1); continue; }
      seedPos(s);
      if (s.state === "air") {
        s.t += dt;
        if (s.t >= s.dur) { s.state = "ground"; s.bounce = 200; s.rot = rand(-0.4, 0.4); }
        else if (s.t > 0) s.rot += s.spin * dt;
      } else if (s.bounce > 0) {
        s.bounce = Math.max(0, s.bounce - dt);
      }
    }
    for (var j = crumbs.length - 1; j >= 0; j--) {
      var c = crumbs[j];
      c.age += dt;
      if (c.age > 380) { crumbs.splice(j, 1); continue; }
      c.vy += 0.0005 * dt;
      c.x += c.vx * dt;
      c.y += c.vy * dt;
    }
    for (var m = notes.length - 1; m >= 0; m--) {
      var nt = notes[m];
      nt.age += dt;
      if (nt.age > nt.life) { notes.splice(m, 1); continue; }
      nt.x += nt.vx * dt;
      nt.y += nt.vy * dt;
    }
  }

  // Where the seeds are thrown from: the mouth of the packet, or the top
  // corner of the screen when there is no packet to be seen.
  function mouth() {
    var sy = window.scrollY;
    if (packEl && getComputedStyle(packEl).display !== "none") {
      var r = packEl.getBoundingClientRect();
      if (r.width) return { x: r.left + r.width * 0.3, y: r.top + r.height * 0.12 + sy };
    }
    return { x: VW - 40, y: sy + VH * 0.12 };
  }

  // The line to scatter them on: the bird's own, if it is standing on one in
  // view; otherwise the nearest line in view to where they are thrown from.
  function feedingLine(from) {
    if (B.mode === "perched") {
      var own = perchOf(B.perchEl);
      if (own && onScreen(own) && own.x1 - own.x0 >= 60) return own;
    }
    var best = null, bestD = 1e9;
    for (var i = 0; i < perches.length; i++) {
      var p = perches[i];
      if (!onScreen(p) || p.x1 - p.x0 < 120) continue;
      var d = Math.hypot(clamp(from.x, p.x0, p.x1) - from.x, p.y - from.y);
      if (d < bestD) { bestD = d; best = p; }
    }
    return best;
  }

  // Throw four to six seeds. Returns how many, 0 if it already has plenty,
  // or -1 if there is no line in view to throw them onto.
  function feed() {
    mapPerches();
    var live = 0;
    for (var i = 0; i < seeds.length; i++) if (seeds[i].state !== "eaten") live++;
    if (live > MAX_SEEDS - 4) return 0;
    var from = mouth();
    var p = feedingLine(from);
    if (!p) return -1;
    var n = 4 + Math.floor(Math.random() * 3);
    var lo = p.x0 + 40, hi = p.x1 - 40;
    if (hi < lo) lo = hi = (p.x0 + p.x1) / 2;
    var spread = Math.min(hi - lo, (n - 1) * rand(13, 19));
    var centre = p.el === B.perchEl ? B.x + B.face * rand(70, 120) : clamp(from.x, p.x0, p.x1) - rand(30, 90);
    centre = clamp(centre, lo + spread / 2, hi - spread / 2);
    for (var k = 0; k < n; k++) {
      var x = clamp(centre - spread / 2 + spread * k / (n - 1) + rand(-4, 4), lo, hi);
      seeds.push({
        el: p.el, rel: (x - p.x0) / Math.max(1, p.x1 - p.x0), lx: x, ly: p.y,
        state: reduced ? "ground" : "air",
        x0: from.x + rand(-3, 3), y0: from.y,
        t: -k * 70 - rand(0, 30), dur: clamp(Math.hypot(x - from.x, p.y - from.y) * 0.8, 420, 950),
        rot: rand(0, 3), spin: rand(-0.02, 0.02), bounce: 0
      });
    }
    B.stayHome = false;              // seeds are an invitation out, even after being called home
    B.handfuls++;
    return n;
  }

  /* ── song ──────────────────────────────────────────────── */

  // Fed, it sings: a twitter of short whistled notes around its "chis-ick"
  // call, synthesised with Web Audio as it plays — there are no sound files,
  // and every song is different. The notes drift up from its beak whether or
  // not the sound is on. Browsers only allow sound after a click, so the
  // audio is started by the click on the seed packet or the song switch;
  // nothing plays on its own.
  var songEl = document.querySelector("[data-song]");
  var songLabel = document.querySelector("[data-song-label]");
  var songOn = true;
  try { songOn = localStorage.getItem("fj-song") !== "off"; } catch (e) {}

  var notes = [];                        // the musical notes drawn drifting up
  var audio = null, bus = null, panner = null, scheduled = 0;

  function unlockAudio() {
    if (!songOn) return null;
    if (!audio) {
      var AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) return null;
      try { audio = new AC(); } catch (e) { return null; }
      bus = audio.createGain();
      bus.gain.value = 0.08;               // high whistles carry: keep it gentle
      if (audio.createStereoPanner) {
        panner = audio.createStereoPanner();
        bus.connect(panner);
        panner.connect(audio.destination);
      } else {
        bus.connect(audio.destination);
      }
    }
    if (audio.state === "suspended" && audio.resume) {
      var p = audio.resume();
      if (p && p.catch) p.catch(function () {});
    }
    return audio;
  }

  // "chis-ick": a falling slur, then a short blip that rises and falls
  function chisick(list, at) {
    list.push({ at: at, dur: 0.07, f0: 7400, f1: 4700 });
    list.push({ at: at + 0.1, dur: 0.055, f0: 5000, f1: 6900, f2: 5600 });
    return at + 0.26;
  }

  // times and pitches in seconds and hertz; the wagtail's song is a rapid,
  // uneven twitter built out of call-like notes
  function composeSong() {
    var list = [];
    var t = chisick(list, 0.02);
    var phrases = 2 + Math.floor(Math.random() * 2);
    for (var p = 0; p < phrases; p++) {
      var n = 4 + Math.floor(Math.random() * 4);
      var base = rand(4300, 6200);
      for (var i = 0; i < n; i++) {
        var d = rand(0.03, 0.07), up = Math.random() < 0.5;
        list.push({
          at: t, dur: d,
          f0: base * (up ? 0.84 : 1.16), f1: base * (up ? 1.18 : 0.82),
          trill: Math.random() < 0.3 ? rand(35, 60) : 0,
          vol: rand(0.6, 1)
        });
        t += d + rand(0.025, 0.06);
        base = clamp(base * rand(0.9, 1.1), 3800, 7000);
      }
      t += rand(0.08, 0.16);
      if (Math.random() < 0.4) t = chisick(list, t);
    }
    t = chisick(list, t);
    return { notes: list, dur: t + 0.1 };
  }

  // one whistled note: a sine sliding between pitches, sometimes trilled,
  // with a fast attack and a quick fall so the notes stay crisp
  function tone(ac, dest, t, n) {
    var o = ac.createOscillator(), env = ac.createGain();
    o.type = "sine";
    o.frequency.setValueAtTime(n.f0, t);
    if (n.f2) {
      o.frequency.exponentialRampToValueAtTime(n.f1, t + n.dur * 0.45);
      o.frequency.exponentialRampToValueAtTime(n.f2, t + n.dur);
    } else {
      o.frequency.exponentialRampToValueAtTime(n.f1, t + n.dur);
    }
    if (n.trill) {
      var lfo = ac.createOscillator(), depth = ac.createGain();
      lfo.frequency.value = n.trill;
      depth.gain.value = n.f0 * 0.07;
      lfo.connect(depth);
      depth.connect(o.frequency);
      lfo.start(t);
      lfo.stop(t + n.dur + 0.03);
    }
    var peak = n.vol || 0.9;
    env.gain.setValueAtTime(0.0001, t);
    env.gain.exponentialRampToValueAtTime(peak, t + Math.min(0.01, n.dur * 0.25));
    env.gain.setValueAtTime(peak, t + n.dur * 0.6);
    env.gain.exponentialRampToValueAtTime(0.0001, t + n.dur);
    o.connect(env);
    env.connect(dest);
    o.start(t);
    o.stop(t + n.dur + 0.03);
  }

  function schedule(ac, dest, song, t0) {
    for (var i = 0; i < song.notes.length; i++) tone(ac, dest, t0 + song.notes[i].at, song.notes[i]);
    return song.notes.length;
  }

  function startSong() {
    var song = composeSong();
    B.sing = { t: 0, dur: song.dur * 1000, notes: song.notes, next: 0 };
    B.songs++;
    if (songOn && audio && audio.state === "running") {
      if (panner) panner.pan.setValueAtTime(clamp(B.x / Math.max(1, VW) * 2 - 1, -1, 1) * 0.6, audio.currentTime);
      scheduled += schedule(audio, bus, song, audio.currentTime + 0.03);
    }
    return song;
  }

  function spawnNote() {
    var sc = B.scale;
    notes.push({
      x: B.x + B.face * 24 * sc, y: B.y - 30 * sc - B.lift,
      vx: B.face * rand(0.008, 0.025), vy: -rand(0.03, 0.045),
      age: 0, life: rand(1100, 1500),
      glyph: Math.random() < 0.6 ? "♪" : "♫", sway: rand(0, 6)
    });
  }

  // head up while singing, and a drifting note for every third one sung
  function singStep(dt) {
    var s = B.sing;
    s.t += dt;
    if (B.mode === "perched") B.bow += (-0.14 - B.bow) * Math.min(1, dt / 120);
    else B.bow = 0;
    while (s.next < s.notes.length && s.notes[s.next].at * 1000 <= s.t) {
      if (s.next % 3 === 0 && B.mode !== "away") spawnNote();
      s.next++;
    }
    if (s.t >= s.dur) {
      B.sing = null;
      B.idle = 0;
      B.nextIdle = rand(1800, 3200);
    }
  }

  // Reduced motion: the same song, heard, but the notes stand still beside it
  function singStill() {
    var song = startSong();
    var sc = B.scale;
    notes = [0, 1, 2].map(function (i) {
      return { x: B.x + B.face * (22 + i * 14) * sc, y: B.y - (34 + i * 12) * sc, vx: 0, vy: 0,
        age: 400, life: 1000, glyph: i % 2 ? "♫" : "♪", sway: 0 };
    });
    draw();
    setTimeout(function () { B.sing = null; B.bow = 0; notes = []; draw(); }, Math.min(2400, song.dur * 1000));
  }

  function drawNotes() {
    if (!notes.length) return;
    var sy = window.scrollY;
    g.save();
    g.fillStyle = COL.call;
    g.textAlign = "center";
    g.font = "25px 'Segoe UI Symbol', 'Apple Symbols', 'Noto Music', serif";
    for (var i = 0; i < notes.length; i++) {
      var n = notes[i], u = n.age / n.life;
      g.globalAlpha = u < 0.12 ? u / 0.12 : 1 - Math.max(0, (u - 0.55) / 0.45);
      g.fillText(n.glyph, n.x + Math.sin(n.sway + n.age * 0.006) * 4, n.y - sy);
    }
    g.restore();
  }

  function paintSong() {
    if (!songEl) return;
    songEl.setAttribute("aria-pressed", songOn ? "true" : "false");
    if (songLabel) songLabel.textContent = songOn ? "song on" : "song off";
  }

  function onSongClick() {
    songOn = !songOn;
    try { localStorage.setItem("fj-song", songOn ? "on" : "off"); } catch (e) {}
    paintSong();
    var ac = songOn && unlockAudio();
    if (!ac) return;
    // a call, to show it can be heard
    var go = function () {
      if (ac.state !== "running") return;
      if (panner) panner.pan.setValueAtTime(0.6, ac.currentTime);
      var c = [];
      chisick(c, 0);
      scheduled += schedule(ac, bus, { notes: c }, ac.currentTime + 0.03);
    };
    if (ac.state === "running") go();
    else if (ac.resume) ac.resume().then(go, function () {});
  }

  /* ── drawing ───────────────────────────────────────────── */

  // Colours come from CSS custom properties, so the bird is recoloured with the
  // page: a black-and-white bird on a dark palette needs a light outline to
  // be seen at all. These defaults match the original notebook palette.
  var COL = {
    ink: "#1C1916", back: "#3A3631", wing: "#26231F", white: "#FBF7EE",
    out: "rgba(28, 25, 22, .9)", shadow: "rgba(38, 34, 30, .13)", leg: "#2A2622", call: "#A2432B",
    seed: "#B98A4B"
  };
  function readColours() {
    var cs = getComputedStyle(document.documentElement);
    var pick = function (prop, key) {
      var v = cs.getPropertyValue(prop).trim();
      if (v) COL[key] = v;
    };
    pick("--bird-ink", "ink"); pick("--bird-back", "back"); pick("--bird-wing", "wing");
    pick("--bird-white", "white"); pick("--bird-outline", "out"); pick("--bird-shadow", "shadow");
    pick("--bird-leg", "leg"); pick("--red", "call"); pick("--seed", "seed");
  }

  function ellipse(x, y, rx, ry, rot) {
    g.beginPath();
    g.ellipse(x, y, rx, ry, rot || 0, 0, Math.PI * 2);
  }

  // local coordinates: feet at (0, 0), facing +x
  function drawBird() {
    var flying = B.mode === "flying";
    var sc = B.scale;
    var sx = B.x, sy = B.y - window.scrollY - B.lift;
    if (sx < -90 || sx > VW + 90 || sy < -90 || sy > VH + 90) return;

    if (B.mode === "perched") {
      g.fillStyle = COL.shadow;
      ellipse(sx, B.y - window.scrollY + 1, 16 * sc * (1 - B.lift / 20), 2.6 * sc);
      g.fill();
    }

    g.save();
    g.translate(sx, sy);
    g.scale(B.face * sc, sc);
    if (flying) g.rotate(B.tilt);
    g.lineJoin = "round";
    g.lineCap = "round";

    // legs, tucked away in flight
    g.strokeStyle = COL.leg;
    g.lineWidth = 1.3 / sc;
    g.beginPath();
    if (flying) {
      g.moveTo(-2, -10); g.lineTo(-7, -8);
      g.moveTo(2, -10); g.lineTo(-3, -8);
    } else {
      g.moveTo(-3, -9); g.lineTo(-4, 0); g.lineTo(-8, 0.5); g.moveTo(-4, 0); g.lineTo(0.5, 0.3);
      g.moveTo(3, -9); g.lineTo(3.5, 0); g.lineTo(-0.5, 0.5); g.moveTo(3.5, 0); g.lineTo(8, 0.4);
    }
    g.stroke();

    // bowing to eat: everything above the legs tips forward at the hip
    // (a negative bow is the upright stance it sings in)
    if (!flying && Math.abs(B.bow) > 0.001) { g.translate(0, -9); g.rotate(B.bow); g.translate(0, 9); }

    // the tail: long, black, white-edged, pumping about its base
    var wag = Math.sin(B.wagPhase) * B.wagAmp;
    g.save();
    g.translate(-12, -17);
    g.rotate(flying ? 0.05 : -0.1 + wag * 0.34);
    g.fillStyle = COL.ink;
    g.beginPath();
    g.moveTo(0, -2.6); g.lineTo(-27, -2.2); g.lineTo(-28, 2.4); g.lineTo(0, 2.8);
    g.closePath();
    g.fill();
    g.fillStyle = COL.white;
    g.fillRect(-27, -2.3, 22, 1.1);
    g.fillRect(-27, 1.3, 22, 1.1);
    g.restore();

    // body
    g.fillStyle = COL.back;
    g.strokeStyle = COL.out;
    g.lineWidth = 1.1 / sc;
    ellipse(0, -17, 15, 8.8, -0.14);
    g.fill(); g.stroke();
    g.fillStyle = COL.white;
    ellipse(3, -12.6, 11.5, 4.8, 0.05);
    g.fill();
    g.fillStyle = COL.ink;
    ellipse(10.5, -15.5, 5.2, 4.6, 0.3);          // the black bib
    g.fill();

    // wing: folded at rest, beating in flight
    g.fillStyle = COL.wing;
    if (flying) {
      var fl = Math.sin(B.flap);
      g.beginPath();
      g.moveTo(4, -21);
      g.quadraticCurveTo(-6, -21 - 18 * fl, -16, -18 - 22 * fl);
      g.quadraticCurveTo(-6, -17, 4, -17);
      g.fill();
      g.strokeStyle = COL.white;
      g.beginPath();
      g.moveTo(1, -20);
      g.quadraticCurveTo(-6, -20 - 12 * fl, -11, -18 - 14 * fl);
      g.stroke();
    } else {
      ellipse(-3, -18.5, 10.5, 5, -0.18);
      g.fill();
      g.strokeStyle = COL.white;
      g.beginPath();
      g.moveTo(-9, -19.5);
      g.quadraticCurveTo(-2, -22, 5, -19.5);
      g.stroke();
    }

    // head, which dips when it pecks
    var dip = 0;
    if (B.peck > 0) {
      var pu = 1 - B.peck / 520;
      dip = Math.max(0, Math.sin(pu * Math.PI * 2)) * 6.5;
    }
    if (B.eat) {
      // two pecks, right down to the line
      dip = Math.max(0, Math.sin(Math.min(1, B.eat.t / B.eat.dur) * Math.PI * 3)) * 10;
    }
    g.save();
    g.translate(dip * 0.35, dip);
    // singing: head thrown back, and the beak open on each note
    var open = 0;
    if (B.sing) {
      if (!flying) { g.translate(11, -22); g.rotate(-0.24); g.translate(-11, 22); }
      var sgt = B.sing.t / 1000;
      for (var k = 0; k < B.sing.notes.length; k++) {
        var sn = B.sing.notes[k];
        if (sn.at > sgt) break;
        if (sgt <= sn.at + sn.dur + 0.03) { open = 1.7; break; }
      }
    }
    g.fillStyle = COL.ink;
    g.beginPath(); g.arc(13, -25, 7, 0, Math.PI * 2); g.fill();
    g.fillStyle = COL.white;
    ellipse(15.6, -23.3, 4.6, 3.6, 0.1);
    g.fill();
    g.fillStyle = COL.ink;
    g.beginPath(); g.arc(16.2, -25.9, 1.35, 0, Math.PI * 2); g.fill();
    g.fillStyle = COL.white;
    g.beginPath(); g.arc(16.6, -26.3, 0.45, 0, Math.PI * 2); g.fill();
    g.fillStyle = COL.ink;
    if (open) {
      g.beginPath(); g.moveTo(19.5, -25.6); g.lineTo(26, -25 - open); g.lineTo(19.6, -24.4); g.closePath(); g.fill();
      g.beginPath(); g.moveTo(19.5, -24.4); g.lineTo(25, -23.6 + open); g.lineTo(19.6, -23.2); g.closePath(); g.fill();
    } else {
      g.beginPath(); g.moveTo(19.5, -25.6); g.lineTo(26, -24.4); g.lineTo(19.6, -23.2); g.closePath(); g.fill();
    }
    g.restore();

    g.restore();

    // its call, lettered in red pencil and drifting up
    if (B.say) {
      var su = B.say.t / 1100;
      g.save();
      g.globalAlpha = su < 0.15 ? su / 0.15 : 1 - Math.max(0, (su - 0.6) / 0.4);
      g.fillStyle = COL.call;
      g.font = "600 20px Caveat, 'Segoe Print', cursive";
      g.textAlign = "center";
      g.fillText("chis-ick!", sx + B.face * 10, sy - 44 * sc / S - su * 16);
      g.restore();
    }
  }

  // a seed in the air follows a thrown arc; on the ground it sits on its line
  function seedAt(s) {
    var tx = s.lx, ty = s.ly - 2;
    if (s.state === "air") {
      if (s.t <= 0) return null;
      var u = s.t / s.dur, iu = 1 - u;
      var cx = (s.x0 + tx) / 2, cy = Math.min(s.y0, ty) - 46 - Math.abs(tx - s.x0) * 0.12;
      return { x: iu * iu * s.x0 + 2 * iu * u * cx + u * u * tx, y: iu * iu * s.y0 + 2 * iu * u * cy + u * u * ty };
    }
    return { x: tx, y: ty - Math.sin((s.bounce / 200) * Math.PI) * 3 };
  }

  function drawSeeds() {
    var sy = window.scrollY;
    g.lineWidth = 0.8;
    g.fillStyle = COL.seed;
    g.strokeStyle = COL.out;
    for (var i = 0; i < seeds.length; i++) {
      if (seeds[i].state === "eaten") continue;
      var at = seedAt(seeds[i]);
      if (!at || at.y - sy < -10 || at.y - sy > VH + 10) continue;
      ellipse(at.x, at.y - sy, 2.9, 1.8, seeds[i].rot);
      g.fill();
      g.stroke();
    }
  }

  function drawCrumbs() {
    if (!crumbs.length) return;
    var sy = window.scrollY;
    g.fillStyle = COL.seed;
    for (var i = 0; i < crumbs.length; i++) {
      var c = crumbs[i];
      g.globalAlpha = 1 - c.age / 380;
      g.fillRect(c.x - 0.8, c.y - sy - 0.8, 1.6, 1.6);
    }
    g.globalAlpha = 1;
  }

  function draw() {
    g.clearRect(0, 0, VW, VH);
    drawSeeds();
    if (B.mode !== "away") drawBird();
    drawCrumbs();
    drawNotes();
  }

  var shownWags = -1;
  function paintCount() {
    if (!wagsEl || B.wags === shownWags) return;
    shownWags = B.wags;
    wagsEl.textContent = B.wags.toLocaleString();
  }

  /* ── input ─────────────────────────────────────────────── */

  addEventListener("pointermove", function (e) {
    if (e.pointerType === "touch") return;
    if (P.on) {
      var d = Math.hypot(e.clientX - P.cx, e.clientY - P.cy);
      if (d < 400) P.speed = Math.max(P.speed * 0.5, d);   // ignore teleports
    }
    P.cx = e.clientX; P.cy = e.clientY; P.on = true;
  }, { passive: true });

  document.documentElement.addEventListener("pointerleave", function () { P.on = false; });
  addEventListener("blur", function () { P.on = false; });

  addEventListener("pointerdown", function (e) {
    if (B.mode !== "perched") return;
    var sx = B.x, sy = B.y - window.scrollY - 18;
    if (Math.hypot(e.clientX - sx, e.clientY - sy) < 70) {
      B.say = { t: 0 };
      B.peck = 0;
    }
  }, { passive: true });

  // Reduced motion: no flight. The bird sits in its cage — or, without a cage,
  // on a line near the middle of the screen — and clicking the cage moves it
  // between the two at once.
  var stillOut = false;

  function onCageClick() {
    if (reduced) { stillOut = !stillOut; stayStill(); return; }
    if (!cage) return;
    if (B.mode === "caged") {
      B.stayHome = false;
      var p = pickPerch();
      if (p) startLeaving(p);
      else { B.say = { t: 0 }; nudge(0.012); }       // nowhere to go yet: it calls instead
    } else if (B.mode === "flying" || B.mode === "perched" || B.mode === "away") {
      B.stayHome = true;
      if (B.mode === "away") { B.x = VW + 50; B.y = window.scrollY + VH * 0.2; }
      flyHome();
    }
    label();
  }

  // the packet: throw a handful, or shake it and say why not
  var tipTimer = 0;
  function packSay(text, ms) {
    if (!packTip) return;
    packTip.textContent = text;
    packEl.classList.add("is-telling");
    clearTimeout(tipTimer);
    tipTimer = setTimeout(function () {
      packTip.textContent = "scatter seeds";
      packEl.classList.remove("is-telling");
    }, ms);
  }

  function scatter() {
    var n = feed();
    if (n > 0 && reduced) eatStill();
    return n;
  }

  function onPackClick() {
    unlockAudio();                                  // this click is what lets it be heard later
    var n = scatter();
    packEl.classList.remove("is-pouring", "is-shaking");
    void packEl.offsetWidth;                        // lets the animation run again
    if (n > 0) {
      packEl.classList.add("is-pouring");
    } else {
      packEl.classList.add("is-shaking");
      packSay(n === 0 ? "that's plenty for now" : "no line to scatter them on", 1700);
    }
  }

  // Reduced motion: no flight and no hopping. It stands by the seeds and
  // takes one every so often, with a still bow for each.
  var stillTimer = 0;
  function eatStill() {
    clearInterval(stillTimer);
    stillOut = true;
    var standBy = function (food) {
      B.mode = "perched"; B.perchEl = food.p.el; B.scale = S;
      B.x = standFor(food, food.x - 1); B.y = food.p.y;
      B.face = B.x <= food.x ? 1 : -1;
    };
    var first = nearestFood();
    if (first) standBy(first);
    label(); draw();
    stillTimer = setInterval(function () {
      mapPerches();
      stepSeeds(0);
      var food = nearestFood();
      if (!food) { clearInterval(stillTimer); B.bow = 0; singStill(); return; }
      standBy(food);
      food.seed.state = "eaten";
      B.seedsEaten++;
      B.bow = 0.38; draw();
      setTimeout(function () { B.bow = 0; stepSeeds(0); draw(); }, 300);
    }, 900);
  }

  /* ── run ───────────────────────────────────────────────── */

  function placeStill() {
    mapPerches();
    var best = null, bestD = 1e9;
    for (var i = 0; i < perches.length; i++) {
      if (!onScreen(perches[i])) continue;
      var d = Math.abs(perches[i].y - window.scrollY - VH * 0.5);
      if (d < bestD) { bestD = d; best = perches[i]; }
    }
    if (best) {
      B.mode = "perched";
      B.perchEl = best.el;
      B.x = best.x0 + (best.x1 - best.x0) * 0.72;
      B.y = best.y;
      B.face = -1;
    } else {
      B.mode = "away";
    }
    draw();
  }

  function stayStill() {
    measureCage();
    if (cage && !stillOut) {
      B.mode = "caged";
      B.cageX = 55; B.face = -1; B.scale = cageScale();
      var h = cagePoint(55, ROD);
      B.x = h.x; B.y = h.y;
      draw();
    } else {
      B.scale = S;
      placeStill();
    }
    label();
  }

  var raf = 0, last = 0;
  function frame(now) {
    raf = requestAnimationFrame(frame);
    var dt = last ? Math.min(48, now - last) : 16;
    last = now;
    step(dt);
    draw();
    paintCount();
    label();
  }

  // The entrance is the first thing anyone sees the bird do, so it waits for
  // the name's underline to ink in rather than landing somewhere arbitrary on
  // a slow connection. Gives up after about three seconds and takes any line,
  // and does not wait at all if the page was reloaded part-way down.
  var entryTries = 0;
  function enter() {
    mapPerches();
    var first = null;
    for (var i = 0; i < perches.length; i++) {
      if (perches[i].first && onScreen(perches[i])) { first = perches[i]; break; }
    }
    if (!first && window.scrollY < VH * 0.5 && entryTries++ < 8) { setTimeout(enter, 400); return; }
    var p = first || pickPerch();
    B.entered = true;
    if (!p) return;                  // stays home (or off-screen) until there is somewhere to go
    var tx = p.x0 + (p.x1 - p.x0) * 0.72;
    if (B.mode === "caged") startLeaving(p, tx);
    else if (B.mode === "away") flyTo(p, tx);
  }

  function boot() {
    readColours();
    resize();
    // the palette preview recolours the page; follow it
    addEventListener("palettechange", function () { readColours(); draw(); });
    addEventListener("resize", resize);
    addEventListener("load", function () { measureCage(); mapPerches(); });
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(function () { measureCage(); mapPerches(); });
    }
    // reveals keep changing which lines exist and exactly where they sit
    setInterval(function () { measureCage(); mapPerches(); }, 700);
    if (cageEl) cageEl.addEventListener("click", onCageClick);
    if (packEl) packEl.addEventListener("click", onPackClick);
    if (songEl) songEl.addEventListener("click", onSongClick);
    paintSong();

    if (reduced) {
      stayStill();
      addEventListener("scroll", stayStill, { passive: true });
      addEventListener("resize", stayStill);
      return;
    }

    // it starts at home, and comes out once the page has inked in
    if (cage) {
      B.mode = "caged";
      B.cageX = 55;
      B.scale = cageScale();
      var h = cagePoint(55, ROD);
      B.x = h.x; B.y = h.y;
    }
    label();
    setTimeout(enter, 1100);
    raf = requestAnimationFrame(frame);
  }

  api.step = function (ms) {
    var n = Math.max(1, Math.round(ms / 16));
    for (var i = 0; i < n; i++) step(16);
    draw();
    paintCount();
    label();
    return api.stats();
  };
  api.stats = function () {
    var el = B.perchEl;
    var cls = el ? (typeof el.className === "string" ? el.className : el.className.baseVal) : null;
    var visible = 0;
    for (var i = 0; i < perches.length; i++) if (onScreen(perches[i])) visible++;
    return {
      mode: B.mode, x: Math.round(B.x), y: Math.round(B.y), face: B.face,
      perch: cls, perches: perches.length, onScreen: visible,
      wags: B.wags, flights: B.flights, hops: B.hops, homecomings: B.homecomings,
      entered: B.entered, reduced: reduced,
      cage: !!cage, stayHome: B.stayHome, scale: Math.round(B.scale * 100) / 100,
      doorOpen: !!cageEl && cageEl.classList.contains("is-open"),
      sway: Math.round(sway.a * 100) / 100,
      cageTip: cageTip ? cageTip.textContent : null,
      seeds: seeds.filter(function (s) { return s.state !== "eaten"; }).length,
      seedsLanded: seeds.filter(function (s) { return s.state === "ground"; }).length,
      seedsEaten: B.seedsEaten, handfuls: B.handfuls,
      eating: B.mode === "perched" && (!!B.eat || (function () {
        var f = nearestFood();
        return !!f && f.p.el === B.perchEl;
      })()),
      bow: Math.round(B.bow * 100) / 100,
      singing: !!B.sing, songs: B.songs, songOn: songOn,
      audio: audio ? audio.state : "none", tonesScheduled: scheduled, notesInAir: notes.length
    };
  };
  api.feed = scatter;
  api.sing = function () { return Math.round(startSong().dur * 1000); };
  // Renders one song offline and measures it — a way to check the sound is
  // really there without speakers, or without a click to allow audio.
  api.renderSong = function () {
    var OAC = window.OfflineAudioContext || window.webkitOfflineAudioContext;
    if (!OAC) return Promise.resolve(null);
    var song = composeSong(), rate = 44100;
    var ac = new OAC(1, Math.ceil((song.dur + 0.2) * rate), rate);
    var gain = ac.createGain();
    gain.gain.value = 0.08;
    gain.connect(ac.destination);
    var count = schedule(ac, gain, song, 0.02);
    return ac.startRendering().then(function (buf) {
      var d = buf.getChannelData(0), peak = 0, sum = 0, voiced = 0, cross = 0;
      for (var i = 1; i < d.length; i++) {
        var v = Math.abs(d[i]);
        if (v > peak) peak = v;
        sum += d[i] * d[i];
        if (v > 1e-4) {
          voiced++;
          if ((d[i - 1] < 0) !== (d[i] < 0)) cross++;
        }
      }
      return {
        tones: count, seconds: Math.round(song.dur * 100) / 100,
        peak: Math.round(peak * 1000) / 1000, rms: Math.round(Math.sqrt(sum / d.length) * 10000) / 10000,
        soundingSeconds: Math.round(voiced / rate * 100) / 100,
        averagePitchHz: voiced ? Math.round(cross / 2 / (voiced / rate)) : 0
      };
    });
  };
  api.remap = mapPerches;
  api.enter = enter;
  api.measureCage = measureCage;
  api.callHome = function () {
    if (!cage || B.mode === "caged" || B.mode === "entering" || B.mode === "leaving") return false;
    B.stayHome = true;
    flyHome();
    label();
    return true;
  };
  api.release = function () {
    if (B.mode !== "caged") return false;
    B.stayHome = false;
    var p = pickPerch();
    if (!p) return false;
    startLeaving(p);
    label();
    return true;
  };

  if (document.readyState === "loading") addEventListener("DOMContentLoaded", boot);
  else boot();

  return api;
})();
