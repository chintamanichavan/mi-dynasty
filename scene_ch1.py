"""Chapter 1 — "The billion-dollar underachievers" (editorial idiom).

The centerpiece: MI's 2008-2012 final standings as a line that spikes toward
the top in 2010 but never reaches the dashed CHAMPIONS line. The story told
by a chart, Wendover-style. All standings verified (Wikipedia season table);
2010 final margin from Cricsheet.

Run stills:  uv run scene_ch1.py --stills
Run clip:    uv run scene_ch1.py
"""

import os
import sys

import skia

import mg

HERE = os.path.dirname(os.path.abspath(__file__))
FRAME_DIR = os.path.join(HERE, "out", "ch1", "frames")
VIDEO = os.path.join(HERE, "out", "ch1", "ch1.mp4")

DURATION_S = 11
N_FRAMES = DURATION_S * mg.FPS

# (season, final standing) — verified.
STANDINGS = [(2008, 5), (2009, 7), (2010, 2), (2011, 3), (2012, 4)]
NOTES = {2009: "7th — their worst", 2010: "Runner-up", 2012: "Playoff exit"}

# Plot geometry
PX0, PX1 = 360, mg.W - 280
PY_TOP, PY_BOT = 500, 858     # standing 1 (best) at top, 8 (worst) at bottom
STD_TOP, STD_BOT = 1, 8


def xyear(y):
    return mg.lerp(PX0, PX1, (y - 2008) / (2012 - 2008))


def ystd(s):
    return mg.lerp(PY_TOP, PY_BOT, (s - STD_TOP) / (STD_BOT - STD_TOP))


def dashed_line(canvas, x0, y0, x1, y1, c, width, alpha=1.0):
    p = skia.Paint(AntiAlias=True, Style=skia.Paint.Style.kStroke_Style)
    p.setColor4f(mg.color(c, alpha))
    p.setStrokeWidth(width)
    p.setPathEffect(skia.DashPathEffect.Make([14.0, 10.0], 0.0))
    canvas.drawLine(x0, y0, x1, y1, p)


def polyline_reveal(canvas, pts, reveal_x, c, width):
    """Draw a polyline left-to-right, clipped at reveal_x (pts sorted by x)."""
    paint = skia.Paint(AntiAlias=True, Style=skia.Paint.Style.kStroke_Style)
    paint.setColor4f(mg.color(c))
    paint.setStrokeWidth(width)
    paint.setStrokeJoin(skia.Paint.Join.kRound_Join)
    paint.setStrokeCap(skia.Paint.Cap.kRound_Cap)
    path = skia.Path()
    started = False
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if reveal_x <= x0:
            break
        if not started:
            path.moveTo(x0, y0)
            started = True
        if reveal_x >= x1:
            path.lineTo(x1, y1)
        else:  # straddle: interpolate y at reveal_x
            t = (reveal_x - x0) / (x1 - x0)
            path.lineTo(reveal_x, mg.lerp(y0, y1, t))
            break
    if started:
        canvas.drawPath(path, paint)


def draw(canvas, fr):
    # --- header ---
    kick_a = mg.window(fr, 6, 22)
    mg.rect(canvas, mg.MARGIN, 150, 46 * kick_a, 5, mg.GOLD)
    mg.text(canvas, "CHAPTER ONE", mg.MARGIN, 172, "SemiBold", 24, mg.BLUE,
            alpha=kick_a, tracking=6.0)
    head_a = mg.window(fr, 16, 26)
    mg.text(canvas, "The billion-dollar underachievers", mg.MARGIN,
            246 + mg.lerp(22, 0, head_a), "Bold", 62, mg.INK, alpha=head_a)
    sub_a = mg.window(fr, 30, 24)
    mg.text(canvas, "Most expensive franchise of 2008 ($111.9M) · five seasons, zero titles",
            mg.MARGIN, 300, "Regular", 28, mg.INK_SOFT, alpha=sub_a)
    mg.text(canvas, "01", mg.W - mg.MARGIN, 172, "Bold", 28, mg.HAIRLINE,
            align="right", alpha=kick_a)

    # --- y-axis reference lines + labels ---
    axis_a = mg.window(fr, 50, 26)
    for s, lab in [(1, "1st"), (4, "4th"), (8, "8th")]:
        y = ystd(s)
        mg.line(canvas, PX0, y, PX1, y, mg.HAIRLINE, 1.5, alpha=axis_a * 0.6)
        mg.text(canvas, lab, PX0 - 24, y + 8, "Medium", 20, mg.INK_SOFT,
                align="right", alpha=axis_a * 0.8)

    # --- the CHAMPIONS line MI never reaches (dashed, at the very top) ---
    champ_a = mg.window(fr, 60, 28)
    cy = ystd(1) - 26
    dashed_line(canvas, PX0, cy, PX1, cy, mg.GOLD, 2, alpha=champ_a)
    mg.text(canvas, "CHAMPIONS", PX1, cy - 16, "SemiBold", 20, mg.GOLD,
            align="right", alpha=champ_a, tracking=3.0)

    # --- x-axis year labels ---
    xlab_a = mg.window(fr, 70, 24)
    for yr, _ in STANDINGS:
        mg.text(canvas, str(yr), xyear(yr), PY_BOT + 50, "Medium", 24,
                mg.INK, align="center", alpha=xlab_a)

    # --- MI standings line draws on left -> right ---
    pts = [(xyear(y), ystd(s)) for y, s in STANDINGS]
    draw_p = mg.window(fr, 96, 80, ease=mg.ease_in_out)
    reveal_x = mg.lerp(PX0, PX1, draw_p)
    polyline_reveal(canvas, pts, reveal_x, mg.BLUE, 4)

    # markers + notes pop as the reveal passes each year
    for i, (yr, s) in enumerate(STANDINGS):
        x, y = xyear(yr), ystd(s)
        if reveal_x < x - 2:
            continue
        a = mg.window(fr, 96 + int(80 * (i / (len(STANDINGS) - 1))) - 6, 18)
        emphasize = yr == 2010
        # Gold is reserved for the unreached CHAMPIONS line — Ch1 has zero titles.
        mg.dot(canvas, x, y, (9 if emphasize else 7) * mg.clamp01(a), mg.BLUE, alpha=a)
        if yr in NOTES:
            above = yr == 2010
            ny = y - 30 if above else y + 40
            mg.text(canvas, NOTES[yr], x, ny, "Medium", 22,
                    mg.INK if emphasize else mg.INK_SOFT, align="center", alpha=a)

    # --- punch callout ---
    punch_a = mg.window(fr, 380, 34)
    if punch_a > 0:
        mg.text(canvas, "Reached one final. Lost it.", mg.MARGIN, 968,
                "SemiBold", 34, mg.INK, alpha=punch_a)
        mg.text(canvas, "A collection of expensive parts — not a machine.",
                mg.MARGIN, 1008, "Regular", 26, mg.INK_SOFT, alpha=punch_a)

    src_a = mg.window(fr, 120, 30)
    mg.text(canvas, "Source: Cricsheet · IPL season tables", mg.W - mg.MARGIN,
            mg.H - 54, "Regular", 19, mg.INK_SOFT, align="right", alpha=src_a * 0.85)


def main():
    if "--stills" in sys.argv:
        out = os.path.join(HERE, "out", "ch1", "stills")
        mg.render_stills(draw, [80, 200, 340, 460, 620], out)
        print(f"[ch1] stills -> {out}")
        return
    print(f"[ch1] {N_FRAMES} frames")
    mg.render(draw, N_FRAMES, FRAME_DIR)
    mg.encode(FRAME_DIR, VIDEO)


if __name__ == "__main__":
    main()
