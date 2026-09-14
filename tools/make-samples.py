"""Draw the sample projects' screenshots and tour videos.

    python tools/make-samples.py

Writes assets/samples/<project>-<view>.webp — three sketched screenshots per
sample project — and, when ffmpeg is on PATH, assets/samples/<project>-tour.mp4
for the projects listed in TOURS.

The sketches are wireframes drawn in the journal's own ink on paper, and every
one carries a red "sample sketch" mark. They exist to show how the projects
page, its gallery and its video player work — they are not client work, and
the cards that use them are stamped Sample for the same reason.
"""
import math
import os
import random
import shutil
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "assets", "samples")

W, H = 1200, 750                      # 16:10, the same shape as the card frames

PAPER, PAPER2, PAPER3 = (241, 234, 219), (231, 221, 200), (250, 246, 236)
INK, INK2, INK3, FAINT = (38, 34, 30), (87, 80, 74), (150, 142, 130), (208, 199, 183)
RED, RED_L = (162, 67, 43), (238, 210, 198)
SAGE, SAGE_L = (94, 110, 71), (216, 222, 200)
AMBER, AMBER_L = (140, 104, 20), (240, 226, 190)

FONT_DIR = os.path.join(os.environ.get("WINDIR", "C:/Windows"), "Fonts")
_fonts = {}


def font(name, size):
    key = (name, size)
    if key not in _fonts:
        try:
            _fonts[key] = ImageFont.truetype(os.path.join(FONT_DIR, name), size)
        except OSError:
            _fonts[key] = ImageFont.load_default()
    return _fonts[key]


def serif(s): return font("georgia.ttf", s)
def ital(s): return font("georgiai.ttf", s)
def hand(s): return font("segoepr.ttf", s)
def mono(s): return font("consola.ttf", s)


rng = random.Random()


def wob(a=1.3):
    return rng.uniform(-a, a)


# ── drawing, by hand ─────────────────────────────────────────

def line(d, pts, fill=INK, width=2, jitter=1.2):
    """A polyline with a slight tremor, so it reads as drawn rather than ruled."""
    out = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(2, int(math.hypot(x1 - x0, y1 - y0) / 36))
        for k in range(n):
            t = k / n
            out.append((x0 + (x1 - x0) * t + wob(jitter), y0 + (y1 - y0) * t + wob(jitter)))
    out.append((pts[-1][0] + wob(jitter), pts[-1][1] + wob(jitter)))
    d.line(out, fill=fill, width=width, joint="curve")


def box(d, x0, y0, x1, y1, fill=None, outline=INK, width=2):
    if fill:
        d.rectangle([x0, y0, x1, y1], fill=fill)
    line(d, [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)], outline, width)


def hatch(d, x0, y0, x1, y1, step=14, fill=FAINT):
    """Diagonal hatching: the wireframe convention for 'a picture goes here'."""
    h = y1 - y0
    c = x0 - h
    while c < x1:
        ax, ay, bx, by = c, y1, c + h, y0
        if ax < x0:
            ay -= x0 - ax
            ax = x0
        if bx > x1:
            by += bx - x1
            bx = x1
        if ax <= bx and ay >= y0 and by <= y1:
            d.line([(ax, ay), (bx, by)], fill=fill, width=2)
        c += step
    box(d, x0, y0, x1, y1)


def bars(d, x, y, width, rows, gap=20, h=7, fill=FAINT, last=0.6):
    """Grey bars standing in for lines of text."""
    for r in range(rows):
        w = width * (last if r == rows - 1 else rng.uniform(0.82, 1.0))
        d.rounded_rectangle([x, y + r * gap, x + w, y + r * gap + h], radius=3, fill=fill)
    return y + rows * gap


def text(d, xy, s, f, fill=INK):
    d.text(xy, s, font=f, fill=fill)


def pill(d, x, y, s, bg=SAGE_L, fg=SAGE):
    f = mono(15)
    w = d.textlength(s, font=f) + 18
    d.rounded_rectangle([x, y, x + w, y + 24], radius=12, fill=bg, outline=fg, width=1)
    d.text((x + 9, y + 3), s, font=f, fill=fg)
    return x + w


def button(d, x, y, s, dark=True):
    f = serif(18)
    w = d.textlength(s, font=f) + 36
    if dark:
        d.rectangle([x, y, x + w, y + 40], fill=INK)
        d.text((x + 18, y + 9), s, font=f, fill=PAPER3)
    else:
        box(d, x, y, x + w, y + 40)
        d.text((x + 18, y + 9), s, font=f, fill=INK)
    return x + w


def arrow(d, a, b, fill=INK):
    line(d, [a, b], fill, 2)
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    for s in (-0.45, 0.45):
        d.line([b, (b[0] - 15 * math.cos(ang + s), b[1] - 15 * math.sin(ang + s))], fill=fill, width=2)


def tick(d, x, y, s=16, fill=RED):
    d.line([(x, y + s * 0.55), (x + s * 0.38, y + s), (x + s, y)], fill=fill, width=3, joint="curve")


def canvas():
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    for y in range(28, H, 32):
        d.line([(0, y), (W, y)], fill=(229, 224, 214), width=1)
    return im, d


def browser(d, url):
    """A browser window drawn on the page; returns its content box."""
    x0, y0, x1, y1 = 40, 34, W - 40, H - 44
    box(d, x0, y0, x1, y1, fill=PAPER3)
    line(d, [(x0, y0 + 46), (x1, y0 + 46)])
    for k in range(3):
        d.ellipse([x0 + 18 + k * 22, y0 + 17, x0 + 30 + k * 22, y0 + 29], outline=INK, width=2)
    d.rounded_rectangle([x0 + 100, y0 + 11, x1 - 40, y0 + 35], radius=12, fill=PAPER, outline=INK3, width=1)
    text(d, (x0 + 116, y0 + 13), url, mono(16), INK2)
    return x0 + 28, y0 + 72, x1 - 28, y1 - 24


def terminal(d):
    x0, y0, x1, y1 = 60, 50, W - 60, H - 60
    box(d, x0, y0, x1, y1, fill=PAPER2)
    line(d, [(x0, y0 + 40), (x1, y0 + 40)])
    text(d, (x0 + 18, y0 + 10), "terminal", mono(16), INK2)
    return x0, y0, x1, y1


def mark(d):
    text(d, (W - 190, H - 40), "sample sketch", hand(20), RED)


# ── 1 · newsroom on Wagtail ──────────────────────────────────

def newsroom_home(d):
    x0, y0, x1, y1 = browser(d, "newsroom.example.com")
    text(d, (x0, y0 - 6), "The Ledger", ital(34))
    nx = x1 - 380
    for i, s in enumerate(["News", "Politics", "Culture", "Sport"]):
        text(d, (nx + i * 92, y0 + 4), s, serif(18), INK2)
    line(d, [(nx, y0 + 30), (nx + 46, y0 + 30)], RED, 3)
    line(d, [(x0, y0 + 50), (x1, y0 + 50)], INK3, 1)
    text(d, (x0, y0 + 76), "Local news,", serif(44))
    text(d, (x0, y0 + 128), "published faster.", serif(44))
    bars(d, x0, y0 + 200, 430, 3, gap=22)
    button(d, x0, y0 + 280, "Read today's edition")
    hatch(d, x0 + 520, y0 + 70, x1, y0 + 330)
    cy, cw = y0 + 370, (x1 - x0 - 40) / 3
    for i, title in enumerate(["Council votes on budget", "New library opens", "Derby ends level"]):
        cx = x0 + i * (cw + 20)
        hatch(d, cx, cy, cx + cw, cy + 110, step=12)
        text(d, (cx, cy + 122), title, serif(19))
        bars(d, cx, cy + 156, cw - 20, 2, gap=18)


def newsroom_article(d):
    x0, y0, x1, y1 = browser(d, "newsroom.example.com/culture/new-library-opens")
    text(d, (x0, y0 - 6), "The Ledger", ital(28))
    line(d, [(x0, y0 + 36), (x1, y0 + 36)], INK3, 1)
    main = x0 + 700
    text(d, (x0, y0 + 56), "Culture", mono(15), RED)
    text(d, (x0, y0 + 80), "A new library opens its doors", serif(34))
    bars(d, x0, y0 + 132, 220, 1, fill=INK3)
    hatch(d, x0, y0 + 158, main, y0 + 380)
    bars(d, x0, y0 + 404, main - x0, 7, gap=22)
    sx = main + 40
    text(d, (sx, y0 + 56), "Most read", serif(22))
    for i in range(5):
        yy = y0 + 100 + i * 64
        text(d, (sx, yy), str(i + 1), ital(30), RED)
        bars(d, sx + 34, yy + 8, x1 - sx - 34, 2, gap=18)
        if i < 4:
            line(d, [(sx, yy + 52), (x1, yy + 52)], FAINT, 1)


def newsroom_admin(d):
    x0, y0, x1, y1 = browser(d, "newsroom.example.com/admin/pages/42/edit")
    sb = x0 + 200
    d.rectangle([x0 - 26, y0 - 26, sb, y1 + 22], fill=PAPER2)
    text(d, (x0 - 8, y0 - 4), "Admin", ital(26))
    for i, s in enumerate(["Dashboard", "Pages", "Images", "Documents", "Snippets", "Settings"]):
        yy = y0 + 46 + i * 40
        if s == "Pages":
            d.rectangle([x0 - 26, yy - 6, sb, yy + 28], fill=PAPER3)
        text(d, (x0 - 8, yy), s, serif(18), INK if s == "Pages" else INK2)
    mx, px = sb + 28, x1 - 220
    text(d, (mx, y0 - 4), "Pages  >  Culture  >  A new library opens", mono(15), INK2)
    text(d, (mx, y0 + 24), "Editing: A new library opens", serif(28))
    by = y0 + 76
    for label, rows in [("Heading", 1), ("Paragraph", 3), ("Image", 0), ("Quote", 2)]:
        h = 44 + rows * 18 + (70 if label == "Image" else 0)
        box(d, mx, by, px - 30, by + h, fill=PAPER)
        text(d, (mx + 14, by + 6), label, hand(18), RED)
        for k in range(3):
            d.line([(px - 60, by + 14 + k * 6), (px - 44, by + 14 + k * 6)], fill=INK3, width=2)
        if label == "Image":
            hatch(d, mx + 14, by + 40, mx + 200, by + 104, step=10)
        else:
            bars(d, mx + 14, by + 42, px - 30 - mx - 60, rows, gap=18)
        by += h + 14
    box(d, px, y0 + 76, x1, y0 + 250, fill=PAPER)
    text(d, (px + 16, y0 + 88), "Status", mono(15), INK2)
    pill(d, px + 16, y0 + 114, "Draft", RED_L, RED)
    button(d, px + 16, y0 + 160, "Publish")
    text(d, (px + 4, y0 + 268), "blocks reorder\nby dragging", hand(18), RED)


# ── 2 · metrics dashboard ────────────────────────────────────

def dashboard_overview(d):
    x0, y0, x1, y1 = browser(d, "metrics.example.com")
    text(d, (x0, y0 - 6), "Metrics", ital(30))
    text(d, (x1 - 150, y0 + 2), "Last 30 days", serif(18), INK2)
    tw = (x1 - x0 - 3 * 20) / 4
    for i, (k, v, dv) in enumerate([("Visitors", "12,480", "+8%"), ("Conversion", "3.2%", "+0.4"),
                                    ("Orders", "846", "+12%"), ("Uptime", "99.9%", "")]):
        tx = x0 + i * (tw + 20)
        box(d, tx, y0 + 50, tx + tw, y0 + 150, fill=PAPER)
        text(d, (tx + 16, y0 + 62), k, mono(15), INK2)
        text(d, (tx + 16, y0 + 88), v, serif(34))
        if dv:
            text(d, (tx + tw - 62, y0 + 98), dv, mono(16), SAGE)
    cx0, cy0, cx1, cy1 = x0, y0 + 180, x0 + 660, y1 - 10
    box(d, cx0, cy0, cx1, cy1, fill=PAPER)
    text(d, (cx0 + 16, cy0 + 12), "Visitors per day", serif(20))
    for g in range(4):
        d.line([(cx0 + 20, cy0 + 70 + g * 80), (cx1 - 20, cy0 + 70 + g * 80)], fill=FAINT, width=1)
    n, pts = 30, []
    for k in range(n):
        x = cx0 + 30 + k * (cx1 - cx0 - 60) / (n - 1)
        v = 0.35 + 0.22 * math.sin(k / 3.2) + k * 0.012 + rng.uniform(-0.04, 0.04)
        pts.append((x, cy1 - 40 - v * (cy1 - cy0 - 110)))
    d.line(pts, fill=RED, width=3, joint="curve")
    bx0 = cx1 + 24
    box(d, bx0, cy0, x1, cy1, fill=PAPER)
    text(d, (bx0 + 16, cy0 + 12), "Orders by channel", serif(20))
    for k, (lab, val) in enumerate([("Search", 0.85), ("Direct", 0.62), ("Email", 0.4), ("Social", 0.28)]):
        yy = cy0 + 70 + k * 70
        text(d, (bx0 + 16, yy), lab, mono(15), INK2)
        hatch(d, bx0 + 100, yy - 2, bx0 + 100 + (x1 - bx0 - 130) * val, yy + 24, step=8, fill=INK3)


def dashboard_table(d):
    x0, y0, x1, y1 = browser(d, "metrics.example.com/orders")
    text(d, (x0, y0 - 6), "Orders", ital(30))
    box(d, x1 - 300, y0, x1, y0 + 34, fill=PAPER, width=1)
    text(d, (x1 - 288, y0 + 6), "Search orders", serif(16), INK3)
    cols = [x0, x0 + 150, x0 + 440, x0 + 640, x0 + 820]
    hy = y0 + 58
    for c, h in zip(cols, ["Order", "Customer", "Date", "Total", "Status"]):
        text(d, (c + 8, hy), h, mono(16), INK2)
    line(d, [(x0, hy + 30), (x1, hy + 30)])
    states = ["Paid", "Paid", "Refunded", "Paid", "Pending", "Paid", "Paid", "Refunded", "Paid"]
    for r, s in enumerate(states):
        yy = hy + 46 + r * 52
        bg, fg = {"Paid": (SAGE_L, SAGE), "Refunded": (RED_L, RED), "Pending": (AMBER_L, AMBER)}[s]
        text(d, (cols[0] + 8, yy), "#%d" % (10482 - r), mono(16))
        d.rounded_rectangle([cols[1] + 8, yy + 6, cols[1] + 8 + rng.randint(140, 230), yy + 14], radius=3, fill=FAINT)
        text(d, (cols[2] + 8, yy), "%02d Sep" % (14 - r), mono(16), INK2)
        text(d, (cols[3] + 8, yy), "$%d.00" % rng.randint(24, 480), mono(16))
        pill(d, cols[4] + 8, yy - 2, s, bg, fg)
        if r < len(states) - 1:
            d.line([(x0, yy + 36), (x1, yy + 36)], fill=FAINT, width=1)


def dashboard_mobile(d):
    px0, py0, px1, py1 = 440, 40, 760, H - 40
    d.rounded_rectangle([px0, py0, px1, py1], radius=36, fill=PAPER3, outline=INK, width=3)
    d.rounded_rectangle([px0 + 120, py0 + 16, px1 - 120, py0 + 26], radius=5, fill=INK)
    x0, y0, x1 = px0 + 24, py0 + 50, px1 - 24
    text(d, (x0, y0), "Metrics", ital(26))
    for i, (k, v) in enumerate([("Visitors", "12,480"), ("Orders", "846")]):
        yy = y0 + 50 + i * 92
        box(d, x0, yy, x1, yy + 78, fill=PAPER)
        text(d, (x0 + 14, yy + 10), k, mono(14), INK2)
        text(d, (x0 + 14, yy + 32), v, serif(30))
    cy = y0 + 250
    box(d, x0, cy, x1, cy + 200, fill=PAPER)
    pts = [(x0 + 16 + k * (x1 - x0 - 32) / 15, cy + 170 - (0.3 + 0.3 * math.sin(k / 2.4) + k * 0.02) * 150)
           for k in range(16)]
    d.line(pts, fill=RED, width=3, joint="curve")
    bars(d, x0, cy + 224, x1 - x0, 4, gap=22)
    text(d, (100, 250), "the same dashboard,\nsized for a phone", hand(26), RED)
    arrow(d, (330, 340), (425, 390), RED)
    text(d, (805, 470), "tables become cards;\nnothing scrolls sideways", hand(22), RED)
    arrow(d, (800, 500), (770, 470), RED)


# ── 3 · checkout sandbox ─────────────────────────────────────

def checkout_form(d):
    x0, y0, x1, y1 = browser(d, "shop.example.com/checkout")
    text(d, (x0, y0 - 6), "Checkout", ital(30))
    fx1, fy = x0 + 600, y0 + 50
    for label, val in [("Email", "you@example.com"), ("Name on card", "Sample Customer"),
                       ("Card number", "4242 4242 4242 4242")]:
        text(d, (x0, fy), label, mono(15), INK2)
        box(d, x0, fy + 24, fx1, fy + 70, fill=PAPER)
        text(d, (x0 + 14, fy + 36), val, serif(19), INK2)
        fy += 96
    half = (fx1 - x0 - 20) / 2
    for k, (label, val) in enumerate([("Expiry", "12 / 29"), ("CVC", "123")]):
        fx = x0 + k * (half + 20)
        text(d, (fx, fy), label, mono(15), INK2)
        box(d, fx, fy + 24, fx + half, fy + 70, fill=PAPER)
        text(d, (fx + 14, fy + 36), val, serif(19), INK2)
    button(d, x0, fy + 100, "Pay $148.00")
    sx = fx1 + 50
    box(d, sx, y0 + 50, x1, y0 + 350, fill=PAPER)
    text(d, (sx + 20, y0 + 64), "Your order", serif(22))
    for k, (item, price) in enumerate([("Field notebook", "$64.00"), ("Pencil set", "$36.00"), ("Delivery", "$48.00")]):
        yy = y0 + 112 + k * 52
        text(d, (sx + 20, yy), item, serif(18), INK2)
        text(d, (x1 - 100, yy), price, mono(17))
    line(d, [(sx + 20, y0 + 280), (x1 - 20, y0 + 280)])
    text(d, (sx + 20, y0 + 296), "Total", serif(22))
    text(d, (x1 - 110, y0 + 298), "$148.00", mono(20))
    text(d, (sx + 6, y0 + 380), "card details go straight to\nthe gateway, never the server", hand(19), RED)


def checkout_receipt(d):
    x0, y0, x1, y1 = browser(d, "shop.example.com/checkout/complete")
    cx = (x0 + x1) / 2
    rx0, rx1 = cx - 260, cx + 260
    box(d, rx0, y0 + 20, rx1, y1 - 10, fill=PAPER)
    d.ellipse([cx - 40, y0 + 50, cx + 40, y0 + 130], outline=SAGE, width=4)
    d.line([(cx - 20, y0 + 92), (cx - 5, y0 + 108), (cx + 22, y0 + 74)], fill=SAGE, width=5, joint="curve")
    for s, f, c, yy in [("Payment received", serif(34), INK, y0 + 150),
                        ("Order #10482 - a receipt is on its way", serif(18), INK2, y0 + 200)]:
        text(d, (cx - d.textlength(s, font=f) / 2, yy), s, f, c)
    yy = y0 + 260
    for item, price in [("Field notebook", "$64.00"), ("Pencil set", "$36.00"), ("Delivery", "$48.00"), ("Total", "$148.00")]:
        if item == "Total":
            line(d, [(rx0 + 40, yy - 12), (rx1 - 40, yy - 12)])
        text(d, (rx0 + 40, yy), item, serif(19), INK if item == "Total" else INK2)
        text(d, (rx1 - 130, yy), price, mono(19))
        yy += 50
    button(d, cx - 90, yy + 20, "Back to shop", dark=False)


def checkout_webhooks(d):
    x0, y0, x1, y1 = browser(d, "shop.example.com/admin/webhooks")
    text(d, (x0, y0 - 6), "Webhook log", ital(30))
    text(d, (x1 - 320, y0 + 2), "failures retry on their own", hand(19), RED)
    hy = y0 + 56
    for c, h in zip([x0, x0 + 110, x0 + 520, x0 + 760], ["Status", "Event", "Received", "Attempts"]):
        text(d, (c + 8, hy), h, mono(16), INK2)
    line(d, [(x0, hy + 30), (x1, hy + 30)])
    events = [("200", "payment_intent.succeeded", "12:04:31", "1"), ("200", "charge.refunded", "12:02:10", "1"),
              ("500", "invoice.paid", "11:58:44", "retrying"), ("200", "invoice.paid", "11:58:52", "2"),
              ("200", "customer.updated", "11:51:03", "1"), ("200", "payment_intent.created", "11:50:59", "1"),
              ("408", "payout.paid", "11:43:20", "retrying"), ("200", "payout.paid", "11:43:35", "2")]
    for r, (code, ev, at, att) in enumerate(events):
        yy, ok = hy + 46 + r * 54, code == "200"
        pill(d, x0 + 8, yy - 3, code, SAGE_L if ok else RED_L, SAGE if ok else RED)
        text(d, (x0 + 118, yy), ev, mono(17))
        text(d, (x0 + 528, yy), at, mono(17), INK2)
        text(d, (x0 + 768, yy), att, mono(17), INK if ok else RED)
        if r < len(events) - 1:
            d.line([(x0, yy + 38), (x1, yy + 38)], fill=FAINT, width=1)


# ── 4 · bookings API ─────────────────────────────────────────

def bookings_docs(d):
    x0, y0, x1, y1 = browser(d, "api.example.com/docs")
    sb = x0 + 250
    text(d, (x0, y0 - 6), "Bookings API", ital(26))
    for i, (m, p) in enumerate([("GET", "/rooms"), ("GET", "/bookings"), ("POST", "/bookings"),
                                ("GET", "/bookings/{id}"), ("PATCH", "/bookings/{id}"), ("DELETE", "/bookings/{id}")]):
        yy = y0 + 50 + i * 40
        if i == 2:
            d.rectangle([x0 - 10, yy - 6, sb - 10, yy + 26], fill=PAPER2)
        text(d, (x0, yy), m, mono(15), SAGE if m == "GET" else RED)
        text(d, (x0 + 66, yy), p, mono(15), INK2)
    line(d, [(sb, y0 - 10), (sb, y1)], FAINT, 1)
    mx = sb + 30
    pill(d, mx, y0, "POST", RED_L, RED)
    text(d, (mx + 80, y0 - 3), "/bookings", mono(22))
    text(d, (mx, y0 + 46), "Create a booking", serif(30))
    bars(d, mx, y0 + 96, x1 - mx, 2, gap=22)
    text(d, (mx, y0 + 156), "Body", serif(20))
    for k, (name, typ, req) in enumerate([("room", "integer", "required"), ("starts_at", "datetime", "required"),
                                          ("ends_at", "datetime", "required"), ("note", "string", "optional")]):
        yy = y0 + 196 + k * 40
        text(d, (mx, yy), name, mono(17))
        text(d, (mx + 180, yy), typ, mono(17), INK2)
        text(d, (mx + 360, yy), req, mono(17), RED if req == "required" else INK3)
        d.line([(mx, yy + 30), (x1, yy + 30)], fill=FAINT, width=1)
    cy = y0 + 370
    d.rectangle([mx, cy, x1, y1 - 6], fill=PAPER2)
    for k, s in enumerate(["curl -X POST https://api.example.com/bookings \\",
                           '  -H "Authorization: Token ..." \\',
                           "  -d '{\"room\": 12, \"starts_at\": \"2026-09-20T09:00\"}'"]):
        text(d, (mx + 18, cy + 18 + k * 30), s, mono(16))


def bookings_json(d):
    x0, y0, x1, y1 = terminal(d)
    rows = [("$ http GET api.example.com/bookings/318", INK), ("HTTP/1.1 200 OK", SAGE),
            ("Content-Type: application/json", INK2), ("", INK), ("{", INK),
            ('    "id": 318,', INK), ('    "room": { "id": 12, "name": "Garden room" },', INK),
            ('    "starts_at": "2026-09-20T09:00:00Z",', INK), ('    "ends_at": "2026-09-20T11:00:00Z",', INK),
            ('    "status": "confirmed",', RED), ('    "created_by": "front-desk"', INK), ("}", INK)]
    for k, (s, c) in enumerate(rows):
        text(d, (x0 + 30, y0 + 64 + k * 40), s, mono(24), c)
    text(d, (x1 - 320, y1 - 60), "same shape, every endpoint", hand(22), RED)


def bookings_admin(d):
    x0, y0, x1, y1 = browser(d, "api.example.com/admin/bookings")
    text(d, (x0, y0 - 6), "Bookings", ital(30))
    fx = x1 - 220
    box(d, fx, y0 + 40, x1, y0 + 360, fill=PAPER)
    text(d, (fx + 16, y0 + 52), "Filter", serif(20))
    for k, (grp, opts) in enumerate([("Status", ["All", "Confirmed", "Cancelled"]), ("Room", ["All", "Garden room", "Library"])]):
        gy = y0 + 92 + k * 130
        text(d, (fx + 16, gy), grp, mono(15), INK2)
        for o, opt in enumerate(opts):
            text(d, (fx + 28, gy + 26 + o * 28), opt, serif(17), RED if o == 1 else INK2)
    tx1 = fx - 24
    cols = [x0, x0 + 80, x0 + 330, x0 + 560]
    hy = y0 + 46
    d.rectangle([x0, hy - 6, tx1, hy + 28], fill=PAPER2)
    for c, h in zip(cols, ["ID", "Room", "Starts", "Status"]):
        text(d, (c + 10, hy), h, mono(16), INK2)
    for r in range(9):
        yy = hy + 46 + r * 50
        d.rectangle([x0 + 10, yy + 2, x0 + 24, yy + 16], outline=INK3, width=2)
        text(d, (cols[0] + 34, yy), str(318 - r), mono(16))
        text(d, (cols[1] + 10, yy), ["Garden room", "Library", "Studio"][r % 3], serif(17))
        text(d, (cols[2] + 10, yy), "%02d Sep, %02d:00" % (20 - r // 2, 9 + r % 5), mono(16), INK2)
        ok = r % 4 != 2
        pill(d, cols[3] + 10, yy - 3, "confirmed" if ok else "cancelled", SAGE_L if ok else RED_L, SAGE if ok else RED)
        d.line([(x0, yy + 34), (tx1, yy + 34)], fill=FAINT, width=1)


# ── 5 · static delivery on AWS ───────────────────────────────

def delivery_diagram(d):
    text(d, (70, 50), "How the site is served", ital(40))
    text(d, (72, 104), "sample architecture", hand(22), RED)

    def node(x, y, title, sub, w=210, h=96):
        box(d, x, y, x + w, y + h, fill=PAPER3)
        text(d, (x + 18, y + 16), title, serif(24))
        text(d, (x + 18, y + 54), sub, mono(15), INK2)
        return x, y, x + w, y + h

    visitor = node(70, 320, "Visitor", "browser, anywhere")
    edge = node(400, 320, "CloudFront", "cache at the edge")
    s3 = node(760, 150, "S3", "static files")
    app = node(760, 340, "EC2 + Nginx", "API and admin")
    db = node(760, 530, "PostgreSQL", "backed up nightly")
    arrow(d, (visitor[2], 368), (edge[0] - 6, 368))
    arrow(d, (edge[2], 350), (s3[0] - 6, 210))
    arrow(d, (edge[2], 384), (app[0] - 6, 388))
    arrow(d, (app[0] + 105, app[3]), (db[0] + 105, db[1] - 6))
    text(d, (410, 440), "most requests\nstop here", hand(22), RED)
    text(d, (995, 190), "deployed with\none command", hand(20), RED)


def delivery_speed(d):
    text(d, (70, 50), "Page load, before and after", ital(38))
    text(d, (72, 102), "sample figures", hand(22), RED)
    ax0, ay0, ax1, ay1 = 150, 170, 1110, 640
    line(d, [(ax0, ay0), (ax0, ay1), (ax1, ay1)])
    scale = (ay1 - ay0) / 4.0
    for k in range(5):
        yy = ay1 - k * scale
        d.line([(ax0 + 4, yy), (ax1, yy)], fill=FAINT, width=1)
        text(d, (ax0 - 60, yy - 10), "%.1fs" % k, mono(16), INK2)
    pages, before, after = ["Home", "Article", "Search", "Checkout"], [3.6, 3.2, 3.9, 2.8], [1.1, 0.9, 1.4, 1.2]
    gw, bw = (ax1 - ax0) / len(pages), 70
    for i, p in enumerate(pages):
        gx = ax0 + i * gw + 40
        hatch(d, gx, ay1 - before[i] * scale, gx + bw, ay1, step=9, fill=INK3)
        d.rectangle([gx + bw + 16, ay1 - after[i] * scale, gx + 2 * bw + 16, ay1], fill=RED_L)
        box(d, gx + bw + 16, ay1 - after[i] * scale, gx + 2 * bw + 16, ay1, outline=RED)
        text(d, (gx + 20, ay1 + 14), p, serif(18), INK2)
    hatch(d, 820, 110, 850, 134, step=7, fill=INK3)
    text(d, (860, 110), "before", mono(16), INK2)
    d.rectangle([960, 110, 990, 134], fill=RED_L)
    box(d, 960, 110, 990, 134, outline=RED)
    text(d, (1000, 110), "after", mono(16), RED)


def delivery_deploy(d):
    x0, y0, x1, y1 = terminal(d)
    rows = [("$ make deploy", INK), ("", INK), ("[ok]  tests passed (212)", SAGE), ("[ok]  built static assets", SAGE),
            ("[ok]  uploaded 1,284 files to s3://site-bucket", SAGE), ("[ok]  ran 2 database migrations", SAGE),
            ("[ok]  restarted app servers, no downtime", SAGE), ("[ok]  invalidated the CloudFront cache", SAGE),
            ("", INK), ("deployed in 1m 42s", INK)]
    for k, (s, c) in enumerate(rows):
        text(d, (x0 + 30, y0 + 70 + k * 42), s, mono(24), c)
    text(d, (x1 - 370, y1 - 64), "anyone on the team can run it", hand(22), RED)


# ── 6 · codebase takeover audit ──────────────────────────────

def audit_report(d):
    px0, px1 = 250, 950
    box(d, px0, 30, px1, H - 30, fill=PAPER3)
    text(d, (px0 + 50, 70), "Codebase audit", ital(40))
    text(d, (px0 + 52, 124), "Sample client - written before any change", mono(15), INK2)
    y = 180
    for head, rows in [("1. What is running", 3), ("2. What is out of date", 4), ("3. What to fix first", 3)]:
        text(d, (px0 + 50, y), head, serif(24))
        y = bars(d, px0 + 50, y + 44, px1 - px0 - 100, rows, gap=22) + 24
    text(d, (px1 + 20, 250), "the audit is\nthe deliverable", hand(24), RED)
    arrow(d, (px1 + 16, 282), (px1 - 30, 252), RED)
    text(d, (30, 470), "yours, whatever\nyou decide next", hand(24), RED)
    arrow(d, (210, 505), (px0 + 30, 475), RED)


def audit_graph(d):
    text(d, (70, 50), "Dependency map", ital(40))
    text(d, (72, 104), "red means out of support", hand(22), RED)
    nodes = {"project": (600, 390, False), "django": (360, 240, True), "wagtail": (820, 230, True),
             "celery": (330, 560, False), "pillow": (600, 620, True), "psycopg2": (880, 560, False),
             "requests": (1000, 380, False), "whitenoise": (190, 400, False)}
    edges = [("project", k) for k in nodes if k != "project"] + [("wagtail", "django"), ("wagtail", "pillow"), ("celery", "django")]
    for a, b in edges:
        line(d, [nodes[a][:2], nodes[b][:2]], INK3, 2)
    for name, (x, y, old) in nodes.items():
        f = mono(18)
        w = d.textlength(name, font=f) + 36
        d.rounded_rectangle([x - w / 2, y - 22, x + w / 2, y + 22], radius=22,
                            fill=RED_L if old else PAPER3, outline=RED if old else INK, width=2)
        text(d, (x - w / 2 + 18, y - 11), name, f, RED if old else INK)


def audit_checklist(d):
    px0, px1 = 220, 980
    box(d, px0, 30, px1, H - 30, fill=PAPER3)
    text(d, (px0 + 50, 66), "Fix first", ital(40))
    items = [("Rotate credentials left by the previous developer", True), ("Verify backups by restoring one", True),
             ("Get the project running locally from the README", True), ("Upgrade Django to a supported release", False),
             ("Replace the forked templates", False), ("Put the test suite back into CI", False), ("Document the deploy", False)]
    f = serif(22)
    for k, (s, done) in enumerate(items):
        yy = 150 + k * 76
        box(d, px0 + 50, yy, px0 + 80, yy + 30, fill=PAPER3)
        if done:
            tick(d, px0 + 54, yy - 2, 26)
        text(d, (px0 + 100, yy + 2), s, f, INK3 if done else INK)
        if done:
            line(d, [(px0 + 98, yy + 17), (px0 + 108 + d.textlength(s, font=f), yy + 17)], INK3, 2, jitter=.6)
    text(d, (px1 - 250, H - 150), "three down,\nfour to go", hand(24), RED)


SAMPLES = {
    "newsroom": [("home", newsroom_home), ("article", newsroom_article), ("admin", newsroom_admin)],
    "dashboard": [("overview", dashboard_overview), ("table", dashboard_table), ("mobile", dashboard_mobile)],
    "checkout": [("form", checkout_form), ("receipt", checkout_receipt), ("webhooks", checkout_webhooks)],
    "bookings": [("docs", bookings_docs), ("json", bookings_json), ("admin", bookings_admin)],
    "delivery": [("diagram", delivery_diagram), ("speed", delivery_speed), ("deploy", delivery_deploy)],
    "audit": [("report", audit_report), ("graph", audit_graph), ("checklist", audit_checklist)],
}
TOURS = ["newsroom", "dashboard"]


# ── the tour videos ──────────────────────────────────────────

VW, VH, FPS = 960, 600, 24
HOLD, FADE = 3.0, 0.6


def cursor(frame, path, t):
    (ax, ay), (bx, by) = path
    e = t * t * (3 - 2 * t)
    x, y = ax + (bx - ax) * e, ay + (by - ay) * e
    d = ImageDraw.Draw(frame)
    pts = [(x, y), (x, y + 26), (x + 7, y + 20), (x + 12, y + 31), (x + 17, y + 29), (x + 12, y + 18), (x + 21, y + 18)]
    d.polygon(pts, fill=PAPER3)
    d.line(pts + [pts[0]], fill=INK, width=2, joint="curve")


def tour(scenes, path, ffmpeg):
    """A slow push-in on each screenshot, a cursor moving across it, and a
    cross-fade into the next — roughly what a screen recording shows."""
    paths = [((260, 300), (640, 440)), ((700, 220), (320, 500)), ((420, 540), (760, 300))]
    starts = [im.resize((VW, VH), Image.LANCZOS) for im in scenes]
    tmp = tempfile.mkdtemp(prefix="tour-")
    n = 0
    try:
        for s, im in enumerate(scenes):
            steps = int(HOLD * FPS)
            for k in range(steps):
                t = k / (steps - 1)
                z = 1.0 + 0.07 * t
                cw, ch = W / z, H / z
                ox, oy = (W - cw) * (0.3 + 0.4 * (s % 2)), (H - ch) * 0.5
                frame = im.crop((ox, oy, ox + cw, oy + ch)).resize((VW, VH), Image.LANCZOS)
                fade_from = 1 - FADE / HOLD
                if s < len(scenes) - 1 and t > fade_from:
                    frame = Image.blend(frame, starts[s + 1], (t - fade_from) / (FADE / HOLD))
                else:
                    cursor(frame, paths[s % 3], min(1.0, t / fade_from))
                frame.save(os.path.join(tmp, "f%05d.jpg" % n), quality=90)
                n += 1
        subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-framerate", str(FPS),
                        "-i", os.path.join(tmp, "f%05d.jpg"), "-c:v", "libx264", "-pix_fmt", "yuv420p",
                        "-crf", "27", "-preset", "slow", "-movflags", "+faststart", path], check=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return n


def main():
    os.makedirs(OUT, exist_ok=True)
    ffmpeg = shutil.which("ffmpeg")
    for name, views in SAMPLES.items():
        rendered = []
        for view, draw in views:
            rng.seed(name + "-" + view)                 # the same sketch every run
            im, d = canvas()
            draw(d)
            mark(d)
            p = os.path.join(OUT, "%s-%s.webp" % (name, view))
            im.save(p, "WEBP", quality=82, method=6)
            rendered.append(im)
            print("wrote assets/samples/%s  %.0f KB" % (os.path.basename(p), os.path.getsize(p) / 1024))
        if name in TOURS:
            if not ffmpeg:
                print("ffmpeg not found on PATH - skipped", name, "tour video")
                continue
            p = os.path.join(OUT, name + "-tour.mp4")
            frames = tour(rendered, p, ffmpeg)
            print("wrote assets/samples/%s  %.0f KB, %d frames" % (os.path.basename(p), os.path.getsize(p) / 1024, frames))


if __name__ == "__main__":
    main()
