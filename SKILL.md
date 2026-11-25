---
name: rea-image
description: Deeply reverse-engineer any image with deterministic forensics, optical and physical realism analysis, and closed-loop multi-pass reconstruction to achieve maximum 1:1 visual parity (exact same to same) or controlled swaps. Extracts exact dimensions, aspect ratio, metadata, 12-color global and 9-zone spatial hex palettes, tone curves, directional lighting, sharpness/grain, and 6x6 coordinate grids; audits camera optics, lighting physics, materials, and anatomy; routes across Reference-Locked Generation, Pixel-Exact Code (HTML/CSS/SVG/Python), Two-Stage Hybrid, or Pixel-Preserving Compositing; and iterates with per-zone SSIM, edge correlation, LAB Delta-E, auto-fix directives, 4x diff heatmaps, and LAB color calibration. Use whenever the user shares or links an image to copy exact same to same, clone or recreate it, reverse-engineer how it was made, or remake any poster, thumbnail, UI, chart, photo, or artwork.
---
# rea-image

Reverse-engineer any image with deep deterministic forensics, optical/physical analysis, and closed-loop multi-pass reconstruction to achieve maximum 1:1 visual parity ("exact same to same").

Core principle: measure every pixel property deterministically, pin every object to exact coordinates, enforce realistic lighting/camera/material/anatomy physics, route to the exact production medium of the image, and verify every pass quantitatively against a 4x difference heatmap before delivering.

## When to Use

- The user wants to copy, clone, or recreate any image "exact same to same"
- The user asks how an image was made (real photo, AI-generated, 3D render, 2D illustration, vector, UI, infographic, poster, collage, or hybrid)
- The user wants an exact forensic breakdown (dimensions, 9-zone hex palette, tone curve, lighting vectors, lens/DOF, typography, and layout coordinates)
- The user wants to recreate an image with controlled swaps (changing text, subject, or product while locking all other forensic parameters)

## Complete 6-Stage Workflow

### Stage 1: Acquire Reference Pixels & Deep Forensic Extraction

Whenever the user supplies a local or uploaded image file, run the bundled forensic inspector before any visual guessing:

```bash
python3 scripts/inspect_image.py <reference_image> --out <work_dir>/forensics
```

If the user supplies only a web URL whose raw image file is not directly accessible locally, retrieve the highest-resolution view available or ask the user to attach the image file so full pixel-level forensics and diff verification can run.

`inspect_image.py` outputs:

- `forensics/report.json`: exact `W x H`, nearest standard aspect ratio, EXIF/PNG/XMP/AIGC metadata, global 12-color hex palette, **9-zone (3x3) spatial dominant hex + luminance + saturation map**, tone-curve percentiles (`p02`, `p15`, `p50`, `p85`, `p98`), color temperature (`R-B`), directional lighting balance, sharpness/grain index (Laplacian variance), edge density, and flat-region ratio
- `forensics/grid_overlay.png`: fine 6x6 coordinate grid with exact pixel `x,y` and `%` markers for locking bounding boxes
- `forensics/tiles_3x3.png`: 3x3 high-res tile sheet for inspecting micro-text, eyes, fingers, brushwork, grain, and specular highlights

### Stage 2: Forensic Visual Review, Physics Audit & Classification

Inspect the original image alongside `forensics/grid_overlay.png` and `forensics/tiles_3x3.png`. Classify into one of the 10 classes in `references/taxonomy.md` and audit every physical/optical property using `references/physics-and-optics.md`.

Record the complete forensic blueprint in `<work_dir>/IMAGE.md`:

1. **Classification & Hard Evidence**: Image class, forensic signals (EXIF, AIGC chunks, flat-region ratio, Laplacian grain), and visual signals.
2. **Canvas, Tone & 9-Zone Color Map**: Exact `W x H`, aspect ratio, tone-curve black/mid/white points, color temperature, and exact top hex codes + mean luminance for all 9 spatial zones.
3. **6x6 Coordinate-Locked Layout**: Pin every subject, prop, horizon line, cloud/light source, and text box to exact `[x1%-x2%, y1%-y2%]` ranges and orientation/rotation angle.
4. **Optics & Realistic Physics Audit**:
   - Camera focal length, vantage angle, perspective vanishing points, and depth-of-field plane (what is razor-sharp vs. foreground/background bokeh blur)
   - Primary key light direction/softness, secondary fill/ambient color, rim/backlighting wrap, and shadow falloff
   - Physical realism: gravity, fabric drape/creases, natural hand/finger/joint anatomy, stem/object weight, surface micro-texture, and reflection/refraction consistency
5. **Typography & Overlays (if any)**: Verbatim text strings (spelling, case, line breaks), font family/weight/tracking, fill/stroke/shadow hex, badges, icons, and borders.

### Stage 3: Route to the Highest-Fidelity Pipeline

Choose the matching pipeline from `references/recreation-routes.md`:

- **Route A - Reference-Locked Multi-Pass Generative Recreation** (Real Photo, AI-Generated, 3D Render, 2D Illustration, Photographic Collage):
  Pass the reference image in `image_references` when available (omit `aspect_ratio` to lock original proportions) and supply a dense coordinate-locked, physics-checked forensic prompt anchoring the 9-zone palette, exact bounding zones, camera optics, and lighting vectors. If generating from text only, encode all 9 spatial zones and exact `[x%, y%]` placements explicitly.

- **Route B - Pixel-Exact Deterministic Code Recreation** (UI Screenshot, Data Chart, Diagram, Infographic, Flat Vector Graphic, Logo, Typographic Poster):
  Rebuild in HTML+CSS (rendered via headless Chromium/Playwright or WeasyPrint), SVG (CairoSVG), or Python (Matplotlib/Pillow) at exact `W x H` using exact sampled hex codes, measured pixel bounding boxes, and verbatim typography.

- **Route C - Two-Stage Hybrid Compositing** (YouTube Thumbnails, Ad Creatives, Magazine Covers, Product Banners, Memes):
  Stage 1: Recreate the clean base visual (no text/UI overlays) via Route A.
  Stage 2: Render crisp verbatim typography, strokes, shadows, badges, and borders programmatically at exact `W x H` via HTML+CSS or Pillow.

- **Route D - Pixel-Preserving Compositing** (Localized Edits, Swaps, Restoration, Color/Crop Adjustments):
  Preserve untouched regions bit-for-bit on the exact `W x H` canvas and composite only the modified region with matched lighting, grain, and color grade.

### Stage 4: Closed-Loop Verification & Surgical Refinement (Up to 3 Passes)

After EVERY pass, run the bundled verifier against the reference image:

```bash
python3 scripts/verify_clone.py <reference_image> <recreated_image> --out <work_dir>/verify_p1
```

Inspect `verify_p1/comparison.png` (Reference | Recreated | 4x Amplified Diff Heatmap with worst-zone boxes) and `verify_p1/metrics.json` (`block_ssim_0_1`, `edge_correlation_0_1`, `color_histogram_similarity_0_1`, `mean_lab_delta_e`, `global_luminance_bias`, `worst_zones`, `auto_fix_directives`).

Iterate up to 3 refinement passes (up to 4 for Route B code) whenever `comparison.png` or `auto_fix_directives` show fixable drift:

1. **Structural / Physics Fixes**: Address every concrete zone error (position shift, scale mismatch, angle/rotation, missing detail, unrealistic hand/fabric/lighting physics, or cloud/background shape) using surgical delta-fix prompts (Route A/C) or exact coordinate/CSS/SVG adjustments (Route B/D).
2. **Color & Dimension Calibration**: When structure aligns but exposure, contrast, or color temperature drifts, run the bundled LAB calibrator:

```bash
python3 scripts/calibrate_clone.py <reference_image> <recreated_image> --out <work_dir>/calibrated.png --strength 0.70
```

3. **Re-Verify**: Run `verify_clone.py` after each fix or calibration and keep whichever candidate scores highest both visually and quantitatively.

### Stage 5: Final Inspection & Clean Delivery

- Verify the final output visually for realistic physics (natural anatomy, gravity, light wrap, bokeh consistency, crisp text) and zero unintended artifacts.
- Present the final recreated image cleanly.
- Report the concise forensic summary (class, exact `W x H`, route used, passes run) alongside actual measured metrics (`SSIM`, `Edge Correlation`, `Color Histogram Similarity`, `CIE LAB Delta-E`).
- Clean up temporary scratch directories after delivering unless the user asked to keep the forensic bundle.

## Gotchas

- **Never eyeball hex codes, dimensions, or placements.** Always read exact values from `scripts/inspect_image.py` and `grid_overlay.png`.
- **Never skip `verify_clone.py` after Pass 1.** The 4x diff heatmap and `auto_fix_directives` immediately expose subtle shifts in scale, exposure, and color balance that casual inspection misses.
- **Do not use pure diffusion for pixel-exact UIs, charts, vectors, or typographic posters.** Route B code rendering locks crisp edges, alignment, and exact typography.
- **Always enforce physical realism.** Check focal-plane blur, rim-light direction, shadow softness, fabric drape, and hand/limb anatomy before accepting any pass.
