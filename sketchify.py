"""Photo -> editorial portrait sketch (pure Python: PIL + numpy).

Pipeline: portrait crop -> grayscale/autocontrast -> color-dodge pencil sketch
combined with edge lines -> duotone into the editorial palette (ink on paper)
-> radial vignette so the face reads and the background fades to paper.

Only meant for FREELY-LICENSED source photos (CC / public domain), used as
stylized derivative art with attribution.

  uv run sketchify.py <input.jpg> <output.png> [--blue]
"""

import sys

import numpy as np
from PIL import Image, ImageFilter, ImageOps

PAPER = (244, 241, 233)
INK = (22, 24, 29)
BLUE = (10, 77, 162)


def _smoothstep(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def _portrait_crop(img, ratio=4 / 5, top_bias=0.42):
    w, h = img.size
    tw, th = w, int(w / ratio)
    if th > h:
        th, tw = h, int(h * ratio)
    x = (w - tw) // 2
    y = int((h - th) * top_bias)
    return img.crop((x, y, x + tw, y + th))


def _vignette(shape, cx=0.5, cy=0.44, rx=0.46, ry=0.54):
    h, w = shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = ((xx / w - cx) / rx) ** 2 + ((yy / h - cy) / ry) ** 2
    return _smoothstep(1.35 - d)


def pencil(gray, sigma=8.0):
    inv = ImageOps.invert(gray).filter(ImageFilter.GaussianBlur(sigma))
    g = np.asarray(gray, np.float32)
    b = np.asarray(inv, np.float32)
    return np.clip(g * 255.0 / (255.0 - b + 1.0), 0, 255) / 255.0


def sketchify(in_path, out_path, line=INK, size=760, gamma=1.45):
    img = _portrait_crop(Image.open(in_path).convert("RGB"))
    img.thumbnail((size, size * 2))
    gray = ImageOps.autocontrast(img.convert("L"), cutoff=1)
    sketch = pencil(gray)                                   # 1=paper, 0=line
    edges = np.asarray(gray.filter(ImageFilter.FIND_EDGES), np.float32) / 255.0
    dark = np.clip((1.0 - sketch) ** gamma + edges * 0.35, 0, 1)
    dark *= _vignette(dark.shape)                           # fade background
    rgb = (np.array(PAPER, np.float32) * (1 - dark[..., None])
           + np.array(line, np.float32) * dark[..., None])
    Image.fromarray(rgb.astype(np.uint8)).save(out_path)
    print(f"[sketch] {out_path}  {Image.open(out_path).size}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    sketchify(args[0], args[1], line=BLUE if "--blue" in sys.argv else INK)
