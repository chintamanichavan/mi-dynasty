"""Intro scene: the dynasty title reveal.

Dark Wankhede-blue void, a gold '5' hero number, 'MUMBAI INDIANS' and
'DYNASTY' lock-up, slow camera push-in, glare bloom. ~4 s at 60 fps.

Run look-dev stills:  uv run scene_intro.py --stills
Run full clip:        uv run scene_intro.py
"""

import os
import sys
import math

import bpy

import mi_lib as L
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "data"))
import mi as DATA  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FRAME_DIR = os.path.join(HERE, "out", "intro", "frames")
VIDEO = os.path.join(HERE, "out", "intro", "intro.mp4")

DURATION_S = 4
F_START = 1
F_END = DURATION_S * L.FPS  # 240 frames


def build():
    L.fresh_scene()
    L.dramatic_world(strength=0.13)

    # Hero '5': reflective gold that also self-emits, so it reads + blooms.
    gold_hero = L.metal("gold_hero", L.GOLD, rough=0.14)
    gold_hero.node_tree.nodes["Principled BSDF"].inputs["Emission Color"].default_value = L.rgb(L.GOLD)
    gold_hero.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 1.6
    gold_glow = L.emission("gold_glow", L.GOLD, strength=3.0)
    white = L.matte("white", L.WHITE, rough=0.3)
    blue_glow = L.emission("blue_glow", L.BLUE, strength=4.0)

    # Reflective floor catches rim light and bloom.
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, -2.4))
    floor = bpy.context.active_object
    floor.data.materials.append(L.metal("floor", L.BLUE_DEEP, rough=0.4))

    # Hero '5' — sized + placed to sit fully in frame above the lock-up.
    five = L.text3d("5", location=(0, 0, 1.7), size=2.7, extrude=0.16,
                    bevel=0.045, material=gold_hero)
    L.pop_in(five, start=8, dur=16, overshoot=1.05)

    # Emissive blue accent bar that wipes in.
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.05, 0.25))
    bar = bpy.context.active_object
    bar.scale = (3.2, 0.035, 0.035)
    bar.data.materials.append(blue_glow)
    bar.scale = (0.001, 0.035, 0.035)
    bar.keyframe_insert("scale", frame=24)
    bar.scale = (3.2, 0.035, 0.035)
    bar.keyframe_insert("scale", frame=44)

    # 'TIME IPL CHAMPIONS' under the bar.
    sub = L.text3d("TIME IPL CHAMPIONS", location=(0, 0, -0.35), size=0.46,
                   extrude=0.03, material=gold_glow)
    L.pop_in(sub, start=40, dur=10)

    # 'MUMBAI INDIANS' headline at the base.
    name = L.text3d("MUMBAI INDIANS", location=(0, 0, -1.4), size=0.62,
                    extrude=0.05, material=white)
    L.pop_in(name, start=54, dur=12)

    L.hype_lights()
    # Front fill near camera so white/gold front faces aren't black.
    bpy.ops.object.light_add(type="AREA", location=(0, -9, 1.5))
    fill = bpy.context.active_object
    fill.data.energy = 900
    fill.data.size = 14
    fill.data.color = L.rgb(L.WHITE)[:3]

    cam, target = L.camera(location=(0, -16, 0.6), look_at=(0, 0, 0.2), lens=46)

    # Slow push-in across the clip.
    L.key_loc(cam, F_START, (0, -16, 0.6))
    L.key_loc(cam, F_END, (0, -13.6, 0.45))

    L.configure_render(F_START, F_END, samples=48)


def main():
    build()
    if "--stills" in sys.argv:
        stills_dir = os.path.join(HERE, "out", "intro", "stills")
        picks = [60, 120, 200]
        L.render_stills(stills_dir, picks)
        print(f"[intro] stills {picks} -> {stills_dir}")
        return
    print(f"[intro] {F_END - F_START + 1} frames @ {L.RES_X}x{L.RES_Y} {L.FPS}fps")
    L.render_frames(FRAME_DIR)
    L.encode(FRAME_DIR, VIDEO)


if __name__ == "__main__":
    main()
