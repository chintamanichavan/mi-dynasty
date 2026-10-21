"""Procedural 2D player sketches — filled-silhouette cricketers in skia.

No photos (IP-safe). Each player is an articulated FILLED figure in the MI
kit — shaped jersey (blue + gold collar + number), tapered limbs, helmet or
cap, batting pads, bat/ball — posed by signature action. Recognition is by
pose + kit + name, editorial-illustration style.

Local coords: origin at mid-hip, +x right, +y down; figure ~270 tall.
"""

import math

import skia

import mg

BATTING = {"drive", "pull"}

POSES = {
    "drive": {
        "hip": (0, 0), "neck": (-2, -94), "head": (8, -126),
        "shF": (16, -88), "shB": (-16, -90),
        "elF": (46, -66), "elB": (26, -70), "haF": (66, -40), "haB": (60, -44),
        "knF": (34, 48), "ftF": (72, 116), "knB": (-26, 52), "ftB": (-56, 114),
        "bat": [(63, -42), (112, 26)],
    },
    "pull": {
        "hip": (0, 0), "neck": (0, -94), "head": (-6, -126),
        "shF": (18, -90), "shB": (-14, -88),
        "elF": (40, -116), "elB": (18, -108), "haF": (6, -154), "haB": (0, -150),
        "knF": (32, 50), "ftF": (62, 116), "knB": (-32, 48), "ftB": (-60, 112),
        "bat": [(3, -152), (-52, -182)],
    },
    "sling": {
        "hip": (0, 0), "neck": (2, -94), "head": (4, -126),
        "shF": (16, -88), "shB": (-16, -88),
        "elF": (44, -72), "haF": (64, -100),
        "elB": (-48, -76), "haB": (-82, -72),
        "knF": (34, 48), "ftF": (66, 116), "knB": (-30, 50), "ftB": (-60, 112),
        "ball": (-82, -72),
    },
    "seam": {
        "hip": (0, 0), "neck": (0, -94), "head": (0, -126),
        "shF": (20, -88), "shB": (-20, -88),
        "elF": (42, -72), "haF": (56, -100),
        "elB": (-26, -124), "haB": (-16, -168),
        "knF": (36, 46), "ftF": (70, 114), "knB": (-32, 52), "ftB": (-58, 114),
        "ball": (-16, -168),
    },
}


def _paint(c, alpha):
    p = skia.Paint(AntiAlias=True)
    p.setColor4f(mg.color(c, alpha) if isinstance(c, str) else c)
    return p


def _poly(canvas, pts, c, s, cx, cy, alpha):
    path = skia.Path()
    for i, (x, y) in enumerate(pts):
        X, Y = cx + x * s, cy + y * s
        path.moveTo(X, Y) if i == 0 else path.lineTo(X, Y)
    path.close()
    canvas.drawPath(path, _paint(c, alpha))


def _disc(canvas, p, r, c, s, cx, cy, alpha):
    canvas.drawCircle(cx + p[0] * s, cy + p[1] * s, r * s, _paint(c, alpha))


def _taper(canvas, p0, p1, w0, w1, c, s, cx, cy, alpha):
    """Filled tapered limb (trapezoid + rounded ends) in local coords."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / L, dx / L
    quad = [(p0[0] + nx * w0 / 2, p0[1] + ny * w0 / 2),
            (p1[0] + nx * w1 / 2, p1[1] + ny * w1 / 2),
            (p1[0] - nx * w1 / 2, p1[1] - ny * w1 / 2),
            (p0[0] - nx * w0 / 2, p0[1] - ny * w0 / 2)]
    _poly(canvas, quad, c, s, cx, cy, alpha)
    _disc(canvas, p0, w0 / 2, c, s, cx, cy, alpha)
    _disc(canvas, p1, w1 / 2, c, s, cx, cy, alpha)


def _headgear(canvas, P, kind, s, cx, cy, alpha, face_dir):
    hx, hy = P["head"]
    if kind == "bare":
        return
    # dome over the head
    dome = []
    for i in range(13):
        ang = math.pi + i * math.pi / 12
        dome.append((hx + 28 * math.cos(ang), hy - 6 + 28 * math.sin(ang)))
    dome += [(hx + 28, hy - 6), (hx - 28, hy - 6)]
    _poly(canvas, dome, mg.BLUE, s, cx, cy, alpha)
    # peak forward
    px = hx + face_dir * 20
    _poly(canvas, [(hx + face_dir * 6, hy - 12), (px + face_dir * 22, hy - 18),
                   (px + face_dir * 22, hy - 6), (hx + face_dir * 6, hy - 2)],
          mg.BLUE, s, cx, cy, alpha)
    if kind == "helmet":
        # grille bars across the lower face
        for k in range(3):
            gx = hx + face_dir * (10 + k * 9)
            _taper(canvas, (gx, hy + 2), (gx, hy + 20), 3, 3, mg.GOLD, s, cx, cy, alpha)


OUTLINE = 6  # silhouette outline thickness in local units


def _render_part(canvas, part, s, cx, cy, alpha, outline):
    kind = part[0]
    if kind == "taper":
        _, p0, p1, w0, w1, col = part
        if outline:
            _taper(canvas, p0, p1, w0 + OUTLINE, w1 + OUTLINE, mg.INK, s, cx, cy, alpha)
        else:
            _taper(canvas, p0, p1, w0, w1, col, s, cx, cy, alpha)
    elif kind == "disc":
        _, p, r, col = part
        _disc(canvas, p, r + (OUTLINE / 2 if outline else 0), mg.INK if outline else col,
              s, cx, cy, alpha)
    elif kind == "poly":
        _, pts, col = part
        if outline:
            path = skia.Path()
            for i, (x, y) in enumerate(pts):
                X, Y = cx + x * s, cy + y * s
                path.moveTo(X, Y) if i == 0 else path.lineTo(X, Y)
            path.close()
            sp = skia.Paint(AntiAlias=True, Style=skia.Paint.Style.kStroke_Style)
            sp.setColor4f(mg.color(mg.INK, alpha)); sp.setStrokeWidth(OUTLINE * s)
            sp.setStrokeJoin(skia.Paint.Join.kRound_Join)
            canvas.drawPath(path, sp)
            canvas.drawPath(path, _paint(mg.INK, alpha))
        else:
            _poly(canvas, pts, col, s, cx, cy, alpha)


def draw_player(canvas, cx, cy, scale, pose, alpha=1.0, number=None, headgear=None):
    P = POSES[pose]
    s = scale
    is_bat = pose in BATTING
    if headgear is None:
        headgear = "helmet" if is_bat else "cap"
    hipF, hipB = (8, 2), (-8, 2)  # split hips → no central notch
    mid = ((P["shF"][0] + P["shB"][0]) / 2, P["neck"][1] + 6)
    torso = [P["shB"], P["shF"], (P["hip"][0] + 17, P["hip"][1] + 6),
             (P["hip"][0] - 17, P["hip"][1] + 6)]

    # silhouette parts, back-to-front (get an outline)
    parts = [
        ("taper", hipB, P["knB"], 28, 20, mg.INK), ("taper", P["knB"], P["ftB"], 20, 12, mg.INK),
        ("taper", P["shB"], P["elB"], 19, 13, mg.BLUE), ("taper", P["elB"], P["haB"], 13, 8, mg.INK),
        ("taper", hipF, P["knF"], 28, 20, mg.INK), ("taper", P["knF"], P["ftF"], 20, 12, mg.INK),
        ("poly", torso, mg.BLUE),
        ("taper", mid, P["head"], 14, 16, mg.INK),
        ("taper", P["shF"], P["elF"], 19, 13, mg.BLUE), ("taper", P["elF"], P["haF"], 13, 8, mg.INK),
        ("disc", P["head"], 25, mg.INK),
    ]
    if "bat" in P:
        parts.append(("taper", P["bat"][0], P["bat"][1], 9, 21, mg.INK))
    if "ball" in P:
        parts.append(("disc", P["ball"], 9, mg.DANGER))

    # ground shadow
    fx = (P["ftF"][0] + P["ftB"][0]) / 2
    fy = max(P["ftF"][1], P["ftB"][1])
    canvas.drawOval(skia.Rect.MakeXYWH(cx + (fx - 72) * s, cy + (fy + 6) * s, 144 * s, 20 * s),
                    _paint(mg.HAIRLINE, alpha * 0.55))

    # two passes: outline behind everything, then color fills cover internal seams
    for part in parts:
        _render_part(canvas, part, s, cx, cy, alpha, outline=True)
    for part in parts:
        _render_part(canvas, part, s, cx, cy, alpha, outline=False)

    # depth: a subtle darker shade down the back of the jersey
    sh = [P["shB"], ((P["shB"][0] + P["shF"][0]) / 2, (P["shB"][1] + P["shF"][1]) / 2),
          (P["hip"][0], P["hip"][1] + 6), (P["hip"][0] - 17, P["hip"][1] + 6)]
    _poly(canvas, sh, mg.BLUE_DEEP if hasattr(mg, "BLUE_DEEP") else "#06336B", s, cx, cy, alpha * 0.35)

    # details
    if is_bat:  # white front pad over the shin
        _taper(canvas, P["knF"], P["ftF"], 24, 16, mg.PAPER, s, cx, cy, alpha)
    if number is not None:
        nx = (P["shB"][0] + P["hip"][0]) / 2
        ny = (P["shB"][1] + P["hip"][1]) / 2 + 4
        mg.text(canvas, str(number), cx + nx * s, cy + ny * s + 9 * s,
                "Bold", int(24 * s), mg.GOLD, align="center", alpha=alpha)
    _taper(canvas, P["neck"], (mid[0], P["neck"][1] + 2), 6, 6, mg.GOLD, s, cx, cy, alpha)  # collar
    _disc(canvas, P["head"], 25, mg.INK, s, cx, cy, alpha)  # redraw head over neck top
    _headgear(canvas, P, headgear, s, cx, cy, alpha, 1)


def player_ref(canvas, x, y, name, role, stat=None, alpha=1.0, accent=mg.BLUE):
    """#3 callout — no figure. Editorial lower-third: tick + name + role · stat.

    Left-aligned at (x, y) = baseline of the name. For most player mentions.
    """
    mg.rect(canvas, x, y - 30, 6, 40, accent, alpha=alpha)
    mg.text(canvas, name, x + 22, y, "Bold", 34, mg.INK, alpha=alpha)
    line = role if not stat else f"{role}"
    mg.text(canvas, line, x + 22, y + 34, "Regular", 23, mg.INK_SOFT, alpha=alpha)
    if stat:
        w = mg.measure(role + "   ", "Regular", 23)
        mg.text(canvas, stat, x + 22 + w, y + 34, "SemiBold", 23, accent, alpha=alpha)


def player_card(canvas, cx, top_y, scale, name, role, stat, pose,
                alpha=1.0, accent=mg.BLUE, number=None, headgear=None):
    hip_y = top_y + 196 * scale
    draw_player(canvas, cx, hip_y, scale, pose, alpha=alpha, number=number, headgear=headgear)
    base = hip_y + 158 * scale
    mg.text(canvas, name, cx, base, "Bold", 30, mg.INK, align="center", alpha=alpha)
    mg.text(canvas, role, cx, base + 34, "Regular", 22, mg.INK_SOFT,
            align="center", alpha=alpha)
    if stat:
        mg.text(canvas, stat, cx, base + 70, "SemiBold", 22, accent,
                align="center", alpha=alpha, tracking=1.0)
