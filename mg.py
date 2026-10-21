"""2D editorial motion-graphics toolkit (Polymatter / Wendover idiom).

Pure-Python: skia-python for pro-grade vector rendering, imageio-ffmpeg for
the encode. No 3D, no bloom, no system deps. The aesthetic is restrained
editorial: warm paper canvas, ink type, one disciplined typeface, muted
accents, generous whitespace, eased motion in service of information.

All animation is a pure function of frame index -> byte-identical re-renders.
"""

import glob
import os

import imageio.v2 as imageio
import numpy as np
import skia

# ----------------------------------------------------------------------------
# Format
# ----------------------------------------------------------------------------
W, H = 1920, 1080
FPS = 60
MARGIN = 130          # editorial left/right margin
FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "fonts")

# ----------------------------------------------------------------------------
# Palette — editorial, MI-derived but desaturated. sRGB hex.
# ----------------------------------------------------------------------------
PAPER = "#F4F1E9"     # warm off-white canvas
INK = "#16181D"       # near-black body
INK_SOFT = "#6B6F78"  # secondary / captions
BLUE = "#0A4DA2"      # MI blue, muted — primary accent
GOLD = "#BE9A34"      # muted editorial gold — used sparingly for emphasis
DANGER = "#B23A2E"    # muted brick red — wickets / jeopardy, used sparingly
HAIRLINE = "#D8D3C6"  # light rules / axes


def color(hex_str, alpha=1.0):
    h = hex_str.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return skia.Color4f(r / 255, g / 255, b / 255, alpha)


# ----------------------------------------------------------------------------
# Fonts
# ----------------------------------------------------------------------------
_TYPEFACES = {
    w: skia.Typeface.MakeFromFile(os.path.join(FONT_DIR, f"IBMPlexSans-{w}.ttf"))
    for w in ("Regular", "Medium", "SemiBold", "Bold")
}


def font(weight, size):
    f = skia.Font(_TYPEFACES[weight], size)
    f.setSubpixel(True)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    return f


# ----------------------------------------------------------------------------
# Easing & interpolation (pure functions of normalized time)
# ----------------------------------------------------------------------------
def clamp01(x):
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def ease_out_cubic(t):
    t = clamp01(t)
    return 1 - (1 - t) ** 3


def ease_out_quint(t):
    t = clamp01(t)
    return 1 - (1 - t) ** 5


def ease_in_out(t):
    t = clamp01(t)
    return 3 * t * t - 2 * t * t * t


def lerp(a, b, t):
    return a + (b - a) * t


def window(frame, start, dur, ease=ease_out_cubic):
    """Normalized eased progress of an animation starting at `start`."""
    return ease((frame - start) / dur) if dur > 0 else (1.0 if frame >= start else 0.0)


# ----------------------------------------------------------------------------
# Drawing helpers
# ----------------------------------------------------------------------------
def _fill(c):
    p = skia.Paint(AntiAlias=True)
    p.setColor4f(c)
    return p


def _stroke(c, width, cap=skia.Paint.Cap.kButt_Cap):
    p = skia.Paint(AntiAlias=True, Style=skia.Paint.Style.kStroke_Style)
    p.setColor4f(c)
    p.setStrokeWidth(width)
    p.setStrokeCap(cap)
    return p


def clear(canvas, c=PAPER):
    canvas.clear(color(c))


def text(canvas, s, x, y, weight, size, c, align="left", alpha=1.0, tracking=0.0):
    """Baseline-positioned text. align in {left,center,right}. tracking in px."""
    f = font(weight, size)
    col = c if isinstance(c, skia.Color4f) else color(c, alpha)
    paint = _fill(col)
    if tracking == 0.0:
        w_text = f.measureText(s)
        ox = {"left": 0, "center": -w_text / 2, "right": -w_text}[align]
        canvas.drawString(s, x + ox, y, f, paint)
        return w_text
    # Tracked (letter-spaced) — draw glyph by glyph.
    widths = [f.measureText(ch) + tracking for ch in s]
    total = sum(widths) - tracking
    ox = {"left": 0, "center": -total / 2, "right": -total}[align]
    cx = x + ox
    for ch, wch in zip(s, widths):
        canvas.drawString(ch, cx, y, f, paint)
        cx += wch
    return total


def measure(s, weight, size, tracking=0.0):
    f = font(weight, size)
    if tracking == 0.0:
        return f.measureText(s)
    return sum(f.measureText(ch) + tracking for ch in s) - tracking


def line(canvas, x0, y0, x1, y1, c, width, alpha=1.0, cap="butt"):
    cm = {"butt": skia.Paint.Cap.kButt_Cap, "round": skia.Paint.Cap.kRound_Cap}[cap]
    col = color(c, alpha) if not isinstance(c, skia.Color4f) else c
    canvas.drawLine(x0, y0, x1, y1, _stroke(col, width, cm))


def rect(canvas, x, y, w, h, c, alpha=1.0, radius=0.0):
    col = color(c, alpha) if not isinstance(c, skia.Color4f) else c
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), radius, radius)
    canvas.drawRRect(r, _fill(col))


def dot(canvas, x, y, r, c, alpha=1.0):
    col = color(c, alpha) if not isinstance(c, skia.Color4f) else c
    canvas.drawCircle(x, y, r, _fill(col))


def ring(canvas, x, y, r, c, width, alpha=1.0):
    col = color(c, alpha) if not isinstance(c, skia.Color4f) else c
    canvas.drawCircle(x, y, r, _stroke(col, width))


# ----------------------------------------------------------------------------
# Render loop + encode
# ----------------------------------------------------------------------------
def render(scene_fn, n_frames, frame_dir, write_pngs=True):
    """Call scene_fn(canvas, frame) for each frame; snapshot to PNG."""
    os.makedirs(frame_dir, exist_ok=True)
    surface = skia.Surface(W, H)
    for fr in range(n_frames):
        with surface as canvas:
            clear(canvas)
            scene_fn(canvas, fr)
        if write_pngs:
            img = surface.makeImageSnapshot()
            img.save(os.path.join(frame_dir, f"f{fr:05d}.png"))
    return surface


def render_stills(scene_fn, frames, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    surface = skia.Surface(W, H)
    for fr in frames:
        with surface as canvas:
            clear(canvas)
            scene_fn(canvas, fr)
        surface.makeImageSnapshot().save(os.path.join(out_dir, f"still_{fr:05d}.png"))


def encode(frame_dir, video_path, fps=FPS):
    frames = sorted(glob.glob(os.path.join(frame_dir, "f*.png")))
    if not frames:
        raise RuntimeError(f"no frames in {frame_dir}")
    w = imageio.get_writer(video_path, fps=fps, codec="libx264", quality=9,
                           macro_block_size=1, ffmpeg_log_level="error")
    for p in frames:
        w.append_data(np.asarray(imageio.imread(p))[..., :3])
    w.close()
    print(f"[encode] {len(frames)} frames -> {video_path}")
