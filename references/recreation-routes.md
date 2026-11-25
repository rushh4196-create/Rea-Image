# High-Fidelity Recreation Routes & Multi-Pass Convergence Playbook

Every recreation follows **Measure -> Audit Physics -> Generate/Render -> Verify Diff -> Surgical Fix -> Calibrate** until visual and quantitative parity converge.

## Route A: Reference-Locked Multi-Pass Generative Recreation

Best for: Real Photos, AI Art, 3D Renders, 2D Illustrations, and Photographic Collages.

1. **Pass 1**: Pass the reference image in `image_references` when available (omit `aspect_ratio` to lock original proportions) and write a coordinate-locked, physics-checked forensic prompt citing exact orientation, `[x%, y%]` bounding zones, 9-zone hex/luminance anchors, camera focal length/DOF, lighting vectors, and tone curve.
2. **Verify**: Run `scripts/verify_clone.py` and inspect `comparison.png` + `auto_fix_directives` + `worst_zones`.
3. **Passes 2-3 (Surgical Delta-Fix)**: Fix ONLY the drifted zones (subject position/scale, pose/anatomy physics, cloud/background shape, shadow depth, or lighting wrap) while keeping already-matched zones locked.
4. **LAB Calibration**: Run `scripts/calibrate_clone.py --strength 0.65` to `0.80` whenever global exposure, contrast, or color temperature drifts, then re-verify with `verify_clone.py`.

## Route B: Pixel-Exact Deterministic Code Recreation

Best for: UI Screenshots, Data Charts, Diagrams, Infographics, Flat Vector Graphics, Logos, and Typographic Posters.

1. Match exact pixel canvas (`W x H`) from `forensics/report.json`.
2. Sample exact hex codes for every background, border, button, icon, and text span directly from the reference pixels.
3. Measure exact bounding boxes (`x, y, w, h`) from `grid_overlay.png` or Python pixel probes.
4. Render at exact `W x H` via HTML+CSS (headless Chromium/Playwright or WeasyPrint), SVG (CairoSVG), or Python (Matplotlib/Pillow).
5. Run `verify_clone.py` and inspect the 4x diff heatmap (`comparison.png`). Fix every bright red edge shift (even 1-3px) and re-render up to 4 passes until the diff heatmap converges.

## Route C: Two-Stage Hybrid Compositing

Best for: YouTube Thumbnails, Ad Creatives, Magazine Covers, Product Banners, and Memes.

1. **Stage 1 (Base Visual)**: Recreate the clean base layer (no text/badges/UI) via Route A with locked lighting, framing, physics, and 9-zone palette.
2. **Stage 2 (Programmatic Overlays)**: Composite crisp verbatim text, exact font weight/stroke/drop-shadow, badges, frames, and icons at exact pixel coordinates on top of the base image using HTML+CSS or Pillow at exact `W x H`.
3. **Stage 3 (Verify & Calibrate)**: Run `verify_clone.py`, iterate overlay coordinates until pixel-aligned, and optionally apply `calibrate_clone.py` to match the final color grade.

## Route D: Pixel-Preserving Compositing

Best for: Localized edits, clean swaps, framing extensions, or color adjustments where unchanged regions must remain bit-exact.

1. Keep the original image as the exact base canvas (`W x H`).
2. Isolate only the target edit region and render or generate strictly the changed element.
3. Composite cleanly with feathered alpha, matched grain, and matched lighting, then verify untouched zones show zero drift (`Delta-E = 0.0`).

## Controlled Swap / Remix Mode

When the user asks to keep the exact layout/style while replacing specific elements (subject, product, or text):

- Keep all measured forensic anchors locked (camera angle, 9-zone palette, lighting vectors, tone curve, typography, and grid layout).
- Modify strictly the requested swap while preserving realistic contact shadows, light wrap, and depth-of-field blur.
