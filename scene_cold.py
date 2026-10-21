"""Cold-open hook — the two 1-run finals, then the turn (editorial, fast).

No chapter chrome, no figures: pure kinetic typography + the ledger drama.
Teases the climax (smallest margin possible, twice) and the arc (flops ->
dynasty), then hands to the title. Faster holds than the chapter scenes.

All numbers Cricsheet-verified. Run:
  uv run scene_cold.py --stills   |   uv run scene_cold.py
"""

import os
import sys

import mg

HERE = os.path.dirname(os.path.abspath(__file__))
FRAME_DIR = os.path.join(HERE, "out", "cold", "frames")
VIDEO = os.path.join(HERE, "out", "cold", "cold.mp4")

CX = mg.W / 2
N_FRAMES = 930


def io(fr, start, dur, fade=16):
    """Fade-in / hold / fade-out alpha for a beat."""
    if fr < start or fr > start + dur:
        return 0.0
    return min(mg.window(fr, start, fade), 1 - mg.window(fr, start + dur - fade, fade))


def draw(canvas, fr):
    # --- Beat 1: the margin ---
    a = io(fr, 0, 205)
    if a > 0:
        mg.text(canvas, "TWO IPL FINALS · THE LAST BALL OF EACH", CX, 436,
                "SemiBold", 24, mg.INK_SOFT, align="center", alpha=a, tracking=5.0)
        pop = 1 + 0.04 * (1 - mg.window(fr, 30, 18))
        canvas.save(); canvas.translate(CX, 600); canvas.scale(pop, pop)
        mg.text(canvas, "1 RUN", 0, 0, "Bold", 184, mg.GOLD, align="center", alpha=a)
        canvas.restore()
        mg.text(canvas, "the smallest margin the game allows", CX, 690,
                "Regular", 30, mg.INK_SOFT, align="center", alpha=a)

    # --- Beat 2: twice — two heists ---
    a = io(fr, 220, 320)
    if a > 0:
        mg.text(canvas, "TWICE.", CX, 320, "Bold", 96, mg.INK, align="center", alpha=a)
        rows = [(2017, "needed 4 off the last ball", 250),
                (2019, "needed 2 off the last ball", 274)]
        for i, (yr, need, t0) in enumerate(rows):
            ra = io(fr, t0, 290 - (t0 - 220), 14)
            y = 460 + i * 110
            mg.text(canvas, str(yr), CX - 470, y, "Bold", 52, mg.INK,
                    align="left", alpha=ra)
            mg.text(canvas, need, CX - 330, y - 6, "Regular", 30, mg.INK_SOFT,
                    align="left", alpha=ra)
            mg.text(canvas, "WON BY 1 RUN", CX + 470, y, "SemiBold", 34, mg.GOLD,
                    align="right", alpha=ra * mg.window(fr, t0 + 24, 16), tracking=1.0)

    # --- Beat 3: the turn ---
    a = io(fr, 560, 200)
    if a > 0:
        mg.text(canvas, "Five years earlier —", CX, 486, "Regular", 36,
                mg.INK_SOFT, align="center", alpha=a)
        mg.text(canvas, "the most expensive flops in the sport.", CX, 566,
                "Bold", 56, mg.INK, align="center", alpha=a)
        mg.text(canvas, "$111.9M franchise  ·  zero titles in five years", CX, 628,
                "SemiBold", 26, mg.GOLD, align="center", alpha=a * mg.window(fr, 600, 20),
                tracking=1.0)

    # --- Beat 4: the hook ---
    a = io(fr, 770, 160)
    if a > 0:
        mg.text(canvas, "How did the billion-dollar underachievers", CX, 506,
                "Regular", 38, mg.INK_SOFT, align="center", alpha=a)
        mg.text(canvas, "become cricket's first dynasty?", CX, 580, "Bold", 60,
                mg.INK, align="center", alpha=a)
        uw = mg.lerp(0, 90, mg.window(fr, 800, 24))
        mg.line(canvas, CX - uw, 636, CX + uw, 636, mg.GOLD, 4, alpha=a)


def main():
    if "--stills" in sys.argv:
        out = os.path.join(HERE, "out", "cold", "stills")
        mg.render_stills(draw, [110, 360, 470, 650, 840], out)
        print(f"[cold] stills -> {out}")
        return
    print(f"[cold] {N_FRAMES} frames ({N_FRAMES / mg.FPS:.1f}s)")
    mg.render(draw, N_FRAMES, FRAME_DIR)
    mg.encode(FRAME_DIR, VIDEO)


if __name__ == "__main__":
    main()
