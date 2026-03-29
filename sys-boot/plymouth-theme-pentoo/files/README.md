# Pentoo Lightning Theme

> *Reaper Tux stands guard while the matrix rains and lightning charges the boot.*

---

## Synopsis

Artwork generated with **HeyGen.com** — prompted with Pentoo branding, Reaper Tux mascot,
glowing scythe, dark matrix background. Luma Dream Machine was used for early lightning
animation experiments (see Luma board below) but the loading bar animation was off and
credits ran out before a clean version could be generated.

**Claude AI** then took the static HeyGen illustration and scripted:
- A growing **teal lightning bolt progress bar** (left to right, branching downward strikes)
- Animated **binary matrix rain side panels** (`01` columns drifting down, matching artwork style)
- Scythe glow pulse, `www.pentoo.ch` footer

MP4 sliced to key frames — GStreamer can flake so reduced to PNG frame sequence for
maximum Plymouth compatibility.

Both themes have a `prompts.md` documenting all AI prompts used — HeyGen took more
prodding to get right.

---

## Asset Sources

| Asset | Tool | Link |
|-------|------|------|
| Reaper Tux illustration | HeyGen AI | https://heygen.com |
| Lightning animation experiments | Luma Dream Machine | https://app.lumalabs.ai/board/43b5387c-a0d9-4a8c-a51e-d46d4680db4c |
| Original Luma Tux Reaper session | Luma / Claude AI | https://claude.ai/a8dcf620-fa2a-4324-846e-d19de73ecb8c |
| Compositor / matrix rain / bolt bar | Claude AI + Python/Pillow | `tools/tux_compositor.py` |

---

## Preview Frames

<!-- Edit locally — replace paths with your hosted images or relative paths -->

| Start | 25% | 50% | 75% | Full |
|-------|-----|-----|-----|------|
| ![f001](sources/preview/frame_001.png) | ![f030](sources/preview/frame_030.png) | ![f060](sources/preview/frame_060.png) | ![f090](sources/preview/frame_090.png) | ![f120](sources/preview/frame_120.png) |

---

## Source MP4

<!-- Edit locally — embed player or link -->

```
sources/pentoo-lightning-v2.mp4
```

---

## Theme Details

| Property | Value |
|----------|-------|
| Name | `pentoo` |
| Frames | 120 @ 24fps |
| Duration | 5 seconds |
| Resolution | 1920x1080 |
| License | GPL-2 / Artistic-2 |

---

## Quick Install

```bash
emerge sys-boot/plymouth-theme-pentoo
plymouth-set-default-theme -R pentoo
```

Add to kernel cmdline: `quiet splash`

---

## GStreamer Mode (optional)

GStreamer Plymouth can flake — frame-PNG is default and most compatible.
To enable MP4 direct playback:

```bash
# /etc/portage/package.use
sys-boot/plymouth gstreamer
sys-boot/plymouth-theme-pentoo gstreamer
```

```bash
emerge sys-boot/plymouth sys-boot/plymouth-theme-pentoo
plymouth-set-default-theme -R pentoo-gst
```

---

## Compositor Pipeline

```bash
# Regenerate 120 frames from source illustration
python3 tools/tux_compositor.py

# Re-encode MP4
ffmpeg -framerate 24 -i frame%04d.png \
  -c:v libx264 -crf 18 -preset slow \
  -pix_fmt yuv420p -movflags +faststart \
  pentoo-lightning-v2.mp4

# Deploy frames to overlay
cp tux_frames/frame*.png /path/to/pentoo-custom/plymouth/pentoo/
```

---

## Prompt Documentation

See `docs/prompts.md` for all Luma Dream Machine and HeyGen prompts,
iteration notes, and what worked vs what didn't.

---

## Notes

- Pentoo GRUB splash work predates this — binary rain with water effects
  was attempted ~1 year prior; Plymouth theming is getting much easier
  to prompt-engineer as AI video tools mature.
- AI text-to-image first attempts had great matting but the loading bar
  missed — compositor approach solved this cleanly.

---

## License

- Ebuilds / compositor scripts: **GPL-2**
- Theme artwork / AI-generated assets: **Artistic License 2.0**

---

*Pentoo Project — https://www.pentoo.ch*  
*Overlay — https://github.com/Necrohol/pentoo-custom*
