"""Chapter 2 — "The Hitman blueprint" (editorial idiom).

Three acts: the PIVOT (Ponting recedes / Rohit steps in, no photos — names +
the avg-10.4 stat that quantifies 'form cratered'); the METHOD (a clean triad
of Rohit's attributes); the PAYOFF (the film's FIRST gold — 2013 & 2015 titles).

All facts verified: Ponting 5 inns / avg 10.4 in 2013; MI lost 5 of first 6 in
2015; 2013 final beat CSK by 23, 2015 by 41 (Rohit POM). Cricsheet-derived.
  uv run scene_ch2.py --stills   |   uv run scene_ch2.py
"""

import math
import os
import sys

import skia

import mg

HERE = os.path.dirname(os.path.abspath(__file__))
FRAME_DIR = os.path.join(HERE, "out", "ch2", "frames")
VIDEO = os.path.join(HERE, "out", "ch2", "ch2.mp4")

CX = mg.W / 2

# Act timing (frames)
DIV_IN, PONT_IN, ROHIT_IN = 60, 84, 140
TRANS_START, TRANS_DUR = 330, 80          # left recedes, right slides to center
TRIAD_IN = 440
THREAD_OUT = 800                           # pivot+triad fade out
PAYOFF_IN = 842
N_FRAMES = 1300


def star(canvas, cx, cy, r, c, alpha=1.0):
    path = skia.Path()
    for i in range(10):
        rr = r if i % 2 == 0 else r * 0.42
        ang = -math.pi / 2 + i * math.pi / 5
        x, y = cx + rr * math.cos(ang), cy + rr * math.sin(ang)
        path.moveTo(x, y) if i == 0 else path.lineTo(x, y)
    path.close()
    p = skia.Paint(AntiAlias=True)
    p.setColor4f(mg.color(c, alpha))
    canvas.drawPath(path, p)


def draw_header(canvas, fr, fade):
    kick_a = mg.window(fr, 8, 22) * fade
    mg.rect(canvas, mg.MARGIN, 122, 46 * mg.window(fr, 8, 22), 5, mg.GOLD, alpha=fade)
    mg.text(canvas, "CHAPTER TWO", mg.MARGIN, 144, "SemiBold", 22, mg.BLUE,
            alpha=kick_a, tracking=6.0)
    mg.text(canvas, "The Hitman blueprint", mg.MARGIN, 196, "Bold", 40, mg.INK,
            alpha=kick_a)
    mg.text(canvas, "02", mg.W - mg.MARGIN, 150, "Bold", 28, mg.HAIRLINE,
            align="right", alpha=kick_a)


def draw_pivot(canvas, fr):
    thread_a = mg.window(fr, ROHIT_IN, 22) * (1 - mg.window(fr, THREAD_OUT, 30))
    left_a = mg.window(fr, PONT_IN, 22) * (1 - mg.window(fr, TRANS_START, TRANS_DUR))
    slide = mg.window(fr, TRANS_START, TRANS_DUR, ease=mg.ease_in_out)
    rohit_x = mg.lerp(CX + 360, CX, slide)

    # center divider
    div_a = (1 - mg.window(fr, TRANS_START, TRANS_DUR)) * mg.window(fr, DIV_IN, 30)
    dh = mg.lerp(0, 270, mg.window(fr, DIV_IN, 36, ease=mg.ease_out_quint))
    mg.line(canvas, CX, 360 - dh * 0.2, CX, 360 + dh, mg.HAIRLINE, 2, alpha=div_a)

    # LEFT — Ponting, receding (grey)
    lx = CX - 360
    if left_a > 0:
        mg.text(canvas, "THE INCUMBENT", lx, 372, "SemiBold", 20, mg.INK_SOFT,
                align="center", alpha=left_a, tracking=4.0)
        mg.text(canvas, "Ricky Ponting", lx, 440, "Bold", 46, mg.INK_SOFT,
                align="center", alpha=left_a)
        text = "10.4"
        mg.text(canvas, text, lx, 588, "Bold", 86, mg.INK_SOFT, align="center", alpha=left_a)
        mg.text(canvas, "BATTING AVERAGE · 5 INNINGS, 2013", lx, 636, "Medium",
                19, mg.INK_SOFT, align="center", alpha=left_a, tracking=2.0)
        mg.text(canvas, "Then he benched himself.", lx, 712, "Medium", 27,
                mg.INK_SOFT, align="center", alpha=left_a)

    # RIGHT — Rohit, vivid; slides to center on the pivot
    if thread_a > 0:
        in_triad = fr >= TRIAD_IN
        mg.text(canvas, "THE PIVOT · APRIL 2013", rohit_x, 372, "SemiBold", 20,
                mg.BLUE, align="center", alpha=thread_a * (1 - mg.window(fr, TRIAD_IN - 20, 24)),
                tracking=4.0)
        mg.text(canvas, "Rohit Sharma", rohit_x, 446, "Bold",
                mg.lerp(46, 54, slide), mg.INK, align="center", alpha=thread_a)
        if not in_triad:
            mg.text(canvas, "New captain · aged 26", rohit_x, 492, "Regular", 26,
                    mg.INK_SOFT, align="center", alpha=thread_a * (1 - mg.window(fr, TRIAD_IN - 20, 24)))


def draw_triad(canvas, fr):
    a = mg.window(fr, TRIAD_IN, 26) * (1 - mg.window(fr, THREAD_OUT, 30))
    if a <= 0:
        return
    mg.text(canvas, "HIS METHOD", CX, 500, "SemiBold", 20, mg.BLUE,
            align="center", alpha=a, tracking=5.0)
    verts = [(CX, 560), (CX - 300, 792), (CX + 300, 792)]
    edges_p = mg.window(fr, TRIAD_IN + 16, 34, ease=mg.ease_out_quint)
    for (x0, y0), (x1, y1) in [(verts[0], verts[1]), (verts[1], verts[2]), (verts[2], verts[0])]:
        mg.line(canvas, x0, y0, mg.lerp(x0, x1, edges_p), mg.lerp(y0, y1, edges_p),
                mg.HAIRLINE, 2, alpha=a)
    labels = ["DATA-DRIVEN", "CALM UNDER PRESSURE", "BACKS DOMESTIC TALENT"]
    offs = [(0, -34), (0, 52), (0, 52)]
    for i, ((vx, vy), lab) in enumerate(zip(verts, labels)):
        na = mg.window(fr, TRIAD_IN + 30 + i * 12, 22)
        mg.dot(canvas, vx, vy, 8 * na, mg.BLUE, alpha=a * na)
        mg.text(canvas, lab, vx + offs[i][0], vy + offs[i][1], "SemiBold", 24,
                mg.INK, align="center", alpha=a * na, tracking=1.5)


def draw_payoff(canvas, fr):
    a = mg.window(fr, PAYOFF_IN, 26)
    if a <= 0:
        return
    mg.text(canvas, "THE BLUEPRINT DELIVERED", CX, 322, "SemiBold", 22, mg.BLUE,
            align="center", alpha=a, tracking=5.0)
    cols = [
        (CX - 320, 2013, "beat Chennai by 23 runs", "First-ever IPL title"),
        (CX + 320, 2015, "beat Chennai by 41 runs", "Lost 5 of first 6 — then won it"),
    ]
    for i, (x, yr, line1, line2) in enumerate(cols):
        sa = mg.window(fr, PAYOFF_IN + 18 + i * 18, 24, ease=mg.ease_out_quint)
        star_y = mg.lerp(440 - 50, 460, sa)
        star(canvas, x, star_y, 46 * mg.clamp01(sa), mg.GOLD, alpha=sa)
        ta = mg.window(fr, PAYOFF_IN + 34 + i * 18, 22)
        mg.text(canvas, str(yr), x, 610, "Bold", 70, mg.INK, align="center", alpha=ta)
        mg.text(canvas, "CHAMPIONS", x, 656, "SemiBold", 26, mg.GOLD,
                align="center", alpha=ta, tracking=4.0)
        mg.text(canvas, line1, x, 702, "Medium", 25, mg.INK, align="center", alpha=ta)
        mg.text(canvas, line2, x, 738, "Regular", 22, mg.INK_SOFT, align="center", alpha=ta)
    tag = mg.window(fr, PAYOFF_IN + 90, 28)
    mg.text(canvas, "No longer just rich. Now smart.", CX, 868, "Bold", 40,
            mg.INK, align="center", alpha=tag)


def draw(canvas, fr):
    fade = 1 - mg.window(fr, PAYOFF_IN - 24, 28)
    draw_header(canvas, fr, fade)
    draw_pivot(canvas, fr)
    draw_triad(canvas, fr)
    draw_payoff(canvas, fr)
    src_a = mg.window(fr, 60, 30) * fade
    mg.text(canvas, "Source: Cricsheet ball-by-ball data", mg.W - mg.MARGIN,
            mg.H - 54, "Regular", 19, mg.INK_SOFT, align="right", alpha=src_a * 0.85)


def main():
    if "--stills" in sys.argv:
        out = os.path.join(HERE, "out", "ch2", "stills")
        mg.render_stills(draw, [250, 540, 700, 1050], out)
        print(f"[ch2] stills -> {out}")
        return
    print(f"[ch2] {N_FRAMES} frames ({N_FRAMES / mg.FPS:.1f}s)")
    mg.render(draw, N_FRAMES, FRAME_DIR)
    mg.encode(FRAME_DIR, VIDEO)


if __name__ == "__main__":
    main()
