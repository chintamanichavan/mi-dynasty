"""Proof scene: MI's 5 titles as an editorial animated timeline.

Wendover/Polymatter idiom — warm paper, ink type, a single hairline axis that
draws on, title markers that rise and label themselves in sequence, the two
1-run finals emphasized in gold. Restrained motion, generous whitespace.

Run stills:  uv run scene_timeline.py --stills
Run clip:    uv run scene_timeline.py
"""

import os
import sys

import mg
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "data"))
import mi as DATA  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FRAME_DIR = os.path.join(HERE, "out", "timeline", "frames")
VIDEO = os.path.join(HERE, "out", "timeline", "timeline.mp4")

DURATION_S = 9
N_FRAMES = DURATION_S * mg.FPS  # 540

# Timeline geometry
AXIS_Y = 660
AXIS_X0 = mg.MARGIN + 60
AXIS_X1 = mg.W - mg.MARGIN - 60
YEAR_MIN, YEAR_MAX = 2012.4, 2020.6  # pad the ends so markers aren't on the edge


def year_x(year):
    t = (year - YEAR_MIN) / (YEAR_MAX - YEAR_MIN)
    return mg.lerp(AXIS_X0, AXIS_X1, t)


def draw(canvas, fr):
    # --- Header block ---
    kick_a = mg.window(fr, 6, 22)
    mg.text(canvas, "THE DYNASTY", mg.MARGIN, 210, "SemiBold", 26, mg.BLUE,
            alpha=kick_a, tracking=6.0)
    # accent tick before kicker
    mg.rect(canvas, mg.MARGIN - 0, 188, 46 * kick_a, 5, mg.GOLD)

    head_a = mg.window(fr, 16, 26)
    head_dy = mg.lerp(26, 0, head_a)
    mg.text(canvas, "Five titles in eight seasons", mg.MARGIN, 296 + head_dy,
            "Bold", 70, mg.INK, alpha=head_a)

    sub_a = mg.window(fr, 30, 24)
    mg.text(canvas, "Every Mumbai Indians IPL final, 2013–2020 · captained by Rohit Sharma",
            mg.MARGIN, 350, "Regular", 30, mg.INK_SOFT, alpha=sub_a)

    # --- Axis draws on left -> right ---
    axis_a = mg.window(fr, 54, 40, ease=mg.ease_out_quint)
    ax_x = mg.lerp(AXIS_X0, AXIS_X1, axis_a)
    mg.line(canvas, AXIS_X0, AXIS_Y, ax_x, AXIS_Y, mg.HAIRLINE, 3)

    # Faint full-span year endpoints once axis is mostly drawn
    end_a = mg.window(fr, 80, 20)
    mg.text(canvas, "2013", AXIS_X0, AXIS_Y + 52, "Medium", 22, mg.INK_SOFT,
            align="center", alpha=end_a * 0.0)  # endpoints implied by markers

    # --- Title markers rise + label, staggered ---
    start = 96
    stagger = 26
    for i, fin in enumerate(DATA.TITLES):
        a = mg.window(fr, start + i * stagger, 30, ease=mg.ease_out_quint)
        if a <= 0:
            continue
        x = year_x(fin.year)
        emphasize = fin.margin_runs == 1
        accent = mg.GOLD if emphasize else mg.BLUE

        # stem grows up from the axis
        stem_h = mg.lerp(0, 150 if emphasize else 120, a)
        mg.line(canvas, x, AXIS_Y, x, AXIS_Y - stem_h, accent, 3)
        # marker dot
        r = 9 if emphasize else 7
        mg.dot(canvas, x, AXIS_Y - stem_h, r, accent, alpha=a)
        if emphasize:
            mg.ring(canvas, x, AXIS_Y - stem_h, r + 7 * a, accent, 2, alpha=a * (1 - a) * 2)

        # year label above the dot
        mg.text(canvas, str(fin.year), x, AXIS_Y - stem_h - 26, "SemiBold", 30,
                mg.INK, align="center", alpha=a)
        # caption below the axis: opponent + margin
        cap_a = mg.window(fr, start + i * stagger + 10, 24)
        mg.text(canvas, f"def. {_short(fin.opponent)}", x, AXIS_Y + 44,
                "Medium", 23, mg.INK, align="center", alpha=cap_a)
        mg.text(canvas, f"by {fin.margin_text}", x, AXIS_Y + 74,
                "Regular", 22, accent if emphasize else mg.INK_SOFT,
                align="center", alpha=cap_a)

    # --- Emphasis callout for the two 1-run finals (clear band above labels) ---
    call_a = mg.window(fr, 300, 30)
    if call_a > 0:
        x17, x19 = year_x(2017), year_x(2019)
        mid_x = (x17 + x19) / 2
        # faint span connector linking the two gold finals
        mg.line(canvas, x17, 432, x19, 432, mg.GOLD, 2, alpha=call_a * 0.5)
        mg.line(canvas, x17, 432, x17, 446, mg.GOLD, 2, alpha=call_a * 0.5)
        mg.line(canvas, x19, 432, x19, 446, mg.GOLD, 2, alpha=call_a * 0.5)
        mg.text(canvas, "TWO FINALS WON BY ONE RUN", mid_x, 410, "SemiBold", 24,
                mg.GOLD, align="center", alpha=call_a, tracking=3.0)

    # --- Source credit (editorial signature) ---
    src_a = mg.window(fr, 120, 30)
    mg.text(canvas, "Source: Cricsheet ball-by-ball data", mg.MARGIN,
            mg.H - 70, "Regular", 20, mg.INK_SOFT, alpha=src_a * 0.85)
    # section number, top-right
    mg.text(canvas, "01", mg.W - mg.MARGIN, 210, "Bold", 28, mg.HAIRLINE,
            align="right", alpha=kick_a)


def _short(team):
    return {
        "Chennai Super Kings": "Chennai",
        "Rising Pune Supergiant": "Pune",
        "Delhi Capitals": "Delhi",
    }.get(team, team)


def main():
    if "--stills" in sys.argv:
        out = os.path.join(HERE, "out", "timeline", "stills")
        picks = [90, 220, 360, 520]
        mg.render_stills(draw, picks, out)
        print(f"[timeline] stills {picks} -> {out}")
        return
    print(f"[timeline] {N_FRAMES} frames @ {mg.W}x{mg.H} {mg.FPS}fps")
    mg.render(draw, N_FRAMES, FRAME_DIR)
    mg.encode(FRAME_DIR, VIDEO)


if __name__ == "__main__":
    main()
