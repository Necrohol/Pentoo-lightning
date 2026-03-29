# Pentoo Plymouth Theme — Luma AI Video Prompts

Documentation for `sys-boot/plymouth-theme-pentoo` and `sys-boot/plymouth-theme-pentoo-skulls`.
Used to generate source MP4 animations for compositor pipeline.

---

## pentoo-lightning — Main Theme

**Status:** v2 generated, compositor in progress  
**Palette:** Teal, white, deep navy  
**File:** `Pentoo_Linux_Boot_5hRMSmkR.mp4`

### Prompt (current best)

```
Pentoo Linux boot splash animation, 1920x1080, cinematic.
Center frame: hooded grim reaper penguin mascot in black cloak
holding a glowing teal energy scythe, menacing pose.
Top center: "PENTOO LINUX" text in white glitch/tech blocky font
with cyan glow.
Upper left: large prominent teal pentoo lock shield logo,
approximately 120x120px, glowing cyan outline, clearly visible
watermark-style in the upper left quadrant —
[pentoo lock branding at https://cdn.sanity.io/images/g1k8g2c7/production/a31bee7ce930edca89a300da46b3e02373db5255-376x376.webp]
Background: deep navy black with faint green cascading matrix code
rain and cyan circuit board trace lines.
Bottom third: a single thin horizontal rectangular progress bar,
fixed position, sharp teal/cyan 2px border, starts empty, fills
left to right over 5 seconds with bright teal electric charge.
The leading edge of the fill emits jagged white-cyan lightning bolts
branching downward striking the floor. Lightning intensity tracks
the fill — sparse at start, violent crackling at full charge.
Bar completes full at end of clip.
Teal, white, deep navy only. High contrast, dramatic lighting.
No secondary bars. No overlapping elements on the bar.
```

### Known Issues / Iteration Notes

- v1: Double progress bar generated, lightning static/not tracking fill
- v2: Lightning glow improved, icon too small, bar drift still present
- v3 target: Icon size fix, bar growth locked left-to-right, lightning tip-tracked

### Compositor Pipeline

- Source: `Pentoo_Linux_Boot_5hRMSmkR.mp4` → 120 frames @ 24fps, 1920x1080
- Script: `bolt_compositor.py`
- Track bar: rows 920–941, x=92–1827
- Bolt centerline: row 930
- Output: `outframes/frame0001.png` → `frame0120.png`
- Ebuild: `sys-boot/plymouth-theme-pentoo-9999`

---

## pentoo-skulls — Skulls Theme

**Status:** Prompt ready, not yet generated  
**Palette:** Black, red, orange, bone white. No blue. No teal.  
**File:** TBD

### Prompt

```
Pentoo Linux boot splash animation, 1920x1080, cinematic.
Top center: "💀PENTOO LINUX💀" in white glitch/tech blocky font
with menacing red glow and skull emoji flanking.
Upper left: large prominent pentoo lock shield logo approximately
120x120px, red/orange glow, clearly visible —
[pentoo lock branding at https://cdn.sanity.io/images/g1k8g2c7/production/a31bee7ce930edca89a300da46b3e02373db5255-376x376.webp]
Right side: hooded grim reaper penguin mascot with single glowing
red Terminator eye visible under hood, holding scythe,
overlooking the battlefield.
Background: dark apocalyptic scorched earth, burning horizon,
red sky, faint Skynet HUD targeting reticles overlaid.
Random plasma bolt strikes rake across the battlefield from above
at intervals — bright white-orange-red plasma arcs.
Bottom third: a Terminator HK-Tank rolls left to right across
scorched ground, crushing a trail of skulls beneath its treads
as it advances — intact skulls on the right, crushed flat on
the left marking progress. Tank headlights blaze white.
Red Skynet targeting HUD overlay on tank. Smoke and plasma fire
erupt from skull contact point at treads.
Starts empty right side full of skulls, tank completes full
crossing at clip end.
Deep black, red, orange, bone white palette only.
High contrast, cinematic, dramatic. No blue. No teal.
```

### Compositor Pipeline (planned)

- Two zones: left of tank = crushed skulls (dark, flat), right = intact (raised, lit)
- Tank x-position = progress position
- Plasma fire: per-frame procedural at tread contact point
- Ebuild: `sys-boot/plymouth-theme-pentoo-skulls-9999`

---

## Reference Assets

| Asset | URL |
|-------|-----|
| Pentoo lock logo | https://cdn.sanity.io/images/g1k8g2c7/production/a31bee7ce930edca89a300da46b3e02373db5255-376x376.webp |
| Pentoo GRUB splash reference | https://www.tecmint.com/wp-content/uploads/2013/11/Pentoo-Linux-Live.png |

---

## Ebuild Locations

```
overlay/
  sys-boot/
    plymouth-theme-pentoo/
      plymouth-theme-pentoo-9999.ebuild
      files/
        plymouthd.conf.example
    plymouth-theme-pentoo-skulls/
      plymouth-theme-pentoo-skulls-9999.ebuild
      files/
        plymouthd.conf.example
```

---

*Part of pentoo-custom overlay — https://github.com/Necrohol/pentoo-custom*
