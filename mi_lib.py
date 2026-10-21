"""Reusable bpy building blocks for the MI dynasty video — broadcast-hype look.

One module by design: small enough that splitting into a package would be
premature. Split when a second video needs it.

Target format: 1920x1080 @ 60 fps (sports-broadcast native), Cycles path-traced
on GPU (OptiX), motion blur + glare compositing for the hype feel.

All animation is a pure function of frame number (no RNG, no wall-clock), so
re-renders are byte-identical.
"""

import glob
import math
import os

import bpy
import imageio.v2 as imageio
import numpy as np
from PIL import Image, ImageFilter

# ----------------------------------------------------------------------------
# Format constants
# ----------------------------------------------------------------------------
RES_X, RES_Y = 1920, 1080
FPS = 60


# ----------------------------------------------------------------------------
# Color — MI brand, sRGB -> linear (Cycles wants linear; brand hexes are sRGB)
# ----------------------------------------------------------------------------
def _s2l(c: float) -> float:
    """Single-channel sRGB -> linear (IEC 61966-2-1)."""
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def rgb(hex_str: str, alpha: float = 1.0):
    """'#004BA0' -> linear RGBA tuple for material inputs."""
    h = hex_str.lstrip("#")
    srgb = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    return (_s2l(srgb[0]), _s2l(srgb[1]), _s2l(srgb[2]), alpha)


# MI palette
BLUE = "#004BA0"      # primary
BLUE_DEEP = "#001E42"  # background
GOLD = "#D1AB3E"      # accent / trophy
WHITE = "#F2F4F8"


# ----------------------------------------------------------------------------
# Scene lifecycle
# ----------------------------------------------------------------------------
def fresh_scene():
    """Empty scene; idempotent across re-runs. Sets smooth keyframe default."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.edit.keyframe_new_interpolation_type = "SINE"


def dramatic_world(top=BLUE_DEEP, strength=0.06):
    w = bpy.data.worlds.new("W")
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs[0].default_value = rgb(top)
    bg.inputs[1].default_value = strength
    bpy.context.scene.world = w


# ----------------------------------------------------------------------------
# Materials
# ----------------------------------------------------------------------------
def _principled(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    return m, m.node_tree.nodes["Principled BSDF"]


def metal(name, hex_color, rough=0.18):
    m, b = _principled(name)
    b.inputs["Base Color"].default_value = rgb(hex_color)
    b.inputs["Metallic"].default_value = 1.0
    b.inputs["Roughness"].default_value = rough
    return m


def matte(name, hex_color, rough=0.5):
    m, b = _principled(name)
    b.inputs["Base Color"].default_value = rgb(hex_color)
    b.inputs["Roughness"].default_value = rough
    return m


def emission(name, hex_color, strength=4.0):
    m, b = _principled(name)
    b.inputs["Base Color"].default_value = rgb(hex_color)
    b.inputs["Emission Color"].default_value = rgb(hex_color)
    b.inputs["Emission Strength"].default_value = strength
    return m


# ----------------------------------------------------------------------------
# 3D text
# ----------------------------------------------------------------------------
def text3d(body, location=(0, 0, 0), size=1.0, extrude=0.04, bevel=0.012,
           material=None, align="CENTER", rot_x_deg=90.0):
    """Extruded 3D text, standing up to face a -Y camera by default."""
    bpy.ops.object.text_add(location=location)
    obj = bpy.context.active_object
    obj.data.body = body
    obj.data.size = size
    obj.data.extrude = extrude
    obj.data.bevel_depth = bevel
    obj.data.align_x = align
    obj.data.align_y = "CENTER"
    obj.rotation_euler = (math.radians(rot_x_deg), 0, 0)
    if material:
        obj.data.materials.append(material)
    return obj


# Counting-number reveals (text body can't be keyframed) will be added with a
# frame_change handler when the stat scenes need them — not before.


# ----------------------------------------------------------------------------
# Animation helpers (keyframe pure functions of frame)
# ----------------------------------------------------------------------------
def key_scale(obj, frame, s):
    obj.scale = (s, s, s)
    obj.keyframe_insert("scale", frame=frame)


def key_loc(obj, frame, loc):
    obj.location = loc
    obj.keyframe_insert("location", frame=frame)


def pop_in(obj, start, dur=12, overshoot=1.06):
    """Scale 0 -> overshoot -> 1 for a punchy reveal."""
    key_scale(obj, start, 0.001)
    key_scale(obj, start + dur, overshoot)
    key_scale(obj, start + dur + 6, 1.0)


# ----------------------------------------------------------------------------
# Lighting & camera
# ----------------------------------------------------------------------------
def hype_lights():
    """Key + rim + cool fill for dramatic broadcast contrast."""
    specs = [
        ("KEY", (7, -8, 9), 1600, 7, WHITE),
        ("RIM", (-6, 5, 6), 900, 5, BLUE),
        ("FILL", (-8, -3, 3), 350, 9, BLUE),
        ("GOLD", (4, -2, 2), 500, 3, GOLD),
    ]
    for name, loc, energy, size, color in specs:
        bpy.ops.object.light_add(type="AREA", location=loc)
        lt = bpy.context.active_object
        lt.name = f"L_{name}"
        lt.data.energy = energy
        lt.data.size = size
        lt.data.color = rgb(color)[:3]


def camera(location=(0, -12, 2.5), look_at=(0, 0, 1.2), lens=50):
    bpy.ops.object.empty_add(location=look_at)
    target = bpy.context.active_object
    target.name = "cam_target"
    bpy.ops.object.camera_add(location=location)
    cam = bpy.context.active_object
    cam.data.lens = lens
    tr = cam.constraints.new("TRACK_TO")
    tr.target = target
    tr.track_axis = "TRACK_NEGATIVE_Z"
    tr.up_axis = "UP_Y"
    bpy.context.scene.camera = cam
    return cam, target


# ----------------------------------------------------------------------------
# Render config — hype quality
# ----------------------------------------------------------------------------
def configure_render(frame_start, frame_end, samples=48, motion_blur=True):
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.render.resolution_x = RES_X
    scene.render.resolution_y = RES_Y
    scene.render.fps = FPS
    scene.frame_start = frame_start
    scene.frame_end = frame_end
    scene.render.use_motion_blur = motion_blur
    scene.render.motion_blur_shutter = 0.5
    scene.render.film_transparent = False

    _enable_gpu(scene)
    scene.render.image_settings.file_format = "PNG"


def _enable_gpu(scene):
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.refresh_devices()
        gpus = [d for d in prefs.devices if d.type in {"OPTIX", "CUDA", "HIP"}]
        if gpus:
            prefs.compute_device_type = "OPTIX" if any(g.type == "OPTIX" for g in gpus) else gpus[0].type
            for d in prefs.devices:
                d.use = d.type != "CPU"
            scene.cycles.device = "GPU"
            print(f"[render] GPU: {gpus[0].name}")
            return
    except Exception as e:  # noqa: BLE001
        print(f"[render] GPU probe failed ({e})")
    scene.cycles.device = "CPU"
    print("[render] CPU")


# ----------------------------------------------------------------------------
# Bloom — multi-scale glow on bright pixels (the broadcast 'hype' shine).
# Deterministic numpy/PIL post-process; replaces Blender's churning compositor.
# ----------------------------------------------------------------------------
def add_bloom(arr, threshold=0.72, intensity=0.55, radii=(4, 12, 30)):
    """Screen-blend a blurred highlight pass back over the image. O(pixels)."""
    f = arr[..., :3].astype(np.float32) / 255.0
    hi = np.clip((f - threshold) / (1.0 - threshold), 0.0, 1.0)
    hi_img = Image.fromarray((hi * 255).astype(np.uint8))
    acc = np.zeros_like(f)
    for r in radii:
        acc += np.asarray(hi_img.filter(ImageFilter.GaussianBlur(r)), np.float32) / 255.0
    acc /= len(radii)
    out = 1.0 - (1.0 - f) * (1.0 - acc * intensity)  # screen blend
    return (np.clip(out, 0.0, 1.0) * 255).astype(np.uint8)


# ----------------------------------------------------------------------------
# Render + encode
# ----------------------------------------------------------------------------
def render_frames(frame_dir):
    os.makedirs(frame_dir, exist_ok=True)
    bpy.context.scene.render.filepath = os.path.join(frame_dir, "f")
    bpy.ops.render.render(animation=True)


def render_stills(frame_dir, frames, bloom=True):
    """Render only specific frames (fast look-dev), bloom applied."""
    os.makedirs(frame_dir, exist_ok=True)
    scene = bpy.context.scene
    for fr in frames:
        scene.frame_set(fr)
        raw = os.path.join(frame_dir, f"still_{fr:04d}.png")
        scene.render.filepath = raw[:-4]
        bpy.ops.render.render(write_still=True)
        if bloom:
            out = add_bloom(np.asarray(imageio.imread(raw)))
            imageio.imwrite(raw, out)


def encode(frame_dir, video_path, fps=FPS, bloom=True):
    frames = sorted(glob.glob(os.path.join(frame_dir, "f*.png")))
    if not frames:
        raise RuntimeError(f"no frames in {frame_dir}")
    w = imageio.get_writer(video_path, fps=fps, codec="libx264", quality=8,
                           macro_block_size=1, ffmpeg_log_level="error")
    for p in frames:
        img = np.asarray(imageio.imread(p))
        w.append_data(add_bloom(img) if bloom else img)
    w.close()
    print(f"[encode] {len(frames)} frames -> {video_path}")
