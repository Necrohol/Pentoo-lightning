#!/usr/bin/env python3
"""
Pentoo Plymouth Boot Animation - Lightning Bolt Compositor
Replaces the static bolt bar with a dynamic growing jagged bolt that IS the progress bar.

Layout from analysis:
  - Progress bar (blue glow): rows 920-937, x=96 to growing right, max x ~1820
  - Bolt bar (wide static): rows 907-919, same x range  
  - Track bar (static full width): rows 938-982, x=310-1610
  - Bar track start x: ~96, end x: ~1820, total width: ~1724
  - Total frames: 120
"""

import os
import sys
import random
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

# ── Layout constants ─────────────────────────────────────────────────────────
# Track bar (wide dark rectangle): rows 920-941, x=92-1827
TRACK_X0      = 92
TRACK_X1      = 1827
TRACK_WIDTH   = TRACK_X1 - TRACK_X0

TRACK_Y0      = 920
TRACK_Y1      = 941
TRACK_CY      = 930

# Clear zone — few rows above for bolt glow bleed room
CLEAR_Y0      = 905
CLEAR_Y1      = 941

# Grow bar fills the track exactly
PROG_Y0       = 920
PROG_Y1       = 941
PROG_CY       = 930

# Bolt centered on same line
BOLT_CY       = 930

TOTAL_FRAMES  = 120
IN_DIR        = "/usr/share/plymouth/themes/pentoo/allframes"
OUT_DIR       = "/usr/share/plymouth/themes/pentoo/outframes"

# ── Color palette ────────────────────────────────────────────────────────────
# Progress bar: deep electric blue → bright cyan at tip
PROG_CORE     = (80,  180, 255)   # bright blue core
PROG_TIP      = (200, 240, 255)   # near-white tip bloom
PROG_GLOW     = (20,  60,  140)   # outer glow (darker blue)

# Bolt: purple/violet → white core, Pentoo aesthetic
BOLT_CORE     = (255, 255, 255)   # white hot core
BOLT_MID      = (180, 120, 255)   # purple mid
BOLT_OUTER    = (80,   30, 160)   # dark purple outer glow
BOLT_BRANCH   = (200, 160, 255)   # branch bolt color

random.seed(42)  # reproducible base — per-frame noise added via frame index

def lerp(a, b, t):
    return a + (b - a) * t

def progress_for_frame(frame_idx):
    """Smooth eased progress 0.0→1.0 over 120 frames."""
    t = frame_idx / (TOTAL_FRAMES - 1)
    # ease-in-out cubic
    if t < 0.5:
        return 4 * t * t * t
    else:
        p = -2 * t + 2
        return 1 - (p * p * p) / 2

def tip_x(progress):
    return int(TRACK_X0 + progress * TRACK_WIDTH)

def make_jagged_bolt(rng, x0, x1, cy, amplitude, segments):
    """Generate a jagged lightning path from x0 to x1 at centerline cy."""
    points = [(x0, cy)]
    seg_w = (x1 - x0) / segments
    for i in range(1, segments):
        xi = x0 + i * seg_w
        # Reduce amplitude near the tip for a sharper leading edge
        fade = 1.0 - (i / segments) ** 2
        yi = cy + rng.uniform(-amplitude * fade, amplitude * fade)
        points.append((xi, yi))
    points.append((x1, cy))
    return points

def draw_bolt_layer(draw, rng, x0, x1, cy, amplitude, width, color, alpha_layer, segments=18):
    """Draw one layer of a multi-pass bolt."""
    points = make_jagged_bolt(rng, x0, x1, cy, amplitude, segments)
    # Draw as polyline
    for i in range(len(points) - 1):
        p1 = (int(points[i][0]), int(points[i][1]))
        p2 = (int(points[i+1][0]), int(points[i+1][1]))
        draw.line([p1, p2], fill=color + (alpha_layer,), width=width)

def draw_branches(draw, rng, x0, x1, cy, n_branches=4):
    """Shoot small branch bolts from random points along the main bolt."""
    for _ in range(n_branches):
        bx = rng.randint(x0, max(x0+1, x1))
        by = cy + rng.randint(-4, 4)
        length  = rng.randint(15, 45)
        angle   = rng.uniform(-60, 60)  # degrees from horizontal
        ex = int(bx + length * math.cos(math.radians(angle)))
        ey = int(by + length * math.sin(math.radians(angle)))
        alpha = rng.randint(80, 180)
        draw.line([(bx, by), (ex, ey)], fill=BOLT_BRANCH + (alpha,), width=1)

def render_frame(frame_idx, in_path, out_path):
    rng = random.Random(frame_idx * 7919 + 13)   # deterministic per-frame RNG

    img = Image.open(in_path).convert("RGBA")
    W, H = img.size

    progress = progress_for_frame(frame_idx)
    tx = tip_x(progress)

    # ── Clear entire bolt+track zone ─────────────────────────────────────────
    base = img.copy()
    base_arr = np.array(base)

    # Wipe from bolt top through track bar bottom — dark purple-black bg
    base_arr[CLEAR_Y0:CLEAR_Y1+1, max(0,TRACK_X0-20):min(W,TRACK_X1+20)] = [10, 5, 18, 255]

    base = Image.fromarray(base_arr, "RGBA")

    # ── Draw on a transparent overlay ────────────────────────────────────────
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    if tx > TRACK_X0 + 2:
        # ── Progress/grow bar (thick, covers the track bar region) ───────────
        # Outer glow — wide halo
        for spread in range(14, 0, -1):
            alpha = int(20 + (14 - spread) * 12)
            draw.rectangle(
                [TRACK_X0, PROG_CY - spread - 2, tx, PROG_CY + spread + 2],
                fill=PROG_GLOW + (alpha,)
            )
        # Solid core bar — full height of track zone
        draw.rectangle(
            [TRACK_X0, PROG_Y0, tx, PROG_Y1],
            fill=PROG_CORE + (210,)
        )
        # Bright center stripe
        draw.rectangle(
            [TRACK_X0, PROG_CY - 2, tx, PROG_CY + 2],
            fill=PROG_TIP + (240,)
        )
        # Tip bloom
        if tx > TRACK_X0 + 10:
            bloom_w = 28
            for bx in range(max(TRACK_X0, tx - bloom_w), min(W, tx + bloom_w)):
                dist = abs(bx - tx)
                alpha = int(220 * (1 - dist / bloom_w) ** 2)
                draw.line(
                    [(bx, PROG_Y0 - 3), (bx, PROG_Y1 + 3)],
                    fill=PROG_TIP + (alpha,)
                )

        # ── Lightning bolt (top layer, multi-pass) ───────────────────────────
        bolt_cy = BOLT_CY

        # Pass 1: wide dark outer glow
        draw_bolt_layer(draw, rng, TRACK_X0, tx, bolt_cy,
                        amplitude=9, width=9, color=BOLT_OUTER, alpha_layer=90, segments=12)

        # Pass 2: mid purple
        draw_bolt_layer(draw, rng, TRACK_X0, tx, bolt_cy,
                        amplitude=7, width=5, color=BOLT_MID, alpha_layer=160, segments=16)

        # Pass 3: bright core
        draw_bolt_layer(draw, rng, TRACK_X0, tx, bolt_cy,
                        amplitude=4, width=2, color=BOLT_CORE, alpha_layer=230, segments=20)

        # Pass 4: thin bright centerline (sharpest)
        draw_bolt_layer(draw, rng, TRACK_X0, tx, bolt_cy,
                        amplitude=2, width=1, color=BOLT_CORE, alpha_layer=255, segments=24)

        # Branches (only if we have enough bar to branch from)
        if tx - TRACK_X0 > 80:
            n_b = rng.randint(2, 5)
            draw_branches(draw, rng, TRACK_X0, tx, bolt_cy, n_branches=n_b)

        # ── Flicker effect on tip (every 2-3 frames) ─────────────────────────
        if frame_idx % 3 != 0 and tx > TRACK_X0 + 30:
            flicker_w = rng.randint(20, 50)
            flicker_alpha = rng.randint(80, 180)
            fx0 = max(TRACK_X0, tx - flicker_w)
            draw.ellipse(
                [fx0, bolt_cy - 8, tx + 4, bolt_cy + 8],
                fill=BOLT_CORE + (flicker_alpha,)
            )

    # ── Composite: base + blur glow + sharp overlay ───────────────────────────
    # Blur the overlay for glow effect
    glow = overlay.filter(ImageFilter.GaussianBlur(radius=3))
    
    result = Image.alpha_composite(base, glow)
    result = Image.alpha_composite(result, overlay)  # sharp on top

    result.convert("RGB").save(out_path, "PNG", optimize=False)

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    total = TOTAL_FRAMES

    for i in range(1, total + 1):
        in_path  = os.path.join(IN_DIR,  f"frame{i:04d}.png")
        out_path = os.path.join(OUT_DIR, f"frame{i:04d}.png")

        if not os.path.exists(in_path):
            print(f"  SKIP: {in_path} not found")
            continue

        render_frame(i - 1, in_path, out_path)

        if i % 10 == 0 or i == total:
            pct = i / total * 100
            bar = "█" * (i // 6) + "░" * (20 - i // 6)
            print(f"\r  [{bar}] {i}/{total} ({pct:.0f}%)", end="", flush=True)

    print(f"\n  Done — {total} frames written to {OUT_DIR}")

if __name__ == "__main__":
    main()
