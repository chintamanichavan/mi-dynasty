"""Chapter 3 — the two 1-run finals (editorial idiom, heightened climax).

Each final's LAST OVER replays ball by ball: a hero equation ticks down
(NEED 11 OFF 6 ... NEED 4 OFF 1), six cells fill with the outcomes, wickets
flash brick-red, and the win lands in gold — the first gold the titles motif
has earned. Then the payoff: two finals, two runs, immortality.

Every ball is from the Cricsheet ledger (verified). Run:
  uv run scene_ch3.py --stills   |   uv run scene_ch3.py
"""

import os
import sys

import mg

HERE = os.path.dirname(os.path.abspath(__file__))
FRAME_DIR = os.path.join(HERE, "out", "ch3", "frames")
VIDEO = os.path.join(HERE, "out", "ch3", "ch3.mp4")

CX = mg.W / 2

# Last-over data: (need_before, balls_left, runs, is_wicket). Ledger-verified.
FINALS = [
    {
        "year": 2017, "bowler": "Mitchell Johnson", "chaser": "RISING PUNE",
        "context": "Mumbai 129 defended  ·  Pune chasing 130",
        "balls": [(11, 6, 4, False), (7, 5, 0, True), (7, 4, 0, True),
                  (7, 3, 1, False), (6, 2, 2, False), (4, 1, 2, True)],
        "result_sub": "Needed 4 off the last ball — Pune managed 2.",
    },
    {
        "year": 2019, "bowler": "Lasith Malinga", "chaser": "CHENNAI",
        "context": "Mumbai 149 defended  ·  Chennai chasing 150",
        "balls": [(9, 6, 1, False), (8, 5, 1, False), (7, 4, 2, False),
                  (5, 3, 1, True), (4, 2, 2, False), (2, 1, 0, True)],
        "result_sub": "Needed 2 off the last ball — Thakur lbw, Malinga.",
    },
]

# Panel timing (local frames)
BALLS_START = 78
BALL_GAP = 46
RESULT_AT = BALLS_START + 6 * BALL_GAP      # 354
PANEL_DUR = RESULT_AT + 170                 # ~524

# Scene layout (frames)
P0_START = 96
P1_START = P0_START + PANEL_DUR + 40
PAYOFF_START = P1_START + PANEL_DUR + 30
N_FRAMES = PAYOFF_START + 320


def panel_alpha(lf, dur):
    if lf < 0 or lf > dur:
        return 0.0
    return min(mg.window(lf, 0, 20), mg.window(dur - lf, 0, 20))


def text_scaled(canvas, s, x, y, weight, size, c, scale, align="center", alpha=1.0):
    canvas.save()
    canvas.translate(x, y)
    canvas.scale(scale, scale)
    mg.text(canvas, s, 0, 0, weight, size, c, align=align, alpha=alpha)
    canvas.restore()


def draw_panel(canvas, fr, start, F):
    lf = fr - start
    a = panel_alpha(lf, PANEL_DUR)
    if a <= 0:
        return

    # context + bowler
    ctx_a = mg.window(lf, 6, 22) * a
    mg.text(canvas, f"{F['year']} FINAL", CX, 332, "Bold", 40, mg.INK,
            align="center", alpha=ctx_a)
    mg.text(canvas, F["context"], CX, 378, "Regular", 26, mg.INK_SOFT,
            align="center", alpha=ctx_a)
    bowl_a = mg.window(lf, 24, 20) * a
    mg.text(canvas, f"FINAL OVER  ·  {F['bowler'].upper()}", CX, 432, "SemiBold",
            22, mg.BLUE, align="center", alpha=bowl_a, tracking=4.0)

    nb = max(0, min(6, int((lf - BALLS_START) / BALL_GAP) + 1)) if lf >= BALLS_START else 0
    in_result = lf >= RESULT_AT

    # hero equation (ticks down) or result
    if not in_result:
        idx = min(nb, 5)
        need, off, _, _ = F["balls"][idx]
        t_in = (lf - BALLS_START) % BALL_GAP if lf >= BALLS_START else 0
        punch = 1.0 + 0.09 * max(0.0, 1 - t_in / 9.0) if lf >= BALLS_START else 1.0
        eq_a = mg.window(lf, 40, 20) * a
        mg.text(canvas, f"{F['chaser']} NEED", CX, 528, "SemiBold", 24,
                mg.INK_SOFT, align="center", alpha=eq_a, tracking=5.0)
        dramatic = off == 1
        text_scaled(canvas, str(need), CX, 622, "Bold", 104,
                    mg.DANGER if dramatic else mg.INK, punch, alpha=eq_a)
        mg.text(canvas, f"OFF {off} BALL{'' if off == 1 else 'S'}", CX, 676,
                "Medium", 28, mg.INK_SOFT, align="center", alpha=eq_a)
    else:
        ra = mg.window(lf, RESULT_AT, 26) * a
        text_scaled(canvas, "WON BY 1 RUN", CX, 600, "Bold", 76, mg.GOLD,
                    1.0 + 0.05 * mg.window(lf, RESULT_AT, 14), align="center", alpha=ra)
        uw = mg.lerp(0, 250, mg.window(lf, RESULT_AT + 6, 24))
        mg.line(canvas, CX - uw, 632, CX + uw, 632, mg.GOLD, 3, alpha=ra)
        mg.text(canvas, F["result_sub"], CX, 690, "Regular", 26, mg.INK_SOFT,
                align="center", alpha=ra)

    # six ball cells fill left -> right
    cw, gap = 80, 22
    total = 6 * cw + 5 * gap
    x0 = CX - total / 2
    for i, (_, _, runs, wk) in enumerate(F["balls"]):
        cx = x0 + i * (cw + gap)
        reveal_t = BALLS_START + i * BALL_GAP
        ca = mg.window(lf, reveal_t, 14) * a
        # empty slot outline always visible while panel up
        mg.rect(canvas, cx, 760, cw, cw, mg.HAIRLINE, alpha=a * 0.5, radius=12)
        if ca <= 0:
            continue
        face = mg.DANGER if wk else mg.BLUE
        mg.rect(canvas, cx, 760, cw, cw, face, alpha=ca, radius=12)
        label = "W" if (wk and runs == 0) else str(runs)
        mg.text(canvas, label, cx + cw / 2, 760 + cw / 2 + 18, "Bold", 46,
                mg.PAPER, align="center", alpha=ca)


def draw_payoff(canvas, fr):
    lf = fr - PAYOFF_START
    if lf < 0:
        return
    a = mg.window(lf, 0, 26)
    mg.text(canvas, "TWO FINALS · TWO RUNS", CX, 430, "Bold", 78, mg.INK,
            align="center", alpha=a)
    sub_a = mg.window(lf, 18, 24)
    mg.text(canvas, "Two runs separating misery from immortality.", CX, 500,
            "Regular", 32, mg.INK_SOFT, align="center", alpha=sub_a)
    # two gold finals
    for i, yr in enumerate((2017, 2019)):
        da = mg.window(lf, 40 + i * 16, 22)
        x = CX + (-1 if i == 0 else 1) * 220
        mg.dot(canvas, x, 640, 12 * da, mg.GOLD, alpha=da)
        mg.text(canvas, str(yr), x, 712, "SemiBold", 34, mg.INK, align="center", alpha=da)
        mg.text(canvas, "won by 1 run", x, 752, "Regular", 24, mg.GOLD,
                align="center", alpha=da)


def draw(canvas, fr):
    # persistent chapter header
    kick_a = mg.window(fr, 8, 22)
    fade = 1.0 - mg.window(fr, PAYOFF_START - 30, 30)  # recede during payoff
    ha = kick_a * fade
    mg.rect(canvas, mg.MARGIN, 122, 46 * kick_a, 5, mg.GOLD, alpha=fade)
    mg.text(canvas, "CHAPTER THREE", mg.MARGIN, 144, "SemiBold", 22, mg.BLUE,
            alpha=ha, tracking=6.0)
    mg.text(canvas, "Dynasties win when defeat looks certain", mg.MARGIN, 196,
            "Bold", 40, mg.INK, alpha=ha)
    mg.text(canvas, "03", mg.W - mg.MARGIN, 150, "Bold", 28, mg.HAIRLINE,
            align="right", alpha=ha)

    draw_panel(canvas, fr, P0_START, FINALS[0])
    draw_panel(canvas, fr, P1_START, FINALS[1])
    draw_payoff(canvas, fr)

    src_a = mg.window(fr, 60, 30) * fade
    mg.text(canvas, "Source: Cricsheet ball-by-ball data", mg.W - mg.MARGIN,
            mg.H - 54, "Regular", 19, mg.INK_SOFT, align="right", alpha=src_a * 0.85)


def main():
    if "--stills" in sys.argv:
        out = os.path.join(HERE, "out", "ch3", "stills")
        mg.render_stills(draw, [P0_START + 300, P0_START + RESULT_AT + 60,
                                P1_START + 300, P1_START + RESULT_AT + 60,
                                PAYOFF_START + 140], out)
        print(f"[ch3] stills -> {out}")
        return
    print(f"[ch3] {N_FRAMES} frames ({N_FRAMES / mg.FPS:.1f}s)")
    mg.render(draw, N_FRAMES, FRAME_DIR)
    mg.encode(FRAME_DIR, VIDEO)


if __name__ == "__main__":
    main()
