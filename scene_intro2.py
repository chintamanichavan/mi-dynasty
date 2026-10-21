"""Editorial intro / title card (Polymatter / Wendover idiom).

Warm paper, ink type, framing hairlines drawing from center, the headline
rising into a mask, and five title-markers populating a hairline — planting
the motif the timeline scene then pays off. Restrained, eased, breathing room
for voiceover.

Run stills:  uv run scene_intro2.py --stills
Run clip:    uv run scene_intro2.py
"""

import os
import sys

import skia

import mg
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "data"))
import mi as DATA  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FRAME_DIR = os.path.join(HERE, "out", "intro2", "frames")
VIDEO = os.path.join(HERE, "out", "intro2", "intro2.mp4")

DURATION_S = 6
N_FRAMES = DURATION_S * mg.FPS  # 360

CX = mg.W / 2
TITLE_Y = 560
TITLE_SIZE = 150


def text_rise(canvas, s, x, y, weight, size, c, prog, align="center"):
    """Headline rises into a fixed mask box — the classic editorial reveal."""
    f = mg.font(weight, size)
    cap = size * 0.78
    drift = cap * 1.15
    canvas.save()
    canvas.clipRect(skia.Rect.MakeLTRB(0, y - cap, mg.W, y + size * 0.22))
    mg.text(canvas, s, x, y + drift * (1 - prog), weight, size, c, align=align)
    canvas.restore()


def center_rule(canvas, y, half_w, prog, c=mg.HAIRLINE, width=3, alpha=1.0):
    w = half_w * mg.clamp01(prog)
    mg.line(canvas, CX - w, y, CX + w, y, c, width, alpha=alpha)


def draw(canvas, fr):
    # --- framing hairlines drawing out from center ---
    rule_a = mg.window(fr, 8, 34, ease=mg.ease_out_quint)
    center_rule(canvas, 372, 300, rule_a)
    center_rule(canvas, 702, 300, rule_a)

    # --- kicker ---
    kick_a = mg.window(fr, 22, 24)
    mg.text(canvas, "2013 — 2020", CX, 350, "SemiBold", 26, mg.BLUE,
            align="center", alpha=kick_a, tracking=8.0)

    # --- hero headline rises into mask ---
    head_p = mg.window(fr, 34, 52, ease=mg.ease_out_quint)
    if head_p > 0:
        text_rise(canvas, "MUMBAI INDIANS", CX, TITLE_Y, "Bold", TITLE_SIZE,
                  mg.INK, head_p)

    # --- subhead ---
    sub_a = mg.window(fr, 78, 26)
    sub_dy = mg.lerp(16, 0, sub_a)
    mg.text(canvas, "The IPL's defining dynasty", CX, 648 + sub_dy,
            "Regular", 38, mg.INK_SOFT, align="center", alpha=sub_a)

    # --- five title markers populate a hairline (motif) ---
    base_a = mg.window(fr, 120, 30, ease=mg.ease_out_quint)
    mk_y = 838
    span = 560
    x0 = CX - span / 2
    center_rule(canvas, mk_y, span / 2, base_a, c=mg.HAIRLINE, width=2)
    for i, fin in enumerate(DATA.TITLES):
        a = mg.window(fr, 132 + i * 14, 26, ease=mg.ease_out_quint)
        if a <= 0:
            continue
        x = x0 + span * (i / (len(DATA.TITLES) - 1))
        accent = mg.GOLD if fin.margin_runs == 1 else mg.BLUE
        mg.dot(canvas, x, mk_y, 11 * a, accent, alpha=a)
        mg.text(canvas, str(fin.year), x, mk_y + 44, "Medium", 21, mg.INK_SOFT,
                align="center", alpha=mg.window(fr, 140 + i * 14, 24))

    lbl_a = mg.window(fr, 210, 28)
    mg.text(canvas, "FIVE IPL TITLES", CX, 770, "SemiBold", 24, mg.INK,
            align="center", alpha=lbl_a, tracking=4.0)


def main():
    if "--stills" in sys.argv:
        out = os.path.join(HERE, "out", "intro2", "stills")
        mg.render_stills(draw, [70, 130, 230, 340], out)
        print(f"[intro2] stills -> {out}")
        return
    print(f"[intro2] {N_FRAMES} frames @ {mg.W}x{mg.H} {mg.FPS}fps")
    mg.render(draw, N_FRAMES, FRAME_DIR)
    mg.encode(FRAME_DIR, VIDEO)


if __name__ == "__main__":
    main()
