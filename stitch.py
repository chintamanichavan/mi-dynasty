"""Stitch all scenes into one master film with cross-dissolves.

Narrative order: intro -> Ch1 (underachievers) -> Ch2 (the pivot) ->
Ch3 (the 1-run finals) -> timeline (closing recap). Consecutive scenes
overlap by FADE frames, linearly cross-dissolved (all share the paper
background, so transitions are seamless). Output: out/film/mi_dynasty.mp4.

  uv run stitch.py
"""

import glob
import os

import imageio.v2 as imageio
import numpy as np

import mg

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "film", "mi_dynasty.mp4")

SCENES = ["intro2", "ch1", "ch2", "ch3", "timeline"]
FADE = 30  # cross-dissolve length in frames (0.5s @ 60fps)


def frames_for(scene):
    fs = sorted(glob.glob(os.path.join(HERE, "out", scene, "frames", "f*.png")))
    if len(fs) <= FADE:
        raise RuntimeError(f"{scene}: too few frames ({len(fs)})")
    return fs


def rgb(path):
    return np.asarray(imageio.imread(path))[..., :3]


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    writer = imageio.get_writer(OUT, fps=mg.FPS, codec="libx264", quality=9,
                                macro_block_size=1, ffmpeg_log_level="error")
    written = 0
    prev_tail = None  # last FADE frame paths of the previous scene

    for si, scene in enumerate(SCENES):
        frames = frames_for(scene)
        is_last = si == len(SCENES) - 1

        start = 0
        if prev_tail is not None:
            # cross-dissolve prev scene's tail into this scene's head
            for k in range(FADE):
                a = rgb(prev_tail[k]).astype(np.float32)
                b = rgb(frames[k]).astype(np.float32)
                t = (k + 1) / (FADE + 1)
                writer.append_data((a * (1 - t) + b * t).astype(np.uint8))
                written += 1
            start = FADE

        end = len(frames) - (0 if is_last else FADE)
        for k in range(start, end):
            writer.append_data(rgb(frames[k]))
            written += 1

        prev_tail = None if is_last else frames[end:]
        print(f"  + {scene}: through frame {end}/{len(frames)} (total {written})")

    writer.close()
    print(f"[film] {written} frames -> {OUT}  ({written / mg.FPS:.1f}s)")


if __name__ == "__main__":
    main()
