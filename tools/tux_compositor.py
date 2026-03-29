#!/usr/bin/env python3
"""
Pentoo Reaper Tux Plymouth Compositor
- Takes portrait 768x1365 source image
- Scales to 1920x1080 (blurred wide bg + sharp center)
- Adds www.pentoo.ch footer
- Animates growing teal lightning bolt progress bar
- Outputs 120 frames @ 24fps (5 seconds) for Plymouth
"""

import os
import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ── Config ───────────────────────────────────────────────────────────────────
SRC_PATH     = "/usr/share/plymouth/themes/pentoo/10742.png"
OUT_DIR      = "/usr/share/plymouth/themes/pentoo/tux_frames"
W, H         = 1920, 1080
TOTAL_FRAMES = 120   # 5s @ 24fps

# Bar geometry — bottom strip above footer
BAR_X0       = 160
BAR_X1       = 1760
BAR_WIDTH    = BAR_X1 - BAR_X0
BAR_Y0       = 980
BAR_Y1       = 1005
BAR_CY       = 992

# Footer
FOOTER_Y     = 1045
FOOTER_TEXT  = "www.pentoo.ch"

# Colors — teal/cyan Pentoo palette
COL_BORDER   = (0,   210, 200, 255)
COL_FILL     = (0,   160, 150, 200)
COL_CORE     = (100, 255, 240, 230)
COL_TIP      = (220, 255, 250, 255)
COL_GLOW     = (0,    80,  90, 150)
COL_BOLT     = (255, 255, 255, 255)
COL_BOLT2    = (80,  220, 210, 220)
COL_FOOTER   = (0,   200, 180, 180)

# ── Build base 1920x1080 frame ───────────────────────────────────────────────
def make_matrix_panel(panel_w, panel_h, seed=42):
    """Generate a matrix rain binary panel matching Pentoo source style."""
    rng = random.Random(seed)
    panel = Image.new("RGB", (panel_w, panel_h), (0, 5, 12))
    draw  = ImageDraw.Draw(panel)

    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 13)
    except:
        font = ImageFont.load_default()

    col_w   = 14    # column spacing px
    n_cols  = panel_w // col_w + 1
    chars   = "01"  # binary only, matching source artwork

    # Multiple streams per column at different speeds/offsets
    streams = []
    for c in range(n_cols):
        n_streams = rng.randint(1, 3)
        for _ in range(n_streams):
            streams.append({
                "col"    : c,
                "length" : rng.randint(8, 28),
                "offset" : rng.randint(0, panel_h),
                "speed"  : rng.uniform(0.4, 1.2),
                "bright" : rng.uniform(0.4, 1.0),
            })

    # Draw static snapshot (base frame — animation per-frame adds drift)
    char_h = 15
    for st in streams:
        cx = st["col"] * col_w + 2
        for row in range(st["length"]):
            cy = (st["offset"] + row * char_h) % panel_h
            # Head char = bright teal
            if row == 0:
                r, g, b = int(60*st["bright"]), int(220*st["bright"]), int(200*st["bright"])
            else:
                fade = 1.0 - row / st["length"]
                r = int(0   * fade * st["bright"])
                g = int(160 * fade * st["bright"])
                b = int(140 * fade * st["bright"])
            ch = rng.choice(chars)
            draw.text((cx, cy), ch, fill=(r, g, b), font=font)

    # Subtle scanline overlay
    for y in range(0, panel_h, 4):
        draw.line([(0, y), (panel_w, y)], fill=(0, 0, 0, 30))

    return panel

def build_base():
    src = Image.open(SRC_PATH).convert("RGB")
    sw, sh = src.size  # 768x1365

    # Scale Tux to fit 1080 height
    tux_h = H
    tux_w = int(sw * tux_h / sh)   # ~607
    tux   = src.resize((tux_w, tux_h), Image.LANCZOS)

    tux_x = (W - tux_w) // 2       # ~656

    # Dark base
    base = Image.new("RGB", (W, H), (0, 5, 12))

    # Left matrix panel
    left_panel  = make_matrix_panel(tux_x, H, seed=1)
    # Right matrix panel
    right_panel = make_matrix_panel(W - (tux_x + tux_w), H, seed=2)

    base.paste(left_panel,  (0, 0))
    base.paste(right_panel, (tux_x + tux_w, 0))

    # Soft gradient blend at Tux edges so it doesn't hard-cut
    tux_arr  = np.array(tux).astype(float)
    base_arr = np.array(base)

    # Paste Tux
    base.paste(tux, (tux_x, 0))

    # Feather left edge of Tux into matrix panel (30px fade)
    fade_w = 40
    base_arr = np.array(base).astype(float)
    for i in range(fade_w):
        alpha = i / fade_w
        col_src = tux_x + i
        col_mat = col_src
        if col_mat < W:
            mat_col  = np.array(left_panel)[:, min(i, left_panel.width-1)].astype(float)
            base_arr[:, col_src] = (
                base_arr[:, col_src] * alpha +
                mat_col * (1 - alpha)
            )
    # Feather right edge
    right_start = tux_x + tux_w
    rp_arr = np.array(right_panel)
    for i in range(fade_w):
        alpha = i / fade_w
        col_src = right_start - 1 - i
        if col_src >= 0:
            rp_col_idx = min(i, rp_arr.shape[1]-1)
            rp_col = rp_arr[:, rp_col_idx].astype(float)
            base_arr[:, col_src] = (
                base_arr[:, col_src] * alpha +
                rp_col * (1 - alpha)
            )

    base_out = Image.fromarray(np.clip(base_arr, 0, 255).astype(np.uint8))
    # Store tux position for use in render
    base_out._tux_x = tux_x
    base_out._tux_w = tux_w
    return base_out

# ── Font ─────────────────────────────────────────────────────────────────────
def get_font(size):
    for path in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

# ── Progress easing ──────────────────────────────────────────────────────────
def progress(idx):
    t = idx / (TOTAL_FRAMES - 1)
    if t < 0.5:
        return 4 * t * t * t
    p = -2 * t + 2
    return 1 - (p * p * p) / 2

def tip_x(prog):
    return int(BAR_X0 + prog * BAR_WIDTH)

# ── Jagged bolt ──────────────────────────────────────────────────────────────
def jagged(rng, x0, x1, cy, amp, segs):
    pts = [(x0, cy)]
    sw = (x1 - x0) / segs
    for i in range(1, segs):
        fade = 1.0 - (i / segs) ** 1.5
        pts.append((x0 + i * sw,
                    cy + rng.uniform(-amp * fade, amp * fade)))
    pts.append((x1, cy))
    return pts

def draw_lightning(draw, rng, x0, x1, cy):
    if x1 <= x0 + 4:
        return
    # Outer purple glow
    for pts in [jagged(rng, x0, x1, cy, 10, 8)]:
        for i in range(len(pts)-1):
            draw.line([pts[i], pts[i+1]], fill=(0,100,120,50), width=12)
    # Mid teal
    for pts in [jagged(rng, x0, x1, cy, 7, 14)]:
        for i in range(len(pts)-1):
            draw.line([pts[i], pts[i+1]], fill=COL_BOLT2[:3]+(160,), width=5)
    # Core white
    for pts in [jagged(rng, x0, x1, cy, 4, 20)]:
        for i in range(len(pts)-1):
            draw.line([pts[i], pts[i+1]], fill=COL_BOLT[:3]+(220,), width=2)
    # Spine
    for pts in [jagged(rng, x0, x1, cy, 2, 26)]:
        for i in range(len(pts)-1):
            draw.line([pts[i], pts[i+1]], fill=(255,255,255,255), width=1)

    # Downward branches from leading half
    if x1 - x0 > 60:
        for _ in range(rng.randint(2, 6)):
            bx = rng.randint(max(x0, x1-300), x1)
            by = cy + rng.randint(-4, 4)
            ln = rng.randint(15, 50)
            ang = rng.uniform(30, 150)
            ex = int(bx + ln * math.cos(math.radians(ang)))
            ey = int(by + ln * math.sin(math.radians(ang)))
            a = rng.randint(80, 200)
            draw.line([(bx,by),(ex,ey)],
                      fill=COL_BOLT2[:3]+(a,), width=1)

# ── Render frame ─────────────────────────────────────────────────────────────
def render_frame(idx, base, font_footer, font_bar, out_path):
    rng  = random.Random(idx * 5003 + 7)
    prog = progress(idx)
    tx   = tip_x(prog)

    img = base.copy().convert("RGBA")
    ov  = Image.new("RGBA", (W, H), (0,0,0,0))
    draw = ImageDraw.Draw(ov)

    # ── Footer text ──
    bbox = font_footer.getbbox(FOOTER_TEXT)
    fw = bbox[2] - bbox[0]
    fx = (W - fw) // 2
    # Subtle glow behind text
    for offset in range(6, 0, -2):
        a = 20 + (6-offset)*15
        draw.text((fx, FOOTER_Y), FOOTER_TEXT,
                  font=font_footer,
                  fill=COL_FOOTER[:3]+(a,))
    draw.text((fx, FOOTER_Y), FOOTER_TEXT,
              font=font_footer, fill=COL_FOOTER)

    # ── Bar track border ──
    draw.rectangle([BAR_X0-2, BAR_Y0-2, BAR_X1+2, BAR_Y1+2],
                   outline=COL_BORDER[:3]+(80,), width=1)

    if tx > BAR_X0 + 4:
        # Outer glow
        for sp in range(14, 0, -2):
            a = int(12 + (14-sp)*9)
            draw.rectangle([BAR_X0, BAR_Y0-sp, tx, BAR_Y1+sp],
                           fill=COL_GLOW[:3]+(a,))
        # Fill
        draw.rectangle([BAR_X0, BAR_Y0, tx, BAR_Y1], fill=COL_FILL)
        # Core stripe
        draw.rectangle([BAR_X0, BAR_CY-2, tx, BAR_CY+2],
                       fill=COL_CORE[:3]+(200,))
        # Tip bloom
        bloom = 40
        for bx in range(max(BAR_X0, tx-bloom), min(W, tx+bloom)):
            dist = abs(bx - tx)
            a = int(240 * (1 - dist/bloom)**2)
            draw.line([(bx, BAR_Y0-5), (bx, BAR_Y1+5)],
                      fill=COL_TIP[:3]+(a,))
        # Lightning bolt
        draw_lightning(draw, rng, BAR_X0, tx, BAR_CY)

        # Tip flicker
        if idx % 3 != 0 and tx > BAR_X0 + 40:
            fa = rng.randint(60, 160)
            fw2 = rng.randint(20, 55)
            draw.ellipse([tx-fw2, BAR_CY-10, tx+8, BAR_CY+10],
                         fill=COL_TIP[:3]+(fa,))

    # ── Animated matrix rain on side panels ──
    src      = Image.open(SRC_PATH).convert("RGB")
    sw, sh   = src.size
    tux_h    = H
    tux_w    = int(sw * tux_h / sh)
    tux_x    = (W - tux_w) // 2

    try:
        mfont = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 13)
    except:
        mfont = ImageFont.load_default()

    chars  = "01"
    col_w  = 14
    char_h = 15
    drift  = idx * 3   # pixels dropped per frame

    for panel_x, panel_w, pseed in [
        (0,          tux_x,          1),
        (tux_x+tux_w, W-(tux_x+tux_w), 2),
    ]:
        prng = random.Random(pseed)
        n_cols = panel_w // col_w + 1
        streams = []
        for c in range(n_cols):
            for _ in range(prng.randint(1, 3)):
                streams.append({
                    "col"   : c,
                    "len"   : prng.randint(8, 28),
                    "offset": prng.randint(0, H),
                    "speed" : prng.uniform(0.4, 1.2),
                    "bright": prng.uniform(0.4, 1.0),
                    "chars" : [prng.choice(chars) for _ in range(30)],
                })
        for st in streams:
            cx = panel_x + st["col"] * col_w + 2
            spd_drift = int(drift * st["speed"])
            for row in range(st["len"]):
                cy = (st["offset"] + spd_drift + row * char_h) % H
                if row == 0:
                    r = int(60  * st["bright"])
                    g = int(220 * st["bright"])
                    b = int(200 * st["bright"])
                else:
                    fade = 1.0 - row / st["len"]
                    r = 0
                    g = int(160 * fade * st["bright"])
                    b = int(140 * fade * st["bright"])
                ch = st["chars"][(row + idx) % len(st["chars"])]
                draw.text((cx, cy), ch, fill=(r, g, b, 200), font=mfont)

    # ── Scythe arc glow pulse (ties animation to the scythe) ──
    # Subtle teal glow pulse on right side where scythe blade is (~x=1350-1700, y=300-750)
    pulse = 0.5 + 0.5 * math.sin(idx * 0.2)
    scythe_glow = Image.new("RGBA", (W, H), (0,0,0,0))
    sg = ImageDraw.Draw(scythe_glow)
    sg_alpha = int(20 + pulse * 30)
    sg.ellipse([1300, 280, 1750, 780],
               fill=(0, 220, 200, sg_alpha))
    scythe_blur = scythe_glow.filter(ImageFilter.GaussianBlur(radius=30))

    # ── Composite ──
    glow = ov.filter(ImageFilter.GaussianBlur(radius=3))
    result = Image.alpha_composite(img, scythe_blur)
    result = Image.alpha_composite(result, glow)
    result = Image.alpha_composite(result, ov)

    result.convert("RGB").save(out_path, "PNG")

# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    print("Building base frame...")
    base = build_base()
    base.save("/mnt/user-data/outputs/tux_base_1920.png")

    font_footer = get_font(28)
    font_bar    = get_font(18)

    print(f"Rendering {TOTAL_FRAMES} frames...")
    for i in range(TOTAL_FRAMES):
        out_path = os.path.join(OUT_DIR, f"frame{i+1:04d}.png")
        render_frame(i, base, font_footer, font_bar, out_path)

        if (i+1) % 12 == 0 or i+1 == TOTAL_FRAMES:
            pct = (i+1)/TOTAL_FRAMES*100
            bar = "█"*((i+1)//6) + "░"*(20-(i+1)//6)
            print(f"\r  [{bar}] {i+1}/{TOTAL_FRAMES} ({pct:.0f}%)",
                  end="", flush=True)

    print(f"\nDone — frames in {OUT_DIR}")

if __name__ == "__main__":
    main()
