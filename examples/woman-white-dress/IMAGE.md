# IMAGE.md — Forensic Blueprint (rea-image, Stage 2)
Reference: examples/woman-white-dress/reference.jpg (cloudyx_art style reference) (cloudyx_art style)
Work dir: examples/woman-white-dress/

## 1. Classification & Hard Evidence
- Class: **2. AI-Generated** (Route A). No EXIF/camera signals, no AIGC metadata (stripped by Instagram upload), smooth shadow transitions, flat-region ratio 0.83, hyper-clean diffused lighting, surreal 90°-rotated composition.
- Canvas: **720 x 1280, 9:16 vertical**. File 86,998 bytes, JPEG, JFIF only.

## 2. Canvas, Tone & 9-Zone Color Map
- Tone curve: p02 black 15.8, p15 shadows 27.5, p50 midtones 91.9 (dark), p85 highlights 176.9, p98 white 228.8.
- Color temperature: **COOL**, R-B = -36.26. Mean saturation 0.38.
- Palette (top 12): #355E65 11.4%, #111412 11.4%, #204C53 11.2%, #82A9B0 9.4%, #648D95 9.3%, #42707A 8.7%, #A5CFD8 7.7%, #121F1C 7.0%, #597C80 7.0%, #282B27 6.8%, #BFE8F0 6.4%, #364D4D 3.7%. No red in top 12 — the red flowers are a tiny fraction of pixels.
- 9-zone luminance: top-left 50.6 (dark grass), top-center 210.7 (brightest — sky glow), top-right 153.0, mid-left 46.8, center 136.7 (woman + sky), mid-right 94.8, bottom-left 37.6 (darkest — grass + red flowers in shadow), bottom-center 113.6, bottom-right 68.7.
- Lighting balance: brighter RIGHT (-37.1) and brighter TOP (+50.9) — key light from top-right, soft and diffused.

## 3. 6x6 Coordinate-Locked Layout (from grid_overlay.png)
- Grassy field edge: vertical band x 0–33%, y 0–100%, dark teal-black with fine dry grass tips; tiny deep-red flowers scattered in the bottom-left (x 0–25%, y 55–100%).
- Woman: lying horizontally across the middle, body x 16–58%, y 40–66%; head at x 48–58%, y 42–52%, dark hair in a low bun, face turned away/up (no facial detail); flowing white dress, fabric draping toward the ground (left); one arm raised up-left, hand relaxed at x ~33%, y ~38%.
- Sky: fills x 33–100%, y 0–100%; pale near-white blue at top-center, deepening to teal at bottom-right.
- Clouds: soft, small — one at top-right (x 66–100%, y 8–30%), one at mid-right/bottom-center (x 33–66%, y 55–85%), warm-tinted edges.
- Watermark: "CLOUDYX.ART" vertical text at x ~8–12%, y ~38–62% — PRESENT in reference; do NOT reproduce in recreations (our rule).

## 4. Optics & Realistic Physics Audit
- Camera: eye-level wide shot, 90° rotated composition (ground edge vertical); deep depth of field — woman + near grass sharp (Laplacian variance 400.6), sky/clouds soft; no visible lens distortion.
- Light: single soft key from top-right; warm rim light on dress edges, hair, and grass tips; shadows cool teal (sky bounce), never neutral black.
- Physics: woman lies flat on the ground (gravity-correct); dress fabric drapes toward the ground on the left; hair falls toward the ground; raised arm has a natural relaxed hand (fingers slightly curled, no extra digits); grass stems bend slightly in one consistent direction; red flowers sit IN the grass at ground level, not floating.
- Materials: dress is translucent white cotton (light passes through the skirt edge); grass is dry, fine, golden-brown tips; skin is soft with no harsh specular highlights.

## 5. Typography & Overlays
- Only the vertical "CLOUDYX.ART" watermark (excluded from recreations). No other text.
