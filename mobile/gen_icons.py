"""One-off script: generates the Capacitor Android app icon set (adaptive
foreground + legacy square/round launcher icons) from a flame image
composited onto a black background. Not part of the app itself - run
manually, then delete or keep for future icon regeneration.

Source flame icon: Flaticon (free license, attribution required - see
README.md credits section).
"""
from PIL import Image
import os

BLACK = "#0a0a0d"  # matches the app's --bg color
SOURCE = os.path.join(os.path.dirname(__file__), "assets", "fire.png")
RES_DIR = os.path.join(os.path.dirname(__file__), "android", "app", "src", "main", "res")

SUPERSAMPLE = 4


def load_source():
    im = Image.open(SOURCE).convert("RGBA")
    return im.crop(im.getbbox())  # trim to actual flame content


def paste_centered(base, glyph, fraction):
    """Paste glyph onto base, scaled to `fraction` of base's width, centered."""
    target_w = int(base.width * fraction)
    scale = target_w / glyph.width
    target_h = int(glyph.height * scale)
    resized = glyph.resize((target_w, target_h), Image.LANCZOS)
    x = (base.width - target_w) // 2
    y = (base.height - target_h) // 2
    base.alpha_composite(resized, (x, y))
    return base


def rounded_square(size, radius_frac, color):
    from PIL import ImageDraw
    hi_res = size * SUPERSAMPLE
    img = Image.new("RGBA", (hi_res, hi_res), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([0, 0, hi_res - 1, hi_res - 1], radius=hi_res * radius_frac, fill=color)
    return img.resize((size, size), Image.LANCZOS)


def circle(size, color):
    from PIL import ImageDraw
    hi_res = size * SUPERSAMPLE
    img = Image.new("RGBA", (hi_res, hi_res), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([0, 0, hi_res - 1, hi_res - 1], fill=color)
    return img.resize((size, size), Image.LANCZOS)


DENSITIES = {
    "mdpi": (48, 108),
    "hdpi": (72, 162),
    "xhdpi": (96, 216),
    "xxhdpi": (144, 324),
    "xxxhdpi": (192, 432),
}

flame = load_source()

for density, (launcher_size, fg_size) in DENSITIES.items():
    d = os.path.join(RES_DIR, f"mipmap-{density}")

    # Adaptive foreground: transparent canvas, flame within the ~66% safe zone
    fg = Image.new("RGBA", (fg_size, fg_size), (0, 0, 0, 0))
    paste_centered(fg, flame, 0.5)
    fg.save(os.path.join(d, "ic_launcher_foreground.png"))

    # Legacy square launcher: black rounded square + flame
    bg = rounded_square(launcher_size, 0.22, BLACK)
    paste_centered(bg, flame, 0.62)
    bg.save(os.path.join(d, "ic_launcher.png"))

    # Legacy round launcher: black circle + flame
    bg_round = circle(launcher_size, BLACK)
    paste_centered(bg_round, flame, 0.62)
    bg_round.save(os.path.join(d, "ic_launcher_round.png"))

    print(f"{density}: wrote foreground {fg_size}px, launcher {launcher_size}px")

print("Done.")
