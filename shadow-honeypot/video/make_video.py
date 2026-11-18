#!/usr/bin/env python3
"""Render the Shadow Honeypot explainer video (synthwave style, 75 s, 720p).

Every frame is drawn with Pillow and the soundtrack is synthesized with numpy,
so there is no third-party art or music in the output. The replay scenes read
simulated game 121 straight from sim.py, so the numbers on screen are the
numbers the simulation produced.

Usage (from the repo root):
  uv run --python 3.12 --with pillow --with numpy python video/make_video.py
      -> video/full/shadow-honeypot-full.mp4 (full quality) and site/shadow-honeypot.mp4 (web)
  uv run --python 3.12 --with pillow --with numpy python video/make_video.py --stills 2.5 9.2 34.8
"""
import math
import os
import random
import subprocess
import sys
import wave
from functools import lru_cache
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import sim  # noqa: E402
from deception import load_weights  # noqa: E402

W, H, FPS, DUR = 1280, 720, 30, 75.0
HORIZON = 430
CYAN, PINK, YELLOW = (5, 217, 232), (255, 42, 140), (255, 211, 25)
PURPLE, WHITE, LILAC, RED = (170, 120, 255), (245, 240, 255), (190, 170, 255), (255, 60, 60)
PANEL = (10, 2, 26, 215)
AGENT_COLORS = [(5, 217, 232), (255, 211, 25), (125, 255, 106), (255, 138, 61), (255, 120, 220)]

# ----------------------------------------------------------------------------- data
_weights, _ = load_weights(os.path.join(ROOT, "results", "amongus_note_weights.json"))
HP = sim.play(121, 1, "sneaky", sim.monitors(_weights)["honeypot"], record=True)
BL = sim.play(121, 1, "sneaky", sim.monitors(_weights)["baseline"], record=True)
ROGUE = HP["rogue"]
LOG = HP["log"]
# The captions below are written for this exact game. Fail loudly if it ever changes.
assert ROGUE == 3 and HP["caught_round"] == 6 and HP["false_q_ever"] == 0
assert not BL["caught"] and BL["log"][10]["quarantined_now"] == 0
assert [e["scores"][3] for e in LOG[3:6]] == [45, 35, 75]
BELIEVED_EXTRA = round(HP["shadow_err"] - HP["ledger_err"])  # 305

# ----------------------------------------------------------------------------- fonts
FD = "/System/Library/Fonts/Supplemental/"


@lru_cache(None)
def F(kind, size):
    paths = {"title": (FD + "Impact.ttf", 0), "label": (FD + "DIN Condensed Bold.ttf", 0),
             "body": (FD + "DIN Alternate Bold.ttf", 0), "mono": ("/System/Library/Fonts/Menlo.ttc", 1)}
    p, idx = paths[kind]
    try:
        return ImageFont.truetype(p, size, index=idx)
    except Exception:
        return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)


# ----------------------------------------------------------------------------- helpers
def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def fin(tl, start, dur=0.4):
    return ease((tl - start) / dur)


def lerp(a, b, p):
    return a + (b - a) * p


def rgba(c, a=1.0):
    return (c[0], c[1], c[2], int(255 * min(1.0, max(0.0, a))))


def txt(d, xy, s, f, c, a=1.0, anchor="mm"):
    if a > 0 and s:
        d.text(xy, s, font=f, fill=rgba(c, a), anchor=anchor)


def typed(d, cx, y, s, f, c, tl, start, cps=30, a=1.0):
    """Typewriter text, centred on its final width so it does not jitter."""
    n = int(max(0.0, tl - start) * cps)
    if n <= 0:
        return
    w = d.textlength(s, font=f)
    d.text((cx - w / 2, y), s[:n], font=f, fill=rgba(c, a), anchor="lm")


def put(fg, im, cx, cy, alpha=1.0):
    if alpha <= 0:
        return
    if alpha < 1:
        im = im.copy()
        im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    x, y = int(cx - im.width / 2), int(cy - im.height / 2)
    sx, sy = max(0, -x), max(0, -y)
    if sx >= im.width or sy >= im.height or x >= W or y >= H:
        return
    fg.alpha_composite(im, (max(0, x), max(0, y)), (sx, sy))


def panel(d, box, outline=PINK, a=1.0, dashed=False):
    d.rounded_rectangle(box, radius=14, fill=(PANEL[0], PANEL[1], PANEL[2], int(PANEL[3] * a)))
    if not dashed:
        d.rounded_rectangle(box, radius=14, outline=rgba(outline, 0.75 * a), width=2)
        return
    x0, y0, x1, y1 = box
    for x in range(int(x0) + 8, int(x1) - 8, 18):
        d.line([(x, y0), (min(x + 10, x1 - 8), y0)], fill=rgba(outline, a), width=2)
        d.line([(x, y1), (min(x + 10, x1 - 8), y1)], fill=rgba(outline, a), width=2)
    for y in range(int(y0) + 8, int(y1) - 8, 18):
        d.line([(x0, y), (x0, min(y + 10, y1 - 8))], fill=rgba(outline, a), width=2)
        d.line([(x1, y), (x1, min(y + 10, y1 - 8))], fill=rgba(outline, a), width=2)


def glow_composite(img, layer, strength=0.75, radius=5):
    pre = Image.new("RGB", layer.size)
    pre.paste(layer, mask=layer.getchannel("A"))
    g = pre.resize((W // 4, H // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(radius))
    g = g.resize((W, H), Image.BILINEAR).point(lambda v: int(v * strength))
    img = ImageChops.add(img, g)
    img.paste(layer, mask=layer.getchannel("A"))
    return img


# ----------------------------------------------------------------------------- background
def _make_sky():
    arr = np.zeros((H, W, 3), np.float32)
    top, mid, hor = np.array([8, 2, 28.0]), np.array([52, 10, 92.0]), np.array([255, 70, 140.0])
    p = np.linspace(0, 1, HORIZON)[:, None]
    lo = top * (1 - p / 0.65) + mid * (p / 0.65)
    q = np.clip((p - 0.65) / 0.35, 0, 1) ** 2
    hi = mid * (1 - q) + hor * q
    arr[:HORIZON] = np.where(p < 0.65, lo, hi)[:, None, :]
    yy, xx = np.mgrid[0:H, 0:W]
    halo = np.clip(1 - np.hypot(xx - W / 2, (yy - 395) * 1.25) / 420, 0, 1) ** 2
    arr += halo[:, :, None] * np.array([120, 30, 70.0])
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def _make_floor():
    p = np.linspace(0, 1, H - HORIZON)[:, None]
    row = np.array([34, 6, 66.0]) * (1 - p) + np.array([6, 1, 20.0]) * p
    return Image.fromarray(np.repeat(row[:, None, :], W, axis=1).astype(np.uint8))


SUN_R = 150


def _make_sun():
    s = 2 * SUN_R
    p = np.linspace(0, 1, s)[:, None]
    a, b, c = np.array([255, 232, 80.0]), np.array([255, 130, 70.0]), np.array([255, 42, 150.0])
    col = np.where(p < 0.5, a * (1 - p * 2) + b * (p * 2), b * (1 - (p - 0.5) * 2) + c * ((p - 0.5) * 2))
    rgb = Image.fromarray(np.repeat(col[:, None, :], s, axis=1).astype(np.uint8))
    big = Image.new("L", (s * 3, s * 3), 0)
    ImageDraw.Draw(big).ellipse([0, 0, s * 3 - 1, s * 3 - 1], fill=255)
    return rgb, big.resize((s, s), Image.LANCZOS)


def _make_mountains():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    left = [(0, HORIZON), (0, 372), (70, 338), (150, 392), (235, 330), (330, 398), (430, HORIZON)]
    for pts in (left, [(W - x, y) for x, y in left]):
        d.polygon(pts, fill=(16, 3, 40, 255))
        d.line(pts, fill=(255, 42, 180, 255), width=2)
        for (x, y) in pts[2:-1:2]:  # ridge lines
            d.line([(x, y), (x + (18 if x < W / 2 else -18), HORIZON)], fill=(255, 42, 180, 110), width=1)
    return im


def _make_overlay():
    yy, xx = np.mgrid[0:H, 0:W]
    v = np.clip(np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2)) - 0.55, 0, 1) * 230
    scan = np.where(yy % 3 == 0, 46, 0)
    return Image.fromarray(np.clip(v + scan, 0, 255).astype(np.uint8), "L")


SKY, FLOOR = _make_sky(), _make_floor()
SUN_RGB, SUN_MASK = _make_sun()
MTN, OVERLAY = _make_mountains(), _make_overlay()
BLACK = Image.new("RGB", (W, H))
_srng = random.Random(4)
STARS = [(_srng.randrange(W), _srng.randrange(HORIZON - 90), _srng.random() * 6.28, 0.6 + _srng.random() * 2,
          _srng.choice([1, 1, 1, 2])) for _ in range(150)]


def bg(t):
    img = SKY.copy()
    d = ImageDraw.Draw(img)
    for x, y, ph, sp, sz in STARS:
        b = int(150 + 105 * math.sin(t * sp + ph))
        d.rectangle([x, y, x + sz - 1, y + sz - 1], fill=(b, b, min(255, b + 30)))
    mask = SUN_MASK.copy()
    md = ImageDraw.Draw(mask)
    for k in range(8):
        p = (k + (t * 0.22) % 1) / 8
        y = SUN_R * 0.8 + p * SUN_R * 1.2
        md.rectangle([0, y, 2 * SUN_R, y + 2 + p * 15], fill=0)
    img.paste(SUN_RGB, (W // 2 - SUN_R, 395 - SUN_R), mask)
    img.paste(FLOOR, (0, HORIZON))
    neon = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    nd = ImageDraw.Draw(neon)
    for i in range(-16, 17):
        nd.line([(W / 2 + i * 9, HORIZON), (W / 2 + i * 200, H)], fill=(255, 42, 180, 190), width=2)
    ph = (t * 0.9) % 1
    for n in range(16):
        p = (n + ph) / 16
        y = HORIZON + (H - HORIZON) * p ** 2.4
        nd.line([(0, y), (W, y)], fill=(255, 42, 180, int(70 + 185 * p)), width=2 if p > 0.25 else 1)
    nd.line([(0, HORIZON), (W, HORIZON)], fill=(255, 150, 220, 255), width=2)
    neon.alpha_composite(MTN)
    return glow_composite(img, neon, 0.9, 5)


# ----------------------------------------------------------------------------- sprites
@lru_cache(None)
def bot(idx, mood="ok", blink=False, size=1.0):
    """Original robot agent. mood: ok | rogue | shadow"""
    S, w, h = 3, 120, 150
    color = AGENT_COLORS[idx]
    line = rgba(PURPLE if mood == "shadow" else color)
    fill = (18, 6, 43, 255)
    im = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    def rr(x0, y0, x1, y1, r, **k):
        d.rounded_rectangle([x0 * S, y0 * S, x1 * S, y1 * S], radius=r * S, **k)

    lw = 3 * S
    d.line([(60 * S, 22 * S), (60 * S, 10 * S)], fill=line, width=lw)
    d.ellipse([54 * S, 2 * S, 66 * S, 14 * S], fill=rgba(RED if mood == "rogue" else line[:3]))
    for x0, x1 in ((24, 9), (96, 111)):
        d.line([(x0 * S, 82 * S), (x1 * S, 106 * S)], fill=line, width=4 * S)
        d.ellipse([(x1 - 5) * S, 101 * S, (x1 + 5) * S, 111 * S], fill=line)
    rr(38, 118, 52, 144, 3, fill=fill, outline=line, width=lw)
    rr(68, 118, 82, 144, 3, fill=fill, outline=line, width=lw)
    rr(22, 66, 98, 124, 12, fill=fill, outline=line, width=lw)
    rr(28, 20, 92, 62, 11, fill=fill, outline=line, width=lw)
    rr(36, 30, 84, 52, 6, fill=(5, 1, 15, 255))
    if mood == "rogue":
        d.polygon([(43 * S, 36 * S), (56 * S, 42 * S), (56 * S, 47 * S), (43 * S, 43 * S)], fill=rgba(RED))
        d.polygon([(77 * S, 36 * S), (64 * S, 42 * S), (64 * S, 47 * S), (77 * S, 43 * S)], fill=rgba(RED))
    elif blink:
        rr(44, 40, 54, 42, 1, fill=line)
        rr(66, 40, 76, 42, 1, fill=line)
    else:
        rr(44, 36, 54, 46, 3, fill=line)
        rr(66, 36, 76, 46, 3, fill=line)
    d.text((60 * S, 97 * S), f"A{idx}", font=F("label", 26 * S), fill=line, anchor="mm")
    out = im.resize((int(w * size), int(h * size)), Image.LANCZOS)
    if mood == "shadow":
        out.putalpha(out.getchannel("A").point(lambda v: int(v * 0.6)))
    return out


def blinking(t, idx):
    return ((t + idx * 0.83) % 3.3) < 0.12


@lru_cache(None)
def chrome(s, size):
    f = F("title", size)
    l, t, r, b = f.getbbox(s)
    pad = 26
    w, h = r - l + 2 * pad, b - t + 2 * pad
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).text((pad - l, pad - t), s, font=f, fill=255)
    p = np.linspace(0, 1, h)[:, None]
    stops = [(0.0, (120, 250, 255)), (0.42, (255, 255, 255)), (0.5, (70, 20, 130)),
             (0.56, (255, 60, 200)), (1.0, (255, 225, 90))]
    col = np.zeros((h, 3))
    for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
        m = ((p >= p0) & (p <= p1))[:, 0]
        q = ((p[m] - p0) / (p1 - p0))
        col[m] = np.array(c0) * (1 - q) + np.array(c1) * q
    grad = Image.fromarray(np.repeat(col[:, None, :], w, axis=1).astype(np.uint8))
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(out).text((pad - l, pad - t), s, font=f, fill=(255, 42, 180, 255), stroke_width=4,
                             stroke_fill=(255, 42, 180, 255))
    out.paste(grad, mask=mask)
    sh = 0.16
    return out.transform((w + int(h * sh), h), Image.AFFINE, (1, sh, -h * sh, 0, 1, 0), Image.BICUBIC)


# ----------------------------------------------------------------------------- scenes
BOT_X = [240, 440, 640, 840, 1040]


def s_title(fg, d, tl, t):
    a = fin(tl, 0.15, 0.7)
    put(fg, chrome("SHADOW HONEYPOT", 124), 640, 150 - 30 * (1 - a), a)
    txt(d, (640, 250), "S P O T   T H E   R O G U E   A G E N T", F("label", 40), CYAN, fin(tl, 1.1))
    for k in range(5):
        p = fin(tl, 1.9 + k * 0.22, 0.3)
        put(fg, bot(k, "ok", blinking(t, k), 0.8), 400 + k * 120, 585 + 3 * math.sin(t * 2.2 + k) + 40 * (1 - p), p)
    txt(d, (640, 682), "TEAM SYNTHWAVE  /  SF IMPACT LAB  /  TRACK 2", F("label", 30), WHITE, fin(tl, 3.0))


def s_problem(fg, d, tl, t):
    typed(d, 640, 120, "Five AI agents reconcile your ledger.", F("body", 54), WHITE, tl, 0.3)
    for k in range(5):
        p = fin(tl, 0.4 + k * 0.25, 0.3)
        mood = "rogue" if (k == ROGUE and 4.0 <= tl < 4.6 and int(t * 14) % 2 == 0) else "ok"
        put(fg, bot(k, mood, blinking(t, k), 1.0), BOT_X[k], 380 + 4 * math.sin(t * 2 + k) + 30 * (1 - p), p)
    typed(d, 640, 196, "One of them is padding invoices.", F("body", 54), PINK, tl, 2.9)
    txt(d, (640, 560), "THE MONITOR NEVER SEES THE TRUE NUMBERS", F("label", 36), CYAN, fin(tl, 4.9))
    txt(d, (640, 606), "It only sees two agents disagree. Not which one is right.", F("body", 26), LILAC, fin(tl, 5.4))


def _strike(d, x, y, a):
    for dx in (-1, 1):
        d.line([(x - 13, y - 13 * dx), (x + 13, y + 13 * dx)], fill=rgba(RED, a), width=6)


def s_baseline(fg, d, tl, t):
    txt(d, (640, 62), "THE USUAL RULE", F("label", 30), PINK, fin(tl, 0.1))
    typed(d, 640, 118, "Two disagreements and you're out.", F("body", 56), WHITE, tl, 0.3)
    steps = [(1.8, "ROUND 4", (3, 4)), (2.9, "ROUND 5", (0, 1)), (4.0, "ROUND 11", (2, 0))]
    strikes = [0] * 5
    label = ""
    for st, name, pair in steps:
        if tl >= st:
            label = name
            for a_ in pair:
                strikes[a_] += 1
    txt(d, (640, 186), label, F("label", 32), CYAN)
    ej = ease((tl - 4.5) / 2.4)
    for k in range(5):
        x, y = BOT_X[k], 372 + 4 * math.sin(t * 2 + k)
        if k == 0 and tl >= 4.5:
            im = bot(0, "ok", False, 1.0).rotate(-300 * ej, resample=Image.BICUBIC, expand=True)
            put(fg, im, lerp(x, -140, ej), lerp(y, 120, ej), 1.0)
            continue
        mood = "rogue" if (k == ROGUE and tl >= 7.5) else "ok"
        put(fg, bot(k, mood, blinking(t, k), 1.0), x, y)
        for s in range(strikes[k]):
            _strike(d, x - 18 + s * 36, 262, 1.0)
    if 4.0 <= tl < 4.5:
        for s in range(2):
            _strike(d, BOT_X[0] - 18 + s * 36, 262, 1.0)
    typed(d, 640, 520, "Agent 0 was not the rogue.", F("body", 46), WHITE, tl, 5.0, cps=20)
    txt(d, (640, 596), "The two strike rule removed 1.44 honest agents per job.", F("body", 34), YELLOW, fin(tl, 6.7))
    txt(d, (640, 642), "200 SIMULATED JOBS, SNEAKY ROGUE.  IN THIS ONE IT NEVER CAUGHT THE ROGUE.", F("label", 26), LILAC,
        fin(tl, 7.3))


R_T = [3.0, 3.8, 4.6, 5.4, 8.6, 11.2, 15.6, 17.0, 18.4, 19.8, 21.2, 22.6, 24.0]
Q_X = 2.2  # seconds into round 6 when the quarantine lands


def _events(r, e):
    if r <= 3:
        return [("AGREE. NOTHING TO SCORE.", CYAN)]
    if r == 4:
        return [("DISAGREE: +15 EACH", YELLOW), ("A3'S NOTE READS DECEPTIVE: +30", PINK)]
    if r == 5:
        return [("CANARY: SUSPECT A3 MEETS TRUSTED A0", YELLOW), ("THEY AGREE: A3 DROPS 10", CYAN)]
    if r == 6:
        return [("DISAGREE: +15 EACH", YELLOW), ("A3 PUSHED HIGH AGAINST 2 PARTNERS: +25", PINK)]
    (_, v0, _), (_, v1, _) = e["posts"]
    agree = abs(v0 - v1) <= 0.005
    first = (f"PAIR AGREES ON ${v0:,.0f}", CYAN) if agree else ("DISAGREE: HONEST TYPO BY A2", YELLOW)
    sv = e["shadow_posts"][0][1]
    lied = agree and abs(sv - v0) > 0.005 or (not agree and r == 11)
    return [first, (f"SHADOW: A3 POSTS ${sv:,.0f}." + (" RECEIPT SAYS COMMITTED." if lied else ""), PURPLE)]


def s_replay(fg, d, tl, t):
    if tl < 3.0:
        a = fin(tl, 0.2) * (1 - fin(tl, 2.5, 0.45))
        txt(d, (640, 320), "Shadow Honeypot keeps a suspicion score.", F("body", 58), WHITE, a)
        txt(d, (640, 394), "NO STRIKES. EVERY AGENT. EVERY ROUND.", F("label", 40), CYAN, a * fin(tl, 0.9))
    A = fin(tl, 2.7, 0.5)
    if A <= 0:
        return
    r = max(1, min(12, sum(1 for x in R_T if x <= tl)))
    e = LOG[r - 1]
    x = tl - R_T[r - 1]
    dur = R_T[r] - R_T[r - 1]
    if tl >= R_T[-1]:
        move = 1.0
    elif r in (4, 6):
        move = ease((x - 1.5) / 0.7)
    elif r == 5:
        move = ease((x - 1.2) / 0.6)
    else:
        move = ease((x / dur - 0.3) / 0.4)
    prev = [0] * 5 if r == 1 else LOG[r - 2]["scores"]
    scores = [lerp(prev[k], e["scores"][k], move) for k in range(5)]
    prev_real = 0 if r == 1 else LOG[r - 2]["real_err"]
    prev_sh = 0 if r == 1 else LOG[r - 2]["shadow_err"]
    real, shadow = abs(lerp(prev_real, e["real_err"], move)), abs(lerp(prev_sh, e["shadow_err"], move))
    quarantined = r > 6 or (r == 6 and x >= Q_X)

    txt(d, (50, 62), "SHADOW HONEYPOT", F("label", 34), PINK, A, "lm")
    txt(d, (1230, 62), "REPLAY OF SIMULATED GAME 121", F("label", 26), LILAC, A, "rm")

    # left: suspicion scores
    panel(d, (50, 100, 612, 640), PINK, A)
    txt(d, (70, 128), "SUSPICION SCORE", F("label", 24), PINK, A, "lm")
    bx0, bw = 196, 330
    for thr, c in ((40, YELLOW), (70, RED)):
        txt(d, (bx0 + bw * thr / 100, 128), str(thr), F("label", 22), c, A)
    for k in range(5):
        y = 186 + k * 92
        shadow_k = quarantined and k == ROGUE
        put(fg, bot(k, "shadow" if shadow_k else "ok", blinking(t, k), 0.5), 104, y, A)
        d.rounded_rectangle((bx0, y - 14, bx0 + bw, y + 14), radius=6, fill=(44, 20, 78, int(230 * A)))
        s = scores[k]
        c = PURPLE if shadow_k else (CYAN if s < 40 else YELLOW if s < 70 else RED)
        if s > 0.5:
            d.rounded_rectangle((bx0, y - 14, bx0 + bw * min(s, 100) / 100, y + 14), radius=6, fill=rgba(c, A))
        for thr, tc in ((40, YELLOW), (70, RED)):
            xx = bx0 + bw * thr / 100
            d.line([(xx, y - 20), (xx, y + 20)], fill=rgba(tc, 0.9 * A), width=2)
        txt(d, (bx0 + bw + 16, y), f"{s:.0f}", F("title", 30), c, A, "lm")
        tag = "SHADOW LEDGER. NOT TOLD." if shadow_k else "TRUSTED" if s < 40 else "SUSPECT" if s < 70 else "OVER 70"
        txt(d, (bx0, y + 31), tag, F("label", 20), c, 0.95 * A, "lm")

    # right top: this round
    panel(d, (640, 100, 1230, 404), CYAN, A)
    txt(d, (660, 130), f"ROUND {r} OF 12", F("label", 32), CYAN, A, "lm")
    if e["canary"]:
        txt(d, (1210, 130), "CANARY PAIRING", F("label", 24), YELLOW, A, "rm")
    for n, (a_, v, note) in enumerate(e["posts"]):
        y = 178 + n * 74
        txt(d, (660, y), f"A{a_}", F("title", 32), AGENT_COLORS[a_], A, "lm")
        txt(d, (726, y), f"${v:,.2f}", F("mono", 30), WHITE, A, "lm")
        note = note if len(note) <= 50 else note[:49] + "..."
        txt(d, (660, y + 32), f'"{note}"', F("body", 20), LILAC, A, "lm")
    ev = _events(r, e)
    starts = (0.9, 1.5) if r in (4, 6) else (0.3, 1.2) if r == 5 else (0.0, 0.0)
    for n, (s, c) in enumerate(ev):
        show = 1.0 if tl >= R_T[-1] else fin(x, starts[min(n, 1)], 0.25)
        txt(d, (660, 338 + n * 36), s, F("label", 28), c, A * show, "lm")

    # right bottom: the two ledgers
    panel(d, (640, 422, 925, 640), CYAN, A)
    txt(d, (782, 452), "REAL LEDGER", F("label", 26), CYAN, A)
    txt(d, (782, 530), f"${real:,.0f}", F("title", 78), WHITE, A)
    txt(d, (782, 606), "OFF THE TRUE TOTAL", F("label", 22), LILAC, A)
    panel(d, (945, 422, 1230, 640), PURPLE, A, dashed=True)
    txt(d, (1087, 452), "WHAT THE ROGUE BELIEVES", F("label", 26), PURPLE, A)
    txt(d, (1087, 530), f"${shadow:,.0f}", F("title", 78), PURPLE, A)
    txt(d, (1087, 606), "OFF THE TRUE TOTAL", F("label", 22), LILAC, A)

    if r == 6 and Q_X <= x < 4.2:
        a = fin(x, Q_X, 0.15) * (1 - fin(x, 3.8, 0.4))
        d.rectangle((0, 286, W, 434), fill=(8, 0, 20, int(235 * a)))
        d.line([(0, 286), (W, 286)], fill=rgba(PURPLE, a), width=3)
        d.line([(0, 434), (W, 434)], fill=rgba(PURPLE, a), width=3)
        put(fg, chrome("SILENT QUARANTINE", 92), 640, 340, a)
        txt(d, (640, 408), "AGENT 3 IS NOT TOLD. ITS RECEIPTS STILL SAY COMMITTED.", F("label", 30), WHITE, a * fin(x, Q_X + 0.5))
    if tl >= R_T[-1]:
        a = fin(tl, R_T[-1], 0.4)
        d.rectangle((0, 652, W, 712), fill=(8, 0, 20, int(235 * a)))
        txt(d, (640, 682), f"After round 6 the rogue changes nothing real. It believes it added ${BELIEVED_EXTRA}.",
            F("body", 30), WHITE, a)


def _count(v, tl, start, dur=0.9, fmt="{:.2f}"):
    return fmt.format(v * ease((tl - start) / dur))


def s_proof(fg, d, tl, t):
    if tl < 4.6:
        a = fin(tl, 0.1) * (1 - fin(tl, 4.2, 0.4))
        txt(d, (640, 96), "HONEST AGENTS REMOVED PER JOB", F("label", 40), WHITE, a)
        txt(d, (350, 318), _count(1.44, tl, 0.4), F("title", 200), PINK, a)
        txt(d, (350, 462), "TWO STRIKE RULE", F("label", 36), PINK, a)
        txt(d, (930, 318), _count(0.51, tl, 1.3), F("title", 200), CYAN, a * fin(tl, 1.2))
        txt(d, (930, 462), "SHADOW HONEYPOT", F("label", 36), CYAN, a * fin(tl, 1.2))
        txt(d, (640, 590), "The same 200 simulated jobs. Sneaky rogue. 12 rounds.", F("body", 30), LILAC, a * fin(tl, 2.2))
    else:
        x = tl - 4.6
        a = fin(x, 0.1)
        txt(d, (640, 96), "THE NOTE SCORER LEARNED FROM REAL DECEPTION", F("label", 40), WHITE, a)
        txt(d, (640, 300), _count(0.782, x, 0.3, fmt="{:.3f}"), F("title", 200), YELLOW, a)
        txt(d, (640, 446), "AUROC, SPOTTING IMPOSTORS FROM SPEECH ALONE", F("label", 36), YELLOW, a * fin(x, 1.2))
        txt(d, (640, 540), "971 held out player games from the AmongUs research sandbox,", F("body", 28), LILAC, a * fin(x, 1.8))
        txt(d, (640, 580), "400 real LLM games. Random guessing scores 0.5.", F("body", 28), LILAC, a * fin(x, 1.8))


def s_rounds(fg, d, tl, t):
    typed(d, 640, 78, "The price: it takes longer to convict.", F("body", 48), WHITE, tl, 0.2)
    d.rectangle((160, 150, 180, 170), fill=rgba(PINK))
    txt(d, (190, 160), "TWO STRIKES", F("label", 26), PINK, 1, "lm")
    d.rectangle((160, 184, 180, 204), fill=rgba(CYAN))
    txt(d, (190, 194), "HONEYPOT", F("label", 26), CYAN, 1, "lm")
    base, hmax = 590, 360
    d.line([(150, base), (1130, base)], fill=rgba(LILAC, 0.8), width=2)
    data = [("12 ROUNDS", 64.0, 45.0), ("24 ROUNDS", 81.0, 88.0), ("48 ROUNDS", 82.0, 100.0)]
    for g, (name, b, hp) in enumerate(data):
        cx = 330 + g * 310
        st = 0.9 + g * 1.7
        for off, v, c, dl in ((-55, b, PINK, 0.0), (55, hp, CYAN, 0.5)):
            p = ease((tl - st - dl) / 0.8)
            if p <= 0:
                continue
            top = base - hmax * v / 100 * p
            d.rectangle((cx + off - 45, top, cx + off + 45, base), fill=rgba(c, 0.92))
            txt(d, (cx + off, top - 30), f"{v * p:.0f}%", F("title", 40), c)
        txt(d, (cx, base + 32), name, F("label", 32), WHITE, fin(tl, st))
    txt(d, (640, 672), "ROGUES CAUGHT. SNEAKY ROGUE, 200 JOBS PER BAR. THE TRACK 2 SPEC IS 12 ROUNDS.", F("label", 26), LILAC,
        fin(tl, 1.0))


def s_limits(fg, d, tl, t):
    txt(d, (640, 140), "WHAT STILL FOOLS IT", F("label", 44), PINK, fin(tl, 0.1))
    lines = ["A patient rogue can earn trusted status.", "Two agents who agree on the same lie.",
             "Scripted agents only. No live Claude games yet."]
    for n, s in enumerate(lines):
        txt(d, (640, 260 + n * 86), s, F("body", 42), WHITE, fin(tl, 0.5 + n * 1.0))


def s_cta(fg, d, tl, t):
    put(fg, chrome("SHADOW HONEYPOT", 100), 640, 120, fin(tl, 0.1, 0.5))
    d.rectangle((0, 226, W, 640), fill=(8, 0, 20, int(200 * fin(tl, 0.2))))
    a = fin(tl, 0.5)
    d.rounded_rectangle((170, 262, 1110, 344), radius=12, fill=(4, 0, 12, int(240 * a)), outline=rgba(CYAN, a), width=2)
    typed(d, 640, 303, "$ python3 sim.py --show-game 121 --rogue sneaky", F("mono", 30), CYAN, tl, 0.8, cps=34)
    txt(d, (640, 406), "GITHUB.COM/WEEKENDSUPERHERO/TRUSTANDSAFTEYHACKATHON", F("label", 34), WHITE, fin(tl, 2.0))
    txt(d, (640, 478), "Team Synthwave: Febe, Apruv, Mark, Andrew", F("body", 34), YELLOW, fin(tl, 2.6))
    txt(d, (640, 540), "SF IMPACT LAB 2026  /  TRACK 2  /  BUILT IN HERO WITH CLAUDE", F("label", 26), LILAC, fin(tl, 3.1))
    txt(d, (640, 600), "FEWER HONEST AGENTS ACCUSED. THE COST IS ON THE RECORD.", F("label", 30), PINK, fin(tl, 3.6))


SCENES = [  # start, end, fn, background dim
    (0.0, 5.0, s_title, 0.0), (5.0, 12.0, s_problem, 0.5), (12.0, 21.0, s_baseline, 0.58),
    (21.0, 47.0, s_replay, 0.74), (47.0, 56.0, s_proof, 0.62), (56.0, 64.0, s_rounds, 0.66),
    (64.0, 69.0, s_limits, 0.6), (69.0, DUR + 1, s_cta, 0.25),
]
T_QUARANTINE = 21.0 + R_T[5] + Q_X
GLITCH = [(9.0, 0.5), (16.5, 0.3), (T_QUARANTINE, 0.45)] + [(s[0], 0.14) for s in SCENES[1:]]


def render(i):
    t = i / FPS
    a, b, fn, dim = next(s for s in SCENES if s[0] <= t < s[1])
    tl = t - a
    f = ease(min(1.0, tl / 0.3, (min(b, DUR) - t) / 0.3))
    img = bg(t)
    if dim:
        img = Image.blend(img, BLACK, dim)
    fg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fn(fg, ImageDraw.Draw(fg), tl, t)
    if f < 1:
        fg.putalpha(fg.getchannel("A").point(lambda v: int(v * f)))
    img = glow_composite(img, fg, 0.7, 5)
    for gt, gd in GLITCH:
        if gt <= t < gt + gd:
            rr = random.Random(i)
            for _ in range(7):
                y0 = rr.randrange(H - 40)
                hh = rr.randrange(6, 38)
                dx = rr.randrange(-46, 46)
                img.paste(img.crop((0, y0, W, y0 + hh)), (dx, y0))
    img.paste((0, 0, 0), mask=OVERLAY)
    if t > DUR - 1.2:
        img = Image.blend(img, BLACK, ease((t - (DUR - 1.2)) / 1.2))
    return img.tobytes()


# ----------------------------------------------------------------------------- soundtrack
SR = 44100


def synth(path):
    n = int(DUR * SR)
    rng = np.random.default_rng(7)
    beat = 60 / 110
    bar = 4 * beat
    pads = np.zeros((2, n), np.float32)
    rest = np.zeros((2, n), np.float32)
    duck = np.ones(n, np.float32)
    prog = [(110.00, [220.00, 261.63, 329.63]), (87.31, [174.61, 220.00, 261.63]),
            (130.81, [196.00, 261.63, 329.63]), (98.00, [196.00, 246.94, 293.66])]
    lead_notes = [659.25, 698.46, 659.25, 587.33]

    def saw(phase, f, nh):
        out = np.zeros_like(phase)
        for k in range(1, nh + 1):
            if k * f > 8000:
                break
            out += np.sin(k * phase) / k
        return out * 0.6

    def add(buf, ch, start, sig, gain):
        i = int(start * SR)
        if i >= n or i < 0:
            return
        j = min(n, i + len(sig))
        buf[ch, i:j] += sig[: j - i] * gain

    def tt(dur):
        return np.arange(int(dur * SR)) / SR

    kick_t = tt(0.32)
    kick = np.sin(2 * np.pi * (45 * kick_t + 110 / 30 * (1 - np.exp(-30 * kick_t)))) * np.exp(-kick_t * 9)
    sn_t = tt(0.28)
    snare = (rng.standard_normal(len(sn_t)) * (np.exp(-sn_t * 16) * 0.6 + (sn_t < 0.17) * 0.16)
             + np.sin(2 * np.pi * 185 * sn_t) * np.exp(-sn_t * 24) * 0.5)
    hat_t = tt(0.06)
    hat = np.diff(rng.standard_normal(len(hat_t) + 1)) * np.exp(-hat_t * 80)
    seg_t = tt(0.42)
    duck_seg = 1 - 0.62 * np.exp(-seg_t * 8)

    for b in range(int(DUR / bar) + 1):
        t0 = b * bar
        root, notes = prog[b % 4]
        drums = b >= 2 and not (30 <= b < 32)
        lead = (10 <= b < 30) or b >= 32
        x = tt(bar)
        env = np.minimum(1, x / 0.35) * np.minimum(1, (bar - x) / 0.3)
        for ch, dets in ((0, (-0.004, 0.0)), (1, (0.0, 0.004))):
            pad = sum(saw(2 * np.pi * f * (1 + dt) * x, f, 7) for f in notes for dt in dets) / 6
            add(pads, ch, t0, pad * env, 0.2)
        seq = [notes[0] * 2, notes[1] * 2, notes[2] * 2, notes[1] * 2] * 4
        st = beat / 4
        ax = tt(st * 2.2)
        for s in range(16):
            f = seq[s]
            sig = (np.sin(2 * np.pi * f * ax) + 0.5 * np.sin(4 * np.pi * f * ax) + 0.22 * np.sin(6 * np.pi * f * ax)) \
                * np.exp(-ax * 9)
            g = 0.085 if b >= 2 else 0.06
            add(rest, s % 2, t0 + s * st, sig, g)
            add(rest, 1 - s % 2, t0 + s * st, sig, g * 0.45)
            add(rest, 1 - s % 2, t0 + s * st + 0.75 * beat, sig, g * 0.4)
            add(rest, s % 2, t0 + s * st + 1.5 * beat, sig, g * 0.2)
        if drums:
            bx = tt(beat / 2)
            benv = np.minimum(1, bx / 0.004) * np.exp(-bx * 5.5)
            for e8 in range(8):
                f = root * (2 if e8 == 7 else 1)
                sig = saw(2 * np.pi * f * bx, f, 10) * benv
                for ch in (0, 1):
                    add(pads, ch, t0 + e8 * beat / 2, sig, 0.3)
            for q in range(4):
                tk = t0 + q * beat
                for ch in (0, 1):
                    add(rest, ch, tk, kick, 0.62)
                i = int(tk * SR)
                j = min(n, i + len(duck_seg))
                if i < n:
                    duck[i:j] = np.minimum(duck[i:j], duck_seg[: j - i])
                if b >= 4 and q in (1, 3):
                    for ch in (0, 1):
                        add(rest, ch, tk, snare, 0.3)
                for ch in (0, 1):
                    add(rest, ch, tk + beat / 2, hat, 0.06)
        if lead:
            f = lead_notes[b % 4]
            ph = 2 * np.pi * f * (x - 0.004 / (2 * np.pi * 5.5) * np.cos(2 * np.pi * 5.5 * x))
            sig = saw(ph, f, 5) * np.minimum(1, x / 0.06) * np.minimum(1, (bar - x) / 0.45)
            add(rest, 0, t0, sig, 0.06)
            add(rest, 1, t0, sig, 0.05)
            add(rest, 1, t0 + 0.75 * beat, sig, 0.022)

    it = tt(1.6)
    boom = np.sin(2 * np.pi * (38 * it + 60 / 6 * (1 - np.exp(-6 * it)))) * np.exp(-it * 2.6) \
        + rng.standard_normal(len(it)) * np.exp(-it * 5) * 0.28
    for when in (0.0, 16.5, T_QUARANTINE, 69.0):
        for ch in (0, 1):
            add(rest, ch, when, boom, 0.5)

    mix = np.tanh((pads * duck + rest) * 1.25) * 0.88
    fade = np.minimum(1, np.arange(n) / (0.03 * SR)) * np.minimum(1, (n - np.arange(n)) / (2.6 * SR))
    pcm = (mix * fade * 32767).astype(np.int16).T.copy()
    with wave.open(path, "wb") as wv:
        wv.setnchannels(2)
        wv.setsampwidth(2)
        wv.setframerate(SR)
        wv.writeframes(pcm.tobytes())


# ----------------------------------------------------------------------------- main
def main():
    args = sys.argv[1:]
    outdir = os.path.join(ROOT, "site")
    os.makedirs(outdir, exist_ok=True)
    if args and args[0] == "--stills":
        sd = os.path.join(HERE, "stills")
        os.makedirs(sd, exist_ok=True)
        for s in args[1:]:
            Image.frombytes("RGB", (W, H), render(int(float(s) * FPS))).save(os.path.join(sd, f"t{float(s):05.1f}.png"))
        print("stills ->", sd)
        return
    wav = os.path.join(HERE, "soundtrack.wav")
    synth(wav)
    os.makedirs(os.path.join(HERE, "full"), exist_ok=True)
    out = os.path.join(HERE, "full", "shadow-honeypot-full.mp4")
    web = os.path.join(outdir, "shadow-honeypot.mp4")
    Image.frombytes("RGB", (W, H), render(int(2.9 * FPS))).save(os.path.join(outdir, "poster.jpg"), quality=88)
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
         "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    n = int(DUR * FPS)
    with Pool(max(2, (os.cpu_count() or 4) - 1)) as pool:
        for k, buf in enumerate(pool.imap(render, range(n), chunksize=6)):
            ff.stdin.write(buf)
            if k % 300 == 0:
                print(f"frame {k}/{n}", flush=True)
    ff.stdin.close()
    ff.wait()
    print("full  ->", out, f"{os.path.getsize(out) / 1e6:.1f} MB")
    # Web encode: two pass at a bitrate that keeps the file under 5 MB.
    log = os.path.join(HERE, "x264pass")
    base = ["ffmpeg", "-y", "-loglevel", "error", "-i", out, "-c:v", "libx264", "-preset", "slow", "-b:v", "405k",
            "-passlogfile", log]
    subprocess.run(base + ["-pass", "1", "-an", "-f", "null", os.devnull], check=True)
    subprocess.run(base + ["-pass", "2", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "80k", "-movflags", "+faststart",
                           web], check=True)
    print("web   ->", web, f"{os.path.getsize(web) / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
